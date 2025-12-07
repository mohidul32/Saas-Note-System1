from celery import shared_task
from .models import NoteHistory
import logging

logger = logging.getLogger(__name__)


@shared_task
def cleanup_old_history():
    """Delete note history entries older than 7 days"""
    try:
        deleted_count = NoteHistory.cleanup_old_history()
        logger.info(f"Cleaned up {deleted_count} old history entries")
        return deleted_count
    except Exception as e:
        logger.error(f"Error cleaning up history: {str(e)}")
        raise