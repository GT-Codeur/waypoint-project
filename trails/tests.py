from django.test import TestCase, Client
from django.urls import reverse
from .models import Park, Trail


class TrailCatalogViewTests(TestCase):
    """Integration tests for the Trail Catalog view and queries."""

    def setUp(self):
        self.client = Client()
        self.park = Park.objects.create(name="Cascade National Park", region="Pacific Northwest")
        
        self.open_trail = Trail.objects.create(
            name="Skyline Ridge",
            park=self.park,
            distance_km=8.5,
            elevation_gain=450,
            difficulty="Moderate",
            is_open=True
        )
        self.closed_trail = Trail.objects.create(
            name="Glacier Pass",
            park=self.park,
            distance_km=14.0,
            elevation_gain=1100,
            difficulty="Expert",
            is_open=False
        )

    def test_open_trails_query_in_catalog(self):
        """Catalog page should list open trails and exclude or badge closed trails appropriately."""
        response = self.client.get(reverse('catalog'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Skyline Ridge")
        self.assertIn('trails', response.context)
        
        # Verify open trail is present in the queryset
        trail_names = [t.name for t in response.context['trails']]
        self.assertIn("Skyline Ridge", trail_names)

    def test_filter_trails_by_park(self):
        """Filtering by ?park=<id> should filter the returned trails queryset."""
        other_park = Park.objects.create(name="Olympic Park", region="West Coast")
        other_trail = Trail.objects.create(
            name="Coastal Loop",
            park=other_park,
            distance_km=4.0,
            elevation_gain=50,
            difficulty="Easy",
            is_open=True
        )

        response = self.client.get(reverse('catalog'), {'park': self.park.id})
        self.assertEqual(response.status_code, 200)
        trail_names = [t.name for t in response.context['trails']]
        self.assertIn("Skyline Ridge", trail_names)
        self.assertNotIn("Coastal Loop", trail_names)


class TrailDetailViewTests(TestCase):
    """Integration tests for individual trail detail routing and 404 handling."""

    def setUp(self):
        self.client = Client()
        self.park = Park.objects.create(name="Rainier Wilderness", region="Washington")
        self.trail = Trail.objects.create(
            name="Reflection Lakes",
            park=self.park,
            distance_km=6.0,
            elevation_gain=200,
            difficulty="Easy",
            is_open=True
        )

    def test_detail_view_returns_200_for_valid_id(self):
        """Valid trail ID returns HTTP 200 and renders trail detail."""
        url = reverse('trail_detail', kwargs={'pk': self.trail.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Reflection Lakes")
        self.assertContains(response, "Rainier Wilderness")

    def test_detail_view_returns_404_for_invalid_id(self):
        """Non-existent trail ID raises 404 Not Found."""
        url = reverse('trail_detail', kwargs={'pk': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)