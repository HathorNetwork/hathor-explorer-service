from unittest.mock import MagicMock

from pytest import fixture

from gateways.block_api_gateway import BlockApiGateway

ELASTIC_SEARCH_BIGGEST_HEIGHT_SUCCESSFUL_RAW_RESPONSE = {
    'took': 3,
    'timed_out': False,
    '_shards': {
        'total': 1,
        'successful': 1,
        'skipped': 0,
        'failed': 0
    },
    'hits': {
        'total': {
            'value': 8178,
            'relation':
            'eq'
        },
        'max_score': None,
        'hits': [
            {
                '_index': 'lucas-mainnet-tx',
                '_id': '00a1786694f2b2248c4272e64f9f414759322b4e6d5e40d39cc5b5aedfd70dfb',
                '_score': None,
                '_source': {
                    'tx_id': '00a1786694f2b2248c4272e64f9f414759322b4e6d5e40d39cc5b5aedfd70dfb',
                    'voided': False,
                    'timestamp': '2022-05-09T18:55:47Z',
                    '@timestamp': '2022-06-01T02:56:20.402864Z',
                    'weight': 60.66999816894531,
                    'hash_rate': 123,
                    'updated_at': '2022-06-01T02:36:14Z',
                    'height': 1740645,
                    'created_at': '2022-06-01T02:31:49Z',
                    'version': 0
                },
                'sort': [1740645]
            }
        ]
    }
}

GATEWAY_BIGGEST_HEIGHT_SUCCESSFUL_RESPONSE = {
    'hits':
    [
        {
            'tx_id': '00a1786694f2b2248c4272e64f9f414759322b4e6d5e40d39cc5b5aedfd70dfb',
            'timestamp': '2022-05-09T18:55:47Z',
            'version': 0,
            'voided': False,
            'height': 1740645,
            'weight': 60.66999816894531,
            'hash_rate': 123,
        }
    ],
    'has_next': False
}


class TestBlockApiGateway:
    @fixture
    def elastic_search_client(self):
        return MagicMock()

    def test_get_block_with_biggest_height(self, elastic_search_client):
        """ Test if ElasticSearch client is being called
            and if the response is being treated before returning the data
        """
        elastic_search_client.search = MagicMock(
            return_value=ELASTIC_SEARCH_BIGGEST_HEIGHT_SUCCESSFUL_RAW_RESPONSE
        )

        gateway = BlockApiGateway(elastic_search_client=elastic_search_client)
        result = gateway.get_block_with_biggest_height()

        elastic_search_client.search.assert_called_once()
        assert result == GATEWAY_BIGGEST_HEIGHT_SUCCESSFUL_RESPONSE
