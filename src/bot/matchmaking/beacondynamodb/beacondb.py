from abc import ABC
from datetime import datetime, timezone
from typing import Dict, Optional, Sequence

import aioboto3
from boto3.dynamodb.conditions import Key

from ..beacons import BeaconBase, Game, Platform, WaitTime
from ..dataaccess import BeaconDataAccessBase


class DynamoDbQueryParams:
    """Class to encapsulate DynamoDb-specific query parameter combinations.

    Attributes:
        index_name: The DynamoDb table's index to query.
        expression: The AWS boto3 KeyConditionExpression.

    """
    def __init__(self, index_name: str, expression: object):
        """Initialise an instance of DynamoDbQueryParams. It is best to only
        use this initialiser directly when creating new query params for a new
        class method of DynamoDbQueryParams.

        Args:
            index_name: The DynamoDb table's index to query.
            expression: The AWS boto3 KeyConditionExpression.

        """
        self.index_name = index_name
        self.expression = expression

    @classmethod
    def list(cls):
        """Return query params for querying all active beacons."""
        return cls("AllAvailableBeacons",
                   Key("TypeName").eq("Beacon") &
                   Key("EndTime").gt(cls.now_timestamp()))

    @classmethod
    def list_for_game(cls, beacon: BeaconBase):
        """Return query params for querying all beacons by a specific game."""
        return cls("BeaconsByGameName",
                   Key("GameName").eq(beacon.game_name) &
                   Key("EndTime").gt(cls.now_timestamp()))

    @classmethod
    def list_by_user_id(cls, beacon: BeaconBase):
        """Return query params for querying all active beacons by user id."""
        return cls("BeaconsByUserId",
                   Key("UserId").eq(beacon.user_id) &
                   Key("EndTime").gt(cls.now_timestamp()))

    @staticmethod
    def now_timestamp() -> int:
        """Return the current time as a Unix timestamp in UTC timezone."""
        dt = datetime.now(timezone.utc)
        timestamp = int(dt.timestamp())
        return timestamp


def _item_from_beacon(beacon: BeaconBase) -> Dict:
    """Return an AWS DynamoDb item from a BeaconBase."""
    return {
        "UniqueId": f"{beacon.user_id}-{beacon.game_name}-"
                    f"{beacon.platform}-{beacon.start_timestamp}",
        "TypeName": "Beacon",
        "GameName": beacon.game_name,
        "PlatformName": beacon.platform,
        "GamePlatformCombination": f"{beacon.game_name}-"
                                   f"{beacon.platform}",
        "StartTime": beacon.start_timestamp,
        "EndTime": beacon.end_timestamp,
        "UserId": beacon.user_id,
        "Username": beacon.username
    }


def items_from_beacons(beacons: Sequence[BeaconBase]) -> Sequence[Dict]:
    """Return a sequence of AWS DynamoDb Items from a Sequence of
    BeaconBase.

    """
    return [_item_from_beacon(beacon) for beacon in beacons]


def item_to_dict(item: Dict) -> Dict:
    """Return a Dictionary, matching BeaconBase.__init__ args, from an AWS
    DynamoDb Item.

    """
    return {
        "user_id": item["UserId"],
        "username": item["Username"],
        "game": Game.from_str(item["GameName"]),
        "wait_time": WaitTime.from_timestamps(
            start_timestamp=int(float(item["StartTime"])),
            end_timestamp=int(float(item["EndTime"]))),
        "platform": Platform.from_str(item["PlatformName"]),
        "start": datetime.fromtimestamp(float(item["StartTime"]), timezone.utc)
    }


def _beacon_from_item(item: Dict) -> BeaconBase:
    """Return a BeaconBase from an AWS DynamoDb Item."""
    item_dict: Dict = item_to_dict(item)
    beacon: BeaconBase = BeaconBase.from_dict(item_dict)
    return beacon


def beacons_from_items(items: Sequence[Dict]) -> Sequence[BeaconBase]:
    """Return a Sequence of BeaconBase from a sequence of AWS DynamoDb
    Items.

    """
    return [_beacon_from_item(item) for item in items]


class BeaconDataAccessDynamoDb(BeaconDataAccessBase):
    """Implement BeaconDataAccessBase for DynamoDb access.

    Attributes:
        table_name: Name of DynamoDb table.
        region: AWS region that DynamoDb table is in.
        endpoint: URL of DynamoDb API endpoint.

    """
    def __init__(self,
                 table_name: str,
                 region: str,
                 endpoint: str,
                 profile: str,
                 *args, **kwargs):
        """Initialise Beacon DynamoDb access.

        Args:
            table_name: Name of DynamoDb table.
            region: AWS region that DynamoDb table is in.
            endpoint: URL of DynamoDb API endpoint.

        """
        super(BeaconDataAccessDynamoDb, self).__init__(*args, **kwargs)
        self.table_name = table_name
        self.region = region
        self.endpoint = endpoint
        self.profile = profile

    async def list(self) -> Sequence[BeaconBase]:
        params = DynamoDbQueryParams.list()
        items = await self._query(params)
        beacons = beacons_from_items(items)
        return beacons

    async def list_for_game(self, beacon: BeaconBase) -> Sequence[BeaconBase]:
        params = DynamoDbQueryParams.list_for_game(beacon)
        items = await self._query(params)
        beacons = beacons_from_items(items)
        return beacons

    async def list_by_user_id(self,
                              beacon: BeaconBase) -> Sequence[BeaconBase]:
        params = DynamoDbQueryParams.list_by_user_id(beacon)
        items = await self._query(params)
        beacons = beacons_from_items(items)
        return beacons

    async def add(self, beacons: Sequence[BeaconBase]) -> None:
        current_beacons = await self.list_by_user_id(beacons[0])
        merged_beacons = self._merge_with_existing(beacons, current_beacons)
        items = items_from_beacons(merged_beacons)
        await self._put(items)

    async def stop_by_user_id(self, beacon: BeaconBase) -> bool:
        current_beacons = await self.list_by_user_id(beacon)
        current_items = items_from_beacons(current_beacons)
        for item in current_items:
            item["EndTime"] = DynamoDbQueryParams.now_timestamp()
        await self._put(current_items)
        return len(current_beacons) > 0

    def _get_resource(self):
        session = aioboto3.session.Session(profile_name=self.profile)
        return session.resource("dynamodb",
                                region_name=self.region,
                                endpoint_url=self.endpoint)

    async def _query(self, params: DynamoDbQueryParams):
        async with self._get_resource() as resource:
            table = await resource.Table(self.table_name)
            response = await table.query(
                IndexName=params.index_name,
                KeyConditionExpression=params.expression
            )
            return response["Items"]

    async def _put(self, items: Sequence[Dict]):
        async with self._get_resource() as resource:
            table = await resource.Table(self.table_name)

            async with table.batch_writer() as writer:
                for item in items:
                    await writer.put_item(Item=item)

    def _merge_with_existing(self,
                             beacons: Sequence[BeaconBase],
                             existing: Sequence[BeaconBase]
                             ) -> Sequence[BeaconBase]:
        merged = []
        for beacon in beacons:
            index = self._try_index_of(beacon, existing)
            if index is None:
                merged.append(beacon)
            else:
                merged.append(self._update_times(beacon, existing[index]))

        return merged

    @staticmethod
    def _try_index_of(beacon: BeaconBase,
                      existing: Sequence[BeaconBase]) -> Optional[int]:
        try:
            return existing.index(beacon)
        except ValueError:
            return None

    @staticmethod
    def _update_times(beacon: BeaconBase,
                      current: BeaconBase) -> BeaconBase:
        wait_time = WaitTime.from_minutes(beacon.minutes_available)
        updated_beacon = BeaconBase.with_wait_time(current, wait_time)
        return updated_beacon
