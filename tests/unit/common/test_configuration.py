import os
from unittest import TestCase, mock

from common import config


class TestConfiguration(TestCase):

    @mock.patch.dict(os.environ, {"I_KNOW_KARATE": "show me"})
    def test_get_key_from_env_when_not_in_file(self):
        assert config.get_key('i_know_karate') == 'show_me'
