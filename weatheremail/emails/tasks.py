import requests

from decimal import Decimal

from celery.schedules import crontab
from celery.task import PeriodicTask, Task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from base.models import WeatherUser


class SendWeatherEmail(Task):
    """
        TODO - do we want to alter max_retries, default_retry_delay or add name?
    """

    def run(self, user_id, *args, **kwargs):
        try:
            user = WeatherUser.objects.get(pk=user_id)

            weather_data = self.get_weather(user.location.city)

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
                avg_temp=self.get_average_temp(user.location.city)
            )


            send_mail(
                subject=subject,
                message=msg_plain,
                from_email=settings.FROM_EMAIL,
                recipient_list=[user.email],
                html_message=msg_html,
            )

        except Exception as exc:
            # TODO - Add logging
            SendWeatherEmail.retry(exc=exc)

    def get_subject_line(self, forecast_icon, curr_temp, avg_temp):
        """
            Uses degrees in F - also using icon with possible values:
            https://serbian.wunderground.com/weather/api/d/docs?d=resources/phrase-glossary&MR=1#forecast_description_phrases
            NOTE: assumptions have been made about the specs. for this project (per curr. weather precip/sunny)
        """
        sunny_values = [
            'clear',
            'partlysunny',
            'mostlysunny',
            'sunny',
        ]

        precip_values = [
            'flurries',
            'sleet',
            'rain',
            'snow',
            'tstorms',
        ]

        # either sunny or 5 degrees warmer
        temp_diff = curr_temp - avg_temp

        if temp_diff >= 5 or forecast_icon in sunny_values:
            return "It's nice out! Enjoy a discount on us."
        elif temp_diff <= 5 or forecast_icon in precip_values:
            return "Not so nice out? That's okay, enjoy a discount on us."
        else:
            return "Enjoy a discount on us."

    def get_average_temp(self, city):
        """
            TODO - We could DRY this code up and create an API client/wrapper
                main diff is just 'almanac' versus 'conditions'

            I've calculated the average temperature taken from the specs here:
            https://www.klaviyo.com/weather-app
        """
        url = '{api}{key}/almanac/q/{state}/{city}.json'.format(
            api=settings.WUNDERGROUND['api_url'],
            key=settings.WUNDERGROUND['key'],
            state=city.state.abbreviation,
            city=city.slug
        )

        try:
            # TODO - validate the returned status code
            resp = requests.get(url)
            hist_data = resp.json()

            norm_high = Decimal(hist_data.get('almanac').get('temp_high').get('normal').get('F'))
            norm_low = Decimal(hist_data.get('almanac').get('temp_low').get('normal').get('F'))
            return (norm_high + norm_low) / 2
        except Exception:
            # TODO - something here.
            pass


    def get_weather(self, city):
        """
            TODO - could this be moved to a lib/helper file somewhere?
        """
        url = '{api}{key}/conditions/q/{state}/{city}.json'.format(
            api=settings.WUNDERGROUND['api_url'],
            key=settings.WUNDERGROUND['key'],
            state=city.state.abbreviation,
            city=city.slug
        )

        try:
            # TODO - validate the returned status code
            resp = requests.get(url)
            return resp.json()
        except Exception:
            # TODO - something here.
            pass


class TestPeriodicTask(PeriodicTask):
    run_every = crontab(minute=0, hour=10)

    def run(self, *args, **kwargs):
        print('we\'re running periodically')

        for user in WeatherUser.objects.iterator():
            TestTask.delay(user.id)

