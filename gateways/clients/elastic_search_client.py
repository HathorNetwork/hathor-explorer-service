from typing import List, Optional

from elasticsearch import Elasticsearch

from common.configuration import ELASTIC_CLOUD_ID, ELASTIC_INDEX, ELASTIC_PASSWORD, ELASTIC_RESULTS_PER_PAGE


class ElasticSearchClient:
    def __init__(self) -> None:
        self.client = Elasticsearch(
            cloud_id=ELASTIC_CLOUD_ID,
            basic_auth=("elastic", ELASTIC_PASSWORD)
        )

    def _build_search_query(self, search_text: str, sort_by: str, order: str, search_after: List[str]) -> dict:
        # Default sort order, if nothing is passed
        sort_order = ['id', 'name']

        if not sort_by or sort_by == 'uid':
            sort_by = 'id'

        if not order:
            order = 'asc'

        primary_sort_key = {}
        primary_sort_key[sort_by+".keyword"] = order
        sort_order.remove(sort_by)

        tie_break_sort_key = {}
        tie_break_sort_key[sort_order.pop()+".keyword"] = "asc"

        body = {
            "size": int(ELASTIC_RESULTS_PER_PAGE) + 1,  # Last element is to check if there is next page.
            "sort": [
                primary_sort_key,
                tie_break_sort_key
            ]
        }

        if search_text:
            body['query'] = {
                "multi_match": {
                    "query": search_text,
                    "fields": ["id", "name", "symbol"]
                }
            }

        if search_after:
            body['search_after'] = search_after

        return body

    def make_query(self, search_text: str, sort_by: str, order: str, search_after: List[str]) -> Optional[dict]:
        result = self.client.search(
            index=ELASTIC_INDEX,
            body=self._build_search_query(search_text, sort_by, order, search_after)
        )

        return dict(result)

    def _get_source_from_hit(self, hit: dict) -> dict:
        result = {
            "id": hit["_source"]["id"],
            "name": hit["_source"]["name"],
            "symbol": hit["_source"]["symbol"],
            "sort": hit["sort"]
        }

        if 'nft' in hit["_source"]:
            result['nft'] = hit["_source"]["nft"]
        else:
            result['nft'] = False

        return result

    def treat_response(self, es_search_result: dict) -> dict:
        response = {
            "hits": [],
            "has_next": False
        }

        hits = list(map(self._get_source_from_hit, es_search_result['hits']['hits']))
        if len(hits) == (int(ELASTIC_RESULTS_PER_PAGE) + 1):
            response['has_next'] = True

        response["hits"] = hits

        return response
