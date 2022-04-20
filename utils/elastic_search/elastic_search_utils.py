from typing import List

from common.configuration import ELASTIC_INDEX, ELASTIC_RESULTS_PER_PAGE, ELASTIC_SEARCH_TIMEOUT


class ElasticSearchUtils:
    def build_search_query(self, search_text: str, sort_by: str, order: str, search_after: List[str]) -> dict:
        """Build the search query that will be sent to ElasticSearch given the parameters provided by API Client.
        Access this link for more details on how ES search API works:
        https://github.com/elastic/elasticsearch-py/blob/main/elasticsearch/_sync/client/__init__.py#L3335

        :param search_text: Input text requested by user
        :type search_text: str

        :param sort_by: How the data will be sorted (By ID, name, or symbol)
        :type sort_by: str

        :param order: If the order of the sorted data will be asc/desc
        :type order: str

        :param search_after: A list with two entries with information of the next page
        :type search_after: List[str]
        """

        # Default sort order, if nothing is passed
        sort_order = ['transaction_timestamp', 'id', 'name', 'symbol']

        if not sort_by or sort_by == 'uid':
            sort_by = 'id'

        sort_fields_data_type = {
            'transaction_timestamp': 'long',
            'id': 'keyword',
            'name': 'keyword',
            'symbol': 'keyword'
        }

        if not order:
            order = 'asc'

        primary_sort_key = {}

        sort_by_complement = '.keyword' if sort_fields_data_type[sort_by] == 'keyword' else ''
        primary_sort_key[sort_by+sort_by_complement] = order

        sort_order.remove(sort_by)

        tie_break_sort_order = sort_order.pop(0)
        tie_break_sort_key = {}

        sort_by_complement = '.keyword' if sort_fields_data_type[tie_break_sort_order] == 'keyword' else ''
        tie_break_sort_key[tie_break_sort_order+sort_by_complement] = 'asc'

        body = {
            'size': int(ELASTIC_RESULTS_PER_PAGE) + 1,  # Last element is to check if there is next page.
            'sort': [
                primary_sort_key,
                tie_break_sort_key
            ],
            'index': ELASTIC_INDEX,
            'request_timeout': int(ELASTIC_SEARCH_TIMEOUT)
        }

        if search_text:
            body['query'] = {
                'multi_match': {
                    'query': search_text,
                    'fields': ['id', 'name', 'symbol']
                }
            }

        if search_after:
            body['search_after'] = search_after

        return body

    def _get_source_from_hit(self, hit: dict) -> dict:
        """Gets a unique hit from ElasticSearch and map it to what API client expects.

        :param hit: Raw ElasticSearch hit
        :type hit: dict
        """
        result = {
            'id': hit['_source']['id'],
            'name': hit['_source']['name'],
            'symbol': hit['_source']['symbol'],
            'transaction_timestamp': hit['_source']['transaction_timestamp'],
            'sort': hit['sort']
        }

        if 'nft' in hit['_source']:
            result['nft'] = hit['_source']['nft']
        else:
            result['nft'] = False

        return result

    def treat_response(self, es_search_result: dict) -> dict:
        """Get the response from ElasticSearch and transform it into what API client expects.

        :param es_search_result: Raw response from ElasticSearch
        :type es_search_result: dict
        """

        response = {
            'hits': [],
            'has_next': False
        }

        hits = list(map(self._get_source_from_hit, es_search_result['hits']['hits']))
        if len(hits) == (int(ELASTIC_RESULTS_PER_PAGE) + 1):
            response['has_next'] = True
            del hits[-1]

        response['hits'] = hits

        return response
