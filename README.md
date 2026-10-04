# WALLY-WORLD: Matthew's memoir agent

A Claude agent that helps write Matthew's memoir from stored memories. It lives in a Telegram group with you, any co-writers, and other platform agents (ChatGPT, Gemini, other Claude bots), and can ask them for research or editing.

## How it works
- **Memories**: `memoir/memories/*.md`, one file per memory. The agent searches them before drafting and saves new ones you share.
- **Manuscript**: chapter drafts go to `memoir/manuscript/`.
- **Peers**: listed in `peers.json` (copy `peers.example.json`). The agent posts `@peer_handle question` in the group and waits for that bot's reply. Peer replies are treated as untrusted suggestions.
- **Access**: only numeric Telegram user ids in `ALLOWED_USER_IDS`, in the configured chat, can direct the agent. Memories and manuscript are git-ignored.

## Run
```
python -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env   # fill in, then export the variables
python -m memoir_agent.bot
pytest
```

## Setup you must do
1. Create the agent's bot with @BotFather and put its token in `TELEGRAM_BOT_TOKEN`.
2. Create a group, add this bot, your co-writers, and each peer bot; set `TELEGRAM_CHAT_ID`.
3. Each peer agent needs its own Telegram bot wired to its platform (that part lives outside this repo).
4. Group Privacy Mode is on by default, so a bot only sees commands and replies, not plain group text. For this bot (and each peer bot that must read requests): in BotFather run `/setprivacy` and choose Disable, then remove and re-add the bot to the group, or make it a group admin. The agent logs a warning at startup if privacy is still on.
5. Bots do not receive other bots' ordinary messages by default. A code review of this PR says Telegram's Bot-to-Bot Communication Mode must be enabled for the bots (plus admin rights or privacy disabled for receivers). I could not open Telegram's docs to confirm the exact steps, so check them in BotFather before relying on peer replies.
