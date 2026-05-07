from django.conf import settings
from django.db import models

# Create your models here.
class UserRank(models.Model):
    name = models.CharField(max_length=50)
    max_xp = models.PositiveIntegerField(default=0)
    min_xp = models.PositiveIntegerField(default=0)