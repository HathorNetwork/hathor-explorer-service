from typing import Any, Callable
from unittest.mock import MagicMock

import pytest

from utils.wrappers.aws.invoke_handler import InvokeEvent, InvokeHandler, LambdaContext


class TestInvokeHandler:
    @pytest.fixture
    def function_to_call(self) -> Callable[[InvokeEvent, LambdaContext, Any], dict]:
        def function(
            event: InvokeEvent, context: LambdaContext, *args: Any, **kwargs: Any
        ) -> dict:
            return {"success": True}

        return function

    @pytest.fixture
    def function_to_call_with_exception(
        self,
    ) -> Callable[[InvokeEvent, LambdaContext, Any], dict]:
        def function(
            event: InvokeEvent, context: LambdaContext, *args: Any, **kwargs: Any
        ) -> dict:
            raise ValueError("Something went wrong")

        return function

    def test_invoke_handler_success(self, function_to_call):
        invoke_handler = InvokeHandler()
        wrapped_function = invoke_handler(function_to_call)

        event = {"key": "value"}
        context = MagicMock()
        result = wrapped_function(event, context)

        assert result == {"success": True}

    def test_invoke_handler_exception(self, function_to_call_with_exception):
        invoke_handler = InvokeHandler()
        wrapped_function = invoke_handler(function_to_call_with_exception)

        event = {"key": "value"}
        context = MagicMock()

        result = wrapped_function(event, context)

        assert result == {"success": False, "error": "Something went wrong"}
