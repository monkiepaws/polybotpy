from __future__ import annotations

import logging
from typing import Optional, Sequence, Tuple

from discord import Colour, Embed, Message
from discord.ext import commands
from discord.ext.commands import Context

from .beacons import BeaconBase, Game, Platform, WaitTime
from .dataaccess import BeaconDataAccessBase


log = logging.getLogger(__name__)


class Beacon(BeaconBase):
    """Responsible for containing matchmaking information and integrity of
    data.

    """

    @classmethod
    def from_discord_request(cls,
                             ctx: Context,
                             game: Game,
                             wait_time: WaitTime = None,
                             platform: WaitTime = None):
        return cls(ctx.author.id,
                   ctx.author.display_name,
                   game,
                   wait_time or WaitTime.from_float(WaitTime.min),
                   platform or Platform.from_str(game.default_platform))


class GamesList:
    """Creates beacon lists for matchmaking, formatted for Discord."""

    @classmethod
    def from_beacons(cls,
                     beacons: Sequence[BeaconBase],
                     title: str) -> str:
        """Return a games list as a string if beacons is not empty,
        a message otherwise.

        """
        if len(beacons):
            return cls.create(beacons=beacons, title=title)
        else:
            return cls.empty_list_message(title)

    @classmethod
    def create(cls, beacons: Sequence[BeaconBase], title: str) -> str:
        """Return a list of Beacons formatted as a table.

        Args:
            beacons: The beacons to be displayed in the games list.
            title: The title of the list, giving context to the user.
                Eg. 'All Available'

        """
        entries = [cls.entry(beacon=beacon) for beacon in beacons]
        table: str = "`"  # code block start
        table += cls.heading(title=title or "All Available")
        table += "".join(entries)
        table += "`"  # code block end
        return table

    @staticmethod
    def heading(title: str) -> str:
        """Return the heading of the games list. It will include a given title.

        Args:
            title: The title that gives context to what sort of Beacons are
                displayed.

        """
        return f"WP Matchmaking\n{title} Beacons\n\n"

    @classmethod
    def entry(cls, beacon: BeaconBase) -> str:
        """Return a game entry formatted in a single line.

        Args:
            beacon: The beacon to be formatted.

        """
        game = beacon.game_name.upper().ljust(6, " ")
        username = cls.take(beacon.username, 16).ljust(17, " ")
        time = cls._time_from_mins(mins=beacon.minutes_remaining).ljust(7, " ")
        platform = beacon.platform.upper().ljust(5)
        return f"🏮 {game} {username}  {time} {platform}\n"

    @staticmethod
    def take(string: str, n: int):
        """Return the first n characters of a string. Will return the
        original string if n is less than or equal to len(string).

        Args:
            string: The string to operate on.
            n: The number of characters to take from the beginning of the
                string.

        """
        if len(string) <= n:
            return string
        else:
            return string[:n]

    @staticmethod
    def _time_from_mins(mins: int) -> str:
        whole_hours: int = int(mins / 60)
        minutes: int = mins % 60
        show_hours: bool = whole_hours > 0

        if show_hours:
            return f"{whole_hours}h {minutes}m"
        else:
            return f"{minutes}m"

    @staticmethod
    def empty_list_message(title: str) -> str:
        """Return a message indicating no beacons exist for this title."""
        return f"No one is waiting for {title or 'any games'}, yet!\n" \
               f"Don't forget to add yourself to the waiting list. Check out" \
               f" **!helpme games**"


class AddedBeaconMessage:
    """Methods to create messages to an author when adding a Beacon."""

    @classmethod
    def create(cls,
               ctx: Context,
               game: Game,
               beacon: BeaconBase,
               current_beacons: Sequence[BeaconBase]) -> Tuple[Embed, str]:
        """Return a formatted confirmation of adding a Beacon
        and mentions to other players who are also waiting for the same game
        as a tuple.

        Args:
            ctx: The Discord message Context.
            game: The Game the beacons are for.
            beacon: The Beacon created from the author's request.
            current_beacons: The beacons currently waiting for this Game.

        """
        text = f"{ctx.author.mention}, added you to the " \
               f"{beacon.game_name.upper()} {beacon.platform.upper()} " \
               f"waiting list!"
        embed = cls._embed(text=text)

        message = f"**{game.message}**"
        entries = cls._entries(
            author=beacon.user_id,
            current=current_beacons
        )
        mentions = message + "".join(entries)

        return embed, mentions

    @staticmethod
    def _embed(text: str) -> Embed:
        """Return a Discord.Embed message using a given string of text."""
        return Embed(
            title="🏮 Looking for games service",
            colour=Colour(0x00ffb9),
            description=text
        )

    @classmethod
    def _entries(cls, author: str, current: Sequence[BeaconBase]) -> Sequence[str]:
        """Return a sequence of mentions."""
        return [cls._mention(b.user_id) for b in current if author != b.user_id]

    @staticmethod
    def _mention(discord_id: str) -> str:
        """Return a formatted string that mentions a Discord user id."""
        return f"\n<@{discord_id}\t"

    @staticmethod
    def _not_author(author: str, other: str) -> bool:
        return author != other


class Matchmaking(commands.Cog):
    def __init__(self, bot: commands.Bot, request: BeaconDataAccessBase):
        self.bot = bot
        self.request = request

    async def _add_beacon(self,
                          ctx: Context,
                          game: Game,
                          beacon: BeaconBase) -> Message:
        """Perform the necessary actions to add a beacon and notify the
        author.

        """
        await self.request.add([beacon])
        current_beacons = await self.request.list_for_game(beacon=beacon)
        embed, mentions = AddedBeaconMessage.create(
            ctx=ctx,
            game=game,
            beacon=beacon,
            current_beacons=current_beacons
        )
        await ctx.send(embed=embed)
        return await ctx.send(content=mentions)

    async def _fetch_active_beacons(self,
                                    ctx: Context,
                                    game: Game) -> Sequence[BeaconBase]:
        """Return a sequence of active beacons for a game if one is specified.
        Otherwise, all active beacons.

        """
        if game is None:
            return await self.request.list()
        else:
            return await self.request.list_for_game(
                Beacon.from_discord_request(ctx=ctx, game=game)
            )

    def _list_title(self, game: Game) -> Optional[str]:
        if game:
            return f"All {game.name.upper()}"
        else:
            return None

    @commands.command(aliases=("g",))
    async def games(self, ctx: Context,
                    game: Optional[Game],
                    wait_time: Optional[WaitTime],
                    platform: Optional[Platform]):
        """Add a beacon for matchmaking."""
        log.info(f"games request by {ctx.message.author.name}: "
                 f"{game}, {wait_time}, {platform}.")
        if (game is None) or (wait_time is None):
            log.info(f"games request: Sending back a list of games.")
            return await self.list(ctx, game, platform)
        else:
            log.info(f"games request: Adding beacon and notifying user.")
            return await self._add_beacon(
                ctx=ctx,
                game=game,
                beacon=Beacon.from_discord_request(
                    ctx,
                    game,
                    wait_time,
                    platform
                )
            )

    @commands.command(aliases=("l",))
    async def list(self,
                   ctx: Context,
                   game: Optional[Game],
                   platform: Optional[Platform]):
        """Show a list of all active beacons, or filtered by game."""
        log.info(f"list request by {ctx.message.author.name}: "
                 f"game={game}, platform={platform}")
        return await ctx.send(
            content=GamesList.from_beacons(
                beacons=await self._fetch_active_beacons(ctx, game),
                title=self._list_title(game=game)
            )
        )

    @commands.command(aliases=("s",))
    async def stop(self, ctx):
        """Stop all active beacons for a user."""
        # TODO: allow finer grain of control over stop command
        log.info(f"stop request: Stopping beacons for "
                 f"{ctx.message.author.name}")
        result: bool = await self.request.stop_by_user_id(
            beacon=Beacon.from_discord_request(
                ctx=ctx,
                game=Game.from_str("sfv")
                # TODO: placeholder game should not be necessary
            )
        )
        return await ctx.send(content=self._stop_message(ctx, result))

    def _stop_message(self, ctx: Context, result: bool) -> str:
        if result:
            return f"{ctx.author.mention} stopped waiting: ** gl;hf! ** 🎉"
        else:
            return f"${ctx.author.mention}, I don't think you were on the " \
                   f"waiting list! 🤔"
