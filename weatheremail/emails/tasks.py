import requests

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
            print('user_id: {}'.format(user_id))

            user = WeatherUser.objects.get(pk=user_id)

            weather_data = self.get_weather(user)
            # TODO - only pass needed data to templates
            msg_plain = render_to_string('weatheremail.txt', {'weather_data': weather_data})
            msg_html = render_to_string('weatheremail.html', {'weather_data': weather_data})

            subject = 'TODO - dynamic'

            # TODO - dynamic subject line
            send_mail(
                subject=subject,
                message=msg_plain,
                from_email=settings.FROM_EMAIL,
                recipient_list=[user.email],
                html_message=msg_html,
            )

            # raise Exception('hahhaha')
        except Exception as exc:
            print('exception!')
            print(exc)
            SendWeatherEmail.retry(exc=exc)

    def get_weather(self, usr):
        """
            TODO - could this be moved to a lib/helper file somewhere?
        """
        url = '{api}{key}/conditions/q/{state}/{city}.json'.format(
            api=settings.WUNDERGROUND['api_url'],
            key=settings.WUNDERGROUND['key'],
            state=usr.location.city.state.abbreviation,
            city=usr.location.city.slug
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

