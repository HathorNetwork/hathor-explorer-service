def es_hit_to_result(hit: dict) -> dict:
    """Gets a unique hit from ElasticSearch and map it to what API client expects.

    :param hit: Raw ElasticSearch hit
    :type hit: dict
    """
    result = {
        "address": hit["_source"]["address"],
        "token_id": hit["_source"]["token_id"],
        "unlocked_balance": hit["_source"]["unlocked_balance"],
        "locked_balance": hit["_source"]["locked_balance"],
        "total": hit["_source"]["total"],
        "sort": hit["sort"],
    }

    return result
