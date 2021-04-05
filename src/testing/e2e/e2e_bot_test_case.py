import abc
import unittest
from typing import Any, Optional, Type

from discord import Message, TextChannel

import src.bot.bot as bot
import src.testing.e2e_bot as e2e_bot
import src.testing.common as common


class E2EBotTest(common.MPIntegrationTest[common.A, common.B], abc.ABC):
    """Test that's specific for end-to-end testing in a Discord environment.

    Attributes:
        channel: The guild channel that the tests will be performed in.
        prefix: The command prefix of Polybot (the system under test).
        message: The message used by this bot to test the system under test.
        actual: Actual value returned from Act testing step.
        result: The result of the test.

    """
    def __init__(self, channel: TextChannel, command_prefix: str):
        super(E2EBotTest, self).__init__()
        self.channel = channel
        self.prefix = command_prefix
        self.message: Optional[Message] = None
        self.actual: Optional[Any] = None
        self.result: bool = False

    @property
    def wait_time(self) -> float:
        """Return the time to wait between each step of the test.

        TODO: eliminate the need for this by using events.

        """
        return 2.0

    async def get_last_message(self, offset: int = 0) -> Message:
        """Return the last message in the guild channel."""
        history = await self.channel.history(limit=4).flatten()
        message = history[offset]
        return message

    async def _send_description(self) -> None:
        await self.channel.send(f"Test: {self.description}")

    async def _arrange(self) -> None:
        message = await self.channel.send(await self.arrange())
        await common.asyncio.sleep(self.wait_time)
        self.message = await self.channel.fetch_message(message.id)

    async def _react(self) -> None:
        await self.message.add_reaction(self.reaction)

    async def start(self) -> None:
        await self._send_description()
        await self._arrange()
        await self._act()
        await self._assert()
        await self._react()


class E2EBotTestCase(unittest.TestCase):
    """TestCase for end-to-end testing in a Discord environment."""

    # Current event loop.
    loop = common.asyncio.get_event_loop()
    # The Client Discord bot for this Test Case.
    e2e_bot = e2e_bot.E2EBot.instance(
        secret_name="E2E_DISCORD_CLIENT_SECRET",
        command_prefix="?"
    )
    # The Discord bot under test.
    polybot = bot.PolyBot.instance(command_prefix="!")
    # Convenience attribute of all bots used in this test case.
    bots = [polybot, e2e_bot]

    def __init__(self, *args, **kwargs):
        super(E2EBotTestCase, self).__init__(*args, **kwargs)

    @classmethod
    def setUpClass(cls) -> None:
        for bot in cls.bots:
            if not bot.is_ready():
                common.asyncio.Task(
                    coro=bot.start(bot.mp_discord_client_token),
                    loop=cls.loop
                )
                cls.loop.run_until_complete(bot.mp_wait_until_ready())

    async def run_tests(self, *tests: Type[E2EBotTest]) -> None:
        """Call unittest methods on behalf of each test passed in. Must be
        called in a method that is named starting with test so it is discovered
        by unittest. Must use E2EBotTest tests.

        Usage:
            @testing.common.async_test
            async def test_example_tests_should_be_true(self):
                await self.run_tests(ExampleTest1, ExampleTest2)

        Args:
            tests: E2EbotTests to be performed.

        """
        for test_class in tests:
            test = test_class(
                channel=self.e2e_bot.test_channel,
                command_prefix=self.polybot.command_prefix
            )
            with self.subTest(command=test.arrange):
                await test.start()
                self.assertTrue(test.result)
