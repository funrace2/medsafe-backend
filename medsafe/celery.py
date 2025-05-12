# medsafe/celery.py

import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medsafe.settings')
app = Celery('medsafe')
# settings.py 의 CELERY_BROKER_URL, CELERY_RESULT_BACKEND 읽어옴
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()