import logging

from celery.task import Task

from base.models import HistoricalData, Location


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