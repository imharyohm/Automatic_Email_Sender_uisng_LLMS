# celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Automatic_Email_Sender.settings')

app = Celery('Automatic_Email_Sender')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related config keys should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check-scheduled-emails': {
        'task': 'mainapp.tasks.check_scheduled_emails',
        'schedule': crontab(minute='*/1'),  # Run every minute
    },
}
