import discord
from discord.ext import commands


class Where(commands.Cog, command_attrs={"hidden": True}):
    """
    The Where Cog solely contains the where command, showing which
    guilds the bot is active in. It is intended for use only by the
    bot owner.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def where(self, ctx: commands.Context):
        """Sends a list of guilds the bot is currently active."""
        guilds = self.bot.guilds
        guild_names = [await self.guild_name(guild) for guild in guilds]
        embed_msg = discord.Embed(title="I'm at home in:",
                                  colour=discord.Colour(0x00ff7b),
                                  description="\n".join(guild_names))
        await ctx.send(embed=embed_msg)

    @staticmethod
    async def guild_name(guild: discord.Guild) -> str:
        """Gets the guild name from a Guild object."""
        if guild.unavailable:
            return f"{guild.id} (guild name unavailable)"
        else:
            return guild.name
