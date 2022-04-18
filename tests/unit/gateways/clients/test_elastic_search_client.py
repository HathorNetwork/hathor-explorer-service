from unittest.mock import MagicMock

from pytest import fixture

from gateways.clients.elastic_search_client import ElasticSearchClient


class TestElasticSearchClient:

    @fixture
    def es_client(self):
        return MagicMock()

    def test_search(self, es_client):
        client = ElasticSearchClient(es_client)

        es_client.search = MagicMock(
            return_value={
                'took': 0,
                'timed_out': False,
                '_shards': {
                    'total': 1,
                    'successful': 1,
                    'skipped': 0,
                    'failed': 0
                },
                'hits': {
                    'total': {
                        'value': 1,
                        'relation': 'eq'
                    },
                    'max_score': None,
                    'hits': [
                        {
                            '_index': 'lucas-test-token',
                            '_id': '00000000906db3a2146ec96b452f9ff7431fa273a432d9b14837eb72e17b587a',
                            '_score': None,
                            '_source': {
                                '@timestamp': '2022-04-05T18:19:05.198109Z',
                                'id': '00000000906db3a2146ec96b452f9ff7431fa273a432d9b14837eb72e17b587a',
                                'name': 'AnotherLucasCoinTest',
                                'symbol': 'ALCT',
                                'created_at': '2022-04-05T18:14:51Z',
                                'updated_at': '2022-04-05T18:14:51Z'
                            },
                            'sort': [
                                '00000000906db3a2146ec96b452f9ff7431fa273a432d9b14837eb72e17b587a',
                                'AnotherLucasCoinTest'
                            ]
                        }
                    ]
                }
            }
        )

        result = client.make_query(search_text="", sort_by="", order="", search_after=[])
        expected_result = {
            'hits': [
                {
                    'id': '00000000906db3a2146ec96b452f9ff7431fa273a432d9b14837eb72e17b587a',
                    'name': 'AnotherLucasCoinTest',
                    'symbol': 'ALCT',
                    'sort': [
                        '00000000906db3a2146ec96b452f9ff7431fa273a432d9b14837eb72e17b587a',
                        'AnotherLucasCoinTest'
                    ],
                    'nft': False
                }
            ],
            'has_next': False
        }

        assert result == expected_result
