# trails/models.py
from django.db import models


class Park(models.Model):
    name = models.CharField(max_length=150)
    region = models.CharField(max_length=100, help_text="e.g. Cascade Range, Olympic Peninsula")
    added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.region})"


class Trail(models.Model):
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Moderate', 'Moderate'),
        ('Hard', 'Hard'),
        ('Expert', 'Expert'),
    ]

    # Relation to Park
    park = models.ForeignKey(
        Park,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='trails',
        help_text="Park or wilderness area this trail belongs to"
    )

    name = models.CharField(max_length=150)
    distance_km = models.DecimalField(max_digits=6, decimal_places=3)
    elevation_gain = models.IntegerField(help_text="Elevation gain in meters")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='Moderate')
    is_open = models.BooleanField(default=True)
    added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['distance_km']

    def __str__(self):
        return f"{self.name} ({self.distance_km} km)"

    @property
    def distance(self):
        return self.distance_km

    @property
    def elevation(self):
        return self.elevation_gain
