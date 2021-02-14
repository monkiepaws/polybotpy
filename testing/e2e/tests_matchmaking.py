from abc import ABC

from testing.e2e.e2e_bot_test_case import E2EBotTest, E2EBotTestCase
from testing.common import async_test


class MatchmakingTest(E2EBotTest[str, str], ABC):
    pass


class AddSingleBeaconTest(MatchmakingTest):
    @property
    def description(self) -> str:
        return "When adding a beacon, should notify the user."

    async def arrange(self) -> str:
        return f"{self.prefix}games st 1.5 pc"

    async def act(self) -> str:
        message = await self.get_last_message(offset=1)
        return message.embeds[0].description

    async def assert_that(self) -> bool:
        return f"{self.message.author.mention}, added you to the ST PC " \
               f"waiting list!" in self.actual


class StopBeaconsTest(MatchmakingTest):
    @property
    def description(self) -> str:
        return "When stopping beacons, should notify the user."

    async def arrange(self) -> str:
        return f"{self.prefix}stop"

    async def act(self) -> str:
        message = await self.get_last_message()
        return message.content

    async def assert_that(self) -> bool:
        return f"{self.message.author.mention} stopped waiting: " \
               f"** gl;hf! ** 🎉" in self.actual


class TestMatchmaking(E2EBotTestCase):
    @async_test
    async def test_add_and_stop_games(self):
        await self.run_tests(AddSingleBeaconTest, StopBeaconsTest)
