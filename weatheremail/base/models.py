from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


class WeatherUser(User):
    user = models.OneToOneField(User)
    # location = models.OneToOneField(TODOMakeLocationModel)

    class Meta:
        db_table = 'weather_user'
        app_label = 'base'