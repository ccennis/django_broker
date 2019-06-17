from urllib.request import Request, urlopen
from multiprocessing.dummy import Pool
from elasticsearch import helpers
import time
import json
import requests
from elasticsearch import Elasticsearch
from broker import elastic
import logging
logger = logging.getLogger(__name__)

class ReindexClass():
    def __init__(self, env, type, dev_domain):
        self.environment = env
        self.type = type
        self.dev_domain = dev_domain

    def full_reindex(self):

        try:
            self.drop_index(self.type + "_rebuild")
            self.create(self.type, True)

            lastPage = self.get_total_pages() + 1
            print("total pages:" + str(lastPage))

            pages = list(range(1, lastPage))

            with Pool(8) as p:
                results = p.map(self.hit_api, pages)
                p.close()
                p.join()

            print('done!')
        except Exception as e:
            print(e)

    def drop_recreate_index(self):
      self.drop_index(self.type)
      self.create(self.type, False)

    def drop_index(self, index_name):
        es = elastic.get(self.environment, self.dev_domain)
        if es.indices.exists(index_name):
            print("deleting '%s' index..." % index_name)
            res = es.indices.delete(index=index_name)
            print(" response: '%s'" % res)

    def create(self, index_name, rebuild):
        index = self.get_index(index_name)
        return self.create_index(index, rebuild)


    def get_index(self, type):
        es = elastic.get(self.environment, self.dev_domain)
        res = es.get(index="indices", doc_type='doc', id=type + "_index")

        return res['_source']

    def create_index(self, index, rebuild):
        try:
            if(rebuild == True):
                index_name = self.type + "_rebuild"
            else:
                index_name = self.type

            logger.info("Creating index " + index_name)
            es = elastic.get(self.environment, self.dev_domain)
            print("creating '%s' index..." % index_name)
            return es.indices.create(index=index_name, body=index)
        except Exception as e:
            print(e)

    def get_total_pages(self):
        print("getting pages")
        q = Request(elastic.get_url(self.environment, self.type, self.dev_domain))
        response = urlopen(q).read().decode('utf8')
        data = json.loads(response)

        for key, value in data.items():
            return value['last_page']

    def hit_api(self, page):
        es = elastic.get(self.environment,self.dev_domain)
        actions = []
        q = Request(elastic.get_url(self.environment, self.type, self.dev_domain) + "?page=" + str(page))
        response = urlopen(q).read().decode('utf8')
        data = json.loads(response)
        for key, value in data.items():
            for item in value['data']:
                action = {
                    "_index": self.type + "_rebuild",
                    "_type": self.type,
                    "_id": item['id'],
                    "_source": item
                }
                actions.append(action)
        return self.parallel_bulk(es, actions, 300)


    def parallel_bulk(self, client, actions, threads, stats_only=False, **kwargs):

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

    def copy_index(self):
        try:
            src = self.type + "_rebuild"
            dest = self.type
            es = elastic.get(self.environment, self.dev_domain)
            print("renaming " + src + " to " + dest)
            if es.indices.exists(src):
               	if es.indices.exists(dest):
                    print("deleting index " + dest)
                    self.drop_index(dest)

                self.create(dest, False)
                url = elastic.getReindexHost(self.environment, self.dev_domain)
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
            print(e)