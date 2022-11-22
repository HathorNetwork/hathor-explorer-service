from unittest.mock import MagicMock

from pytest import fixture

from gateways.token_api_gateway import TokenApiGateway


class TestTokenApiGateway:
    @fixture
    def elastic_search_client(self):
        return MagicMock()

    def test_get_tokens(self, elastic_search_client):
        elastic_search_client.search = MagicMock(
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
                                "transactions": 0,
                                "created_at": "2022-04-19T12:41:04Z",
                                "transaction_timestamp": 1649473276,
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
                                "transactions": 0,
                                "created_at": "2022-04-19T12:41:07Z",
                                "transaction_timestamp": 1000000000,
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

        gateway = TokenApiGateway(elastic_search_client=elastic_search_client)
        result = gateway.get_tokens("", "", "", "")

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

        elastic_search_client.search.assert_called_once()

        assert result == expected_result

    def test_get_token(self, elastic_search_client):
        elastic_search_client.search = MagicMock(
            return_value={
                "took": 70,
                "timed_out": False,
                "_shards": {"total": 1, "successful": 1, "skipped": 0, "failed": 0},
                "hits": {
                    "total": {"value": 1, "relation": "eq"},
                    "max_score": 4.592441,
                    "hits": [
                        {
                            "_index": "token-index",
                            "_id": "00",
                            "_score": 4.592441,
                            "_source": {
                                "transaction_timestamp": None,
                                "transactions": 2061288,
                                "name": "Hathor",
                                "created_at": "2022-08-19T15:38:55Z",
                                "id": "00",
                                "@timestamp": "2022-08-24T13:42:10.124937Z",
                                "symbol": "HTR",
                                "updated_at": "2022-08-24T13:42:00Z",
                            },
                        }
                    ],
                },
            }
        )

        gateway = TokenApiGateway(elastic_search_client=elastic_search_client)
        result = gateway.get_token("00")

        expected_result = {
            "hits": [
                {
                    "id": "00",
                    "name": "Hathor",
                    "symbol": "HTR",
                    "transaction_timestamp": None,
                    "transactions_count": 2061288,
                    "nft": False,
                }
            ],
            "has_next": False,
        }

        elastic_search_client.search.assert_called_once()
        assert result == expected_result

        elastic_search_client.search = MagicMock(
            return_value={
                "took": 70,
                "timed_out": False,
                "_shards": {"total": 1, "successful": 1, "skipped": 0, "failed": 0},
                "hits": {
                    "total": {"value": 0, "relation": "eq"},
                    "max_score": None,
                    "hits": [],
                },
            }
        )

        expected_result = {
            "hits": [],
            "has_next": False,
        }

        result_not_found = gateway.get_token("missing_token")

        assert result_not_found == expected_result
