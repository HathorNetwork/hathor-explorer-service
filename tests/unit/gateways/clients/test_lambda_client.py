import json
from io import BytesIO
from unittest.mock import patch

from botocore.response import StreamingBody
from botocore.stub import Stubber

from gateways.clients.lambda_client import LambdaClient


class TestLambdaClient:
    @patch("gateways.clients.lambda_client.LAMBDA_INVOKE_URL", None)
    def test_invoke_async(self):
        lambda_client = LambdaClient()

        stubber = Stubber(lambda_client.client)
        payload = {"you_shall_not": "pass"}

        lambda_expected_params = {
            "InvocationType": "Event",
            "FunctionName": "balrog-caller",
            "Payload": json.dumps(payload),
        }
        lambda_response = {"StatusCode": 202}
        stubber.add_response("invoke", lambda_response, lambda_expected_params)

        stubber.activate()

        result = lambda_client.invoke_async("balrog-caller", payload)

        assert result == 202

    @patch(
        "gateways.clients.lambda_client.LAMBDA_INVOKE_URL",
        "http://lambda.invoke.endpoint",
    )
    def test_invoke(self):
        lambda_client = LambdaClient()

        stubber = Stubber(lambda_client.client)
        payload = {"winter_is": "comming"}

        lambda_expected_params = {
            "FunctionName": "westeros-house-detector",
            "Payload": json.dumps(payload),
        }
        lambda_response = {
            "StatusCode": 200,
            "Payload": StreamingBody(
                BytesIO("You are a stark".encode("utf8")), len("You are a stark")
            ),
        }
        stubber.add_response("invoke", lambda_response, lambda_expected_params)
        stubber.activate()

        result = lambda_client.invoke("westeros-house-detector", payload)

        assert result["StatusCode"] == 200
        assert result["Payload"].read().decode() == "You are a stark"

    @patch("gateways.clients.lambda_client.LAMBDA_INVOKE_URL", None)
    def test_reuses_boto3_client_across_instances(self):
        # Warm Lambda invocations must not build a new boto3 client each time.
        assert LambdaClient().client is LambdaClient().client

    def test_builds_one_boto3_client_per_endpoint(self):
        with patch("gateways.clients.lambda_client.LAMBDA_INVOKE_URL", None):
            default_client = LambdaClient().client
        with patch(
            "gateways.clients.lambda_client.LAMBDA_INVOKE_URL", "http://lambda.local"
        ):
            custom_client = LambdaClient().client

        assert default_client is not custom_client
        assert custom_client.meta.endpoint_url == "http://lambda.local"
