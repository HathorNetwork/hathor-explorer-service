from typing import List

from common.configuration import (
    ELASTIC_INDEX,
    ELASTIC_RESULTS_PER_PAGE,
    ELASTIC_SEARCH_TIMEOUT,
    ELASTIC_TOKEN_BALANCES_INDEX,
    ELASTIC_TX_INDEX
)
from utils.elastic_search.transformations.token_api import es_hit_to_result as token_api_es_hit_to_result
from utils.elastic_search.transformations.token_balances import es_hit_to_result as token_balances_es_hit_to_result
from utils.elastic_search.transformations.tx import es_hit_to_result as tx_es_hit_to_result

# Each possible sortable field and its primary type for each elastic search index
SORTABLE_FIELDS_BY_INDEX = {
    ELASTIC_INDEX: {
        'transaction_timestamp': 'long',
        'uid': 'keyword',
        'id': 'keyword',
        'name': 'keyword',
        'symbol': 'keyword',
    },
    ELASTIC_TOKEN_BALANCES_INDEX: {
        'address': 'keyword',
        'token_id': 'keyword',
        'unlocked_balance': 'long',
        'locked_balance': 'long',
        'total': 'long',
    }
}

SEARCH_TEXT_FIELDS_BY_INDEX = {
    ELASTIC_INDEX: ['id', 'name', 'symbol'],
    ELASTIC_TOKEN_BALANCES_INDEX: ['token_id']
}

DEFAULT_SORT_ORDER_BY_INDEX = {
    ELASTIC_INDEX: ['transaction_timestamp', 'id', 'name', 'symbol'],
    ELASTIC_TOKEN_BALANCES_INDEX: ['unlocked_balance', 'locked_balance', 'total', 'address'],
}

RESPONSE_TRANSFORMATION_BY_INDEX = {
    ELASTIC_INDEX: token_api_es_hit_to_result,
    ELASTIC_TOKEN_BALANCES_INDEX: token_balances_es_hit_to_result,
    ELASTIC_TX_INDEX: tx_es_hit_to_result,
}


class ElasticSearchUtils:

    def __init__(self, elastic_index: str):
        self.elastic_index = elastic_index

    def get_sort_by_complement(self, sortable_fields: dict, sort_by: str) -> str:
        """ Returns the complement (if any) on sort_by field that is passed to ES

        :param sort_by: Which field is currently being used for primary sorting
        :type sort_by: str
        """

        # For sorting purposes, only .keyword must be added as complement
        # Other types (such as long) do not need complement
        return '.keyword' if sortable_fields[sort_by] == 'keyword' else ''

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
        sort_order = DEFAULT_SORT_ORDER_BY_INDEX[self.elastic_index].copy()

        if not sort_by:
            sort_by = sort_order[0]

        if not order:
            order = 'asc'

        primary_sort_key = {}

        sort_by_complement = self.get_sort_by_complement(sortable_fields=SORTABLE_FIELDS_BY_INDEX[self.elastic_index],
                                                         sort_by=sort_by)
        primary_sort_key[sort_by+sort_by_complement] = order

        sort_order.remove(sort_by)

        tie_break_sort_order = sort_order.pop(0)
        tie_break_sort_key = {}

        sort_by_complement = self.get_sort_by_complement(sortable_fields=SORTABLE_FIELDS_BY_INDEX[self.elastic_index],
                                                         sort_by=tie_break_sort_order)
        tie_break_sort_key[tie_break_sort_order+sort_by_complement] = 'asc'

        body = {
            'size': int(ELASTIC_RESULTS_PER_PAGE) + 1,  # Last element is to check if there is next page.
            'sort': [
                primary_sort_key,
                tie_break_sort_key
            ],
            'index': self.elastic_index,
            'request_timeout': int(ELASTIC_SEARCH_TIMEOUT),
        }

        if search_text:
            fields = SEARCH_TEXT_FIELDS_BY_INDEX[self.elastic_index]
            body['query'] = {
                'multi_match': {
                    'query': search_text,
                    'fields': fields
                }
            }

        if search_after:
            body['search_after'] = search_after

        return body

    def treat_response(self, es_search_result: dict) -> dict:
        """Get the response from ElasticSearch and transform it into what API client expects.

        :param es_search_result: Raw response from ElasticSearch
        :type es_search_result: dict
        """

        response = {
            'hits': [],
            'has_next': False
        }

        transformation = RESPONSE_TRANSFORMATION_BY_INDEX[self.elastic_index]
        hits = list(map(transformation, es_search_result['hits']['hits']))
        if len(hits) == (int(ELASTIC_RESULTS_PER_PAGE) + 1):
            response['has_next'] = True
            del hits[-1]

        response['hits'] = hits

        return response
