import discord

from testing.common import A, B
from testing.e2e.e2e_bot_test_case import E2EBotTest, E2EBotTestCase

class GuildNameReturnsAGuildName(E2EBotTest[A, B]):
    @property
    def description(self):
        return "Should return the name of the guild."

    async def arrange(self) -> str:
        return f""
