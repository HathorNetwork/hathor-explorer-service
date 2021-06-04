from usecases.save_node_data import SaveNodeData


def handle(node_status: dict, _context: None = None) -> dict:

    save_node_data = SaveNodeData()
    result = save_node_data.save(node_status)

    if result:
        return {
            "statusCode": 200,
            "body": "{}"
        }

    return {
        "statusCode": 400,
        "body": "{}"
    }
