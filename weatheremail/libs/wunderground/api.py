import requests

from decimal import Decimal

from django.conf import settings


class WundergroundAPIException(Exception):
    pass


class WundergroundAPI(object):

    def __init__(self):
        self.base_url = '{api}{key}/'.format(
            api=settings.WUNDERGROUND['api_url'],
            key=settings.WUNDERGROUND['key'],
        )

    def get_average_temp(self, state_abbrev, city_slug):
        """
            I've calculated the average temperature taken from the specs here:
            https://www.klaviyo.com/weather-app
        """
        url = '{base_url}/almanac/q/{state}/{city}.json'.format(
            base_url=self.base_url,
            state=state_abbrev,
            city=city_slug
        )

        try:
            # TODO - validate the returned status code - use above exceptions
            resp = requests.get(url)
            hist_data = resp.json()

            norm_high = Decimal(hist_data.get('almanac').get('temp_high').get('normal').get('F'))
            norm_low = Decimal(hist_data.get('almanac').get('temp_low').get('normal').get('F'))
            return (norm_high + norm_low) / 2
        except Exception:
            # TODO - something here.
            pass


    def get_weather(self, state_abbrev, city_slug):
        url = '{base_url}/conditions/q/{state}/{city}.json'.format(
            base_url=self.base_url,
            state=state_abbrev,
            city=city_slug
        )

        try:
            # TODO - validate the returned status code
            resp = requests.get(url)
            return resp.json()
        except Exception:
            # TODO - something here.
            pass