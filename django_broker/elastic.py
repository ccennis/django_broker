from elasticsearch import Elasticsearch

def get():
    environment = request.session['environment']
    ES_HOST = {"host": get_host("elastic"), "port": 9200}

    return Elasticsearch(hosts=[ES_HOST], timeout=60, retry_on_timeout=True, maxsize=200)

def get_host(host_type):
    environment = request.session['environment']
    if (environment) == "prod":
         host = "{prod-host-ip}" if host_type == 'elastic' else "internal-api.com"
    elif (environment) == "dev":
        #since we have variable release domains allow them to pass their specific domain
        host = "dev-internal-api.com" if type == 'elastic' else request.session['dev_domain_var']
    elif (environment) == "stage":
        host = "stage-internal-api.com"
    else:
        host = "localhost"

    return host

def get_url():

    var_type = request.session['dev_domain_var']
    environment = request.session['environment']

    referrer = "https://" if environment == 'prod' else "http://"
    return referrer + get_host("api") + "/api/v2/" + var_type