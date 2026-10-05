"""Telegram front end: one group shared by Matthew, co-writers and peer agents."""
from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path

from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from .agent import MemoirAgent, build_options, build_server
from .memory import MemoryStore
from .peers import PeerHub, load_peers


def route(hub: PeerHub, allowed_ids: set[int], user_id: int | None, username: str | None) -> str:
    """Classify a group message: 'peer_reply', 'direct' (authorized human) or 'ignore'.

    Humans are authorized by immutable Telegram user id, never by changeable username.
    """
    if hub.is_peer_username(username):
        return "peer_reply"
    if user_id is not None and user_id in allowed_ids:
        return "direct"
    return "ignore"


def main() -> None:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = int(os.environ["TELEGRAM_CHAT_ID"])
    allowed = {int(u) for u in os.environ["ALLOWED_USER_IDS"].split(",") if u.strip()}
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
                u = msg.from_user
                kind = route(hub, allowed, u.id if u else None, u.username if u else None)
                if kind == "peer_reply":
                    hub.deliver(u.username, msg.text)
                elif kind == "direct":
                    # Background task so peer replies keep flowing; agent.reply serializes turns.
                    asyncio.create_task(_answer(u.first_name, msg.text))

            async def _answer(name: str, text: str) -> None:
                await send(await agent.reply(name, text))

            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))
            async with app:
                me = await app.bot.get_me()
                if not me.can_read_all_group_messages:
                    logging.warning(
                        "Group Privacy Mode is ON: this bot will miss plain group text. "
                        "Disable it in BotFather (/setprivacy) and re-add the bot, or make it an admin."
                    )
                await app.start()
                await app.updater.start_polling()
                await asyncio.Event().wait()

    asyncio.run(run())


if __name__ == "__main__":
    main()
