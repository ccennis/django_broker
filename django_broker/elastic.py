from elasticsearch import Elasticsearch
import logging
logger = logging.getLogger(__name__)

def get(environment,dev_domain):
    ES_HOST = {"host": get_host("elastic", environment, dev_domain), "port": 9200}

    return Elasticsearch(hosts=[ES_HOST], timeout=60, retry_on_timeout=True, maxsize=200)

def getReindexHost(environment,dev_domain):
    url = "http://" + get_host("elastic", environment, dev_domain) + ":9200/_reindex/"
    return url

def get_host(host_type, environment, dev_domain):
    if (environment) == "prod":
         host = "{prod-host-ip}" if host_type == 'elastic' else "internal-api.com"
    elif (environment) == "dev":
        host = "dev-internal-api.com" if host_type == 'elastic' else dev_domain
    elif (environment) == "stage":
        host = "stage-internal-api.com"
    else:
        host = "localhost"

    return host

def get_url(environment, var_type, dev_domain):
    referrer = "https://" if environment == 'prod' else "http://"
    return referrer + get_host("api",environment,dev_domain) + "/api/v2/" + var_type + "/"