import asyncio

from claude_agent_sdk import AssistantMessage, TextBlock

from memoir_agent.agent import MemoirAgent


class FakeClient:
    """Mimics the SDK's single shared response stream: overlapping turns would interleave."""

    def __init__(self):
        self.active = 0
        self.max_active = 0
        self.last = ""

    async def query(self, text):
        self.active += 1
        self.max_active = max(self.max_active, self.active)
        self.last = text

    async def receive_response(self):
        await asyncio.sleep(0.01)
        yield AssistantMessage(content=[TextBlock(text=f"re: {self.last}")], model="m")
        self.active -= 1


async def test_turns_are_serialized_and_not_misattributed():
    client = FakeClient()
    agent = MemoirAgent(None, client=client)
    a, b = await asyncio.gather(agent.reply("A", "one"), agent.reply("B", "two"))
    assert client.max_active == 1
    assert (a, b) == ("re: A: one", "re: B: two")
