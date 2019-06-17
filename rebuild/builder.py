from elasticsearch import Elasticsearch
import urllib.parse
from urllib.request import Request, urlopen
import urllib.request
import urllib.parse
import json
import logging
logger = logging.getLogger(__name__)

from broker import elastic


def rebuild_single(env, type, dev_domain, id):

    try:
        logger.info('rebuilding id ' + id)

        es = elastic.get(env, dev_domain);

        q = Request(elastic.get_url(env, type, dev_domain) + id + '?elastic=true')
        response = urlopen(q).read().decode('utf8')

        data = json.loads(response)
        if data.get("response") is None:
            res = es.delete(index=type, doc_type=type, id=id, ignore=[400, 404])
        else:
            for key, value in data.items():
                res = es.index(index=type, doc_type=type, id=id, body=value)

        return res['result']
    except Exception as e:
        logger.error(e)