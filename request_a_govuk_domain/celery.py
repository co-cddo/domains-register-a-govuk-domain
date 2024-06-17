import os

from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "request_a_govuk_domain.settings")

app = Celery("request_a_govuk_domain")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "email-fail-checker": {
        "task": "request_a_govuk_domain.request.tasks.email_fail_check_task",
        "schedule": crontab(minute="*/1"),
    },
}
