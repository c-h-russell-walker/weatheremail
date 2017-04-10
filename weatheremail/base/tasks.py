import logging

from celery.task import Task

from base.models import HistoricalData, Location
from libs.wunderground.api import WundergroundAPI, WundergroundAPIException


class UpsertHistoricalData(Task):
    logger = logging.getLogger('weatheremail.base.tasks.UpsertHistoricalData')
    """
        Again as mentioned elsewhere we're only dealing with norm high and low
        If and when this app were to be expanded we'd most likely want to store
        more of the data points returned from the API
    """

    def run(self, city_slug, weather_data, *arg, **kwargs):
        """
            @param weather_data: dict currently only containing 'high_temp' & 'low_temp'
        """
        try:
            _, created = HistoricalData.objects.update_or_create(
                location=Location.get_by_city_slug(city_slug=city_slug),
                defaults=weather_data,
            )
            self.logger.info('Task {} a HistoricalData entry.'.format('created' if created else 'updated'))
        except Exception as exc:
            self.logger.error('Unexpected Exception occurred - retrying task', exc_info=True)
            UpsertHistoricalData.retry(exc=exc)


class FetchUpsertHistoricalData(Task):
    """
        I was thinking we could use a chained set of Tasks but that may be overcomplicating it too early
    """
    logger = logging.getLogger('weatheremail.base.tasks.FetchUpsertHistoricalData')

    def run(self, loc_id):
        # This should always get us a Location - if not we can't do much of anything
        location = Location.objects.get(pk=loc_id)
        wapi = WundergroundAPI()
        try:
            city_slug = location.city.slug
            hist_data = wapi.get_hist_data(
                state_abbrev=location.city.state.abbreviation,
                city_slug=city_slug
            )

            weather_data = {
                'high_temp': hist_data.get('high_temp'),
                'low_temp': hist_data.get('low_temp'),
            }

            UpsertHistoricalData.delay(city_slug=city_slug, weather_data=weather_data)
        except WundergroundAPIException as exc:
            self.logger.warning('Got a WundergroundAPIException in Task', exc_info=True)
            FetchUpsertHistoricalData.retry(exc=exc)
        except Exception as exc:
            self.logger.error('Unexpected Exception occurred - retrying task', exc_info=True)
            FetchUpsertHistoricalData.retry(exc=exc)

