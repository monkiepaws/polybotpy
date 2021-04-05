from __future__ import annotations

import itertools
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple, TypeVar, Union

from discord.ext.commands import BadArgument, Context

T = TypeVar("T")


def load_games() -> dict:
    """Default games data to load."""
    games_file = Path(__file__).parent.joinpath("resource", "games.json")
    with games_file.open() as file:
        data = json.load(file)
        return data["games"]


def load_aliases() -> dict:
    """Default game name alias data to load."""
    aliases_file = Path(__file__).parent.joinpath("resource", "aliases.json")
    with aliases_file.open() as file:
        data = json.load(file)
        return data["aliases"]


def load_platforms(games_data: dict) -> Sequence[str]:
    """Default game platforms data to load."""
    platform_combinations = [v["platforms"] for (k, v) in games_data.items()]
    platforms = list(itertools.chain(*platform_combinations))
    return list(set(platforms))


class Game:
    """A Game, its information, and operations. Helper for BeaconBase.

    Attributes:
        name: The short name of the Game.
        title: The full title for the Game.
        aliases: All aliases for the Game.
        platforms: All platforms the Game is available on.
        default_platorm: The default platform for the Game.
        message: The catch phrase for the Game.

    """
    default_list = load_games()
    default_alias_list = load_aliases()

    def __init__(self,
                 name: str,
                 data: dict,
                 game_list: Dict = None,
                 aliases: Dict = None):
        """Initialise a Game.

        Args:
            name: The Game's short name.
            data: A Dictionary with a Game's information.
            game_list: The full Dictionary of information for all games.
            aliases: The full Dictionary of information for all aliases.

        """
        self.name = name
        self.title: str = data.get("title")
        self.aliases: List[str] = data.get("aliases")
        self.platforms: List[str] = data.get("platforms")
        self.default_platform: str = data.get("defaultPlatform")
        self.message: str = data.get("message")
        self._data: Dict[str, str] = data
        self._list: Dict = game_list
        self._alias_list: Dict = aliases

    def __repr__(self):
        return f"Game('{self.name}', {self._data})"

    def __str__(self):
        return f"Game.name = {self.name}"

    @property
    def list(self):
        """Return the full Dictionary of games and their information.

        If this instance wasn't instantiated with a games_list, then will
        return a default list. This is mainly to assist in testable code.

        """
        if self._list is None:
            return self.default_list
        else:
            return self._list

    @property
    def alias_list(self):
        """Return the full Dictionary of alias-game relationships.

        If this instance wasn't instantiated with aliases, then will return
        a default list. This is mainly to assist in testable code.

        """
        if self._alias_list is None:
            return self.default_alias_list
        else:
            return self._alias_list

    @classmethod
    async def convert(cls, ctx: Context, arg: str) -> Game:
        """Return a Game from a string. Called by discord.py command."""
        return cls.from_str(arg)

    @classmethod
    def from_str(cls,
                 arg,
                 provided_game_list: Dict = None,
                 provided_aliases: Dict = None
                 ) -> Game:
        """Return a Game from a string.

        Args:
            arg: The short name of the Game or an alias.
            provided_game_list: Custom data for all Games.
            provided_aliases: Custom data for all aliases and their Games.

        Raises:
            BadArgument: arg does not match a valid Game or alias.

        """
        arg_lower = arg.lower()
        game_list, forwarded_list = cls._obj_or_default(
            obj=provided_game_list,
            default=cls.default_list
        )
        aliases, forwarded_aliases = cls._obj_or_default(
            obj=provided_aliases,
            default=cls.default_alias_list
        )

        alias = aliases.get(arg_lower)
        if alias:
            name = alias["game"]
            data = game_list.get(name)
            return cls(name=name,
                       data=data,
                       game_list=forwarded_list,
                       aliases=forwarded_aliases)
        else:
            raise BadArgument(f"Can't find {arg_lower}, sorry!")

    @staticmethod
    def _obj_or_default(obj: T, default: T) -> Tuple[T, T]:
        """Return a tuple with default and None values if an object is None.
        Otherwise, return a tuple with the object as both values.

        """
        if obj is None:
            return default, None
        else:
            return obj, obj

    def __eq__(self, other) -> bool:
        return self.name == other.name


class WaitTime:
    """The waiting time of a BeaconBase.

    Attributes:
        value: Number of hours the author of a Beacon will wait for.

    """

    # Minimum wait time is 15 minutes
    min: float = 0.25
    # Maximum wait time is 24 hours
    max: float = 24.0

    def __init__(self, wait_time: float):
        """Initialise WaitTime.

        Alternatives:
            from_float
            from_timestamps
            from_minutes

        """

        self.value: float = self.normalise(wait_time)

    def __repr__(self):
        return f"WaitTime('{self.value}')"

    @classmethod
    async def convert(cls, ctx: Context, arg: float) -> WaitTime:
        """Return a WaitTime instance from an arg. Used by discord.py
        command.

        Use WaitTime.from_float instead.

        """
        return cls.from_float(arg)

    @classmethod
    def from_float(cls, arg: float) -> WaitTime:
        """Return a WaitTime instance.

        Args:
            arg: Number of hours.

        """
        try:
            wait_time = float(arg)
            return cls(wait_time)
        except ValueError:
            raise BadArgument("{arg} is not a float!")

    @classmethod
    def from_timestamps(cls, start_timestamp: int, end_timestamp: int):
        """Return a WaitTime instance from a start and end timestamp.

        Args:
            start_timestamp: The starting time as a Unix timestamp.
            end_timestamp: The end time as a Unix timestamp.

        """
        delta_microsecs: int = end_timestamp - start_timestamp
        delta_hours: float = delta_microsecs / 3600
        return cls.from_float(delta_hours)

    @classmethod
    def from_minutes(cls, minutes: int) -> WaitTime:
        """Return a WaitTime instance.

        Args:
            minutes: Number of minutes the author of a Beacon will wait for.

        """
        return cls(minutes / 60)

    @classmethod
    def normalise(cls, wait_time: float):
        """Return the minimum, maximum or given hours if in between.

        Args:
            wait_time: Number of hours.

        """
        if wait_time < cls.min:
            return cls.min
        elif wait_time > cls.max:
            return cls.max
        else:
            return wait_time

    @property
    def minutes(self) -> int:
        """Return the wait time in minutes."""
        return int(self.value * 60)

    def __eq__(self, other):
        return self.minutes == other.minutes


class Platform:
    """The Platform (eg. PS4, PC etc) a BeaconBase's game is for.

    Attributes:
        value: The platform as a string.

    """

    default_list: Sequence[str] = load_platforms(Game.default_list)

    def __init__(self, value: str, platform_list: Sequence[str] = None):
        """Initialise a Platform instance.

        Prefer using Platform.from_str, especially for testable code.

        """
        self.value: str = value
        self._list: Sequence[str] = platform_list

    def __repr__(self):
        return f"Platform('{self.value}')"

    def __str__(self):
        return f"Platform.value = {self.value}"

    @property
    def list(self):
        if self._list is None:
            return self.default_list
        else:
            return self._list

    @classmethod
    async def convert(cls, ctx: Context, arg: str) -> Platform:
        """Return a Platform instance. Used by discord.py commands.

        Args:
            arg: A platform name.

        """
        return cls.from_str(arg)

    @classmethod
    def from_str(cls,
                 arg: str,
                 platform_list: Sequence[str] = None
                 ) -> Platform:
        """Return a Platform instance.

        Args:
            arg: A platform name.
            platform_list: A List of all platforms as strings.

        """
        arg_lower = arg.lower()
        if platform_list is not None and arg_lower in platform_list:
            return cls(value=arg_lower,
                       platform_list=platform_list)
        elif arg_lower in cls.default_list:
            return cls(value=arg_lower)
        else:
            raise BadArgument(f"Can't find {arg_lower} platform, sorry!")

    def __eq__(self, other):
        return self.value == other.value


class BeaconBase:
    """Base class for a beacon (the abstraction of a matchmaking request).

    Attributes:
        user_id: The user's Discord ID.
        username: The user's Discord Guild display name, otherwise username.
        game_name: Name of the Game the beacon is for.
        minutes_available: The waiting time of the beacon in minutes.
        platform: Platform of the Game the beacon is for.

    """

    def __init__(self,
                 user_id: Union[int, str],
                 username: str,
                 game: Game,
                 wait_time: WaitTime,
                 platform: Platform,
                 start: Optional[datetime] = None):
        """Initialise a BeaconBase instance. This is not an abstract class.

        Can also use BeaconBase.from_dict.

        Args:
            user_id: The user's Discord ID.
            username: The user's Discord Guild display name, or username.
            game: The Game the beacon is for.
            wait_time: The WaitTime the beacon is for.
            platform: The Platform the beacon is for.
            start: Start time, if the beacon has already been created.

        """

        self.user_id: str = str(user_id)
        self.username: str = username
        self.game_name: str = game.name
        self.minutes_available: int = wait_time.minutes
        self.platform: str = self.platform_or_default(platform, game)
        self._start_datetime: datetime = self.datetime_or_default(start)

    @property
    def start_timestamp(self) -> int:
        """Return the starting time as a Unix timestamp."""
        return int(self._start_datetime.timestamp())

    @property
    def end_timestamp(self) -> int:
        """Return the ending time as a Unix timestamp."""
        delta = timedelta(minutes=self.minutes_available)
        end_datetime = self._start_datetime + delta
        timestamp = int(end_datetime.timestamp())
        return timestamp

    @property
    def minutes_remaining(self) -> int:
        """Return remaining minutes if greater than 0, or 0 otherwise."""
        delta = self.end_timestamp - datetime.now(timezone.utc).timestamp()
        minutes = int(delta / 60)

        if minutes > 0:
            return minutes
        else:
            return 0

    @staticmethod
    def platform_or_default(platform: Platform, game: Game) -> str:
        """Return the default Platform if a given platform doesn't exist for
        the given Game.

        Args:
            platform: Platform for a game.
            game: A Game. Its platforms will be compared to the platform arg.

        """
        if platform is not None and platform.value in game.platforms:
            return platform.value
        else:
            return game.default_platform

    @staticmethod
    def datetime_or_default(value: Optional[datetime]) -> datetime:
        """Return the current datetime if the given value is None.

        Args:
            value: A datetime. Can be None.

        """
        if value is None:
            return datetime.now(timezone.utc)
        else:
            return value

    @classmethod
    def from_dict(cls, arg: Dict) -> BeaconBase:
        """Return a BeaconBase instance.

        Args:
            arg: Dictionary of BeaconBase.__init__ arguments.

        """
        return cls(user_id=arg["user_id"],
                   username=arg["username"],
                   game=arg["game"],
                   wait_time=arg["wait_time"],
                   platform=arg["platform"],
                   start=arg["start"])

    @classmethod
    def with_wait_time(cls,
                       beacon:BeaconBase,
                       wait_time: WaitTime
                       ) -> BeaconBase:
        """Return a new BeaconBase instance, updating the given beacon with
        the given wait_time.

        Args:
            beacon: Beacon to copy.
            wait_time: WaitTime to replace the given beacon's wait time.

        """
        game = Game.from_str(beacon.game_name)
        platform = Platform.from_str(beacon.platform)
        new_beacon = BeaconBase(
            user_id=beacon.user_id,
            username=beacon.username,
            game=game,
            wait_time=wait_time,
            platform=platform,
            start=beacon._start_datetime
        )
        return new_beacon

    def _to_tuple(self) -> Tuple[str, str, str, str]:
        return self.user_id, self.username, self.game_name, self.platform

    def __eq__(self, other: BeaconBase) -> bool:
        return self._to_tuple() == other._to_tuple()

    def full_equality(self, other):
        """Return true if all attributes of self and other are equal.
        False otherwise.

        Args:
            other: A second BeaconBase instance to compare to self.

        """
        return self.user_id == other.user_id \
               and self.username == other.username \
               and self.game_name == other.game_name \
               and self.minutes_available == other.minutes_available \
               and self.platform == other.platform \
               and self.start_timestamp == other.start_timestamp
