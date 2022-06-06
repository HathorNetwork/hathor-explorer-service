from utils.elastic_search.transformations.tx import es_hit_to_result

ELASTIC_SEARCH_RAW_HIT = {
    '_source': {
        'tx_id': '00a1786694f2b2248c4272e64f9f414759322b4e6d5e40d39cc5b5aedfd70dfb',
        'voided': False,
        'timestamp': '2022-05-09T18:55:47Z',
        '@timestamp': '2022-06-01T02:56:20.402864Z',
        'weight': 60.66999816894531,
        'updated_at': '2022-06-01T02:36:14Z',
        'height': 1740645,
        'created_at': '2022-06-01T02:31:49Z',
        'version': 0,
        'hash_rate': 123
    }
}

ELASTIC_SEARCH_HIT_MAPPED = {
    'tx_id': '00a1786694f2b2248c4272e64f9f414759322b4e6d5e40d39cc5b5aedfd70dfb',
    'timestamp': '2022-05-09T18:55:47Z',
    'version': 0,
    'voided': False,
    'height': 1740645,
    'weight': 60.66999816894531,
    'hash_rate': 123
}

ES_HIT_TO_RESULT_EXPECTED_RETURN = {
    'tx_id': '00a1786694f2b2248c4272e64f9f414759322b4e6d5e40d39cc5b5aedfd70dfb',
    'timestamp': '2022-05-09T18:55:47Z',
    'version': 0,
    'voided': False,
    'height': 1740645,
    'weight': 60.66999816894531,
    'hash_rate': 123
}


class TestTx:
    def test_tx_transformation(self):
        tx_transformation = es_hit_to_result(ELASTIC_SEARCH_RAW_HIT)
        assert tx_transformation == ES_HIT_TO_RESULT_EXPECTED_RETURN
