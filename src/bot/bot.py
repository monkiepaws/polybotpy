from __future__ import annotations

import abc
import asyncio
import logging
import os
import re
from pathlib import Path
from typing import Optional

import discord
from discord.ext import commands
from dotenv import load_dotenv

import src.bot.matchmaking.beacons as beacons
import src.bot.matchmaking.beacondynamodb.beacondb as beacondb
import src.bot.matchmaking.matchmaking as matchmaking
import src.bot.subscribe as subscribe
import src.bot.where as where

logging.basicConfig(
    # filename="{:%Y-%m-%d}.log".format(datetime.now()),
    level=logging.INFO
)
log = logging.getLogger(__name__)


def load_environment():
    """Load environment variables from .env file."""
    env_path = Path(__file__).resolve().parent.parent.parent.joinpath(
        '.env')
    str_path = str(env_path)
    load_dotenv(dotenv_path=str_path)


class MPBotBase(commands.Bot, abc.ABC):
    """A subclass of commands.Bot with additions for use in Polybot."""
    def __init__(self,
                 secret_name: str = "DISCORD_CLIENT_SECRET",
                 *args,
                 **kwargs):
        """This class is not intended to be instantiated.

        Args:
            secret_name: Environment variable containing Discord token.

        """
        super(MPBotBase, self).__init__(*args, **kwargs)
        self._mp_secret_name = secret_name

    async def on_ready(self):
        """Called by base class when bot is ready."""
        log.info(f"Logged in as {self.user}")

    @abc.abstractmethod
    def instance(self,
                 command_prefix: str,
                 *args,
                 **kwargs):
        pass

    async def mp_wait_until_ready(self):
        """Loop until bot is ready.

        Used by internal testing packages during test setup.

        """
        max_iterations = 10
        iterations = 0
        while not self.is_ready():
            if iterations < max_iterations:
                iterations += 1
                await asyncio.sleep(1.0)
            else:
                raise RuntimeError("Could not login to Discord.")

    async def on_message(self, message):
        """Invokes commands if message is not from a bot, except test bot."""
        e2e_bot_client_id = int(os.getenv("E2E_DISCORD_CLIENT_ID"))
        if message.author.bot and message.author.id != e2e_bot_client_id:
            log.debug(f"{message.author.name} is a bot, ignored")
        else:
            ctx = await self.get_context(message)
            await self.invoke(ctx)

    @staticmethod
    def mp_intents() -> discord.Intents:
        """Return the discord intents required for the bots."""
        intents = discord.Intents.default()
        intents.typing = False
        intents.presences = False
        intents.members = True
        return intents

    @staticmethod
    def mp_load_environment():
        """Load environment variables from .env file."""
        load_environment()

    @property
    def mp_discord_client_token(self) -> str:
        """Return the Discord client token from an environment variable."""
        token = os.getenv(self._mp_secret_name)
        return token


class PolyBot(MPBotBase):
    """A Discord bot for matchmaking fighting games.

    Attributes:
        allowed_chars: Compiled regex pattern for sanitising messages.

    """

    _instance: Optional[PolyBot] = None

    def __init__(self, *args, **kwargs):
        """When instantiating, please use at least one argument.

        Args:
            command_prefix: The message prefix the bot should watch for.

        """
        super(PolyBot, self).__init__(*args, **kwargs)
        self.allowed_chars: re.Pattern[str] = re.compile(r'^[\w !.]+$')

    @classmethod
    def instance(cls, command_prefix: str, *args, **kwargs) -> MPBotBase:
        if cls._instance:
            return cls._instance
        else:
            cls._instance = cls(
                command_prefix=command_prefix,
                intents=cls.mp_intents()
            ).with_setup()
            return cls._instance

    def with_setup(self) -> PolyBot:
        """Load configuration and command cogs. Return self."""
        self.mp_load_environment()
        self._mp_add_checks()
        self._mp_add_cogs()
        return self

    def _mp_add_checks(self) -> None:
        """Add all global checks to the bot."""
        self.add_check(self._globally_block_dms)
        self.add_check(self._globally_block_characters)

    def _mp_add_cogs(self) -> None:
        """Add all command cogs to the bot."""
        self.add_cog(where.Where(self))
        self.add_cog(subscribe.Subscribe(self))
        self.add_cog(
            matchmaking.Matchmaking(self,
                        request=beacondb.BeaconDataAccessDynamoDb(
                            table_name=os.getenv("DYNAMO_DB_TABLE_NAME"),
                            region=os.getenv("DYNAMO_DB_REGION"),
                            endpoint=os.getenv("DYNAMO_DB_ENDPOINT"),
                            profile=os.getenv("DYNAMO_DB_AWS_PROFILE")
                        )
            )
        )

    async def _globally_block_dms(self, ctx: commands.Context) -> bool:
        """Configure bot to globally block direct messages.

        Args:
            ctx: A Discord message Context.

        """
        check = ctx.guild is not None
        return check

    async def _globally_block_characters(self,
                                         ctx: commands.Context) -> bool:
        """Configure bot to globally block unnecessary characters.
        Uses allowed_chars attribute.

        Args:
            ctx: A Discord message Context.

        """
        message: discord.Message = ctx.message
        match = self.allowed_chars.fullmatch(message.content)
        if match is None:
            return False
        else:
            return True


# def main():
#     """Setup and run Polybot. Blocking, so not suitable for testing."""
#     polybot = PolyBot.instance(command_prefix="$")
#     polybot.run(polybot.mp_discord_client_token)
#
#
# if __name__ == '__main__':
#     main()
