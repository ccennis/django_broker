from __future__ import absolute_import, unicode_literals
from celery.utils.log import get_task_logger
from django_broker.celery import app as app
from .builder import rebuild_single

logger = get_task_logger(__name__)

@app.task(bind=True, name="reindex", max_retries=3)
def rebuild_task(self, env,type,dev_domain,id):
    try:
        rebuild_single(env,type,dev_domain,id)

    except Exception as e:
        self.retry(e=e, countdown=180)