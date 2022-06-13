ELASTIC_SEARCH_BEST_CHAIN_HEIGHT_SUCCESSFUL_RAW_RESPONSE = {
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
                '_index': 'dev-tx',
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

GATEWAY_BEST_CHAIN_HEIGHT_SUCCESSFUL_RESPONSE = {
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
    'has_next': False,
}

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

ES_HIT_TO_RESULT_EXPECTED_RETURN = {
    'tx_id': '00a1786694f2b2248c4272e64f9f414759322b4e6d5e40d39cc5b5aedfd70dfb',
    'timestamp': '2022-05-09T18:55:47Z',
    'version': 0,
    'voided': False,
    'height': 1740645,
    'weight': 60.66999816894531,
    'hash_rate': 123
}
