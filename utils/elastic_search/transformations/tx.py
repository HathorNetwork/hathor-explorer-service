def es_hit_to_result(hit: dict) -> dict:
    """Gets a unique hit from ElasticSearch and map it to what API client expects.

    :param hit: Raw ElasticSearch hit
    :type hit: dict
    """
    result = {
        "tx_id": hit["_source"]["tx_id"],
        "timestamp": hit["_source"]["timestamp"],
        "version": hit["_source"]["version"],
        "voided": hit["_source"]["voided"],
        "height": hit["_source"]["height"],
        "weight": hit["_source"]["weight"],
        "hash_rate": hit["_source"]["hash_rate"],
    }

    return result
