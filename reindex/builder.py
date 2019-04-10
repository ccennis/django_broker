from urllib.request import Request, urlopen
from multiprocessing.dummy import Pool
from elasticsearch import helpers
import time
import json
import requests
from elasticsearch import Elasticsearch
from django_broker import elastic
import logging
logger = logging.getLogger(__name__)

def full_reindex(env,type, dev_domain):

    try:
        global environment
        global var_type
        global dev_domain_var
    
        environment = env
        var_type = type
        dev_domain_var = dev_domain
    
        t1 = time.time()
        drop_index(type + "_rebuild")
        print("creating index...")
        create(type, True)
    
        lastPage = get_total_pages() + 1
        print("total pages:", lastPage)
    
        pages = list(range(1, lastPage))
    
        pool = Pool(10)
        print("indexing...")
        pool.map(hit_api, pages)
        pool.close()
        pool.join()
    
        copy_index(type + '_rebuild', type)
        t2 = time.time()

        logger.info('done! used time: {}'.format(t2 - t1))
    except Exception as e:
        logger.error(e)

def drop_recreate_index(env, type):
  global environment
  global var_type

  environment = env
  var_type = type

  drop_index(type)
  create(type, False)

def drop_index(index_name):
    es = elastic.get()
    if es.indices.exists(index_name):
        print("deleting '%s' index..." % index_name)
        res = es.indices.delete(index=index_name)
        print(" response: '%s'" % res)

def create(type, rebuild):

    index = get_index(type)
    return create_index(type, index, rebuild)


def get_index(type):
    es = elastic.get()
    res = es.get(index="indices", doc_type='doc', id=type + "_index")

    return res['_source']

def create_index(type, index, rebuild):
    if(rebuild == True):
        index_name = type + "_rebuild"
    else:
        index_name = type

    es = elastic.get()
    print("creating '%s' index..." % index_name)
    return es.indices.create(index=index_name, body=index)

def get_total_pages():
    q = Request(elastic.get_url())
    q.add_header('Authorization', '96f661bf-f4bf-11e8-9784-0242c0a83002')
    response = urlopen(q).read().decode('utf8')
    data = json.loads(response)

    for key, value in data.items():
        return value['last_page']

def hit_api(page):
    es = get()
    actions = []
    q = Request(elastic.get_url() + "?page=" + str(page))
    q.add_header('Authorization', 'xxx-xxx-xxx-xxx-xxx-xxx')
    response = urlopen(q).read().decode('utf8')
    data = json.loads(response)
    for key, value in data.items():
        for item in value['data']:
            action = {
                "_index": var_type + "_rebuild",
                "_type": var_type,
                "_id": item['id'],
                "_source": item
            }
            actions.append(action)
    parallel_bulk(es, actions, 200)


def parallel_bulk(client, actions, threads, stats_only=False, **kwargs):

    success, failed = 0, 0

    # list of errors to be collected is not stats_only
    errors = []

    for ok, item in helpers.parallel_bulk(client, actions, thread_count=threads, **kwargs):
        # print ok, item
        # go through request-reponse pairs and detect failures
        if not ok:
            if not stats_only:
                errors.append(item)
            failed += 1
        else:
            success += 1

    return success, failed if stats_only else errors

def copy_index(src, dest):
    try:
        es = elastic.get()
        ES_HOST = "http://" + elastic.get_host("elastic") + ":9200"
        print("renaming " + src + " to " + dest)
        if es.indices.exists(src):
            if es.indices.exists(dest):
                print("deleting '%s' index..." % dest)
                drop_index(dest)
                create(dest, False)
            url = ES_HOST + '/_reindex/'
            payload = {
                "source": {
                    "index": src
                },
                "dest": {
                    "index": dest
                }
            }
    
            headers = {'content-type': 'application/json'}
    
            response = requests.post(url, data=json.dumps(payload), headers=headers)
    except Exception as e:
        logger.error(e)