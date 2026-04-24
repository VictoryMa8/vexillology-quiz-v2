from django.db import models
from django.contrib.auth.models import AbstractUser

class Vexillologist(AbstractUser):
    high_score = models.IntegerField(default=0)
    games_played = models.IntegerField(default=0)

    def __str__(self):
        return self.username

class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    flag_emoji = models.CharField(max_length=10, null=True, blank=True)
    flag_image_url = models.URLField(max_length=500, null=True, blank=True, help_text="Link to Wikimedia image of flag")
    capital = models.CharField(max_length=100, null=True, blank=True)
    population = models.BigIntegerField(null=True, blank=True)
    area_km2 = models.IntegerField(null=True, blank=True, help_text="Area in square kilometers")
    official_language = models.CharField(max_length=100, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    entry_type = models.CharField(max_length=100, default="Country", help_text="e.g. Country, Autonomous Region, Territory")
    fact = models.TextField(null=True, blank=True, help_text="An interesting fact about this place")

    def __str__(self):
        return self.name