from django.db import models


class UserRank(models.Model):
    name = models.CharField(max_length=50)
    max_xp = models.PositiveIntegerField(default=0)
    min_xp = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return self.name
