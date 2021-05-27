import json

from usecases.list_available_nodes import ListAvailableNodes


def handle(event: dict, context: dict):

    list_available_nodes = ListAvailableNodes()
    response = list_available_nodes.list()

    return {
        "statusCode": 200,
        "body": json.dumps(response),
        "headers": {
            "Content-Type": "application/json"
        }
    }
