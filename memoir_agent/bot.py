"""Telegram front end: one group shared by Matthew, co-writers and peer agents."""
from __future__ import annotations

import asyncio
import os
from pathlib import Path

from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from .agent import MemoirAgent, build_options, build_server
from .memory import MemoryStore
from .peers import PeerHub, load_peers


def route(hub: PeerHub, allowed: set[str], username: str | None, text: str) -> str:
    """Classify an incoming group message: 'peer_reply', 'direct' (authorized human) or 'ignore'."""
    if hub.is_peer_username(username):
        return "peer_reply"
    if username and username.lower() in allowed:
        return "direct"
    return "ignore"


def main() -> None:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = int(os.environ["TELEGRAM_CHAT_ID"])
    allowed = {u.strip().lstrip("@").lower() for u in os.environ["ALLOWED_USERS"].split(",") if u.strip()}
    root = Path(os.environ.get("MEMOIR_DIR", "memoir"))

    async def run() -> None:
        app = Application.builder().token(token).build()

        async def send(text: str) -> None:
            await app.bot.send_message(chat_id, text)

        hub = PeerHub(
            load_peers(Path(os.environ.get("PEERS_FILE", "peers.json"))),
            send,
            float(os.environ.get("PEER_TIMEOUT_SECONDS", "120")),
        )
        store = MemoryStore(root / "memories")
        options = build_options(build_server(store, hub, root / "manuscript"))

        async with MemoirAgent(options) as agent:

            async def on_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
                msg = update.effective_message
                if not msg or not msg.text or msg.chat_id != chat_id:
                    return
                user = msg.from_user.username if msg.from_user else None
                kind = route(hub, allowed, user, msg.text)
                if kind == "peer_reply":
                    hub.deliver(user, msg.text)
                elif kind == "direct":
                    # Run in the background so peer replies can be delivered while the agent waits.
                    asyncio.create_task(_answer(user, msg.text))

            async def _answer(user: str, text: str) -> None:
                await send(await agent.reply(user, text))

            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))
            async with app:
                await app.start()
                await app.updater.start_polling()
                await asyncio.Event().wait()

    asyncio.run(run())


if __name__ == "__main__":
    main()
