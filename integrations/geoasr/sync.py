import logging
from apps.institutions.models import Institution
from .client import GeoASRClient

logger = logging.getLogger(__name__)

class GeoASRSyncService:
    @staticmethod
    def map_type(endpoint_key):
        mapping = {
            'schools': Institution.SCHOOL,
            'kindergartens': Institution.KINDERGARTEN,
            'ssv': Institution.SSV
        }
        return mapping.get(endpoint_key)

    @staticmethod
    def sync_all():
        client = GeoASRClient()
        stats = {'created': 0, 'updated': 0, 'errors': 0}

        for endpoint_key in ['schools', 'kindergartens', 'ssv']:
            try:
                data = client.fetch(endpoint_key)
                if not data:
                    continue

                for item in data:
                    try:
                        # Assuming 'id' in item is the external unique identifier
                        # And mapping other fields as per requirement
                        institution, created = Institution.objects.update_or_create(
                            external_id=item.get('id'),
                            defaults={
                                'name': item.get('name'),
                                'type': GeoASRSyncService.map_type(endpoint_key),
                                'region': item.get('region'),
                                'district': item.get('district'),
                                'latitude': item.get('lat'),
                                'longitude': item.get('lng'),
                                'address': item.get('address'),
                            }
                        )
                        if created:
                            stats['created'] += 1
                        else:
                            stats['updated'] += 1
                    except Exception as e:
                        logger.error(f"Error syncing item {item.get('id')}: {str(e)}")
                        stats['errors'] += 1

            except Exception as e:
                logger.error(f"Error syncing {endpoint_key}: {str(e)}")
                stats['errors'] += 1

        logger.info(f"Sync completed: {stats}")
        return stats
