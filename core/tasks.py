import requests
from celery import shared_task
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task
def keep_backend_alive():
    """
    Vazifa: Render serverini uyg'oq saqlash uchun o'z-o'ziga so'rov yuboradi.
    """
    render_url = "https://loyiha-manzilingiz.onrender.com/health/" # Buni o'zgartirish kerak
    try:
        response = requests.get(render_url, timeout=10)
        logger.info(f"Keep-alive ping sent to {render_url}. Status: {response.status_code}")
    except Exception as e:
        logger.error(f"Keep-alive ping failed: {str(e)}")
