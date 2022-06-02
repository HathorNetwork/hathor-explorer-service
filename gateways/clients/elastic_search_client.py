from typing import List, Optional

from elasticsearch import Elasticsearch

from common.configuration import ELASTIC_CLOUD_ID, ELASTIC_PASSWORD, ELASTIC_USER
from utils.elastic_search.elastic_search_utils import ElasticSearchUtils


class ElasticSearchClient:
    def __init__(self, elastic_index: str, client: Optional[Elasticsearch]) -> None:
        """Client to make async requests to ElasticSearch, using Cloud ID and Elastic Password
        """

        if client:
            self.client = client
        else:
            self.client = Elasticsearch(
                cloud_id=ELASTIC_CLOUD_ID,
                basic_auth=(ELASTIC_USER, ELASTIC_PASSWORD)
            )

        self.utils = ElasticSearchUtils(elastic_index=elastic_index)

    def run(self, payload: dict) -> dict:
        return dict(self.client.search(**payload))

    def make_query(self, search_text: str, sort_by: str, order: str, search_after: List[str]) -> dict:
        """Use ES client to call the cluster and get the information. Also, it calls auxiliary methods to treat data.

        :param search_text: Input text requested by user
        :type search_text: str

        :param sort_by: How the data will be sorted (By ID, name, or symbol)
        :type sort_by: str

        :param order: If the order of the sorted data will be asc/desc
        :type order: str

        :param search_after: A list with two entries with information of the next page
        :type search_after: List[str]
        """
        payload = self.utils.build_search_query(search_text, sort_by, order, search_after)
        result = self.client.search(**payload)

        return self.utils.treat_response(dict(result))
