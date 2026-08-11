"""Module author: waypoint_core project

Module description:
    Provides domain models for waypoint trail planning, including distance conversion,
    trail metadata validation, and itinerary aggregation.

Functions:
    Distance.__init__
    Distance.convert
    Distance.__repr__
    Trail.__init__
    Trail.validate_difficulty
    Trail.validate_non_negative
    Trail.set_default_unit
    Trail.get_difficulty
    Trail.set_difficulty
    Trail.from_dict
    Trail.__eq__
    Trail.__hash__
    Trail.__repr__
    Itinerary.__init__
    Itinerary.trails
    Itinerary.add_trail
    Itinerary.total_distance
"""

from typing import Any, Dict, List, Optional, Set


class Distance:
    """Immutable value type representing a physical distance with magnitude and unit."""

    KM_TO_MI = 0.6213711922
    MI_TO_KM = 1.609344
    ALLOWED_UNITS = {"km", "mi"}

    def __init__(self, magnitude: float, unit: str):
        """Initialize a Distance instance.

        Parameters:
            magnitude: Numeric value of the distance. Must be non-negative.
            unit: Unit of measure, either 'km' or 'mi'.

        Returns:
            None
        """
        unit_clean = unit.lower()
        if unit_clean not in self.ALLOWED_UNITS:
            raise ValueError(f"Invalid unit '{unit}'. Must be one of {self.ALLOWED_UNITS}")
        if magnitude < 0:
            raise ValueError("Distance magnitude cannot be negative.")

        self._magnitude = float(magnitude)
        self._unit = unit_clean

    @property
    def magnitude(self) -> float:
        return self._magnitude

    @property
    def unit(self) -> str:
        return self._unit

    def convert(self, target_unit: str) -> "Distance":
        """Convert this Distance to another unit.

        Parameters:
            target_unit: The desired unit for the returned Distance. Must be 'km' or 'mi'.

        Returns:
            A new Distance instance with the converted magnitude and requested unit.
        """
        target_clean = target_unit.lower()
        if target_clean not in self.ALLOWED_UNITS:
            raise ValueError(f"Invalid target unit '{target_unit}'.")

        if self._unit == target_clean:
            return Distance(self._magnitude, self._unit)

        if self._unit == "km" and target_clean == "mi":
            new_mag = self._magnitude * self.KM_TO_MI
        else:
            new_mag = self._magnitude * self.MI_TO_KM

        return Distance(new_mag, target_clean)

    def __repr__(self) -> str:
        """Return a developer-friendly string representation of the Distance."""
        return f"Distance({self._magnitude:.2f}, '{self._unit}')"


class Trail:
    """Domain model representing a single trail."""

    default_unit: str = "km"
    ALLOWED_DIFFICULTIES: Set[str] = {"Easy", "Moderate", "Hard", "Expert"}

    def __init__(
        self,
        trail_id: str | int,
        name: str,
        distance: Distance,
        elevation_gain_m: float,
        difficulty: str,
    ):
        """Initialize a Trail instance with validation.

        Parameters:
            trail_id: Unique identifier for the trail.
            name: Human-readable trail name.
            distance: Distance object for the trail length.
            elevation_gain_m: Elevation gain in meters. Must be non-negative.
            difficulty: Difficulty level string validated against allowed choices.

        Returns:
            None
        """
        self.id = trail_id
        self.name = name

        if not isinstance(distance, Distance):
            raise TypeError("distance must be an instance of Distance.")
        self.distance = distance

        self.elevation_gain_m = self.validate_non_negative(
            elevation_gain_m, "elevation_gain_m"
        )

        self._difficulty: str = ""
        self.set_difficulty(difficulty)

    @staticmethod
    def validate_difficulty(difficulty: str, allowed_set: Set[str]) -> str:
        """Validate the difficulty string against a permitted set.

        Parameters:
            difficulty: User-provided difficulty label.
            allowed_set: Set of valid difficulty strings.

        Returns:
            The validated difficulty string.
        """
        if difficulty not in allowed_set:
            raise ValueError(
                f"Invalid difficulty '{difficulty}'. Allowed: {allowed_set}"
            )
        return difficulty

    @staticmethod
    def validate_non_negative(value: float, field_name: str) -> float:
        """Validate that a numeric value is non-negative.

        Parameters:
            value: Numeric value to validate.
            field_name: Name of the field to include in error messages.

        Returns:
            The value converted to float if valid.
        """
        if value < 0:
            raise ValueError(f"{field_name} cannot be negative.")
        return float(value)

    @classmethod
    def set_default_unit(cls, unit: str) -> None:
        """Update the class-level default distance unit for newly created Trail objects.

        Parameters:
            unit: The default unit to use for new trails, either 'km' or 'mi'.

        Returns:
            None
        """
        unit_clean = unit.lower()
        if unit_clean not in Distance.ALLOWED_UNITS:
            raise ValueError(f"Invalid unit '{unit}'.")
        cls.default_unit = unit_clean

    def get_difficulty(self) -> str:
        """Return the difficulty level assigned to this trail."""
        return self._difficulty

    def set_difficulty(self, difficulty: str) -> None:
        """Validate and set a new difficulty level for this trail.

        Parameters:
            difficulty: The difficulty level to assign. Must be in the allowed set.

        Returns:
            None
        """
        self.validate_difficulty(difficulty, self.ALLOWED_DIFFICULTIES)
        self._difficulty = difficulty

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Trail":
        """Alternate constructor building a Trail from an API-shaped dict.

        Parameters:
            data: Dictionary containing trail fields, including 'id', 'name', 'distance',
                'elevation_gain_m', and 'difficulty'. Optional 'unit' field controls
                the Distance unit for the created object.

        Returns:
            A Trail instance populated from the provided payload.
        """
        unit = data.get("unit", cls.default_unit)
        dist_mag = data.get("distance")

        if dist_mag is None:
            raise ValueError("Missing 'distance' key in data payload.")

        distance_obj = Distance(dist_mag, unit)

        return cls(
            trail_id=data["id"],
            name=data["name"],
            distance=distance_obj,
            elevation_gain_m=data["elevation_gain_m"],
            difficulty=data["difficulty"],
        )

    def __eq__(self, other: object) -> bool:
        """Compare two Trail instances for equality by identifier.

        Parameters:
            other: Object to compare against.

        Returns:
            True if the other object is a Trail with the same id, otherwise False.
        """
        if not isinstance(other, Trail):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Return a hash value based on the trail identifier."""
        return hash(self.id)

    def __repr__(self) -> str:
        """Return a developer-friendly string representation of the Trail."""
        return f"Trail(id={self.id!r}, name={self.name!r}, distance={self.distance})"


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