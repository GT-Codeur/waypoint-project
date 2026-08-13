from typing import Optional, List
from distance import Distance
from trails.base import Trail
class Itinerary:
    """Composes an ordered list of trails into a complete route."""

    def __init__(self, trails: Optional[List[Trail]] = None):
        """Initialize an Itinerary with an optional list of Trail objects.

        Parameters:
            trails: Optional list of Trail instances to seed the itinerary.

        Returns:
            None
        """
        # Deep copy list reference to protect instance state encapsulation
        self._trails: List[Trail] = list(trails) if trails is not None else []

    @property
    def trails(self) -> List[Trail]:
        """Return a shallow copy of the itinerary trail list."""
        return list(self._trails)

    def add_trail(self, trail: Trail) -> None:
        """Append a Trail to the itinerary.

        Parameters:
            trail: Trail instance to add to the itinerary.

        Returns:
            None
        """
        if not isinstance(trail, Trail):
            raise TypeError("Expected a Trail instance.")
        self._trails.append(trail)

    def total_distance(self, target_unit: Optional[str] = None) -> Distance:
        """Calculate the sum of distances for all trails in the itinerary.

        Parameters:
            target_unit: Optional unit for the returned Distance. If omitted,
                the Trail.default_unit is used.

        Returns:
            A Distance instance representing the itinerary total.
        """
        unit = target_unit.lower() if target_unit else Trail.default_unit
        total_mag = sum(t.distance.convert(unit).magnitude for t in self._trails)
        return Distance(total_mag, unit)