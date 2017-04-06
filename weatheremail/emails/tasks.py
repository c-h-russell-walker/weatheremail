import logging

from decimal import Decimal

from celery.schedules import crontab
from celery.task import PeriodicTask, Task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from base.models import WeatherUser
from libs.wunderground.api import WundergroundAPI, WundergroundAPIException
from libs.wunderground.helpers import sunny, precipitating


""" TODO (Architectural notes):
Soooo I realized once porting the http requests to their own client that there's no reason we need
to do them for the same actual location (not user location) more than once - meaning no point in making the
same call for Boston, MA repeatedly
Also we shouldn't have the tasks spun up for each user wait synchronously on those API calls

Another thought is we can get the historical data used for average temperature really at any point - we could
decide on when it would be considered 'stale' for a location re-fetch (thinking about using a postsave signal
for when a user signs up)

So my thoughts are that we could have another periodic task that fires before the current one
This task could make the API calls for each unique location we have in our DB
and save the results to another table maybe

EDGE CASE consideration:
We can have some exception handling flow control in our current per-user-task that would indeed make the
API calls - if for instance a user signs up with a new location we haven't gotten the data for yet

Also,
Obviously if we can batch requests with an API that will help with our amount of calls as well
"""

class SendWeatherEmail(Task):
    logger = logging.getLogger('weatheremail.emails.tasks.SendWeatherEmail')
    """
        TODO - do we want to alter max_retries, default_retry_delay or add name?
    """

    def run(self, user_id, *args, **kwargs):
        try:
            self.logger.debug('Running SendWeatherEmailTask')
            wapi = WundergroundAPI()
            user = WeatherUser.objects.get(pk=user_id)

            state_abbrev = user.location.city.state.abbreviation
            city_slug = user.location.city.slug

            weather_data = wapi.get_weather(state_abbrev=state_abbrev, city_slug=city_slug)

            curr_obsv = weather_data.get('current_observation')
            template_data = {
                'user_name': user.email,
                'location_string': user.location,
                'temp_string': curr_obsv.get('temperature_string'),
                'weather_string': curr_obsv.get('weather'),
                'weather_image': curr_obsv.get('icon_url'),
            }
            msg_plain = render_to_string('weatheremail.txt', template_data)
            msg_html = render_to_string('weatheremail.html', template_data)

            subject = self.get_subject_line(
                forecast_icon=curr_obsv.get('icon'),
                curr_temp=Decimal(curr_obsv.get('temp_f')),
                avg_temp=wapi.get_average_temp(state_abbrev=state_abbrev, city_slug=city_slug)
            )

            # Once concerned with scale we should use an email service not directly tied to Django
            send_mail(
                subject=subject,
                message=msg_plain,
                from_email=settings.FROM_EMAIL,
                recipient_list=[user.email],
                html_message=msg_html,
            )

        except WundergroundAPIException as exc:
            self.logger.warning('Got a WundergroundAPIException in SendWeatherEmail Task', exc_info=True)
            SendWeatherEmail.retry(exc=exc)
        except Exception as exc:
            self.logger.warning('Unexpected Exception in SendWeatherEmail Task', exc_info=True)
            SendWeatherEmail.retry(exc=exc)

    def get_subject_line(self, forecast_icon, curr_temp, avg_temp):
        """
            Uses degrees in F - also using icon with possible values:
            https://serbian.wunderground.com/weather/api/d/docs?d=resources/phrase-glossary&MR=1#forecast_description_phrases
            NOTE: assumptions have been made about the specs. for this project (per curr. weather precip/sunny)
        """
        temp_diff = curr_temp - avg_temp

        if temp_diff >= 5 or sunny(forecast_icon):
            return "It's nice out! Enjoy a discount on us."
        elif temp_diff <= 5 or precipitating(forecast_icon):
            return "Not so nice out? That's okay, enjoy a discount on us."
        else:
            return "Enjoy a discount on us."


class EmailUsersPeriodicTask(PeriodicTask):
    logger = logging.getLogger('weatheremail.emails.tasks.EmailUsersPeriodicTask')
    run_every = crontab(minute=0, hour=10)

    def run(self, *args, **kwargs):
        """
            Using .iterator() is better for memory consumption - from the docs:
            `iterator() will read results directly, without doing any caching at the QuerySet`

            Also using values_list for memory consumption - from the docs:
            `...values_list() ... intended as optimizations for a specific use case: retrieving
            a subset of data without the overhead of creating a model instance`

            # TODO - we should concern ourselves with batching when we get >= million rows
                # We could use a raw query even too??
        """
        self.logger.info('Running EmailUsersPeriodicTask')
        for user_id in WeatherUser.objects.values_list('id', flat=True).iterator():
            SendWeatherEmail.delay(user_id)
