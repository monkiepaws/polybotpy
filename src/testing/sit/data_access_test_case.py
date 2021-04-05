import abc
import os
import unittest
from typing import Dict, Sequence, Type

import src.bot.bot as bot
import src.bot.matchmaking.beacondynamodb.beacondb as beacondb
import src.testing.common as common


# must load environment file for later use.
bot.load_environment()


class DataAccessTest(common.MPIntegrationTest[common.A, common.B], abc.ABC):
    """Test specific for accessing Beacon data from DynamoDb."""
    def __init__(self, db: beacondb.BeaconDataAccessDynamoDb, *args, **kwargs):
        super(DataAccessTest, self).__init__(*args, **kwargs)
        self.db: beacondb.BeaconDataAccessDynamoDb = db

    async def _setup(self) -> None:
        """Delete all items that exist in test database before testing."""
        async def get_items():
            async with self.db._get_resource() as resource:
                table = await resource.Table(self.db.table_name)
                response = await table.scan()
                return response["Items"]

        async def delete_items(items_to_delete: Sequence[Dict]):
            async with self.db._get_resource() as resource:
                table = await resource.Table(self.db.table_name)

                async with table.batch_writer() as writer:
                    for item in items_to_delete:
                        await writer.delete_item(Key={
                            "UniqueId": item["UniqueId"],
                            "StartTime": item["StartTime"]
                        })

        items = await get_items()
        await delete_items(items)


class DataAccessTestCase(unittest.TestCase):
    """TestCase specific for testing Beacon access from DynamoDb."""

    # Data access instance to test.
    db: beacondb.BeaconDataAccessDynamoDb = beacondb.BeaconDataAccessDynamoDb(
        table_name=os.getenv("DYNAMO_DB_TABLE_NAME"),
        region=os.getenv("DYNAMO_DB_REGION"),
        endpoint=os.getenv("DYNAMO_DB_ENDPOINT"),
        profile=os.getenv("DYNAMO_DB_AWS_PROFILE")
    )

    def __init__(self, *args, **kwargs):
        super(DataAccessTestCase, self).__init__(*args, **kwargs)

    async def run_tests(self, *tests: Type[DataAccessTest]) -> None:
        """Call unittest methods on behalf of each test passed in. Must be
        called in a method that is named starting with test so it is discovered
        by unittest. Must use DataAccessTest tests.

        Usage:
            @testing.common.async_test
            async def test_example_tests_should_be_true(self):
                await self.run_tests(ExampleTest1, ExampleTest2)

        Args:
            tests: DataAccessTest to be performed.

        """
        for test_class in tests:
            test = test_class(self.db)
            with self.subTest(command=test.description):
                await test.start()
                self.assertTrue(test.result)
