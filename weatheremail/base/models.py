from __future__ import unicode_literals

from datetime import timedelta

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True, blank=False, editable=False)
    updated = models.DateTimeField(auto_now=True, blank=False, editable=False)

    class Meta:
        abstract = True


class State(models.Model):
    """
        Using 50 states plus DC, Micronesia, etc.
    """
    abbreviation = models.CharField(primary_key=True, max_length=6)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'state'
        app_label = 'base'


class City(models.Model):
    name = models.CharField(primary_key=True, max_length=100)
    state = models.ForeignKey(State)

    class Meta:
        db_table = 'city'
        app_label = 'base'

    @property
    def slug(self):
        return self.name.replace(' ', '_')


class Location(models.Model):
    """
        This model is for use primarily with the Wunderground weather API
        We'll seed the data for the top 100 cities in the US by population
        Using these two sources for the ranking data:
            https://gist.github.com/Miserlou/c5cd8364bf9b2420bb29
            http://www.baruch.cuny.edu/nycdata/world_cities/largest_cities-usa.htm
    """
    city = models.ForeignKey(City)
    rank = models.IntegerField()

    class Meta:
        db_table = 'location'
        app_label = 'base'

    def __str__(self):
        return '{}, {}'.format(self.city.name, self.city.state.abbreviation)

    @classmethod
    def get_by_city_slug(cls, city_slug):
        city_name = city_slug.replace('_', ' ')
        return cls.objects.get(city=City.objects.get(name=city_name))


class WeatherUser(User):
    user = models.OneToOneField(User)
    location = models.ForeignKey(Location)

    class Meta:
        db_table = 'weather_user'
        app_label = 'base'

    def save(self, *args, **kwargs):
        # Since we're inherting from the Django User we have to have a username
        if not self.username and self.email:
            self.username = self.email
        super(WeatherUser, self).save(*args, **kwargs)


class HistoricalData(BaseModel):
    """
        This may currently be a misnomer since we're only going to store low and high temp to start
    """
    location = models.ForeignKey(Location)
    high_temp = models.DecimalField(max_digits=5, decimal_places=2)
    low_temp = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        db_table = 'historical_data'
        app_label = 'base'

    @property
    def stale(self):
        oldest_date = timezone.now() - timedelta(**settings.STALE_DATA_DELTA)
        return self.updated < oldest_date

