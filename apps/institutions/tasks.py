from celery import shared_task
from integrations.geoasr.sync import GeoASRSyncService
import logging

logger = logging.getLogger(__name__)

@shared_task(name="sync_geoasr_data")
def sync_geoasr_data():
    """
    Daily sync with GeoASR API.
    """
    logger.info("Starting GeoASR sync task...")
    try:
        results = GeoASRSyncService.sync_all()
        logger.info(f"GeoASR sync finished: {results}")
        return results
    except Exception as e:
        logger.error(f"GeoASR sync task failed: {str(e)}")
        raise
