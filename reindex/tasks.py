from __future__ import absolute_import, unicode_literals
from celery.utils.log import get_task_logger
from broker.celery import app as app
from .builder import ReindexClass

logger = get_task_logger(__name__)

@app.task(bind=True, name="full_reindex",queue="elastic-reindex", max_retries=3)
def full_reindex_task(self,env,type,dev_domain):
    try:
        reindexer = ReindexClass(env, type, dev_domain)
        reindexer.full_reindex()

    except Exception as e:
        self.retry(e=e, countdown=180)

@app.task(bind=True, name="copy_index", queue="elastic-reindex",max_retries=3)
def copy_index_task(self,env,type,dev_domain):
    try:
        reindexer = ReindexClass(env, type, dev_domain)
        reindexer.copy_index()

    except Exception as e:
        self.retry(e=e, countdown=180)