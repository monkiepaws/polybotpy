import asyncio
import datetime
from abc import ABC, abstractmethod
from typing import Generic, Optional, Tuple, TypeVar

import src.bot.matchmaking.beacons as beacons

A = TypeVar("A")
B = TypeVar("B")


def async_test(func):
    """Decorator allowing coroutines to be called by synchronous functions."""

    def wrapper(*args):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(func(*args))

    return wrapper


def create_beacon(game_name: str = "st",
                  waiting_time: float = 12.0,
                  platform_name: str = "pc",
                  start: datetime.datetime = None,
                  user_id: int = 1234567890
                  ) -> beacons.BeaconBase:
    """Return a BeaconBase instance. Convenience function."""
    return beacons.BeaconBase.from_dict({
        "user_id": user_id,
        "username": "Test Dummy Name",
        "game": beacons.Game.from_str(game_name),
        "wait_time": beacons.WaitTime.from_float(waiting_time),
        "platform": beacons.Platform.from_str(platform_name),
        "start": start
    })


def create_beacon_and_now_datetime(
        game_name: str = "st",
        waiting_time: float = 12.0,
        platform_name: str = "pc"
) -> Tuple[beacons.BeaconBase, datetime.datetime]:
    """Return a BeaconBase instance with start time to current time."""
    now = datetime.datetime.now(datetime.timezone.utc) \
        .replace(microsecond=0)
    beacon = create_beacon(game_name=game_name,
                           waiting_time=waiting_time,
                           platform_name=platform_name,
                           start=now)
    return beacon, now


class MPIntegrationTest(Generic[A, B], ABC):
    """Class that eases creating integration tests on the Discord platform.

    Tests are generally created by overriding the abstract methods, which are
    named after the Arrange/Act/Assert unit testing pattern, and the
    description method.

    The companion private methods, which usually set values, can be overridden
    if custom logic is necessary.

    Attributes:
        result: The result of a test's assertion.
        arranged_value: The value set from the Arrange step.

    """
    def __init__(self):
        self.result: bool = False
        self.arranged_value: Optional[A] = None

    @property
    def reaction(self) -> str:
        """Return the emoji used for Pass/Fail for a Discord reaction."""
        if self.result:
            return "✅"
        else:
            return "❌"

    @property
    @abstractmethod
    def description(self) -> str:
        """Return the description of the test."""
        raise NotImplementedError

    @abstractmethod
    async def arrange(self) -> A:
        """Return a value from the Arrange step of a test."""
        raise NotImplementedError

    async def _arrange(self) -> None:
        """Set the arranged_value attribute. Override for custom logic."""
        self.arranged_value = await self.arrange()

    @abstractmethod
    async def act(self) -> B:
        """Return the actual value to test from the Act step."""
        raise NotImplementedError

    async def _act(self) -> None:
        """Set the actual attribute. Override for custom logic."""
        self.actual = await self.act()

    @abstractmethod
    async def assert_that(self) -> bool:
        """Return true if true has passed, false otherwise, testing with
        custom logic.

        """
        raise NotImplementedError

    async def _assert(self) -> None:
        """Set the result attribute. Override for custom logic."""
        self.result = await self.assert_that()

    async def _setup(self) -> None:
        """Override to perform any necessary setup for the test."""
        pass

    async def start(self) -> None:
        """Perform the steps of a test."""
        await self._setup()
        await self._arrange()
        await self._act()
        await self._assert()
