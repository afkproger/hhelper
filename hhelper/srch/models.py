from django.db import models


class Indicators(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class StaffMembers(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    login = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=128)
    indicators = models.ManyToManyField(Indicators, blank=True)

    def __str__(self):
        return self.full_name
