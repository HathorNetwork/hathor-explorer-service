import json
from typing import Optional

from aws_lambda_context import LambdaContext

from usecases.send_report import SendReport
from utils.wrappers.aws.api_gateway import ApiGateway, ApiGatewayEvent


@ApiGateway()
def handle(event: ApiGatewayEvent, __: LambdaContext, send_report: Optional[SendReport] = None) -> dict:

    send_report = send_report or SendReport()
    type = event.body.get('type')
    id = event.body.get('id')
    description = event.body.get('description')

    response = send_report.send(type, id, description)

    return {
        "statusCode": 200,
        "body": json.dumps({'ok': response}),
        "headers": {
            "Content-Type": "application/json"
        }
    }
