from django.db import models
from django.contrib.auth.models import AbstractUser

class Vexillologist(AbstractUser):
    high_score = models.IntegerField(default=0)
    games_played = models.IntegerField(default=0)

    def __str__(self):
        return self.username