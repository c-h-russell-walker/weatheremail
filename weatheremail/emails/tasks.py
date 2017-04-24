import logging

from decimal import Decimal

from celery.schedules import crontab
from celery.task import PeriodicTask, Task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from weatheremail.base.models import WeatherUser
from weatheremail.libs.wunderground.api import WundergroundAPI, WundergroundAPIException
from weatheremail.libs.wunderground.helpers import sunny, precipitating


class SendWeatherEmail(Task):
    logger = logging.getLogger('weatheremail.emails.tasks.SendWeatherEmail')

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
        self.logger.info('Running EmailUsersPeriodicTask')
        for user_id in WeatherUser.objects.values_list('id', flat=True).iterator():
            SendWeatherEmail.delay(user_id)
