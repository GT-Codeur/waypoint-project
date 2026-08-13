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

    def __add__(self, other: "Distance") -> "Distance":
        if not isinstance(other, Distance):
            return NotImplemented
        converted = other.convert(self._unit)
        return Distance(self._magnitude + converted.magnitude, self._unit)

    def __sub__(self, other: "Distance") -> "Distance":
        if not isinstance(other, Distance):
            return NotImplemented
        converted = other.convert(self._unit)
        new_mag = self._magnitude - converted.magnitude
        if new_mag < 0:
            raise ValueError("Subtractions yielding negative distance are not allowed.")
        return Distance(new_mag, self._unit)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Distance):
            return False
        converted = other.convert(self._unit)
        return abs(self._magnitude - converted.magnitude) < 1e-6

    def __lt__(self, other: "Distance") -> bool:
        if not isinstance(other, Distance):
            return NotImplemented
        converted = other.convert(self._unit)
        return self._magnitude < converted.magnitude

    def __gt__(self, other: "Distance") -> bool:
        if not isinstance(other, Distance):
            return NotImplemented
        converted = other.convert(self._unit)
        return self._magnitude > converted.magnitude

    def __str__(self) -> str:
        return f"{self._magnitude:.2f} {self._unit}"

    def __repr__(self) -> str:
        return f"Distance({self._magnitude:.2f}, '{self._unit}')"


