from common.configuration import ELASTIC_INDEX
from utils.elastic_search.elastic_search_utils import ElasticSearchUtils


class TestElasticSearchUtils:

    def test_empty_search_string(self):
        utils = ElasticSearchUtils(elastic_index=ELASTIC_INDEX)

        search_text = ""
        sort_by = ""
        order = ""
        search_after = []

        result = utils.build_search_query(search_text, sort_by, order, search_after)

        assert 'query' not in result
        assert 'search_after' not in result

    def test_filled_search_string(self):
        utils = ElasticSearchUtils(elastic_index=ELASTIC_INDEX)
        search_text = "Test"
        sort_by = "transaction_timestamp"
        order = "desc"
        search_after = []

        result = utils.build_search_query(search_text, sort_by, order, search_after)
        print(result)
        assert result['query'] is not None
        assert result['query']['multi_match'] is not None
        assert result['query']['multi_match']['query'] == search_text
        assert result['sort'] == [{'transaction_timestamp': 'desc'}, {'id.keyword': 'asc'}]
        assert 'search_after' not in result

    def test_search_query_without_search_after(self):
        utils = ElasticSearchUtils(elastic_index=ELASTIC_INDEX)
        search_text = "Test"
        sort_by = "name"
        order = "asc"
        search_after = []

        result = utils.build_search_query(search_text, sort_by, order, search_after)

        assert 'search_after' not in result

    def test_search_query_with_search_after(self):
        utils = ElasticSearchUtils(elastic_index=ELASTIC_INDEX)
        search_text = "Test"
        sort_by = "name"
        order = "asc"
        search_after = ["00012601-afdf-11ec-a98a-02465f", "000125e7-afdf-11ec-a98a-02465f3c843c"]

        result = utils.build_search_query(search_text, sort_by, order, search_after)
        assert result['search_after'] is not None
        assert result['search_after'] == search_after

    def test_treat_response(self):
        utils = ElasticSearchUtils(elastic_index=ELASTIC_INDEX)

        es_response = {
            "took": 0,
            "timed_out": False,
            "_shards": {
                "total": 1,
                "successful": 1,
                "skipped": 0,
                "failed": 0
            },
            "hits": {
                "total": {
                    "value": 2,
                    "relation": "eq"
                },
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
                            "transactions": 3,
                            "id": "00000000906db3a2146ec96b452f9ff7431fa273a432d9b14837eb72e17b587a"
                        },
                        "sort": [
                            "00000000906db3a2146ec96b452f9ff7431fa273a432d9b14837eb72e17b587a",
                            1649473276
                        ]
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
                            "transactions": 3,
                            "id": "10000000906db3a2146ec96b452f9ff7431fa273a432d9b14837eb72e17b587a"
                        },
                        "sort": [
                            "10000000906db3a2146ec96b452f9ff7431fa273a432d9b14837eb72e17b587a",
                            1000000000
                        ]
                    }
                ]
            }
        }
        expected_treated_response = {
            "hits": [
                {
                    "id": "00000000906db3a2146ec96b452f9ff7431fa273a432d9b14837eb72e17b587a",
                    "name": "Test1",
                    "symbol": "TST1",
                    "transaction_timestamp": 1649473276,
                    "sort": [
                        "00000000906db3a2146ec96b452f9ff7431fa273a432d9b14837eb72e17b587a",
                        1649473276
                    ],
                    "transactions_count": 3,
                    "nft": False
                },
                {
                    "id": "10000000906db3a2146ec96b452f9ff7431fa273a432d9b14837eb72e17b587a",
                    "name": "Test2",
                    "symbol": "TST2",
                    "transaction_timestamp": 1000000000,
                    "sort": [
                        "10000000906db3a2146ec96b452f9ff7431fa273a432d9b14837eb72e17b587a",
                        1000000000
                    ],
                    "transactions_count": 3,
                    "nft": False
                }
            ],
            "has_next": False,
        }

        result = utils.treat_response(es_response)
        print(result)
        print(expected_treated_response)
        assert result == expected_treated_response
