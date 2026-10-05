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
5. In [@BotFather](https://t.me/BotFather), select this bot and enable **Bot-to-Bot Communication Mode**; repeat for every peer bot. For this repository's ordinary `@peer_handle question` exchange, every receiving bot (including this bot receiving peer responses) must also be a group admin **or** have Group Privacy Mode disabled as in step 4. A plain `@handle` is not a command mention. These requirements are documented in Telegram's [Bot-to-Bot communication guide](https://core.telegram.org/api/bots/bot-to-bot).
6. Before relying on the group, send plain text from an account in `ALLOWED_USER_IDS` and confirm this bot responds. Then ask it to consult a configured peer and confirm the request and response both arrive without a timeout. Enabling the Telegram settings does not wire a peer to its AI platform; each peer's handler must accept this bot's requests and send responses in the same group.
