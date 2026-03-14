import requests
import time
import logging
from django.conf import settings
from rest_framework.exceptions import APIException

logger = logging.getLogger(__name__)

class GeoASRClient:
    BASE_URL = "https://duasr.uz"
    ENDPOINTS = {
        'schools': '/api4/maktab44',
        'kindergartens': '/api4/bogcha',
        'ssv': '/api4/ssv'
    }

    def __init__(self):
        self.token = settings.GEOASR_TOKEN
        self.timeout = 30
        self.max_retries = 3

    def _get_headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json"
        }

    def fetch(self, endpoint_key):
        if endpoint_key not in self.ENDPOINTS:
            raise ValueError(f"Invalid endpoint key: {endpoint_key}")

        url = f"{self.BASE_URL}{self.ENDPOINTS[endpoint_key]}"
        
        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    url, 
                    headers=self._get_headers(),
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                logger.error(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise APIException(f"GeoASR API error: {str(e)}")
                time.sleep(2 ** attempt) # Exponential backoff

        return None
