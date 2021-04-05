import logging
import unittest
from abc import ABC
from typing import Sequence

import discord

import src.testing.common as common
import src.testing.e2e.e2e_bot_test_case as e2e_bot_test_case


class SubscribeTest(e2e_bot_test_case.E2EBotTest[str, Sequence[
    discord.Role]], ABC):
    """Specific subclass of E2EBotTest for testing Subscribe cog."""
    def fetch_own_roles(self):
        """Return a sequence of roles that an author of a message possesses."""
        return [role.name for role in self.message.author.roles]


class AddSingleRoleTest(SubscribeTest):
    @property
    def description(self) -> str:
        return "Subscribe should add a single role."

    async def arrange(self) -> str:
        return f"{self.prefix}sub add chun"

    async def act(self) -> Sequence[discord.Role]:
        return self.fetch_own_roles()

    async def assert_that(self):
        return "chun" in self.actual


class RemoveSingleRoleTest(SubscribeTest):
    @property
    def description(self) -> str:
        return "Subscribe should remove a single role"

    async def arrange(self) -> str:
        return f"{self.prefix}sub remove chun"

    async def act(self) -> Sequence[discord.Role]:
        return self.fetch_own_roles()

    async def assert_that(self):
        return "chun" not in self.actual


class AddMultipleRolesTest(SubscribeTest):
    @property
    def description(self) -> str:
        return "Subscribe should add multiple roles."

    async def arrange(self) -> str:
        return f"{self.prefix}sub add chun newrole"

    async def act(self) -> Sequence[discord.Role]:
        return self.fetch_own_roles()

    async def assert_that(self):
        return "chun" in self.actual and "newrole" in self.actual


class RemoveMultipleRolesTest(SubscribeTest):
    @property
    def description(self) -> str:
        return "Subscribe should remove multiple roles."

    async def arrange(self) -> str:
        return f"{self.prefix}sub remove chun newrole"

    async def act(self) -> Sequence[discord.Role]:
        return self.fetch_own_roles()

    async def assert_that(self):
        return "chun" not in self.actual and "newrole" not in self.actual


class DoNotAddRoleWithPermissionsTest(SubscribeTest):
    @property
    def description(self) -> str:
        return "Subscribe should not allow adding a role with permissions."

    async def arrange(self) -> str:
        return f"{self.prefix}sub add karin"

    async def act(self) -> Sequence[discord.Role]:
        return self.fetch_own_roles()

    async def assert_that(self):
        return "karin" not in self.actual


class DoNotAddRoleWithHigherPositionTest(SubscribeTest):
    @property
    def description(self) -> str:
        return "Subscribe should not add a role with higher role position."

    async def arrange(self) -> str:
        return f"{self.prefix}sub add highrole"

    async def act(self) -> Sequence[discord.Role]:
        return self.fetch_own_roles()

    async def assert_that(self):
        return "highrole" not in self.actual


class ListReturnsRolesWithNoPermissionsTest(SubscribeTest):
    @property
    def description(self) -> str:
        return "Subscribe should list roles with no permissions."

    async def arrange(self) -> str:
        return f"{self.prefix}sub list"

    async def act(self) -> Sequence[discord.Role]:
        # Get a cleaned description from Polybot's embed message.
        message = await self.get_last_message()
        description: str = message.embeds[0].description
        cleaned_description = description.replace("*", "")

        # From this description, separate into role names
        role_names = cleaned_description.split("\n")
        role_names_log_string = "\n".join(role_names)
        logging.debug(f"Role Names in List:\n{role_names_log_string}\n")

        # All roles in guild
        roles = self.channel.guild.roles
        # The value of the permissions of a role when it has no permissions.
        no_permissions = discord.Permissions.none()
        # Separate roles that exist from those that don't.
        existing_roles = [role for role in roles if role.name in role_names]

        # Filter banned roles, which are those that have greater than 0
        # permissions.
        banned_roles = [role.name for role in existing_roles
                        if role.permissions != no_permissions]
        banned_roles_log_string = "\n".join(banned_roles)
        logging.debug(f"Banned Roles list:\n{banned_roles_log_string}\n")
        return banned_roles

    async def assert_that(self):
        return len(self.actual) == 0


class TestSubscribe(e2e_bot_test_case.E2EBotTestCase):
    @common.async_test
    async def test_add_adds_and_removes_single_role_if_valid(self):
        await self.run_tests(AddSingleRoleTest, RemoveSingleRoleTest)

    @common.async_test
    async def test_add_adds_and_removes_multiple_roles_if_valid(self):
        await self.run_tests(AddMultipleRolesTest, RemoveMultipleRolesTest)

    @common.async_test
    async def test_add_does_not_add_role_with_higher_position(self):
        await self.run_tests(DoNotAddRoleWithHigherPositionTest)

    @common.async_test
    async def test_add_does_not_add_role_with_permissions(self):
        await self.run_tests(DoNotAddRoleWithPermissionsTest)

    @common.async_test
    async def test_list_returns_roles_with_no_permissions(self):
        await self.run_tests(ListReturnsRolesWithNoPermissionsTest)


if __name__ == "__main__":
    unittest.main()
