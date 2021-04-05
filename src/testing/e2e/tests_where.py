import discord

import src.testing.common as common
import src.testing.e2e.e2e_bot_test_case as e2e_bot_test_case

class GuildNameReturnsAGuildName(e2e_bot_test_case.E2EBotTest[common.A,
                                                              common.B]):
    @property
    def description(self):
        return "Should return the name of the guild."

    async def arrange(self) -> str:
        return f""
