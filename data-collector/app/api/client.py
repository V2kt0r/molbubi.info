import logging

import requests
from requests.exceptions import RequestException

from app.core.config import settings

logger = logging.getLogger(__name__)

class ApiClient:
    def __init__(self, api_url: str = settings.NEXTBIKE_API_URL, timeout: int = 10):
        self.api_url = api_url
        self.timeout = timeout

    def fetch_bike_data(self) -> dict | None:
        try:
            response = requests.get(self.api_url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            logger.error(f"Error fetching data from Nextbike API: {e}")
            return None
