from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

include='reindex.tasks'
include='elastic.tasks'

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'broker.settings')

app = Celery('broker')
app.config_from_object('django.conf:settings')

app.autodiscover_tasks()

app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'
app.conf.accept_content = ['json']

app.conf.task_create_missing_queues = True
app.conf.worker_prefetch_multiplier = 1