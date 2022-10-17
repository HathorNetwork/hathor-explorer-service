from typing import List, Optional

from elasticsearch import Elasticsearch

from common.configuration import (
    ELASTIC_RESULTS_PER_PAGE,
    ELASTIC_SEARCH_TIMEOUT,
    ELASTIC_TOKEN_BALANCES_INDEX,
)
from gateways.clients.elastic_search_client import ElasticSearchClient
from utils.elastic_search.elastic_search_utils import ElasticSearchUtils

SORTABLE_FIELDS = {
    "address": "keyword",
    "token_id": "keyword",
    "unlocked_balance": "long",
    "locked_balance": "long",
    "total": "long",
}


class TokenBalancesApiGateway:
    """Gateway to interact with the Hathor ElasticSearch cluster with the token balances index"""

    def __init__(
        self,
        elastic_search_client: Optional[Elasticsearch] = None,
    ) -> None:
        self.elastic_search_client = ElasticSearchClient(
            elastic_index=ELASTIC_TOKEN_BALANCES_INDEX, client=elastic_search_client
        )

    def _build_filtered_query(self, token_id: str) -> dict:
        return {
            "bool": {
                "must": [
                    {"match": {"token_id": token_id}},
                    {"range": {"total": {"gt": 0}}},
                ]
            }
        }

    def get_token_information(self, token_id: str) -> dict:
        """Retrieve total number of addresses and transactions for a given token_id"""
        body = {
            "size": 0,
            "query": self._build_filtered_query(token_id),
            "index": ELASTIC_TOKEN_BALANCES_INDEX,
            "request_timeout": int(ELASTIC_SEARCH_TIMEOUT),
            "aggs": {
                "address_count": {"value_count": {"field": "address.keyword"}},
            },
        }

        response = self.elastic_search_client.run(body)

        return {"addresses": response["aggregations"]["address_count"]["value"]}

    def get_token_balances(
        self, token_id: str, sort_by: str, order: str, search_after: List[str]
    ) -> dict:
        """Retrieve all token balances that match user's query"""

        elastic_search_utils = ElasticSearchUtils(
            elastic_index=ELASTIC_TOKEN_BALANCES_INDEX
        )

        if not sort_by:
            sort_by = "total"

        if not order:
            order = "asc"

        primary_sort_key = {}

        sort_by_complement = elastic_search_utils.get_sort_by_complement(
            sortable_fields=SORTABLE_FIELDS, sort_by=sort_by
        )
        primary_sort_key[sort_by + sort_by_complement] = order

        # In this case, since we are not displaying any unique values, we should always use the unique_id
        # as a tie breaker
        tie_break_sort_key = {"unique_id.keyword": "desc"}

        body = {
            "size": int(ELASTIC_RESULTS_PER_PAGE)
            + 1,  # Last element is to check if there is next page.
            "sort": [primary_sort_key, tie_break_sort_key],
            "index": ELASTIC_TOKEN_BALANCES_INDEX,
            "request_timeout": int(ELASTIC_SEARCH_TIMEOUT),
            "query": self._build_filtered_query(token_id),
        }

        if search_after:
            body["search_after"] = search_after

        return elastic_search_utils.treat_response(self.elastic_search_client.run(body))
