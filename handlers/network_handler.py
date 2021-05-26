import json

from usecases.get_network import GetNetwork
from usecases.list_available_nodes import ListAvailableNodes


def handle(event: dict, context: dict):
    response = None
    if event['pathParameters'] is not None:
        get_network = GetNetwork()
        response = get_network.get(event['pathParameters']['hash'])
    else:
        list_available_nodes = ListAvailableNodes()
        response = list_available_nodes.list()

    return {
        "statusCode": 200,
        "body": json.dumps(response),
        "headers": {
            "Content-Type": "application/json"
        }
    }
