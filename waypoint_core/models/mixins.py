class ElevationMixin:
    """Mixin for calculating average slope/grade percentage."""

    def average_grade(self) -> float:
        # Assumes self has distance (Distance) and elevation_gain_m (float)
        dist_m = self.distance.convert("km").magnitude * 1000.0  # type: ignore
        if dist_m == 0:
            return 0.0
        return (self.elevation_gain_m / dist_m) * 100  # type: ignore

    def summary(self) -> str:
        base = super().summary() if hasattr(super(), "summary") else ""  # type: ignore
        return f"{base} | Avg Grade: {self.average_grade():.1f}%"


class RatingMixin:
    """Mixin for tracking user rating scores."""

    def __init__(self, *args, rating: float = 5.0, **kwargs):
        super().__init__(*args, **kwargs)
        self.rating = rating

    def summary(self) -> str:
        base = super().summary() if hasattr(super(), "summary") else ""  # type: ignore
        return f"{base} | Rating: {self.rating}/5.0★"