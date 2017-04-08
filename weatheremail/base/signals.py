import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from base.models import WeatherUser, HistoricalData


logger = logging.getLogger('weatheremail.base.signals')

@receiver(post_save, sender=WeatherUser, dispatch_uid='weather_user_post_save_loc_hist_upsert')
def post_save_loc_hist_upsert(sender, instance, created, **kwargs):
    try:
        # If WeatherUser created it's worth checking that we have the historical data
        # (also, arguably we could check for stale data any time there's a WeatherUser save)
        if created:
            try:
                city = instance.location.city
                hist_data = HistoricalData.objects.get(city=city)
                if hist_data.stale:
                    print('we should re-fetch the data using API - maybe that\'s a task?')
                    # TODO - actually fire task that updates stale data
            except HistoricalData.DoesNotExist:
                logger.info('We don\'t yet have HistoricalData for {}'.format(city))
                print('Actually do the work of creating one here')
                # TODO - actually create entry
