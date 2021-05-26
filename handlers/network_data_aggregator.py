from usecases.save_network_data import SaveNetworkData


def handle(node_status: dict, _context) -> dict:

    save_network_data = SaveNetworkData()
    result = save_network_data.save(node_status)

    if result:
        return {
            "statusCode": 200,
            "body": "{}"
        }
    
    return {
        "statusCode": 400,
        "body": "{}"
    }
