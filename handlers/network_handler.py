import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)


def handle(event, context):
    response = None
    if event['pathParameters'] is not None:
        response = redis_client.get(event['pathParameters']['hash']).decode()
    else:
        response = json.dumps([k.decode() for k in redis_client.keys()])

    return {
        "statusCode": 200,
        "body": response,
        "headers": {
            "Content-Type": "application/json"
        }
    }
