import asyncio
import json

import pytest

from memoir_agent.bot import route
from memoir_agent.peers import PeerHub, load_peers


def make_hub(tmp_path, send=None, timeout=1):
    f = tmp_path / "peers.json"
    f.write_text(json.dumps([{"name": "Researcher", "handle": "@Res_Bot", "platform": "openai", "role": "facts"}]))
    sent = []

    async def default_send(t):
        sent.append(t)

    return PeerHub(load_peers(f), send or default_send, timeout), sent


def test_load_peers_missing_file(tmp_path):
    assert load_peers(tmp_path / "nope.json") == []


async def test_ask_posts_mention_and_returns_reply(tmp_path):
    hub, sent = make_hub(tmp_path)
    task = asyncio.create_task(hub.ask("researcher", "When did the ferry stop?"))
    await asyncio.sleep(0)
    await asyncio.sleep(0)
    assert sent == ["@res_bot When did the ferry stop?"]
    assert hub.deliver("Res_Bot", "1974")
    assert await task == "1974"


async def test_ask_times_out_and_clears_pending(tmp_path):
    hub, _ = make_hub(tmp_path, timeout=0.01)
    with pytest.raises(TimeoutError):
        await hub.ask("Researcher", "hi")
    assert not hub.deliver("res_bot", "late")


async def test_unknown_peer_raises(tmp_path):
    hub, _ = make_hub(tmp_path)
    with pytest.raises(KeyError):
        await hub.ask("Nobody", "hi")


def test_route_authorization(tmp_path):
    hub, _ = make_hub(tmp_path)
    allowed = {42}
    assert route(hub, allowed, 7, "res_bot") == "peer_reply"
    assert route(hub, allowed, 42, "anything") == "direct"
    assert route(hub, allowed, 42, None) == "direct"
    assert route(hub, allowed, 99, "matthew") == "ignore"  # a username alone grants nothing
    assert route(hub, allowed, None, None) == "ignore"


def test_username_changes_do_not_transfer_human_access(tmp_path):
    hub, _ = make_hub(tmp_path)
    allowed = {42}
    assert route(hub, allowed, 42, "matthew") == "direct"
    assert route(hub, allowed, 42, "new_name") == "direct"
    assert route(hub, allowed, 42, None) == "direct"
    assert route(hub, allowed, 99, "matthew") == "ignore"
