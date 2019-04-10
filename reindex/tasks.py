from __future__ import absolute_import, unicode_literals
from celery.utils.log import get_task_logger
from django_broker.celery import app as app
from .builder import full_reindex

logger = get_task_logger(__name__)

@app.task(bind=True, name="full_reindex", max_retries=3)
def full_reindex_task(self,env,type, dev_domain):
    try:
        full_reindex(env,type, dev_domain)

    except Exception as e:
        self.retry(e=e, countdown=180)