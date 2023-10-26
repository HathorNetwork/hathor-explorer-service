import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from utils.healthcheck.healthcheck_ping_manager import HealthcheckPingManager


@patch(
    "utils.healthcheck.healthcheck_ping_manager.HEALTHCHECK_PING_ENABLED",
    True,
)
class TestHealthcheckPingManager(unittest.IsolatedAsyncioTestCase):
    @patch("aiohttp.ClientSession.post")
    async def test_send_post(self, mock_post):
        ping_manager = HealthcheckPingManager()

        mock_response = MagicMock()
        mock_response.status = 200
        mock_post.return_value.__aenter__.return_value = mock_response

        await ping_manager._send_post("http://test.com")

        mock_post.assert_called_once()

    @patch("aiohttp.ClientSession.post")
    async def test_send_post_server_error(self, mock_post):
        ping_manager = HealthcheckPingManager()

        mock_response = MagicMock()
        mock_response.status = 500
        mock_post.return_value.__aenter__.return_value = mock_response

        # Shouldn't raise any exception
        await ping_manager._send_post("http://test.com")

        mock_post.assert_called_once()

    @patch("aiohttp.ClientSession.post")
    async def test_send_post_network_error(self, mock_post):
        ping_manager = HealthcheckPingManager()

        mock_post.side_effect = Exception("test")

        # Shouldn't raise any exception
        await ping_manager._send_post("http://test.com")

        mock_post.assert_called_once()

    @patch(
        "utils.healthcheck.healthcheck_ping_manager.HEALTHCHECK_DATA_COLLECTOR_URL",
        "http://test.com",
    )
    @patch(
        "utils.healthcheck.healthcheck_ping_manager.HealthcheckPingManager._send_post"
    )
    async def test_send_ping(self, mock_send_post):
        ping_manager = HealthcheckPingManager()
        ping_manager.targets["data_collector"][
            "latest_ping"
        ] = datetime.now() - timedelta(minutes=10)

        await ping_manager.send_ping("data_collector")

        mock_send_post.assert_called_once_with("http://test.com")

    @patch(
        "utils.healthcheck.healthcheck_ping_manager.HealthcheckPingManager._send_post"
    )
    async def test_send_ping_disabled(self, mock_send_post):
        with patch(
            "utils.healthcheck.healthcheck_ping_manager.HEALTHCHECK_PING_ENABLED", False
        ):
            ping_manager = HealthcheckPingManager()
            await ping_manager.send_ping("data_collector")

            mock_send_post.assert_not_called()

    async def test_send_ping_invalid_target(self):
        ping_manager = HealthcheckPingManager()

        with self.assertRaises(ValueError):
            await ping_manager.send_ping("invalid_target")


if __name__ == "__main__":
    unittest.main()
