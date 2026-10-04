# WALLY-WORLD: Matthew's memoir agent

A Claude agent that helps write Matthew's memoir from stored memories. It lives in a Telegram group with you, any co-writers, and other platform agents (ChatGPT, Gemini, other Claude bots), and can ask them for research or editing.

## How it works
- **Memories**: `memoir/memories/*.md`, one file per memory. The agent searches them before drafting and saves new ones you share.
- **Manuscript**: chapter drafts go to `memoir/manuscript/`.
- **Peers**: listed in `peers.json` (copy `peers.example.json`). The agent posts `@peer_handle question` in the group and waits for that bot's reply. Peer replies are treated as untrusted suggestions.
- **Access**: only usernames in `ALLOWED_USERS`, in the configured chat, can direct the agent. Memories and manuscript are git-ignored.

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

## Known gap
Telegram's rules on whether one bot receives another bot's group messages could not be checked from this environment. If peer replies never arrive, check BotFather's privacy and bot-to-bot settings for every bot in the group.
