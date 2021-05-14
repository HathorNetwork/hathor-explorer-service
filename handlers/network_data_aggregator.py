import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def handle(node_status: dict, _context):

    redis_client.set(node_status['server']['id'], json.dumps(node_status))
    return {
        "statusCode": 200,
        "body": "{}"
    }