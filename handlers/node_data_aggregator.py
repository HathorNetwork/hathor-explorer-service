from usecases.save_node_data import SaveNodeData
from usecases.aggregate_node_data import AggregateNodeData


def handle(node_status: dict, _context: None = None) -> dict:

    save_node_data = SaveNodeData()
    aggregate_node_data = AggregateNodeData()

    result_save = save_node_data.save(node_status)
    result_aggregate = aggregate_node_data.aggregate()

    if result_save and result_aggregate:
        return {
            "statusCode": 200,
            "body": "{}"
        }

    return {
        "statusCode": 400,
        "body": "{}"
    }
