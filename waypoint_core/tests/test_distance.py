"""Module author: Germain Tegomo

Module description:
    Contains unit tests for the waypoint_core models, validating distance conversion.

Functions:
    TestDistance.test_distance_valid_initialization
    TestDistance.test_distance_rejects_negative_magnitude
    TestDistance.test_distance_rejects_invalid_unit
    TestDistance.test_distance_convert_round_trip
"""

import pytest
from models.distance import Distance

class TestDistanceInitialization:
    """Tests for constructor validation and read-only properties."""

    def test_valid_initialization(self):
        d = Distance(10.5, "km")
        assert d.magnitude == 10.5
        assert d.unit == "km"

    def test_unit_case_insensitivity(self):
        d1 = Distance(5, "KM")
        d2 = Distance(5, "Mi")
        assert d1.unit == "km"
        assert d2.unit == "mi"

    def test_rejects_negative_magnitude(self):
        with pytest.raises(ValueError, match="cannot be negative"):
            Distance(-1.0, "km")

    def test_rejects_invalid_unit(self):
        with pytest.raises(ValueError, match="Invalid unit"):
            Distance(10.0, "meters")

    def test_read_only_accessors(self):
        d = Distance(5.0, "km")
        with pytest.raises(AttributeError):
            d.magnitude = 10.0
        with pytest.raises(AttributeError):
            d.unit = "mi"


class TestDistanceConversion:
    """Tests for unit conversion and round-trip tolerance."""

    def test_convert_same_unit(self):
        d = Distance(10.0, "km")
        converted = d.convert("km")
        assert converted.magnitude == 10.0
        assert converted.unit == "km"

    def test_convert_km_to_mi(self):
        d_km = Distance(10.0, "km")
        d_mi = d_km.convert("mi")
        assert d_mi.unit == "mi"
        assert pytest.approx(d_mi.magnitude, abs=1e-4) == 6.2137

    def test_convert_mi_to_km(self):
        d_mi = Distance(6.213711922, "mi")
        d_km = d_mi.convert("km")
        assert d_km.unit == "km"
        assert pytest.approx(d_km.magnitude, abs=1e-4) == 10.0

    def test_convert_round_trip_tolerance(self):
        original = Distance(12.34, "km")
        round_trip = original.convert("mi").convert("km")
        assert pytest.approx(original.magnitude, abs=1e-5) == round_trip.magnitude
        assert round_trip.unit == "km"

    def test_convert_invalid_target_unit(self):
        d = Distance(5.0, "km")
        with pytest.raises(ValueError, match="Invalid target unit"):
            d.convert("yards")


class TestDistanceArithmetic:
    """Tests for operator overloading: addition, subtraction, and mixed units."""

    def test_addition_same_units(self):
        # AC: Distance(3,"km") + Distance(2,"km") equals Distance(5,"km")
        d1 = Distance(3, "km")
        d2 = Distance(2, "km")
        assert (d1 + d2) == Distance(5, "km")

    def test_addition_mixed_units_converts_to_left_operand(self):
        d_km = Distance(3, "km")
        d_mi = Distance(1, "mi")  # ~1.60934 km
        result = d_km + d_mi

        assert result.unit == "km"
        assert pytest.approx(result.magnitude, abs=1e-4) == 4.6093

    def test_subtraction_same_units(self):
        d1 = Distance(5, "km")
        d2 = Distance(2, "km")
        assert d1 - d2 == Distance(3, "km")

    def test_subtraction_mixed_units(self):
        d_km = Distance(5, "km")
        d_mi = Distance(1, "mi")  # ~1.60934 km
        result = d_km - d_mi
        assert result.unit == "km"
        assert pytest.approx(result.magnitude, abs=1e-4) == 3.3906

    def test_subtraction_negative_result_raises_error(self):
        d1 = Distance(2, "km")
        d2 = Distance(5, "km")
        with pytest.raises(ValueError, match="negative distance"):
            _ = d1 - d2

    def test_arithmetic_invalid_operand(self):
        d = Distance(5, "km")
        with pytest.raises(TypeError):
            _ = d + 10
        with pytest.raises(TypeError):
            _ = d - "5km"


class TestDistanceComparisonsAndSorting:
    """Tests for equality, ordering (<, >), and sorting mixed units."""

    def test_equality_same_units(self):
        assert Distance(5.0, "km") == Distance(5.0, "km")
        assert Distance(5.0, "km") != Distance(4.9, "km")

    def test_equality_mixed_units(self):
        d_km = Distance(1.609344, "km")
        d_mi = Distance(1.0, "mi")
        assert d_km == d_mi

    def test_equality_non_distance_object(self):
        d = Distance(5.0, "km")
        assert d != "5.0 km"
        assert d != 5.0

    def test_less_than_and_greater_than(self):
        d1 = Distance(3, "km")
        d2 = Distance(5, "km")
        assert d1 < d2
        assert d2 > d1

    def test_comparison_mixed_units(self):
        d_km = Distance(2, "km")
        d_mi = Distance(1, "mi")  # ~1.609 km
        assert d_mi < d_km
        assert d_km > d_mi

    def test_sorting_list_of_distances(self):
        # AC: a list of distances sorts with <
        distances = [
            Distance(10, "km"),
            Distance(2, "mi"),   # ~3.218 km
            Distance(1, "km"),
            Distance(0.5, "mi")  # ~0.804 km
        ]
        sorted_distances = sorted(distances)

        expected_order = [
            Distance(0.5, "mi"),
            Distance(1, "km"),
            Distance(2, "mi"),
            Distance(10, "km")
        ]
        assert sorted_distances == expected_order


class TestDistanceRepresentation:
    """Tests for __str__ and __repr__ formatting."""

    def test_str_formatting(self):
        d = Distance(5.25, "km")
        assert str(d) == "5.25 km"

    def test_repr_formatting(self):
        d = Distance(5.25, "km")
        assert repr(d) == "Distance(5.25, 'km')"