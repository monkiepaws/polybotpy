from __future__ import annotations

import logging
from typing import Optional

import discord

from src.bot import MPBotBase

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("e2e_bot")


class E2EBot(MPBotBase):
    """Discord bot for end-to-end testing of Polybot."""

    _instance: Optional[E2EBot] = None

    def __init__(self, *args, **kwargs):
        super(E2EBot, self).__init__(*args, **kwargs)

    @property
    def test_channel(self):
        """Return discord channel in guild to perform tests."""
        channel = self.guilds[0].channels[1]
        log.debug(channel.name)
        return channel

    @classmethod
    def instance(cls,
                 command_prefix: str,
                 **kwargs) -> E2EBot:
        if cls._instance:
            return cls._instance
        else:
            cls._instance = cls(
                command_prefix=command_prefix,
                intents=cls.mp_intents(),
                secret_name=kwargs["secret_name"]
            )
            return cls._instance
