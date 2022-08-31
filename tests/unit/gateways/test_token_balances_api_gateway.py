from unittest.mock import MagicMock

from pytest import fixture

from gateways.token_balances_api_gateway import TokenBalancesApiGateway


class TestTokenBalancesApiGateway:
    @fixture
    def elastic_search_client(self):
        return MagicMock()

    def test_get_token_information(self, elastic_search_client):
        elastic_search_client.search = MagicMock(
            return_value={
                "took": 2,
                "timed_out": False,
                "_shards": {"total": 3, "successful": 3, "skipped": 0, "failed": 0},
                "hits": {
                    "total": {"value": 10000, "relation": "gte"},
                    "max_score": None,
                    "hits": [],
                },
                "aggregations": {"address_count": {"value": 10868}},
            }
        )

        gateway = TokenBalancesApiGateway(elastic_search_client=elastic_search_client)
        result = gateway.get_token_information("")

        expected_result = {
            "addresses": 10868,
        }

        elastic_search_client.search.assert_called_once()

        assert result == expected_result

    def test_get_token_balances(self, elastic_search_client):
        elastic_search_client.search = MagicMock(
            return_value={
                "took": 1,
                "timed_out": False,
                "_shards": {"total": 1, "successful": 1, "skipped": 0, "failed": 0},
                "hits": {
                    "total": {"value": 10000, "relation": "gte"},
                    "max_score": None,
                    "hits": [
                        {
                            "_index": "dev-token-balance",
                            "_id": "00_WQFF1JvkdknFVKtvbR4piKXmj1ekJ2G9eB",
                            "_score": None,
                            "_source": {
                                "transactions": 364025,
                                "unlocked_authorities": 0,
                                "timelock_expires": None,
                                "token_id": "00",
                                "unlocked_balance": 1164880000,
                                "created_at": "2022-05-24T19:28:27Z",
                                "address": "WQFF1JvkdknFVKtvbR4piKXmj1ekJ2G9eB",
                                "locked_authorities": 0,
                                "updated_at": "2022-05-29T15:55:14Z",
                                "@timestamp": "2022-06-02T04:01:03.314590Z",
                                "locked_balance": 0,
                                "total": 1164880000,
                                "unique_id": "00_WQFF1JvkdknFVKtvbR4piKXmj1ekJ2G9eB",
                            },
                            "sort": [
                                1164880000,
                                "00_WQFF1JvkdknFVKtvbR4piKXmj1ekJ2G9eB",
                            ],
                        },
                        {
                            "_index": "dev-token-balance",
                            "_id": "00_WV4QgcgBoLM2BC7kgJLa8Xni6NPd4ug2eZ",
                            "_score": None,
                            "_source": {
                                "transactions": 128480,
                                "unlocked_authorities": 0,
                                "timelock_expires": None,
                                "token_id": "00",
                                "unlocked_balance": 440025600,
                                "created_at": "2022-05-24T19:28:27Z",
                                "address": "WV4QgcgBoLM2BC7kgJLa8Xni6NPd4ug2eZ",
                                "locked_authorities": 0,
                                "updated_at": "2022-05-29T22:10:46Z",
                                "@timestamp": "2022-06-02T04:18:03.378470Z",
                                "locked_balance": 960000,
                                "total": 440985600,
                                "unique_id": "00_WV4QgcgBoLM2BC7kgJLa8Xni6NPd4ug2eZ",
                            },
                            "sort": [
                                440985600,
                                "00_WV4QgcgBoLM2BC7kgJLa8Xni6NPd4ug2eZ",
                            ],
                        },
                    ],
                },
            }
        )

        gateway = TokenBalancesApiGateway(elastic_search_client=elastic_search_client)
        result = gateway.get_token_balances("", "", "", "")

        expected_result = {
            "hits": [
                {
                    "address": "WQFF1JvkdknFVKtvbR4piKXmj1ekJ2G9eB",
                    "token_id": "00",
                    "unlocked_balance": 1164880000,
                    "locked_balance": 0,
                    "total": 1164880000,
                    "sort": [1164880000, "00_WQFF1JvkdknFVKtvbR4piKXmj1ekJ2G9eB"],
                },
                {
                    "address": "WV4QgcgBoLM2BC7kgJLa8Xni6NPd4ug2eZ",
                    "token_id": "00",
                    "unlocked_balance": 440025600,
                    "locked_balance": 960000,
                    "total": 440985600,
                    "sort": [440985600, "00_WV4QgcgBoLM2BC7kgJLa8Xni6NPd4ug2eZ"],
                },
            ],
            "has_next": False,
        }

        elastic_search_client.search.assert_called_once()

        assert result == expected_result
