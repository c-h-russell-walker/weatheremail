import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from base.models import WeatherUser, HistoricalData
from base.tasks import FetchUpsertHistoricalData



logger = logging.getLogger('weatheremail.base.signals')

@receiver(post_save, sender=WeatherUser, dispatch_uid='weather_user_post_save_loc_hist_upsert')
def post_save_loc_hist_upsert(sender, instance, created, **kwargs):
    try:
        # If WeatherUser created it's worth checking that we have the historical data
        # (also, arguably we could check for stale data any time there's a WeatherUser save)
        if created:
            try:
                hist_data = HistoricalData.objects.get(location=instance.location)
                if hist_data.stale:
                    FetchUpsertHistoricalData.delay(loc_id=location.id)
            except HistoricalData.DoesNotExist:
                FetchUpsertHistoricalData.delay(loc_id=location.id)
