# trails/models.py
from django.db import models


class Trail(models.Model):
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Moderate', 'Moderate'),
        ('Hard', 'Hard'),
        ('Expert', 'Expert'),
    ]

    name = models.CharField(max_length=150)
    distance_km = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        help_text="Trail length in kilometers"
    )
    elevation_gain = models.IntegerField(help_text="Elevation gain in meters")
    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='Moderate'
    )
    is_open = models.BooleanField(default=True)
    added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['distance_km']

    def __str__(self):
        return f"{self.name} ({self.distance_km} km)"

    # Compatibility properties so catalog.html requires zero modifications
    @property
    def distance(self):
        return self.distance_km

    @property
    def elevation(self):
        return self.elevation_gain