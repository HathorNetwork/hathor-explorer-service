from typing import Any, Callable

from aws_lambda_context import LambdaContext

from common.logging import get_logger

logger = get_logger()


class MetadataUpdateEvent:

    def __init__(self, event: dict, context: LambdaContext) -> None:
        self.id = event.get('id')
        self.metadata = event.get('metadata') or {}


class InvokeGateway:

    def __call__(
            self,
            function_to_call: Callable[[dict, LambdaContext, Any], dict]
    ) -> Callable[[dict, LambdaContext, Any], dict]:
        def wrapper(event: dict, context: LambdaContext, *args: Any, **kwargs: Any) -> dict:
            try:
                result = function_to_call(event, context, *args, **kwargs)

                return result
            except Exception as error:
                logger.exception(error)
                return error

        return wrapper
