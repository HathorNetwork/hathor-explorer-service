import asyncio
import json
import math
import unittest
from typing import Any
from unittest.mock import ANY, AsyncMock, MagicMock, patch

import requests
from aiohttp import ContentTypeError, RequestInfo
from pytest import raises

from gateways.clients.hathor_core_client import HathorCoreAsyncClient, HathorCoreClient


def _make_response(
    status: int, json_data: Any = None, text_data: str = ""
) -> MagicMock:
    """Build a minimal aiohttp response mock."""
    mock = MagicMock()
    mock.status = status
    mock.text = AsyncMock(return_value=text_data)
    mock.json = AsyncMock(return_value=json_data)
    return mock


def _as_ctx(response_mock: MagicMock) -> MagicMock:
    """Wrap a response mock so it can be used as an async context manager."""
    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=response_mock)
    cm.__aexit__ = AsyncMock(return_value=None)
    return cm


def _make_non_json_error() -> ContentTypeError:
    request_info = MagicMock(spec=RequestInfo)
    request_info.real_url = "http://test.node/v1a/status"
    return ContentTypeError(request_info=request_info, history=())


class _FakeClock:
    """Stands in for `monotonic`: time only moves when a test advances it."""

    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def _respond_after(clock: _FakeClock, steps: list) -> Any:
    """`session.get` side effect: each call advances the clock, then responds."""
    pending = iter(steps)

    def respond(*args: Any, **kwargs: Any) -> MagicMock:
        seconds, response = next(pending)
        clock.advance(seconds)
        return _as_ctx(response)

    return respond


class TestHathorCoreAsyncClientGet(unittest.IsolatedAsyncioTestCase):
    @patch("aiohttp.ClientSession.get")
    @patch("gateways.clients.hathor_core_client.asyncio.sleep", new_callable=AsyncMock)
    async def test_get_success(self, mock_sleep, mock_get):
        """200 response: returns parsed JSON, no retries."""
        data = {"success": True}
        mock_get.return_value = _as_ctx(_make_response(200, json_data=data))

        client = HathorCoreAsyncClient("http://test.node")
        result = await client.get("/v1a/status")

        assert result == data
        mock_sleep.assert_not_called()

    @patch("aiohttp.ClientSession.get")
    @patch("gateways.clients.hathor_core_client.asyncio.sleep", new_callable=AsyncMock)
    async def test_get_retries_on_502_then_succeeds(self, mock_sleep, mock_get):
        """502 on first attempt, 200 on retry: no warning logged, returns data."""
        data = {"id": "abc"}
        mock_get.side_effect = [
            _as_ctx(_make_response(502, text_data="<html>502 Bad Gateway</html>")),
            _as_ctx(_make_response(200, json_data=data)),
        ]

        client = HathorCoreAsyncClient("http://test.node")
        with patch.object(client, "log") as mock_log:
            result = await client.get("/v1a/status")

        assert result == data
        mock_log.warning.assert_not_called()
        mock_sleep.assert_called_once_with(HathorCoreAsyncClient.RETRY_DELAY)

    @patch("gateways.clients.hathor_core_client.aiohttp.ClientSession")
    @patch("gateways.clients.hathor_core_client.asyncio.sleep", new_callable=AsyncMock)
    async def test_get_reuses_single_session_across_retries(
        self, mock_sleep, mock_client_session
    ):
        """Retries reuse one aiohttp session, bounded by the total timeout."""
        data = {"id": "abc"}
        session = MagicMock()
        session.get.side_effect = [
            _as_ctx(_make_response(502, text_data="<html>502 Bad Gateway</html>")),
            _as_ctx(_make_response(200, json_data=data)),
        ]
        session_cm = MagicMock()
        session_cm.__aenter__ = AsyncMock(return_value=session)
        session_cm.__aexit__ = AsyncMock(return_value=None)
        mock_client_session.return_value = session_cm

        client = HathorCoreAsyncClient("http://test.node")
        result = await client.get("/v1a/status", timeout=7)

        assert result == data
        mock_client_session.assert_called_once()
        assert session.get.call_count == 2
        for call in session.get.call_args_list:
            assert 0 < call.kwargs["timeout"].total <= 7
        mock_sleep.assert_called_once_with(HathorCoreAsyncClient.RETRY_DELAY)

    @patch("aiohttp.ClientSession.get")
    @patch("gateways.clients.hathor_core_client.asyncio.sleep", new_callable=AsyncMock)
    async def test_get_logs_each_retry(self, mock_sleep, mock_get):
        """Each retry is logged with the upstream status and the attempt number."""
        data = {"id": "abc"}
        mock_get.side_effect = [
            _as_ctx(_make_response(503, text_data="unavailable")),
            _as_ctx(_make_response(200, json_data=data)),
        ]

        client = HathorCoreAsyncClient("http://test.node")
        with patch.object(client, "log") as mock_log:
            result = await client.get("/v1a/status")

        assert result == data
        mock_log.info.assert_called_once()
        assert mock_log.info.call_args.args == ("hathor_core_retry",)
        kwargs = mock_log.info.call_args.kwargs
        assert kwargs["path"] == "/v1a/status"
        assert kwargs["status"] == 503
        assert kwargs["attempt"] == 1
        assert kwargs["elapsed"] >= 0

    @patch("aiohttp.ClientSession.get")
    @patch("gateways.clients.hathor_core_client.asyncio.sleep", new_callable=AsyncMock)
    async def test_get_skips_retry_that_does_not_fit_the_budget(
        self, mock_sleep, mock_get
    ):
        """A 5xx near the end of the budget is returned instead of retried."""
        retry_body = "<html>504 Gateway Timeout</html>"
        clock = _FakeClock()
        # The 504 arrives after 4.5 s of a 5 s budget: no room for delay + attempt.
        mock_get.side_effect = _respond_after(
            clock, [(4.5, _make_response(504, text_data=retry_body))]
        )

        client = HathorCoreAsyncClient("http://test.node")
        with patch("gateways.clients.hathor_core_client.monotonic", clock):
            with patch.object(client, "log") as mock_log:
                result = await client.get("/v1a/status", timeout=5)

        assert result == {"error": "status 504", "body": retry_body}
        assert mock_get.call_count == 1
        mock_sleep.assert_not_called()
        mock_log.info.assert_not_called()
        mock_log.warning.assert_called_once_with(
            "hathor_core_error",
            path="/v1a/status",
            status=504,
            body=retry_body,
            attempt=1,
            elapsed=4.5,
            budget_exhausted=True,
        )

    @patch("aiohttp.ClientSession.get")
    @patch("gateways.clients.hathor_core_client.asyncio.sleep", new_callable=AsyncMock)
    async def test_get_second_attempt_gets_only_the_remaining_budget(
        self, mock_sleep, mock_get
    ):
        """After a retry, the next attempt's timeout is what is left of the budget."""
        data = {"id": "abc"}
        clock = _FakeClock()
        mock_sleep.side_effect = clock.advance
        # The 502 takes 2 s and the retry delay 1 s, so 7 s of 10 s are left.
        mock_get.side_effect = _respond_after(
            clock,
            [
                (2.0, _make_response(502, text_data="bad gateway")),
                (0.1, _make_response(200, json_data=data)),
            ],
        )

        client = HathorCoreAsyncClient("http://test.node")
        with patch("gateways.clients.hathor_core_client.monotonic", clock):
            result = await client.get("/v1a/status", timeout=10)

        assert result == data
        first, second = mock_get.call_args_list
        assert first.kwargs["timeout"].total == 10
        assert second.kwargs["timeout"].total == 7
        # No rounding of the deadline up to the next second.
        assert first.kwargs["timeout"].ceil_threshold == math.inf

    @patch("aiohttp.ClientSession.get")
    @patch("gateways.clients.hathor_core_client.asyncio.sleep", new_callable=AsyncMock)
    async def test_get_attempt_timeout_stays_positive_after_oversleep(
        self, mock_sleep, mock_get
    ):
        """If the retry delay overruns the budget, the attempt still gets a timeout.

        aiohttp treats a total <= 0 as "no timeout at all", so a blocked event
        loop must not turn the last attempt into an unbounded request.
        """
        clock = _FakeClock()
        # The delay should take 1 s but takes 3 s (busy event loop).
        mock_sleep.side_effect = lambda delay: clock.advance(3.0)
        mock_get.side_effect = _respond_after(
            clock,
            [
                (8.0, _make_response(502, text_data="bad gateway")),
                (0.0, _make_response(200, json_data={"id": "abc"})),
            ],
        )

        client = HathorCoreAsyncClient("http://test.node")
        with patch("gateways.clients.hathor_core_client.monotonic", clock):
            await client.get("/v1a/status", timeout=10)

        second = mock_get.call_args_list[1]
        assert second.kwargs["timeout"].total > 0

    @patch("aiohttp.ClientSession.get")
    @patch("gateways.clients.hathor_core_client.asyncio.sleep", new_callable=AsyncMock)
    async def test_get_retry_budget_boundary(self, mock_sleep, mock_get):
        """A retry starts only if the delay plus a minimum attempt still fit."""
        # Budget 10 s, delay 1 s, minimum attempt 1 s: a 502 after 8 s leaves
        # exactly enough room, and one after 8.01 s does not.
        for elapsed, retried in [(8.0, True), (8.01, False)]:
            with self.subTest(elapsed=elapsed):
                mock_get.reset_mock()
                mock_sleep.reset_mock()
                clock = _FakeClock()
                mock_get.side_effect = _respond_after(
                    clock,
                    [
                        (elapsed, _make_response(502, text_data="bad gateway")),
                        (0.0, _make_response(200, json_data={"id": "abc"})),
                    ],
                )

                client = HathorCoreAsyncClient("http://test.node")
                with patch("gateways.clients.hathor_core_client.monotonic", clock):
                    result = await client.get("/v1a/status", timeout=10)

                assert (mock_get.call_count == 2) is retried
                assert mock_sleep.called is retried
                assert (result == {"id": "abc"}) is retried

    @patch("aiohttp.ClientSession.get")
    @patch("gateways.clients.hathor_core_client.asyncio.sleep", new_callable=AsyncMock)
    async def test_get_returns_last_5xx_when_a_retry_times_out(
        self, mock_sleep, mock_get
    ):
        """A retry that times out returns the 5xx that caused it, not the timeout."""
        error_body = {"error": "fullnode overloaded"}
        mock_get.side_effect = [
            _as_ctx(_make_response(503, text_data=json.dumps(error_body))),
            asyncio.TimeoutError(),
        ]

        client = HathorCoreAsyncClient("http://test.node")
        with patch.object(client, "log") as mock_log:
            result = await client.get("/v1a/status")

        assert result == error_body
        assert mock_get.call_count == 2
        mock_log.error.assert_not_called()
        mock_log.warning.assert_called_once_with(
            "hathor_core_error",
            path="/v1a/status",
            status=503,
            body=json.dumps(error_body),
            attempt=2,
            elapsed=ANY,
            retry_timed_out=True,
            error="TimeoutError()",
        )

    @patch("aiohttp.ClientSession.get")
    @patch("gateways.clients.hathor_core_client.asyncio.sleep", new_callable=AsyncMock)
    async def test_get_first_attempt_timeout_is_an_error(self, mock_sleep, mock_get):
        """A timeout with no earlier 5xx is reported as an error, without retry."""
        mock_get.side_effect = asyncio.TimeoutError()

        client = HathorCoreAsyncClient("http://test.node")
        with patch.object(client, "log") as mock_log:
            result = await client.get("/v1a/status")

        assert result == {"error": repr(asyncio.TimeoutError())}
        assert mock_get.call_count == 1
        mock_sleep.assert_not_called()
        mock_log.error.assert_called_once()

    @patch("aiohttp.ClientSession.get")
    @patch("gateways.clients.hathor_core_client.asyncio.sleep", new_callable=AsyncMock)
    async def test_get_logs_warning_after_all_retries_exhausted(
        self, mock_sleep, mock_get
    ):
        """All attempts return 502: exactly one warning logged, returns error dict."""
        retry_body = "<html>502 Bad Gateway</html>"
        total_attempts = HathorCoreAsyncClient.MAX_RETRIES + 1
        mock_get.side_effect = [
            _as_ctx(_make_response(502, text_data=retry_body))
            for _ in range(total_attempts)
        ]

        client = HathorCoreAsyncClient("http://test.node")
        with patch.object(client, "log") as mock_log:
            result = await client.get("/v1a/status")

        assert "error" in result
        mock_log.warning.assert_called_once_with(
            "hathor_core_error",
            path="/v1a/status",
            status=502,
            body=retry_body,
            attempt=3,
            elapsed=ANY,
            budget_exhausted=False,
        )
        assert mock_sleep.call_count == HathorCoreAsyncClient.MAX_RETRIES

    @patch("aiohttp.ClientSession.get")
    @patch("gateways.clients.hathor_core_client.asyncio.sleep", new_callable=AsyncMock)
    async def test_get_no_retry_on_4xx(self, mock_sleep, mock_get):
        """4xx error: logged immediately without any retry, JSON body kept."""
        error_body = {"success": False, "message": "not found"}
        mock_get.return_value = _as_ctx(
            _make_response(404, text_data=json.dumps(error_body))
        )

        client = HathorCoreAsyncClient("http://test.node")
        with patch.object(client, "log") as mock_log:
            result = await client.get("/v1a/missing")

        assert result == error_body
        mock_sleep.assert_not_called()
        mock_log.warning.assert_called_once()

    @patch("aiohttp.ClientSession.get")
    @patch("gateways.clients.hathor_core_client.asyncio.sleep", new_callable=AsyncMock)
    async def test_get_4xx_non_json_body_returns_status_and_body(
        self, mock_sleep, mock_get
    ):
        """4xx non-JSON error bodies are returned as status + raw body."""
        response = _make_response(404, text_data="Not Found")
        # json() must never be called: we decode the text body ourselves.
        response.json = AsyncMock(side_effect=_make_non_json_error())
        mock_get.return_value = _as_ctx(response)

        client = HathorCoreAsyncClient("http://test.node")
        with patch.object(client, "log") as mock_log:
            result = await client.get("/v1a/missing")

        assert result == {"error": "status 404", "body": "Not Found"}
        response.json.assert_not_called()
        mock_sleep.assert_not_called()
        mock_log.warning.assert_called_once_with(
            "hathor_core_error",
            path="/v1a/missing",
            status=404,
            body="Not Found",
            attempt=1,
            elapsed=ANY,
            budget_exhausted=False,
        )
        mock_log.error.assert_not_called()

    @patch("aiohttp.ClientSession.get")
    @patch("gateways.clients.hathor_core_client.asyncio.sleep", new_callable=AsyncMock)
    async def test_get_5xx_non_json_body_returns_status_and_body_after_retries(
        self, mock_sleep, mock_get
    ):
        """Retryable 5xx non-JSON bodies are returned as status + raw body."""
        retry_body = "<html>502 Bad Gateway</html>"
        total_attempts = HathorCoreAsyncClient.MAX_RETRIES + 1
        responses = []
        for _ in range(total_attempts):
            response = _make_response(502, text_data=retry_body)
            response.json = AsyncMock(side_effect=_make_non_json_error())
            responses.append(_as_ctx(response))
        mock_get.side_effect = responses

        client = HathorCoreAsyncClient("http://test.node")
        with patch.object(client, "log") as mock_log:
            result = await client.get("/v1a/status")

        assert result == {"error": "status 502", "body": retry_body}
        for response_ctx in responses:
            response_ctx.__aenter__.return_value.json.assert_not_called()
        assert mock_sleep.call_count == HathorCoreAsyncClient.MAX_RETRIES
        mock_log.warning.assert_called_once_with(
            "hathor_core_error",
            path="/v1a/status",
            status=502,
            body=retry_body,
            attempt=3,
            elapsed=ANY,
            budget_exhausted=False,
        )

    @patch("aiohttp.ClientSession.get")
    @patch("gateways.clients.hathor_core_client.asyncio.sleep", new_callable=AsyncMock)
    async def test_get_5xx_json_body_returned_after_retries(self, mock_sleep, mock_get):
        """Retryable 5xx with a JSON body keeps the server-provided payload."""
        error_body = {"error": "upstream exploded"}
        total_attempts = HathorCoreAsyncClient.MAX_RETRIES + 1
        mock_get.side_effect = [
            _as_ctx(_make_response(503, text_data=json.dumps(error_body)))
            for _ in range(total_attempts)
        ]

        client = HathorCoreAsyncClient("http://test.node")
        result = await client.get("/v1a/status")

        assert result == error_body
        assert mock_sleep.call_count == HathorCoreAsyncClient.MAX_RETRIES

    @patch("aiohttp.ClientSession.get")
    @patch("gateways.clients.hathor_core_client.asyncio.sleep", new_callable=AsyncMock)
    async def test_get_retry_false_skips_retries_on_5xx(self, mock_sleep, mock_get):
        """retry=False returns the first 5xx response without retrying."""
        retry_body = "<html>503 Service Unavailable</html>"
        mock_get.return_value = _as_ctx(_make_response(503, text_data=retry_body))

        client = HathorCoreAsyncClient("http://test.node")
        with patch.object(client, "log") as mock_log:
            result = await client.get("/v1a/health", retry=False)

        assert result == {"error": "status 503", "body": retry_body}
        assert mock_get.call_count == 1
        mock_sleep.assert_not_called()
        mock_log.warning.assert_called_once_with(
            "hathor_core_error",
            path="/v1a/health",
            status=503,
            body=retry_body,
            attempt=1,
            elapsed=ANY,
            budget_exhausted=False,
        )

    @patch("aiohttp.ClientSession.get")
    @patch("gateways.clients.hathor_core_client.asyncio.sleep", new_callable=AsyncMock)
    async def test_get_retry_false_keeps_json_body_on_5xx(self, mock_sleep, mock_get):
        """retry=False still returns the server-provided JSON body as-is."""
        health_body = {"status": "fail", "checks": {}}
        mock_get.return_value = _as_ctx(
            _make_response(503, text_data=json.dumps(health_body))
        )

        client = HathorCoreAsyncClient("http://test.node")
        result = await client.get("/v1a/health", retry=False)

        assert result == health_body
        assert mock_get.call_count == 1
        mock_sleep.assert_not_called()

    @patch("aiohttp.ClientSession.get")
    @patch("gateways.clients.hathor_core_client.asyncio.sleep", new_callable=AsyncMock)
    async def test_get_no_retry_on_exception(self, mock_sleep, mock_get):
        """Network exception: logged as error immediately, no retry."""
        mock_get.side_effect = Exception("connection refused")

        client = HathorCoreAsyncClient("http://test.node")
        with patch.object(client, "log") as mock_log:
            result = await client.get("/v1a/status")

        assert "error" in result
        mock_log.error.assert_called_once()
        mock_sleep.assert_not_called()


class TestHathorCoreClient:
    @patch("gateways.clients.hathor_core_client.requests.get")
    def test_get_text(self, mocked_get):
        mocked_get.return_value.status_code = 200
        expected = json.dumps({"success": True})
        mocked_get.return_value.text = expected

        client = HathorCoreClient("https://mydomain.com")

        result = client.get_text("/some/path", {"page": 2})

        mocked_get.assert_called_once_with(
            "https://mydomain.com/some/path", params={"page": 2}
        )
        assert result
        assert result == expected

    @patch("gateways.clients.hathor_core_client.requests.get")
    def test_get(self, mocked_get):
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.text = json.dumps({"success": True})

        client = HathorCoreClient("http://mydomain.com")

        result = client.get("/some/path", {"page": 2})

        mocked_get.assert_called_once_with(
            "http://mydomain.com/some/path", params={"page": 2}
        )
        assert result
        assert result["success"] is True

    @patch("gateways.clients.hathor_core_client.requests.get")
    def test_get_no_200(self, mocked_get):
        mocked_get.return_value.status_code = 404

        client = HathorCoreClient("https://mydomain.com")

        result = client.get("/some/path", {"id": 42})

        mocked_get.assert_called_once_with(
            "https://mydomain.com/some/path", params={"id": 42}
        )
        assert result is None

    @patch("gateways.clients.hathor_core_client.requests.get")
    def test_get_raises(self, mocked_get):
        mocked_get.side_effect = Exception("Boom!")

        client = HathorCoreClient("https://mydomain.com")

        with raises(Exception, match=r"Boom!"):
            result = client.get("/some/path", {"page": -12})

            mocked_get.assert_called_once_with(
                "https://mydomain.com/some/path", params={"page": -12}
            )

            assert result
            assert result["error"] == "Boom!"

    @patch("gateways.clients.hathor_core_client.requests.get")
    def test_get_timeout(self, mocked_get):
        mocked_get.side_effect = requests.ReadTimeout("reason")

        client = HathorCoreClient("https://mydomain.com")

        with raises(Exception, match=r"timeout"):
            client.get("/some/path", {"page": 69})
        mocked_get.assert_called_once_with(
            "https://mydomain.com/some/path", params={"page": 69}
        )
