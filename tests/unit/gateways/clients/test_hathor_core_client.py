import json
import unittest
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

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
        """Retries reuse one aiohttp session while keeping per-attempt timeouts."""
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
        assert mock_client_session.call_args.kwargs["timeout"].total == 7
        assert session.get.call_count == 2
        mock_sleep.assert_called_once_with(HathorCoreAsyncClient.RETRY_DELAY)

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
        )
        assert mock_sleep.call_count == HathorCoreAsyncClient.MAX_RETRIES

    @patch("aiohttp.ClientSession.get")
    @patch("gateways.clients.hathor_core_client.asyncio.sleep", new_callable=AsyncMock)
    async def test_get_no_retry_on_4xx(self, mock_sleep, mock_get):
        """4xx error: logged immediately without any retry."""
        mock_get.return_value = _as_ctx(
            _make_response(404, text_data="Not Found", json_data=None)
        )

        client = HathorCoreAsyncClient("http://test.node")
        with patch.object(client, "log") as mock_log:
            await client.get("/v1a/missing")

        mock_sleep.assert_not_called()
        mock_log.warning.assert_called_once()

    @patch("aiohttp.ClientSession.get")
    @patch("gateways.clients.hathor_core_client.asyncio.sleep", new_callable=AsyncMock)
    async def test_get_4xx_non_json_body_returns_error_without_parsing_json(
        self, mock_sleep, mock_get
    ):
        """4xx error bodies must not be parsed as JSON."""
        response = _make_response(404, text_data="Not Found")
        response.json = AsyncMock(side_effect=_make_non_json_error())
        mock_get.return_value = _as_ctx(response)

        client = HathorCoreAsyncClient("http://test.node")
        with patch.object(client, "log") as mock_log:
            result = await client.get("/v1a/missing")

        assert result == {"error": "status 404"}
        response.json.assert_not_called()
        mock_sleep.assert_not_called()
        mock_log.warning.assert_called_once_with(
            "hathor_core_error",
            path="/v1a/missing",
            status=404,
            body="Not Found",
        )

    @patch("aiohttp.ClientSession.get")
    @patch("gateways.clients.hathor_core_client.asyncio.sleep", new_callable=AsyncMock)
    async def test_get_5xx_non_json_body_returns_error_after_retries(
        self, mock_sleep, mock_get
    ):
        """Retryable 5xx error bodies must not be parsed as JSON after retries."""
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

        assert result == {"error": "status 502"}
        for response_ctx in responses:
            response_ctx.__aenter__.return_value.json.assert_not_called()
        assert mock_sleep.call_count == HathorCoreAsyncClient.MAX_RETRIES
        mock_log.warning.assert_called_once_with(
            "hathor_core_error",
            path="/v1a/status",
            status=502,
            body=retry_body,
        )

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
