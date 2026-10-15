import json

from common.configuration import LAMBDA_INVOKE_URL
from gateways.clients.boto3_client import get_boto3_client


class LambdaClient:
    """This is an abstraction for boto3 lambda client"""

    def __init__(self) -> None:
        self.client = get_boto3_client("lambda", LAMBDA_INVOKE_URL)

    def invoke_async(self, function: str, payload: dict) -> int:
        """Invoke lambda asyncronously

        :param function: Name of function do be invoked
        :type function: str

        :param payload: Body of the request
        :type payload: dict

        :return: Request status code
        :rtype: int
        """
        return self.client.invoke(
            InvocationType="Event", FunctionName=function, Payload=json.dumps(payload)
        )["StatusCode"]

    def invoke(self, function: str, payload: dict) -> dict:
        """Invoke lambda syncronously

        Response structure
        {
            'StatusCode': 123,
            'FunctionError': 'string',
            'LogResult': 'string',
            'Payload': StreamingBody(),
            'ExecutedVersion': 'string'
        }

        :param function: Name of function do be invoked
        :type function: str

        :param payload: Body of the request
        :type payload: dict

        :return: Request response
        :rtype: dict
        """
        return self.client.invoke(FunctionName=function, Payload=json.dumps(payload))
