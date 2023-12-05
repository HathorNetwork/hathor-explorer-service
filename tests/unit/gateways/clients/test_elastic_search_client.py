from unittest.mock import MagicMock

from pytest import fixture

from common.configuration import ELASTIC_INDEX
from gateways.clients.elastic_search_client import ElasticSearchClient


class TestElasticSearchClient:
    @fixture
    def es_client(self):
        return MagicMock()

    def test_search(self, es_client):
        client = ElasticSearchClient(elastic_index=ELASTIC_INDEX, client=es_client)

        es_client.search = MagicMock(
            return_value={
                "took": 0,
                "timed_out": False,
                "_shards": {"total": 1, "successful": 1, "skipped": 0, "failed": 0},
                "hits": {
                    "total": {"value": 2, "relation": "eq"},
                    "max_score": None,
                    "hits": [
                        {
                            "_index": "dev-token",
                            "_id": "00000000906db3a2146ec96b452f9ff7431fa273a432d9b14837eb72e17b587a",
                            "_score": None,
                            "_source": {
                                "updated_at": "2022-04-19T13:55:30Z",
                                "symbol": "TST1",
                                "@timestamp": "2022-04-19T13:56:04.371602Z",
                                "name": "Test1",
                                "created_at": "2022-04-19T12:41:04Z",
                                "transaction_timestamp": 1649473276,
                                "transactions": 0,
                                "id": "00000000906db3a2146ec96b452f9ff7431fa273a432d9b14837eb72e17b587a",
                            },
                            "sort": [
                                "00000000906db3a2146ec96b452f9ff7431fa273a432d9b14837eb72e17b587a",
                                1649473276,
                            ],
                        },
                        {
                            "_index": "dev-token",
                            "_id": "10000000906db3a2146ec96b452f9ff7431fa273a432d9b14837eb72e17b587a",
                            "_score": None,
                            "_source": {
                                "updated_at": "2022-04-19T13:55:30Z",
                                "symbol": "TST2",
                                "@timestamp": "2022-04-19T13:56:04.372449Z",
                                "name": "Test2",
                                "created_at": "2022-04-19T12:41:07Z",
                                "transaction_timestamp": 1000000000,
                                "transactions": 0,
                                "id": "10000000906db3a2146ec96b452f9ff7431fa273a432d9b14837eb72e17b587a",
                            },
                            "sort": [
                                "10000000906db3a2146ec96b452f9ff7431fa273a432d9b14837eb72e17b587a",
                                1000000000,
                            ],
                        },
                    ],
                },
            }
        )

        result = client.make_query(
            search_text="", sort_by="", order="", search_after=[]
        )
        expected_result = {
            "hits": [
                {
                    "id": "00000000906db3a2146ec96b452f9ff7431fa273a432d9b14837eb72e17b587a",
                    "name": "Test1",
                    "symbol": "TST1",
                    "transaction_timestamp": 1649473276,
                    "transactions_count": 0,
                    "sort": [
                        "00000000906db3a2146ec96b452f9ff7431fa273a432d9b14837eb72e17b587a",
                        1649473276,
                    ],
                    "nft": False,
                },
                {
                    "id": "10000000906db3a2146ec96b452f9ff7431fa273a432d9b14837eb72e17b587a",
                    "name": "Test2",
                    "symbol": "TST2",
                    "transaction_timestamp": 1000000000,
                    "transactions_count": 0,
                    "sort": [
                        "10000000906db3a2146ec96b452f9ff7431fa273a432d9b14837eb72e17b587a",
                        1000000000,
                    ],
                    "nft": False,
                },
            ],
            "has_next": False,
        }

        assert result == expected_result

    def test_health(self, es_client):
        client = ElasticSearchClient(elastic_index=ELASTIC_INDEX, client=es_client)

        es_client.cluster.health = MagicMock(
            return_value={"cluster_name": "dev-cluster", "status": "green"}
        )

        assert client.health() == {"cluster_name": "dev-cluster", "status": "green"}
