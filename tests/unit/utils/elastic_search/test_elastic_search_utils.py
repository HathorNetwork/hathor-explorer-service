from utils.elastic_search.elastic_search_utils import ElasticSearchUtils


class TestElasticSearchUtils:

    def test_empty_search_string(self):
        utils = ElasticSearchUtils()

        search_text = ""
        sort_by = ""
        order = ""
        search_after = []

        result = utils.build_search_query(search_text, sort_by, order, search_after)

        assert 'query' not in result
        assert 'search_after' not in result

    def test_filled_search_string(self):
        utils = ElasticSearchUtils()
        search_text = "Test"
        sort_by = ""
        order = ""
        search_after = []

        result = utils.build_search_query(search_text, sort_by, order, search_after)
        assert result['query'] is not None
        assert result['query']['multi_match'] is not None
        assert result['query']['multi_match']['query'] == search_text

    def test_search_query_without_search_after(self):
        utils = ElasticSearchUtils()
        search_text = "Test"
        sort_by = "name"
        order = "asc"
        search_after = []

        result = utils.build_search_query(search_text, sort_by, order, search_after)

        assert 'search_after' not in result

    def test_search_query_with_search_after(self):
        utils = ElasticSearchUtils()
        search_text = "Test"
        sort_by = "name"
        order = "asc"
        search_after = ["00012601-afdf-11ec-a98a-02465f", "000125e7-afdf-11ec-a98a-02465f3c843c"]

        result = utils.build_search_query(search_text, sort_by, order, search_after)
        assert result['search_after'] is not None
        assert result['search_after'] == search_after

    def test_treat_response(self):
        utils = ElasticSearchUtils()

        es_response = {
            "took": 5,
            "timed_out": False,
            "_shards": {
                "total": 1,
                "successful": 1,
                "skipped": 0,
                "failed": 0
            },
            "hits": {
                "total": {
                    "value": 1,
                    "relation": "eq"
                },
                "max_score": None,
                "hits": [
                    {
                        "_index": "mainnet-token",
                        "_id": "00db7e187ab5b247f28d2d50003f6927ca9d856acf5f1610b186cb0fed5b3438",
                        "_score": None,
                        "_source": {
                            "banned": False,
                            "verified": False,
                            "id": "00db7e187ab5b247f28d2d50003f6927ca9d856acf5f1610b186cb0fed5b3438",
                            "@timestamp": "2022-03-30T03: 39: 05.846296Z",
                            "nft": True,
                            "symbol": "NNSC",
                            "updated_at": "2022-03-24T19: 53: 55Z",
                            "name": "New New Santos Coin",
                            "created_at": "2022-03-24T19: 53: 55Z"
                        },
                        "sort": [
                            "00db7e187ab5b247f28d2d50003f6927ca9d856acf5f1610b186cb0fed5b3438",
                            "New New Santos Coin"
                        ]
                    }
                ]
            }
        }
        expected_treated_response = {
            "hits": [
                {
                    "id": "00db7e187ab5b247f28d2d50003f6927ca9d856acf5f1610b186cb0fed5b3438",
                    "name": "New New Santos Coin",
                    "symbol": "NNSC",
                    "sort": [
                        "00db7e187ab5b247f28d2d50003f6927ca9d856acf5f1610b186cb0fed5b3438",
                        "New New Santos Coin"
                    ],
                    "nft": True
                }
            ],
            "has_next": False
        }

        result = utils.treat_response(es_response)
        assert result == expected_treated_response
