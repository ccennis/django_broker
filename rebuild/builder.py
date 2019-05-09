from elasticsearch import Elasticsearch
import urllib.parse
from urllib.request import Request, urlopen
import urllib.request
import urllib.parse
import json
import logging
logger = logging.getLogger(__name__)

from django_broker import elastic

env_var = "dev"
var_type = ""

def rebuild_single(env, type, dev_domain, id):

    try:
        logger.info('rebuilding id' + id)

        global env_var
        global var_type
        global dev_domain_var

        env_var = env
        var_type = type
        dev_domain_var = dev_domain
        es = elastic.get();

        q = Request(elastic.get_url())
        q.add_header('Authorization', '{auth-key}')
        response = urlopen(q).read().decode('utf8')

        data = json.loads(response)
        if data.get("response") is None:
            res = es.delete(index=var_type, doc_type=type, id=id, ignore=[400, 404])
        else:
            for key, value in data.items():
                res = es.index(index=type, doc_type=type, id=id, body=value)

        logger.info(res['result'])
        return res['result']
    except Exception as e:
        logger.error(e)