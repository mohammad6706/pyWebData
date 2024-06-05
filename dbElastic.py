from elasticsearch import Elasticsearch, ElasticsearchWarning
from configparser import ConfigParser
import warnings


warnings.simplefilter('ignore', ElasticsearchWarning)

file = "config.ini"
config = ConfigParser()
config.read(file)


class dbElastic:
    def __init__(self, dataQuery):
        self.__client = Elasticsearch(config["address_ES"]["host_port"])
        self.__indexName = config["address_ES"]["indexName"]
        self.__dataQuery = dataQuery
        self.__checkindex()

    def insertDB(self):
        self.__client.index(index=self.__indexName, body=self.__dataQuery)
        return True

    def searchDB(self):
        data = self.__client.search(index=self.__indexName, body= self.__querysearch())
        return data['hits']['hits']

    def __checkindex(self):
        if not self.__client.indices.exists(index=self.__indexName):
            self.__client.indices.create(index=self.__indexName)

    def __querysearch(self):
        url = self.__dataQuery['url']
        q ={
            "sort": [
                {
                    "_score": {
                        "order": "desc"
                    }
                }
            ],
            "fields": [
                {
                    "field": "*",
                    "include_unmapped": "true"
                }
            ],
            "_source": False,
            "query": {
                "bool": {
                    "must": [
                        {
                            "bool": {
                                "should": [
                                    {
                                        "match_phrase": {
                                            "url": url
                                        }
                                    }
                                ],
                                "minimum_should_match": 1
                            }
                        }
                    ],
                    "filter": [],
                    "should": [],
                    "must_not": []
                }
            }
        }
        return q