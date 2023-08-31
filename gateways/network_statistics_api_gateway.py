from typing import Optional

from elasticsearch import Elasticsearch
from hathorlib import TxVersion

from common.configuration import (
    ELASTIC_SEARCH_TIMEOUT,
    ELASTIC_TX_INDEX,
)
from gateways.clients.elastic_search_client import ElasticSearchClient
from utils.elastic_search.elastic_search_utils import ElasticSearchUtils


# REGULAR_BLOCK = 0
# REGULAR_TRANSACTION = 1
# TOKEN_CREATION_TRANSACTION = 2
# MERGE_MINED_BLOCK = 3
# NANO_CONTRACT = 4


class NetworkStatisticsApiGateway:
    def __init__(self, elastic_search_client: Optional[Elasticsearch] = None) -> None:
        self.elastic_search_client = ElasticSearchClient(
            elastic_index=ELASTIC_TX_INDEX, client=elastic_search_client
        )

    def get_transaction_statistics(self) -> dict:
        """Get basic statistics from transaction index."""

        body = {
            "index": ELASTIC_TX_INDEX,
            "size": 0,
            "sort": [{"height": {"order": "desc"}}],
            "request_timeout": int(ELASTIC_SEARCH_TIMEOUT),
            "query": {
                "bool": {
                    "should": [
                        {"term": {"version": TxVersion.REGULAR_TRANSACTION}},
                        {"term": {"version": TxVersion.TOKEN_CREATION_TRANSACTION}}
                    ]
                }
            },
            "aggs": {
                "total_transactions": {
                    "sum": {
                        "script": {
                            "source": f"doc['version'].value == {TxVersion.REGULAR_TRANSACTION} || doc['version'].value == {TxVersion.TOKEN_CREATION_TRANSACTION} ? 1 : 0"
                        }
                    }
                },
                "total_custom_tokens": {
                    "sum": {
                        "script": {
                            "source": f"doc['version'].value == {TxVersion.TOKEN_CREATION_TRANSACTION} ? 1 : 0"
                        }
                    }
                },
                "highest_height": {
                    "max": {
                        "field": "height"
                    }
                }
            }
        }

        elastic_search_utils = ElasticSearchUtils(
            elastic_index=ELASTIC_TX_INDEX)

        elastic_search_response = self.elastic_search_client.run(body)
        return elastic_search_utils.treat_response(elastic_search_response)
