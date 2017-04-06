import logging
import requests

from decimal import Decimal

from django.conf import settings


class WundergroundAPIException(Exception):
    pass


class WundergroundAPI(object):
    logger = logging.getLogger('weatheremail.libs.wunderground.WundergroundAPI')

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
            self.logger.debug('About to make wunderground request: {}'.format(url))
            resp = requests.get(url)
            if resp.status_code != requests.codes.ok:
                raise WundergroundAPIException(resp.status_code)

            hist_data = resp.json()

            norm_high = Decimal(hist_data.get('almanac').get('temp_high').get('normal').get('F'))
            norm_low = Decimal(hist_data.get('almanac').get('temp_low').get('normal').get('F'))
            return (norm_high + norm_low) / 2
        except Exception:
            # Would be cool to use 'Exception Chaining' here - https://www.python.org/dev/peps/pep-3134/
            self.logger.warning('Unexpected wunderground exception - get_average_temp()', exc_info=True)
            raise WundergroundAPIException(str(exc))


    def get_weather(self, state_abbrev, city_slug):
        url = '{base_url}/conditions/q/{state}/{city}.json'.format(
            base_url=self.base_url,
            state=state_abbrev,
            city=city_slug
        )

        try:
            self.logger.debug('About to make wunderground request: {}'.format(url))
            resp = requests.get(url)
            if resp.status_code != requests.codes.ok:
                raise WundergroundAPIException(resp.status_code)
            return resp.json()
        except Exception as exc:
            # Would be cool to use 'Exception Chaining' here - https://www.python.org/dev/peps/pep-3134/
            self.logger.warning('Unexpected wunderground exception - get_weather()', exc_info=True)
            raise WundergroundAPIException(str(exc))
