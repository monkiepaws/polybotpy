from abc import ABC, abstractmethod
from typing import Sequence

from matchmaking.beacons import BeaconBase


class BeaconDataAccessBase(ABC):
    """Abstract class for accessing Beacon and matchmaking data."""
    @abstractmethod
    async def list(self) -> Sequence[BeaconBase]:
        """Return all active beacons."""
        return []

    @abstractmethod
    async def list_for_game(self, beacon: BeaconBase) -> Sequence[BeaconBase]:
        """Return all active beacons for a specific game."""
        return []

    @abstractmethod
    async def list_by_user_id(self,
                              beacon: BeaconBase) -> Sequence[BeaconBase]:
        """Return all active beacons for a specific user id."""
        return []

    @abstractmethod
    async def add(self, beacons: Sequence[BeaconBase]) -> None:
        """Update a beacon if it exists, otherwise add a new beacon."""
        return None

    @abstractmethod
    async def stop_by_user_id(self, beacon: BeaconBase) -> bool:
        """Stop all active beacons by a specific user id."""
        return False
