import pytest

from models.distance import Distance
from models.trail import (
    BackpackingRoute,
    DayHike,
    FakeTrail,
    GuidedDayHike,
    Trail,
    TrailRun,
)

# =====================================================================
# Plain Helper Function
# =====================================================================


def create_sample_day_hike() -> DayHike:
    """Helper function to build a default DayHike instance."""
    return DayHike(
        trail_id=1,
        name="Cascade Pass",
        distance=Distance(12.0, "km"),
        elevation_gain_m=600.0,
        difficulty="Moderate",
    )


# =====================================================================
# 1. Abstract Base Class & Validation Tests
# =====================================================================


def test_trail_direct_instantiation_raises_type_error():
    """Verifies that Trail cannot be instantiated directly (ABC protection)."""
    with pytest.raises(TypeError, match="Can't instantiate abstract class Trail"):
        Trail(1, "Test", Distance(10, "km"), 200, "Easy")  # type: ignore


def test_invalid_distance_type_raises_type_error():
    """Verifies that non-Distance objects passed to distance trigger a TypeError."""
    with pytest.raises(
        TypeError, match="distance must be an instance of Distance."
    ):
        DayHike(1, "Test", "12 km", 200, "Easy")  # Passing raw string instead of Distance


def test_negative_elevation_raises_value_error():
    """Verifies state guard for negative elevation gain."""
    with pytest.raises(ValueError, match="elevation_gain_m cannot be negative."):
        DayHike(1, "Test", Distance(10, "km"), -50.0, "Easy")


@pytest.mark.parametrize("invalid_diff", ["Extreme", "easy", "SuperHard", ""])
def test_invalid_difficulty_raises_value_error(invalid_diff: str):
    """Verifies state guard for allowed difficulty set."""
    with pytest.raises(ValueError, match="Invalid difficulty"):
        DayHike(1, "Test", Distance(10, "km"), 200, invalid_diff)


def test_difficulty_getter_and_setter():
    """Verifies encapsulated difficulty getter and setter."""
    hike = create_sample_day_hike()
    assert hike.get_difficulty() == "Moderate"

    hike.set_difficulty("Hard")
    assert hike.get_difficulty() == "Hard"


def test_set_default_unit():
    """Verifies class-level default unit updates and validation."""
    DayHike.set_default_unit("mi")
    assert DayHike.default_unit == "mi"

    with pytest.raises(ValueError, match="Invalid unit 'invalid_unit'."):
        DayHike.set_default_unit("invalid_unit")

    # Reset default unit back to km
    DayHike.set_default_unit("km")


# =====================================================================
# 2. Polymorphic Factory (`from_dict`) Tests
# =====================================================================


def test_from_dict_routing_and_deserialization():
    """Verifies dynamic factory creation from API-shaped dictionary."""
    payload = {
        "id": "T100",
        "name": "Skyline Loop",
        "distance": 8.0,
        "unit": "km",
        "elevation_gain_m": 400.0,
        "difficulty": "Hard",
        "kind": "TrailRun",
    }

    trail = Trail.from_dict(payload)
    assert isinstance(trail, TrailRun)
    assert trail.id == "T100"
    assert trail.name == "Skyline Loop"
    assert trail.get_difficulty() == "Hard"


def test_from_dict_with_subclass_specific_kwargs():
    """Verifies passing extra kwargs (like recommended_days or guide_name) via from_dict."""
    backpack_payload = {
        "id": 2,
        "name": "Wonderland Trail",
        "distance": 150.0,
        "elevation_gain_m": 7000.0,
        "difficulty": "Expert",
        "kind": "BackpackingRoute",
        "recommended_days": 10,
    }
    route = Trail.from_dict(backpack_payload)
    assert isinstance(route, BackpackingRoute)
    assert route.recommended_days == 10

    guided_payload = {
        "id": 3,
        "name": "Glacier Trail",
        "distance": 10.0,
        "elevation_gain_m": 500.0,
        "difficulty": "Moderate",
        "kind": "GuidedDayHike",
        "guide_name": "Sarah Connor",
    }
    guided = Trail.from_dict(guided_payload)
    assert isinstance(guided, GuidedDayHike)
    assert guided.guide_name == "Sarah Connor"


def test_from_dict_missing_distance_raises_error():
    """Verifies error handling when distance key is missing."""
    with pytest.raises(
        ValueError, match="Missing 'distance' key in data payload."
    ):
        Trail.from_dict({"id": 1, "name": "No Dist", "elevation_gain_m": 100})


def test_from_dict_unknown_kind_raises_error():
    """Verifies error handling for unregistered trail kind."""
    payload = {
        "id": 1,
        "name": "Unknown",
        "distance": 5.0,
        "elevation_gain_m": 100,
        "difficulty": "Easy",
        "kind": "SpaceHike",
    }
    with pytest.raises(ValueError, match="Unknown trail kind 'SpaceHike'."):
        Trail.from_dict(payload)


# =====================================================================
# 3. Subclass Method & Calculation Tests
# =====================================================================


def test_day_hike_calculations():
    """Verifies DayHike estimated time (Naismith's Rule: km/4 + elev/600)."""
    hike = DayHike(1, "Pass", Distance(12.0, "km"), 600.0, "Moderate")

    # (12 / 4.0) + (600 / 600.0) = 3.0 + 1.0 = 4.0 hours
    assert hike.estimated_time() == 4.0
    assert "Day Hike: Pass" in hike.summary()


def test_trail_run_calculations():
    """Verifies TrailRun estimated time (km/10 + elev/1000)."""
    run = TrailRun(1, "Fast Loop", Distance(20.0, "km"), 1000.0, "Hard")

    # (20 / 10.0) + (1000 / 1000.0) = 2.0 + 1.0 = 3.0 hours
    assert run.estimated_time() == 3.0
    assert "Trail Run: Fast Loop" in run.summary()


def test_backpacking_route_gear_and_calculations():
    """Verifies BackpackingRoute time calculation and extended packing list."""
    route = BackpackingRoute(
        1, "PCT Section", Distance(25.0, "km"), 800.0, "Hard", recommended_days=3
    )

    # (25 / 2.5) + (800 / 400.0) = 10.0 + 2.0 = 12.0 hours
    assert route.estimated_time() == 12.0
    assert "3 days" in route.summary()

    # Packing list must contain base items PLUS extended equipment
    items = route.packing_list()
    assert "Water" in items
    assert "First Aid Kit" in items
    assert "Tent" in items
    assert "Camp Stove" in items


def test_guided_day_hike_calculations():
    """Verifies GuidedDayHike overrides."""
    guided = GuidedDayHike(
        1,
        "Summit",
        Distance(9.0, "km"),
        500.0,
        "Moderate",
        guide_name="Alex Honnold",
    )

    # (9 / 3.0) + (500 / 500.0) = 3.0 + 1.0 = 4.0 hours
    assert guided.estimated_time() == 4.0
    assert "Guided Hike with Alex Honnold: Summit" in guided.summary()


# =====================================================================
# 4. Identity, Equality & Duck Typing Tests
# =====================================================================


def test_trail_equality_and_hashing():
    """Verifies identity equality based on trail_id."""
    hike1 = DayHike(101, "Trail A", Distance(5, "km"), 100, "Easy")
    hike2 = DayHike(101, "Trail A (Updated Name)", Distance(10, "km"), 200, "Hard")
    hike3 = DayHike(202, "Trail B", Distance(5, "km"), 100, "Easy")

    assert hike1 == hike2
    assert hike1 != hike3
    assert hike1 != "NotATrailObject"
    assert hash(hike1) == hash(hike2)


def test_polymorphic_duck_typing():
    """Verifies that FakeTrail works seamlessly in polymorphic operations (WP-206)."""
    fake = FakeTrail("Virtual Route", 2.5)
    assert fake.estimated_time() == 2.5
    assert fake.summary() == "FakeTrail (Mock): Virtual Route"

    trails = [fake]
    for t in trails:
        assert hasattr(t, "estimated_time")
        assert hasattr(t, "summary")