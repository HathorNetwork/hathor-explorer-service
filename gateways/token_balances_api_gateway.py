from typing import List, Optional
from elasticsearch import Elasticsearch
from gateways.clients.elastic_search_client import ElasticSearchClient
from common.configuration import ELASTIC_TOKEN_BALANCES_INDEX


class TokenBalancesApiGateway:
    """ Gateway to interact with the Hathor ElasticSearch cluster with the token balances index
    """

    def __init__(
        self,
        elastic_search_client: Optional[Elasticsearch] = None,
    ) -> None:
        self.elastic_search_client = ElasticSearchClient(elastic_index=ELASTIC_TOKEN_BALANCES_INDEX, client=elastic_search_client)

    def get_token_balances(self, search_text: str, sort_by: str, order: str, search_after: List[str]) -> dict:
        """Retrieve all token balances that match user's query
        """
        return self.elastic_search_client.make_query(search_text, sort_by, order, search_after)
