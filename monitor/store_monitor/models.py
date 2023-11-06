from django.db import models
from .taxonomies import WeekDayType

# Create your models here.
class Store(models.Model):
    store_id = models.BigIntegerField(
        null=False,
        blank=False,
    )
    status = models.CharField(null=False, blank=False, max_length=10)
    timestamp_utc = models.DateTimeField(auto_now=False, auto_now_add=False)


class BusinessHour(models.Model):
    store_id = models.BigIntegerField(
        null=True,
        blank=True,
    )
    day = models.IntegerField(
        choices=WeekDayType.choices, null=True
    )
    start_time_local = models.TimeField(auto_now=False, auto_now_add=False)
    end_time_local = models.TimeField(auto_now=False, auto_now_add=False)


class StoreTimezone(models.Model):
    store_id = models.BigIntegerField(
        null=True,
        blank=True,
    )
    timezone_str = models.CharField(
        null=False, 
        blank=False,
        default="America/Chicago",
        max_length=100
    )