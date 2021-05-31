import fakeredis
from gateways.cache.cache_client import CacheClient
from pytest import fixture


class TestCacheClient:

    @fixture
    def cache_client(self):
        client = CacheClient()
        client.client = fakeredis.FakeStrictRedis()
        return client

    def test_set(self, cache_client):
        assert cache_client.set('jedis', 'obi-wan', {'surname': 'kenobi'})

    def test_get(self, cache_client):
        cache_client.set('lightsaber-owners', 'purple', {'name': 'Mace Windu'})

        assert cache_client.get('lightsaber-owners', 'purple') == {'name': 'Mace Windu'}
        assert cache_client.get('lightsaber-owners', 'green') is None
        assert cache_client.get('lightsaber', 'purple') is None

    def test_keys(self, cache_client):
        cache_client.set('spaceships', 'millenium-falcon', {'owner': 'Han Solo'})
        cache_client.set('spaceships', 'deathstar', {'owner': 'Darth Vader'})
        cache_client.set('spaceships', 'x-wing', {'owner': 'Alliance'})
        cache_client.set('darth-vader-children', 'luke', {'surname': 'skywalker'})
        cache_client.set('darth-vader-children', 'leia', {'surname': 'organa'})

        expected_spaceships_keys = ['millenium-falcon', 'deathstar', 'x-wing']
        expected_vader_chidren_keys = ['luke', 'leia']

        assert cache_client.keys('spaceships') == expected_spaceships_keys
        assert cache_client.keys('darth-vader-children') == expected_vader_chidren_keys
        assert cache_client.keys('crash-sound') == []
