def es_hit_to_result(hit: dict) -> dict:
    """Gets a unique hit from ElasticSearch and map it to what API client expects.

    :param hit: Raw ElasticSearch hit
    :type hit: dict
    """
    result = {
        "id": hit["_source"]["id"],
        "name": hit["_source"]["name"],
        "symbol": hit["_source"]["symbol"],
        "transaction_timestamp": hit["_source"]["transaction_timestamp"],
        "transactions_count": hit["_source"]["transactions"],
    }

    # If we are searching for a single result, we won't have sort in the result
    if "sort" in hit:
        result["sort"] = hit["sort"]

    if "nft" in hit["_source"]:
        result["nft"] = hit["_source"]["nft"]
    else:
        result["nft"] = False

    return result
