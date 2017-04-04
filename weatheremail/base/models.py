from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


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
        # Slug will be used for Wunderground weather API
        raise NotImplementedError


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

