from typing import Optional

from elasticsearch import Elasticsearch, TransportError, RequestError, AuthorizationException
from hathorlib.base_transaction import TxVersion

from common.configuration import ELASTIC_SEARCH_TIMEOUT, ELASTIC_TX_INDEX
from gateways.clients.elastic_search_client import ElasticSearchClient
from utils.elastic_search.elastic_search_utils import ElasticSearchUtils


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

    def get_best_chain_height(self) -> dict:
        """ Get the best chain height
        """

        body = {
            'index': ELASTIC_TX_INDEX,
            # This query can be transalated to
            # ((TxVersion.REGULAR_BLOCK or TxVersion.MERGE_MINED_BLOCK) and voided == False)
            'query': {
                'bool': {
                    'must': [
                        {
                            'bool': {
                                'should': [
                                    {
                                        'match': {
                                            'version': TxVersion.REGULAR_BLOCK,
                                        }
                                    },
                                    {
                                        'match': {
                                            'version': TxVersion.MERGE_MINED_BLOCK
                                        }
                                    }
                                ]
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
            'size': 1,
            'request_timeout': int(ELASTIC_SEARCH_TIMEOUT),
        }

        elastic_search_utils = ElasticSearchUtils(elastic_index=ELASTIC_TX_INDEX)

        try:
            elastic_search_response = self.elastic_search_client.run(body)
            return elastic_search_utils.treat_response(elastic_search_response)
        except RequestError:
            return {'error': 'Bad request to ElasticSearch', 'status': 400}
        except AuthorizationException:
            return {'error': 'Explorer Service was not authorized to access ElasticSearch', 'status': 403}
        except TransportError:
            return {'error': 'An error ocurred before an HTTP response arrived',  'status': 500}
