import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Periodic tasks
app.conf.beat_schedule = {
    'cleanup-old-history': {
        'task': 'apps.notes.tasks.cleanup_old_history',
        'schedule': crontab(hour=2, minute=0),  # Run daily at 2 AM
    },
}