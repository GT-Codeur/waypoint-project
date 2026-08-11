"""Module author: waypoint_core project

Module description:
    Contains unit tests for the waypoint_core models, validating distance conversion,
    trail validation, and itinerary aggregation logic.

Functions:
    TestDistance.test_distance_valid_initialization
    TestDistance.test_distance_rejects_negative_magnitude
    TestDistance.test_distance_rejects_invalid_unit
    TestDistance.test_distance_convert_round_trip
    TestTrail.test_build_trail_from_dict_populates_correctly
    TestTrail.test_from_dict_negative_distance_raises_value_error
    TestTrail.test_invalid_difficulty_raises_value_error
    TestTrail.test_two_trails_same_id_compare_equal
    TestTrail.test_two_trails_different_id_compare_not_equal
    TestTrail.test_changing_default_unit_affects_newly_created_trails_only
    TestItinerary.test_itinerary_three_trails_reports_correct_total_distance
    TestItinerary.test_itinerary_isolation_adding_trail_does_not_mutate_others
    TestItinerary.test_itinerary_constructor_list_encapsulation
"""

import pytest
from models import Distance, Itinerary, Trail


class TestDistance:
    """WP-101 & AC: Distance rejects negative magnitude and convert() round-trips within tolerance."""

    def test_distance_valid_initialization(self):
        """Verify Distance stores magnitude and unit correctly on initialization."""
        d = Distance(10.0, "km")
        assert d.magnitude == 10.0
        assert d.unit == "km"

    def test_distance_rejects_negative_magnitude(self):
        """Ensure initializing Distance with a negative magnitude raises ValueError."""
        with pytest.raises(ValueError, match="cannot be negative"):
            Distance(-5.0, "km")

    def test_distance_rejects_invalid_unit(self):
        """Confirm Distance rejects unsupported units during initialization."""
        with pytest.raises(ValueError, match="Invalid unit"):
            Distance(10.0, "furlongs")

    def test_distance_convert_round_trip(self):
        """Validate that converting a Distance to miles and back returns the original value."""
        original = Distance(10.0, "km")
        converted_to_mi = original.convert("mi")
        round_trip = converted_to_mi.convert("km")

        # Round-trips within small tolerance
        assert pytest.approx(original.magnitude, abs=1e-5) == round_trip.magnitude
        assert round_trip.unit == "km"


class TestTrail:
    """WP-102, WP-103, WP-104 & AC: Trail creation, validation, equality, and default unit changes."""

    def test_build_trail_from_dict_populates_correctly(self):
        """Verify Trail.from_dict creates a Trail object with correct values from input data."""
        payload = {
            "id": "T-100",
            "name": "Pacific Crest Section",
            "distance": 15.5,
            "elevation_gain_m": 800,
            "difficulty": "Hard",
            "unit": "km",
        }
        trail = Trail.from_dict(payload)

        assert trail.id == "T-100"
        assert trail.name == "Pacific Crest Section"
        assert trail.distance.magnitude == 15.5
        assert trail.distance.unit == "km"
        assert trail.elevation_gain_m == 800.0
        assert trail.get_difficulty() == "Hard"

    def test_from_dict_negative_distance_raises_value_error(self):
        """Check that Trail.from_dict raises on negative distance values."""
        payload = {
            "id": "T-101",
            "name": "Invalid Trail",
            "distance": -12.0,
            "elevation_gain_m": 100,
            "difficulty": "Easy",
        }
        with pytest.raises(ValueError, match="cannot be negative"):
            Trail.from_dict(payload)

    def test_invalid_difficulty_raises_value_error(self):
        """Ensure both constructor and setter reject invalid difficulty strings."""
        dist = Distance(5.0, "km")
        with pytest.raises(ValueError, match="Invalid difficulty"):
            Trail("T-102", "Extreme Trail", dist, 200, "Insane")

        trail = Trail("T-102", "Extreme Trail", dist, 200, "Easy")
        with pytest.raises(ValueError, match="Invalid difficulty"):
            trail.set_difficulty("Impossible")

    def test_two_trails_same_id_compare_equal(self):
        """Verify that Trail equality is based on id, not on other fields."""
        d1 = Distance(10.0, "km")
        d2 = Distance(25.0, "mi")

        trail_a = Trail(
            trail_id="T-001",
            name="Trail Alpha",
            distance=d1,
            elevation_gain_m=300,
            difficulty="Easy",
        )
        trail_b = Trail(
            trail_id="T-001",  # Same ID
            name="Trail Alpha (Updated)",
            distance=d2,
            elevation_gain_m=600,
            difficulty="Hard",
        )

        assert trail_a == trail_b

    def test_two_trails_different_id_compare_not_equal(self):
        """Ensure Trail objects with different ids do not compare equal."""
        d = Distance(10.0, "km")
        trail_a = Trail("T-001", "Trail A", d, 300, "Easy")
        trail_b = Trail("T-002", "Trail B", d, 300, "Easy")

        assert trail_a != trail_b

    def test_changing_default_unit_affects_newly_created_trails_only(self):
        """Confirm changing Trail.default_unit only impacts new Trail instances."""
        Trail.set_default_unit("km")
        payload = {
            "id": "T-201",
            "name": "First Trail",
            "distance": 10.0,
            "elevation_gain_m": 100,
            "difficulty": "Moderate",
        }
        trail_1 = Trail.from_dict(payload)

        # Switch class default unit
        Trail.set_default_unit("mi")

        trail_2 = Trail.from_dict(
            {
                "id": "T-202",
                "name": "Second Trail",
                "distance": 10.0,
                "elevation_gain_m": 100,
                "difficulty": "Moderate",
            }
        )

        # Pre-existing trail retains its original unit; new trail picks up new default
        assert trail_1.distance.unit == "km"
        assert trail_2.distance.unit == "mi"


class TestItinerary:
    """WP-105 & AC: Itinerary distance aggregation and state isolation."""

    @pytest.fixture
    def sample_trails(self):
        """Provide a reusable set of sample Trail objects for itinerary tests."""
        return [
            Trail("1", "Trail 1", Distance(5.0, "km"), 100, "Easy"),
            Trail("2", "Trail 2", Distance(10.0, "km"), 200, "Moderate"),
            Trail("3", "Trail 3", Distance(15.0, "km"), 300, "Hard"),
        ]

    def test_itinerary_three_trails_reports_correct_total_distance(self, sample_trails):
        """Validate total_distance aggregates all trail distances in the requested unit."""
        itinerary = Itinerary(sample_trails)
        total = itinerary.total_distance(target_unit="km")

        assert total.magnitude == 30.0
        assert total.unit == "km"

    def test_itinerary_isolation_adding_trail_does_not_mutate_others(self, sample_trails):
        """Ensure adding a trail to one itinerary does not mutate other itinerary instances."""
        itinerary_a = Itinerary([sample_trails[0]])
        itinerary_b = Itinerary([sample_trails[1]])

        itinerary_a.add_trail(sample_trails[2])

        assert len(itinerary_a.trails) == 2
        assert len(itinerary_b.trails) == 1

    def test_itinerary_constructor_list_encapsulation(self, sample_trails):
        """Check the Itinerary constructor copies the provided list to avoid external state mutation."""
        external_list = [sample_trails[0]]
        itinerary = Itinerary(external_list)

        # Modifying the external list passed into __init__ should not mutate itinerary state
        external_list.append(sample_trails[1])
        assert len(itinerary.trails) == 1