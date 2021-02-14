import datetime
import unittest
from abc import ABC
from typing import Sequence

from src.matchmaking.beacondynamodb import beacondb
from src.matchmaking.beacons import BeaconBase, Game, Platform, WaitTime
from testing.common import A, B, async_test, create_beacon, \
    create_beacon_and_now_datetime
from testing.sit.data_access_test_case \
    import DataAccessTest, DataAccessTestCase


class BeaconDataAccessTest(DataAccessTest[A, B], ABC):
    """Concrete class specific for Beacon data access testing.
    Currently no extra functionality.

    """
    def __init__(self,
                 db: beacondb.BeaconDataAccessDynamoDb,
                 *args,
                 **kwargs):
        super(BeaconDataAccessTest, self).__init__(db, *args, **kwargs)


class AddBeaconAndQueryBeaconTest(BeaconDataAccessTest[
                                      BeaconBase,
                                      Sequence[BeaconBase]
                                  ]):
    @property
    def description(self) -> str:
        return "Should be able to add a Beacon to database."

    async def arrange(self) -> BeaconBase:
        return create_beacon()

    async def act(self) -> Sequence[BeaconBase]:
        await self.db.add([self.arranged_value])
        return await self.db.list()

    async def assert_that(self) -> bool:
        return self.arranged_value in self.actual and len(self.actual) == 1


class AddDuplicateBeaconsTest(BeaconDataAccessTest[
                                  BeaconBase,
                                  Sequence[BeaconBase]
                              ]):
    @property
    def description(self) -> str:
        return "Adding a beacon again updates current in database."

    async def arrange(self) -> BeaconBase:
        return create_beacon()

    async def act(self) -> Sequence[BeaconBase]:
        await self.db.add([self.arranged_value])
        await self.db.add([self.arranged_value])
        return await self.db.list()

    async def assert_that(self) -> bool:
        return self.arranged_value in self.actual and len(self.actual) == 1


class AddMultipleBeaconsTest(BeaconDataAccessTest[
                                 Sequence[BeaconBase],
                                 Sequence[BeaconBase]
                             ]):
    @property
    def description(self) -> str:
        return "Should be able to add multiple matchmaking to a database."

    async def arrange(self) -> Sequence[BeaconBase]:
        return [create_beacon(),
                create_beacon(game_name="mk11",
                              waiting_time=6.0,
                              platform_name="ps4")]

    async def act(self) -> Sequence[BeaconBase]:
        await self.db.add(self.arranged_value)
        return await self.db.list()

    async def assert_that(self) -> bool:
        return (self.arranged_value[0] in self.actual) and \
               (self.arranged_value[1] in self.actual) and \
               len(self.actual) == 2


class StopByUserIdTest(BeaconDataAccessTest[
                           Sequence[BeaconBase],
                           Sequence[BeaconBase]
                       ]):
    @property
    def description(self) -> str:
        return "Should be able to delete all matchmaking by a user in a db."

    async def arrange(self) -> Sequence[BeaconBase]:
        b1 = create_beacon()
        b2 = create_beacon(game_name="usf4",
                           waiting_time=6.0,
                           platform_name="pc")
        b2.user_id = "DUMMY"
        return [b1, b2]

    async def act(self) -> Sequence[BeaconBase]:
        await self.db.add(self.arranged_value)
        await self.db.stop_by_user_id(self.arranged_value[1])
        return await self.db.list_by_user_id(self.arranged_value[1])

    async def assert_that(self) -> bool:
        return len(self.actual) == 0


class ListReturnsValidBeacons(BeaconDataAccessTest[
                                  Sequence[BeaconBase],
                                  Sequence[BeaconBase]
                              ]):
    @property
    def description(self) -> str:
        return "Should return matchmaking with valid timeframes."

    async def arrange(self) -> Sequence[BeaconBase]:
        b1 = create_beacon()
        b2 = create_beacon(game_name="mk11",
                           waiting_time=6.0,
                           platform_name="ps4")
        b2._start_datetime = datetime.datetime.now(datetime.timezone.utc)
        b2._start_datetime -= datetime.timedelta(hours=1)
        b2.minutes_available = 15
        return [b1, b2]

    async def act(self) -> Sequence[BeaconBase]:
        await self.db.add(self.arranged_value)
        return await self.db.list()

    async def assert_that(self) -> bool:
        return self.arranged_value[0] in self.actual and len(self.actual) == 1


class ListForGameReturnsCorrectBeacons(BeaconDataAccessTest[
                                           Sequence[BeaconBase],
                                           Sequence[BeaconBase]
                                       ]):
    @property
    def description(self) -> str:
        return "Should return matchmaking only for requested game."

    async def arrange(self) -> Sequence[BeaconBase]:
        return [create_beacon(),
                create_beacon(game_name="3s",
                              waiting_time=6.0,
                              platform_name="pc")]

    async def act(self) -> Sequence[BeaconBase]:
        await self.db.add(self.arranged_value)
        return await self.db.list_for_game(self.arranged_value[1])

    async def assert_that(self) -> bool:
        return self.arranged_value[1] in self.actual and len(self.actual) == 1


class ListByUserIdReturnsCorrectBeacons(BeaconDataAccessTest[
                                            Sequence[BeaconBase],
                                            Sequence[BeaconBase]
                                        ]):
    @property
    def description(self) -> str:
        return "Should return matchmaking only for requested user."

    async def arrange(self) -> Sequence[BeaconBase]:
        b1 = create_beacon()
        b2 = create_beacon(game_name="usf4",
                           waiting_time=6.0,
                           platform_name="pc")
        b2.user_id = "DUMMY"
        return [b1, b2]

    async def act(self) -> Sequence[BeaconBase]:
        await self.db.add(self.arranged_value)
        return await self.db.list_by_user_id(self.arranged_value[1])

    async def assert_that(self) -> bool:
        return self.arranged_value[1] in self.actual and len(self.actual) == 1


class TestBeaconDataAccess(DataAccessTestCase):
    @async_test
    async def test_add_and_query_a_beacon(self):
        await self.run_tests(AddBeaconAndQueryBeaconTest)

    @async_test
    async def test_add_duplicates(self):
        await self.run_tests(AddDuplicateBeaconsTest)

    @async_test
    async def test_add_multiple(self):
        await self.run_tests(AddMultipleBeaconsTest,
                             StopByUserIdTest)

    @async_test
    async def test_list_returns_valid_beacons(self):
        await self.run_tests(ListReturnsValidBeacons,
                             ListForGameReturnsCorrectBeacons,
                             ListByUserIdReturnsCorrectBeacons)


class TestBeaconDataAccessFunctions(unittest.TestCase):
    def test_item_from_beacon(self):
        beacon = create_beacon()

        expected = {
            "UniqueId": f"1234567890-st-pc-{beacon.start_timestamp}",
            "TypeName": "Beacon",
            "GameName": "st",
            "PlatformName": "pc",
            "GamePlatformCombination": "st-pc",
            "StartTime": beacon.start_timestamp,
            "EndTime": beacon.end_timestamp,
            "UserId": "1234567890",
            "Username": "Test Dummy Name"
        }

        actual = beacondb._item_from_beacon(
            beacon)
        self.assertTrue(actual == expected)

    def test_items_from_beacons(self):
        b1, now = create_beacon_and_now_datetime()
        b2 = create_beacon(game_name="mk11",
                           waiting_time=6.0,
                           platform_name="pc",
                           start=now)

        expected1 = {
            "UniqueId": f"1234567890-st-pc-{b1.start_timestamp}",
            "TypeName": "Beacon",
            "GameName": "st",
            "PlatformName": "pc",
            "GamePlatformCombination": "st-pc",
            "StartTime": b1.start_timestamp,
            "EndTime": b1.end_timestamp,
            "UserId": "1234567890",
            "Username": "Test Dummy Name"
        }

        expected2 = {
            "UniqueId": f"1234567890-mk11-pc-{b2.start_timestamp}",
            "TypeName": "Beacon",
            "GameName": "mk11",
            "PlatformName": "pc",
            "GamePlatformCombination": "mk11-pc",
            "StartTime": b2.start_timestamp,
            "EndTime": b2.end_timestamp,
            "UserId": "1234567890",
            "Username": "Test Dummy Name"
        }

        actual = beacondb.items_from_beacons([b1, b2])
        self.assertEqual(actual, [expected1, expected2])

    def test_item_to_dict(self):
        beacon, now = create_beacon_and_now_datetime()

        item = {
            "UniqueId": f"1234567890-st-pc-{beacon.start_timestamp}",
            "TypeName": "Beacon",
            "GameName": "st",
            "PlatformName": "pc",
            "GamePlatformCombination": "st-pc",
            "StartTime": beacon.start_timestamp,
            "EndTime": beacon.end_timestamp,
            "UserId": "1234567890",
            "Username": "Test Dummy Name"
        }

        expected = {
            "user_id": beacon.user_id,
            "username": beacon.username,
            "game": Game.from_str(beacon.game_name),
            "wait_time": WaitTime.from_timestamps(
                start_timestamp=beacon.start_timestamp,
                end_timestamp=beacon.end_timestamp
            ),
            "platform": Platform.from_str(beacon.platform),
            "start": beacon._start_datetime
        }

        actual = beacondb.item_to_dict(item)
        self.assertEqual(actual, expected)

    def test_beacon_from_item(self):
        beacon, now = create_beacon_and_now_datetime()

        item = {
            "UniqueId": f"1234567890-st-pc-{beacon.start_timestamp}",
            "TypeName": "Beacon",
            "GameName": "st",
            "PlatformName": "pc",
            "GamePlatformCombination": "st-pc",
            "StartTime": beacon.start_timestamp,
            "EndTime": beacon.end_timestamp,
            "UserId": "1234567890",
            "Username": "Test Dummy Name"
        }

        beacon_from_item = beacondb._beacon_from_item(item)
        actual = beacon_from_item.full_equality(beacon)
        self.assertTrue(actual)

    def test_beacons_from_items(self):
        b1, now = create_beacon_and_now_datetime()
        b2 = create_beacon(game_name="mk11",
                           waiting_time=6.0,
                           platform_name="pc",
                           start=now)

        items = [
            {
                "UniqueId": f"1234567890-st-pc-{b1.start_timestamp}",
                "TypeName": "Beacon",
                "GameName": "st",
                "PlatformName": "pc",
                "GamePlatformCombination": "st-pc",
                "StartTime": b1.start_timestamp,
                "EndTime": b1.end_timestamp,
                "UserId": "1234567890",
                "Username": "Test Dummy Name"
            },
            {
                "UniqueId": f"1234567890-mk11-pc-{b2.start_timestamp}",
                "TypeName": "Beacon",
                "GameName": "mk11",
                "PlatformName": "pc",
                "GamePlatformCombination": "mk11-pc",
                "StartTime": b2.start_timestamp,
                "EndTime": b2.end_timestamp,
                "UserId": "1234567890",
                "Username": "Test Dummy Name"
            }
        ]

        beacons = beacondb.beacons_from_items(items)
        actual1 = b1.full_equality(beacons[0])
        actual2 = b2.full_equality(beacons[1])
        self.assertTrue(actual1 and actual2)


class TestDataDynamoDbQueryParams(unittest.TestCase):
    def test_list_does_not_throw(self):
        try:
            beacondb.DynamoDbQueryParams \
                .list()
        except Exception:
            self.fail("list() raised an exception.")

    def test_list_for_game_does_not_throw(self):
        try:
            beacon = create_beacon()
            beacondb.DynamoDbQueryParams.list_for_game(beacon)
        except Exception:
            self.fail("list_for_game() raised an exception.")

    def test_list_by_user_id_does_not_throw(self):
        try:
            beacon = create_beacon()
            beacondb.DynamoDbQueryParams.list_by_user_id(beacon)
        except Exception:
            self.fail("list_by_user_id() raised an exception.")

    def test_now_timestamp_returns_int(self):
        timestamp = beacondb.DynamoDbQueryParams.now_timestamp()
        self.assertTrue(type(timestamp) is int)
