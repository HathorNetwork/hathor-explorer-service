from tests.fixtures.elastic_search_fixtures import (
    ELASTIC_SEARCH_RAW_HIT,
    ES_HIT_TO_RESULT_EXPECTED_RETURN
)

from utils.elastic_search.transformations.tx import es_hit_to_result


class TestTx:
    def test_tx_transformation(self):
        tx_transformation = es_hit_to_result(ELASTIC_SEARCH_RAW_HIT)
        assert tx_transformation == ES_HIT_TO_RESULT_EXPECTED_RETURN
