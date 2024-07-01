import json
from unittest.mock import patch

import requests
from pytest import raises

from gateways.clients.hathor_core_client import HathorCoreClient


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
