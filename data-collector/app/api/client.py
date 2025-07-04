import requests
from requests.exceptions import RequestException
import logging

from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_bike_data() -> dict | None:
    """
    Fetches raw bike data from the Nextbike API.

    Returns:
        A dictionary containing the API response JSON, or None if an error occurs.
    """
    try:
        response = requests.get(settings.NEXTBIKE_API_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        logger.error(f"Error fetching data from Nextbike API: {e}")
        return None
