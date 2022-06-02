from typing import Optional
from elasticsearch import Elasticsearch
from common.configuration import ELASTIC_TX_INDEX
from utils.elastic_search.elastic_search_utils import ElasticSearchUtils
from gateways.clients.elastic_search_client import ElasticSearchClient

BLOCK_TX_VERSION = 0


class BlockApiGateway:
    """ Gateway to interact with ElasticSearch Cluster
        To get information about Blocks
    """

    def __init__(
        self,
        elastic_search_client: Optional[Elasticsearch] = None
    ) -> None:
        self.elastic_search_client = ElasticSearchClient(elastic_index=ELASTIC_TX_INDEX,
                                                         client=elastic_search_client
                                                         )

    def get_block_with_biggest_height(self):
        body = {
            'index': ELASTIC_TX_INDEX,
            'query': {
                'bool': {
                    'must': [
                        {
                            'match': {
                                'version': BLOCK_TX_VERSION,
                            }
                        },
                        {
                            'match': {
                                'voided': False
                            }
                        }
                    ],
                },
            },
            'sort': [
                {
                    'height': {
                        'order': 'desc'
                    }
                }
            ],
            'size': 1
        }

        elastic_search_utils = ElasticSearchUtils(elastic_index=ELASTIC_TX_INDEX)
        return elastic_search_utils.treat_response(self.elastic_search_client.run(body))
