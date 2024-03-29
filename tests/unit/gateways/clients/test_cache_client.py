from unittest.mock import MagicMock

import fakeredis
import pytest
from pytest import fixture

from gateways.clients.cache_client import CacheClient


class TestCacheClient:
    @fixture
    def cache_client(self):
        client = CacheClient()
        client.client = fakeredis.FakeStrictRedis()
        return client

    def test_set(self, cache_client):
        assert cache_client.set("jedis", "obi-wan", {"surname": "kenobi"})

    def test_get(self, cache_client):
        cache_client.set("lightsaber-owners", "purple", {"name": "Mace Windu"})

        assert cache_client.get("lightsaber-owners", "purple") == {"name": "Mace Windu"}
        assert cache_client.get("lightsaber-owners", "green") is None
        assert cache_client.get("lightsaber", "purple") is None

    def test_keys(self, cache_client):
        cache_client.set("planet", "tatooine", {"where": "Middle of nowhere"})
        cache_client.set("planet-system", "kamino", {"where": "Not in archives"})

        cache_client.set("spaceships", "millenium-falcon", {"owner": "Han Solo"})
        cache_client.set("spaceships", "deathstar", {"owner": "Darth Vader"})
        cache_client.set("spaceships", "x-wing", {"owner": "Alliance"})
        cache_client.set("darth-vader-children", "luke", {"surname": "skywalker"})
        cache_client.set("darth-vader-children", "leia", {"surname": "organa"})

        expected_planet_keys = ["tatooine"]
        expected_spaceships_keys = ["millenium-falcon", "deathstar", "x-wing"]
        expected_vader_chidren_keys = ["luke", "leia"]

        assert sorted(cache_client.keys("planet")) == sorted(expected_planet_keys)
        assert sorted(cache_client.keys("spaceships")) == sorted(
            expected_spaceships_keys
        )
        assert sorted(cache_client.keys("darth-vader-children")) == sorted(
            expected_vader_chidren_keys
        )
        assert sorted(cache_client.keys("crash-sound")) == []

    def test_ping(self, cache_client):
        assert cache_client.ping()

    def test_ping_exception(self):
        client = CacheClient()
        client.client = MagicMock()

        client.client.ping.side_effect = Exception("Redis is down")

        with pytest.raises(Exception) as e:
            client.ping()
