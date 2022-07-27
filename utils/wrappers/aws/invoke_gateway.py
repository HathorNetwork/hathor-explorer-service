from typing import Any, Callable, List, Union

from aws_lambda_context import LambdaContext

from common.errors import EventValidationError
from common.logging import get_logger

logger = get_logger()

InvokeEvent = Union[List[Any], dict, str, float, None]


class MetadataUpdateEvent:

    def __init__(self, id: str, metadata: Union[dict, None] = None) -> None:
        self.id = id
        self.metadata = metadata or {}

    @classmethod
    def from_event(cls, event: InvokeEvent) -> 'MetadataUpdateEvent':
        try:
            assert isinstance(event, dict)
            assert 'id' in event

            if 'metadata' in event:
                assert isinstance(event['metadata'], dict)

            return cls(event['id'], event.get('metadata'))
        except AssertionError:
            raise EventValidationError('event is not a metadata update event')


class InvokeHandler:

    def __call__(
            self,
            function_to_call: Callable[[InvokeEvent, LambdaContext, Any], dict]
    ) -> Callable[[InvokeEvent, LambdaContext, Any], dict]:
        def wrapper(event: InvokeEvent, context: LambdaContext, *args: Any, **kwargs: Any) -> dict:
            try:
                result = function_to_call(event, context, *args, **kwargs)  # type: ignore

                return result
            except Exception as error:
                logger.exception(error)
                wrapped_error = dict(success=False)
                wrapped_error.update(error.args)
                return wrapped_error

        return wrapper
