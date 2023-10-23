from typing import Optional

from elasticsearch import Elasticsearch
from hathorlib import TxVersion

from common.configuration import ELASTIC_SEARCH_TIMEOUT, ELASTIC_TX_INDEX
from gateways.clients.elastic_search_client import ElasticSearchClient


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
            "aggs": {
                "total_transactions": {
                    "sum": {
                        "script": {
                            "source": f"doc['version'].value == {TxVersion.REGULAR_TRANSACTION} || doc['version'].value == {TxVersion.TOKEN_CREATION_TRANSACTION} || doc['version'].value == {TxVersion.NANO_CONTRACT} ? 1 : 0"
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
                "highest_height": {"max": {"field": "height"}},
            },
        }

        elastic_search_response = self.elastic_search_client.run(body)
        aggr_result = elastic_search_response["aggregations"]
        # {my_prop: {value: 1.0}} -> {my_prop: 1}
        result = {k: int(kv.get("value")) for (k, kv) in aggr_result.items()}
        return result
