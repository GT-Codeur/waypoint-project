from abc import ABC, abstractmethod
from typing import List, Set, Dict, Any, Type, TypeVar
from models.distance import Distance
from models.mixins import ElevationMixin, RatingMixin

T = TypeVar("T", bound="Trail")

class Trail(ABC):
    """Abstract Base Class maintaining all Sprint 1 state guards + Sprint 2 polymorphism."""

    default_unit: str = "km"
    ALLOWED_DIFFICULTIES: Set[str] = {"Easy", "Moderate", "Hard", "Expert"}

    def __init__(
        self,
        trail_id: str | int,
        name: str,
        distance: Distance,
        elevation_gain_m: float,
        difficulty: str,
        **kwargs,
    ):
        super().__init__(**kwargs)
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

    # --- WP-103: Static Validators & Class Methods ---
    @staticmethod
    def validate_difficulty(difficulty: str, allowed_set: Set[str]) -> str:
        if difficulty not in allowed_set:
            raise ValueError(
                f"Invalid difficulty '{difficulty}'. Allowed: {allowed_set}"
            )
        return difficulty

    @staticmethod
    def validate_non_negative(value: float, field_name: str) -> float:
        if value < 0:
            raise ValueError(f"{field_name} cannot be negative.")
        return float(value)

    @classmethod
    def set_default_unit(cls, unit: str) -> None:
        unit_clean = unit.lower()
        if unit_clean not in Distance.ALLOWED_UNITS:
            raise ValueError(f"Invalid unit '{unit}'.")
        cls.default_unit = unit_clean

    # --- WP-102: Encapsulated Difficulty State Guards ---
    def get_difficulty(self) -> str:
        return self._difficulty

    def set_difficulty(self, difficulty: str) -> None:
        self.validate_difficulty(difficulty, self.ALLOWED_DIFFICULTIES)
        self._difficulty = difficulty

    # --- WP-103: Polymorphic Alternate Constructor ---
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Constructs a Trail instance from an API-shaped dict."""
        unit = data.get("unit", cls.default_unit)
        dist_mag = data.get("distance")

        if dist_mag is None:
            raise ValueError("Missing 'distance' key in data payload.")

        distance_obj = Distance(dist_mag, unit)

        # If invoked directly on Trail, route to concrete subclass via 'kind' key
        target_cls = cls
        if target_cls is Trail:
            kind = data.get("kind", "DayHike")
            registry = {
                "DayHike": DayHike,
                "BackpackingRoute": BackpackingRoute,
                "TrailRun": TrailRun,
                "GuidedDayHike": GuidedDayHike,
            }
            if kind not in registry:
                raise ValueError(f"Unknown trail kind '{kind}'.")
            target_cls = registry[kind]  # type: ignore

        # Filter out explicitly consumed parameters
        extra_kwargs = {
            k: v
            for k, v in data.items()
            if k not in {"id", "name", "distance", "elevation_gain_m", "difficulty", "unit", "kind"}
        }

        return target_cls(
            trail_id=data["id"],
            name=data["name"],
            distance=distance_obj,
            elevation_gain_m=data["elevation_gain_m"],
            difficulty=data["difficulty"],
            **extra_kwargs,
        )

    # --- WP-201: Abstract Methods & Behavioral Defaults ---
    @abstractmethod
    def estimated_time(self) -> float:
        """Returns estimated completion time in hours."""
        pass

    @abstractmethod
    def summary(self) -> str:
        """Returns a summary string of the trail."""
        pass

    def packing_list(self) -> List[str]:
        return ["Water", "First Aid Kit", "Navigation Map"]

    # --- WP-104: Identity Equality ---
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Trail):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id!r}, name={self.name!r}, distance={self.distance})"

class TrailRun(Trail):
    """Fast-paced trail running route."""

    def estimated_time(self) -> float:
        # Fast pace: ~10 km/h + 1 hour per 1000m elevation
        km = self.distance.convert("km").magnitude
        return (km / 10.0) + (self.elevation_gain_m / 1000.0)

    def summary(self) -> str:
        return f"Trail Run: {self.name} ({self.distance})"

class DayHike(Trail):
    """Single-day hiking route."""

    def estimated_time(self) -> float:
        # Naismith's Rule: ~4 km/h plus 1 hour per 600m elevation gain
        km = self.distance.convert("km").magnitude
        return (km / 4.0) + (self.elevation_gain_m / 600.0)

    def summary(self) -> str:
        return f"Day Hike: {self.name} ({self.distance})"


class BackpackingRoute(Trail):
    """Multi-day expedition route."""

    def __init__(self, *args, recommended_days: int = 2, **kwargs):
        super().__init__(*args, **kwargs)
        self.recommended_days = recommended_days

    def estimated_time(self) -> float:
        # Slower pace due to heavy packs: ~2.5 km/h + 1 hr per 400m elevation
        km = self.distance.convert("km").magnitude
        return (km / 2.5) + (self.elevation_gain_m / 400.0)

    def summary(self) -> str:
        return f"Backpacking Route: {self.name} ({self.recommended_days} days)"

    # WP-204: Method Override extending parent behavior
    def packing_list(self) -> List[str]:
        items = super().packing_list()
        items.extend(["Tent", "Sleeping Bag", "Multi-day Food", "Camp Stove"])
        return items

# WP-203: Further inheritance level
class GuidedDayHike(DayHike):
    """A day hike led by a professional guide."""

    def __init__(self, *args, guide_name: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.guide_name = guide_name

    def estimated_time(self) -> float:
        # Guided hikes run slightly slower (3 km/h pace) due to group stops
        km = self.distance.convert("km").magnitude
        return (km / 3.0) + (self.elevation_gain_m / 500.0)

    def summary(self) -> str:
        return f"Guided Hike with {self.guide_name}: {self.name}"


# WP-205: Composed class combining Mixins + Inheritance
class RatedAlpineHike(ElevationMixin, RatingMixin, DayHike):
    """A day hike composed with Elevation and Rating mixins."""

    pass


# =====================================================================
# WP-206: Polymorphic Duck-Typed Object
# =====================================================================
class FakeTrail:
    """Duck-typed object inheriting nothing from Trail."""

    def __init__(self, name: str, fixed_time_hours: float):
        self.name = name
        self.fixed_time_hours = fixed_time_hours

    def estimated_time(self) -> float:
        return self.fixed_time_hours

    def summary(self) -> str:
        return f"FakeTrail (Mock): {self.name}"

