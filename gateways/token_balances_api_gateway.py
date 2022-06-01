from typing import List, Optional
from elasticsearch import Elasticsearch
from gateways.clients.elastic_search_client import ElasticSearchClient
from utils.elastic_search.elastic_search_utils import ElasticSearchUtils
from common.configuration import ELASTIC_RESULTS_PER_PAGE, ELASTIC_SEARCH_TIMEOUT, ELASTIC_INDEX, ELASTIC_TOKEN_BALANCES_INDEX

SORTABLE_FIELDS = {
    'address': 'keyword',
    'token_id': 'keyword',
    'unlocked_balance': 'long',
    'locked_balance': 'long',
    'total': 'long',
}

class TokenBalancesApiGateway:
    """ Gateway to interact with the Hathor ElasticSearch cluster with the token balances index
    """

    def __init__(
        self,
        elastic_search_client: Optional[Elasticsearch] = None,
    ) -> None:
        self.elastic_search_client = ElasticSearchClient(elastic_index=ELASTIC_TOKEN_BALANCES_INDEX, client=elastic_search_client)

    def get_token_information(self, token_id: str) -> dict:
        """Retrieve total number of addresses and transactions for a given token_id
        """

        body = {
            'size': 0,
            'query': {
                'match': {
                    'token_id': token_id
                }
            },
            'aggs': {
                'address_count': {
                    'value_count': {
                        'field': 'address.keyword'
                    }
                },
                'transaction_sum': {
                    'sum': {
                        'field': 'transactions'
                    }
                }
            }
        }

        response = self.elastic_search_client.run(body)

        return {
            'transactions': response['aggregations']['transaction_sum']['value'],
            'addresses': response['aggregations']['address_count']['value']
        }

    def get_token_balances(self, token_id: str, sort_by: str, order: str, search_after: List[str]) -> dict:
        """Retrieve all token balances that match user's query
        """

        elastic_search_utils = ElasticSearchUtils(elastic_index=ELASTIC_TOKEN_BALANCES_INDEX)
        sort_order = ['total', 'unlocked_balance', 'locked_balance', 'address']

        if not sort_by:
            sort_by = sort_order[0]

        if not order:
            order = 'asc'

        primary_sort_key = {}

        sort_by_complement = elastic_search_utils.get_sort_by_complement(sortable_fields=SORTABLE_FIELDS, sort_by=sort_by)
        primary_sort_key[sort_by+sort_by_complement] = order

        sort_order.remove(sort_by)

        tie_break_sort_order = sort_order.pop(0)
        tie_break_sort_key = {}

        sort_by_complement = elastic_search_utils.get_sort_by_complement(sortable_fields=SORTABLE_FIELDS, sort_by=tie_break_sort_order)

        tie_break_sort_key[tie_break_sort_order+sort_by_complement] = 'asc'

        body = {
            'size': int(ELASTIC_RESULTS_PER_PAGE) + 1,  # Last element is to check if there is next page.
            'sort': [
                primary_sort_key,
                tie_break_sort_key
            ],
            'index': ELASTIC_TOKEN_BALANCES_INDEX,
            'request_timeout': int(ELASTIC_SEARCH_TIMEOUT),
            'query': {
                'match': {
                    'token_id': token_id
                }
            }
        }

        return elastic_search_utils.treat_response(self.elastic_search_client.run(body))
