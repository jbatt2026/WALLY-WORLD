"""Peer agent registry and reply correlation for agents sharing a Telegram group."""
from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Peer:
    name: str
    handle: str  # Telegram username, no leading @
    platform: str
    role: str


def load_peers(path: Path) -> list[Peer]:
    path = Path(path)
    if not path.exists():
        return []
    return [
        Peer(p["name"], p["handle"].lstrip("@").lower(), p.get("platform", ""), p.get("role", ""))
        for p in json.loads(path.read_text(encoding="utf-8"))
    ]


class PeerHub:
    """Sends a message to a peer and waits for that peer's next reply in the group."""

    def __init__(self, peers: list[Peer], send, timeout: float = 120):
        self._peers = {p.name.lower(): p for p in peers}
        self._by_handle = {p.handle: p for p in peers}
        self._send = send  # async (text: str) -> None, posts to the shared group
        self._timeout = timeout
        self._pending: dict[str, asyncio.Future[str]] = {}

    def roster(self) -> list[Peer]:
        return list(self._peers.values())

    def find(self, name: str) -> Peer | None:
        return self._peers.get(name.strip().lower())

    def is_peer_username(self, username: str | None) -> bool:
        return bool(username) and username.lower() in self._by_handle

    def deliver(self, username: str, text: str) -> bool:
        """Feed an incoming group message from a peer bot. Returns True if it answered a request."""
        fut = self._pending.get(username.lower())
        if fut and not fut.done():
            fut.set_result(text)
            return True
        return False

    async def ask(self, name: str, message: str) -> str:
        peer = self.find(name)
        if peer is None:
            raise KeyError(f"unknown peer {name!r}; known: {sorted(self._peers)}")
        if peer.handle in self._pending and not self._pending[peer.handle].done():
            raise RuntimeError(f"already waiting on {peer.name}")
        fut: asyncio.Future[str] = asyncio.get_running_loop().create_future()
        self._pending[peer.handle] = fut
        try:
            await self._send(f"@{peer.handle} {message}")
            return await asyncio.wait_for(fut, self._timeout)
        finally:
            self._pending.pop(peer.handle, None)
