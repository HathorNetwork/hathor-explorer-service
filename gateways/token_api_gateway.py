from typing import List, Optional

from elasticsearch import Elasticsearch

from common.configuration import ELASTIC_INDEX
from gateways.clients.elastic_search_client import ElasticSearchClient


class TokenApiGateway:
    """ Gateway to interact with the Hathor ElasticSearch cluster
    """

    def __init__(
        self,
        elastic_search_client: Optional[Elasticsearch] = None,
    ) -> None:
        self.elastic_search_client = ElasticSearchClient(elastic_index=ELASTIC_INDEX,
                                                         client=elastic_search_client
                                                         )

    def get_tokens(self, search_text: str, sort_by: str, order: str, search_after: List[str]) -> dict:
        """Retrieve all tokens that match user's query
        """
        return self.elastic_search_client.make_query(search_text, sort_by, order, search_after)
