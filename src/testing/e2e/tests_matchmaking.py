from abc import ABC

import src.testing.e2e.e2e_bot_test_case as e2e_bot_test_case
import src.testing.common as common


class MatchmakingTest(e2e_bot_test_case.E2EBotTest[str, str], ABC):
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


class TestMatchmaking(e2e_bot_test_case.E2EBotTestCase):
    @common.async_test
    async def test_add_and_stop_games(self):
        await self.run_tests(AddSingleBeaconTest, StopBeaconsTest)
