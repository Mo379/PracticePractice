import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "PP2.settings")
app = Celery("django_celery")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
