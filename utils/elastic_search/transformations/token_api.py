def es_hit_to_result(hit: dict) -> dict:
    """Gets a unique hit from ElasticSearch and map it to what API client expects.

    :param hit: Raw ElasticSearch hit
    :type hit: dict
    """
    print("\n\n\nWILL PRINT HIT")
    print(hit)
    print("\n\n\nPRINTED HIT")
    result = {
        'id': hit['_source']['id'],
        'name': hit['_source']['name'],
        'symbol': hit['_source']['symbol'],
        'transaction_timestamp': hit['_source']['transaction_timestamp'],
        'sort': hit['sort']
    }

    if 'nft' in hit['_source']:
        result['nft'] = hit['_source']['nft']
    else:
        result['nft'] = False

    return result