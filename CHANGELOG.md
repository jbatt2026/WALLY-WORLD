# Changelog

All notable changes to this project are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- Memoir agent (`memoir_agent/`): Claude Agent SDK agent that writes Matthew's memoir from stored memories.
- Telegram group hub (`bot.py`) where the agent @mentions peer bots (ChatGPT, Gemini, others) and awaits their replies.
- Markdown memory store with keyword-ranked search.
- Peer registry (`peers.example.json`) and `PeerHub` request/reply matching with timeouts.
- Tests for memory, peers, routing and serialized agent turns.
- README setup guide, `.env.example`, pinned requirements.

### Security
- Peer replies are treated as untrusted data.
- Humans are authorized by numeric Telegram user ID; only the configured chat is served.
- Memories, manuscript, `.env` and `peers.json` are git-ignored.
