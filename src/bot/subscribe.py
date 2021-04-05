from __future__ import annotations
from discord import Colour, Embed, Forbidden, Guild, Permissions, Role, User
from discord.ext import commands
from discord.ext.commands import Context
from typing import Callable, Coroutine, Optional, Sequence
import logging


class SubRole:
    """A wrapper around discord.Role for performing operations in Subscribe.

    Attributes:
        ctx: The Discord message Context.
        role: The Discord Role object that is wrapped by this class.
        permissions_none: The Discord value for no permissions.

    """

    def __init__(self, ctx: Context, role: Role):
        """Initialise a SubRole object.

        Args:
            ctx: The Discord message Context.
            role: The Discord Role object that is wrapped by this class.

        """
        self.ctx = ctx
        self.role = role
        self.permissions_none: Permissions = Permissions.none()

    def __repr__(self):
        return f"{self.role.name}"

    @classmethod
    async def convert(cls, ctx: Context, arg) -> Optional[SubRole]:
        """Called by discord.py when converting message parameters."""
        try:
            return await cls.convert_role(ctx, arg)
        except commands.BadArgument:
            logging.debug(f"Role not found: {arg}")
            return None

    @classmethod
    async def convert_role(cls,
                           ctx: Context,
                           arg: str) -> Optional[SubRole]:
        """Create a SubRole from a string. Requires a discord.Context.

        Args:
            ctx: The Discord message Context.
            arg: The role name.

        Returns:
            A new SubRole object.

        """
        converted_role = await commands.RoleConverter().convert(ctx, arg)
        subscribe_role = cls(ctx, converted_role)
        return subscribe_role.checked

    @classmethod
    def from_role_list(cls,
                       ctx: Context,
                       roles: Sequence[Role]) -> Sequence[SubRole]:
        """Return a sequence of SubRole converted from discord.Role.

        Args:
            ctx: The Discord message Context.
            roles: A sequence of discord.Role.

        Returns:
            A sequence of SubRoles.

        """
        sub_roles = [cls(ctx, role) for role in roles]
        return cls.filter(sub_roles)

    @classmethod
    def to_list(cls,
                requested_roles: Sequence[Optional[SubRole]]
                ) -> Sequence[SubRole]:
        """Return a sequence of SubRole with None elements filtered out.

        Args:
            requested_roles: A sequence of SubRole that may have None values.

        Returns:
            A sequence of SubRole free of None values.

        """
        return cls.filter_none(requested_roles)

    @staticmethod
    def list_to_string(sub_roles: Sequence[SubRole]) -> str:
        """Return a concatenated string of SubRole names.

        Args:
            sub_roles: The sequence of SubRole to convert.

        Returns:
            A string of concatenated SubRole names, separated by new lines.

        """
        return "\n".join(str(role) for role in sub_roles)

    @staticmethod
    def to_role(sub_roles: Sequence[SubRole]) -> Sequence[Role]:
        """Return a sequence of discord.Role converted from SubRole.

        Args:
            sub_roles: A sequence of SubRole to convert.

        Returns:
            A sequence of discord.Role.

        """
        return [sub_role.role for sub_role in sub_roles]

    @staticmethod
    def filter(sub_roles: Sequence[Optional[SubRole]]) -> Sequence[SubRole]:
        """Return a sequence of SubRole only with valid roles.

        Args:
            sub_roles: A sequence of SubRole that may have None values.

        Returns:
            A sequence of SubRole.

        """
        return [role for role in sub_roles if role.is_ok and role is not None]

    @staticmethod
    def filter_none(seq: Sequence[Optional[SubRole]]) -> Sequence[SubRole]:
        """Return a sequence of SubRole without None values.

        Args:
            seq: A sequence of SubRole that may include None values.

        Returns:
            A sequence of SubRole.

        """
        return [element for element in seq if element is not None]

    @property
    def checked(self) -> Optional[SubRole]:
        """Return self if the underlying role is valid, None otherwise."""
        if self.is_ok:
            logging.debug(f"Role found and ok: {self.name}, {self.id}")
            return self
        else:
            logging.debug(f"Role found and banned: {self.name}, {self.id}")
            return None

    @property
    def name(self) -> str:
        """Return the discord.Role name."""
        return self.role.name

    @property
    def id(self) -> str:
        """Return the discord.Role id."""
        return self.role.id

    @property
    def is_ok(self) -> bool:
        """Return True if the role is allowed by the bot, False otherwise."""
        return self.no_permissions and self.below_me and self.is_not_everyone

    @property
    def no_permissions(self) -> bool:
        """Return True if the role has zero permissions, False otherwise."""
        return self.role.permissions == self.permissions_none

    @property
    def my_top_role(self) -> int:
        """Return the bot's position in the guild."""
        return self.ctx.me.top_role.position

    @property
    def below_me(self) -> bool:
        """Return True if role is below the bot's position, False otherwise."""
        return self.role.position < self.my_top_role

    @property
    def is_not_everyone(self) -> bool:
        """Return True if the role is not the @everyone role,
        False otherwise."""
        return self.role.name != "@everyone"


class RoleService:
    @staticmethod
    async def available(ctx: Context) -> Sequence[SubRole]:
        """Return the roles available to be subscribed by the bot.

        Args:
            ctx: The Discord message Context.

        Returns:
            A sequence of SubRole. This represents all roles available to
            the bot that pass rules in SubRole.from_role_list.

        """
        guild: Guild = ctx.guild
        if guild.unavailable:
            return []
        else:
            return SubRole.from_role_list(ctx, guild.roles)

    @staticmethod
    async def add(ctx: Context, sub_roles: Sequence[SubRole]):
        """Add a role to a user.

        Args:
            ctx: A Discord message Context. Roles are added to the author.
            sub_roles: The roles to add to a user.

        """
        try:
            await ctx.author.add_roles(*SubRole.to_role(sub_roles))
        except Forbidden as err:
            logging.warning(err.args)

    @staticmethod
    async def remove(ctx: Context, sub_roles: Sequence[SubRole]):
        """Remove a role from a user.

        Args:
            ctx: A Discord message Context. Roles are removed from the author.
            sub_roles: The roles to remove from a user.

        """
        try:
            await ctx.author.remove_roles(*SubRole.to_role(sub_roles))
        except Forbidden as err:
            logging.warning(err.args)


class Subscribe(commands.Cog):
    """A discord.py Cog that facilitates subscribing to discord.Roles.

    Attributes:
        bot: The discord client.
        max_args: The maximum arguments accepted by the discord command.

    """

    def __init__(self, bot: commands.Bot, max_args: int = 6):
        """This class should only be instantiated for commands.Bot.

        Args:
            bot: The discord client object using the Subscribe Cog.
            max_args: The maximum number of arguments to accept per command.

        """
        self.bot: commands.Bot = bot
        self.max_args: int = max_args

    @commands.command()
    async def sub(self, ctx: Context, *requested_roles: SubRole):
        """Parent of subscribe commands. Run 'list' if sub-command not
        provided.

        Discord usage:    !sub

        """
        if requested_roles:
            return await self.add(ctx, *requested_roles)
        else:
            return await self.list(ctx)

    async def list(self, ctx: Context):
        """Sub-command. List all available roles in the guild.

        Discord usage:    !sub list

        """
        available_roles = await RoleService.available(ctx)
        msg = self.embed_msg(title_end="💗",
                             action="requested",
                             roles=available_roles,
                             author=ctx.author)
        await ctx.send(embed=msg)

    async def add(self, ctx: Context, *requested_roles: SubRole):
        """Sub-command. Add a sequence of roles to the author if valid.

        Discord usage:    !sub add MyRole1 MyRole2

        """
        await self.process(ctx=ctx,
                           requested_roles=requested_roles,
                           title_end="💘",
                           action="added",
                           func=RoleService.add)

    async def remove(self, ctx: Context, *requested_roles: SubRole):
        """Sub-command. Remove a sequence of roles from an author if
        valid.

        Discord usage:    !sub remove MyRole1 MyRole2

        """
        await self.process(ctx=ctx,
                           requested_roles=requested_roles,
                           title_end="💔",
                           action="removed",
                           func=RoleService.remove)

    @commands.command()
    async def unsub(self, ctx: Context, *requested_roles: SubRole):
        if requested_roles:
            return await self.remove(ctx, *requested_roles)
        else:
            return await self.list(ctx)

    async def process(self,
                      ctx: Context,
                      requested_roles: Sequence[SubRole],
                      title_end: str,
                      action: str,
                      func: Callable[[Context, Sequence[SubRole]], Coroutine]):
        """Filter valid roles, run action function, send back message.

        Add and Remove follow the same logical flow. Pass a Callable (func) to
        action on the given requested_roles.

        Args:
            ctx: The Discord message Context.
            requested_roles: Sequence of SubRole to take action on.
            title_end: Display text at end of the returned message title.
            action: Display text informing action taken in returned message.
            func: The Callable that will be passed ctx, requested_roles.

        """
        filtered_roles = SubRole.to_list(requested_roles)
        if len(filtered_roles):
            await func(ctx, filtered_roles)
            msg = self.embed_msg(title_end=title_end,
                                 action=action,
                                 roles=filtered_roles,
                                 author=ctx.author)
            await ctx.send(embed=msg)
        else:
            await ctx.send(self.nothing_to_do_msg(ctx))

    @staticmethod
    def embed_msg(title_end: str,
                  action: str,
                  roles: Sequence[SubRole],
                  author: User) -> Embed:
        """Returns formatted discord.Embed object.

        Args:
            title_end: Display text at end of the returned message title.
            action: Display text informing action taken in returned message.
            roles: Sequence of SubRole.name will be concatenated.
            author: The author to mention in the message. A discord.User.
        """
        roles_msg = SubRole.list_to_string(roles)
        embed = Embed(title=f"**Role subs {title_end}**",
                      colour=Colour(0xff0057),
                      description=f"**{roles_msg}**")
        return embed.add_field(name=f"{action} by ", value=author.mention)

    @staticmethod
    def nothing_to_do_msg(ctx: Context) -> str:
        """Return a message string that the command can not be actioned.

        Args:
            ctx: The Discord message Context. The author and command is
                 mentioned.

        """
        return f"{ctx.author.mention}, no roles to " \
               f"{ctx.command.name}."
