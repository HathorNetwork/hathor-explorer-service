import os

from collections import UserDict
from enum import Enum

import yaml
from typing import Union, List


SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
CONFIGURATION_FILE = os.path.join(SRC_DIR, 'configuration.yml')

assert os.path.exists(CONFIGURATION_FILE), f'File {CONFIGURATION_FILE} not found.'


class Environment(Enum):
    PROD = 'PROD'
    DEV = 'DEV'
    TEST = 'TEST'

    @property
    def is_prod(self) -> bool:
        return self is self.PROD

    @property
    def is_dev(self) -> bool:
        return self is self.DEV

    @property
    def is_test(self) -> bool:
        return self is self.TEST

    @classmethod
    def default(cls) -> 'Environment':
        return cls.DEV


class Configuration(UserDict):
    def __init__(self):
        super().__init__()
        with open(CONFIGURATION_FILE, "r") as file:
            data = yaml.safe_load(file)

        self.data = data

    @property
    def environment(self) -> Environment:
        env = os.environ.get("ENVIRONMENT", Environment.default().value)
        return Environment(env.upper())

    @property
    def api_url(self) -> Union[str, None]:
        return self.get_key("api_url")

    @property
    def lambda_invoke_url(self) -> Union[str, None]:
        return self.get_key("lambda_invoke_url")

    @property
    def data_aggregator_lambda_name(self) -> Union[str, None]:
        return self.get_key("data_aggregator_lambda_name")

    @property
    def hathor_core_domain(self) -> Union[str, None]:
        return self.get_key('hathor_core_domain')

    @property
    def hathor_nodes(self) -> List:
        nodes = self.get_key('hathor_nodes')

        if nodes:
            return nodes.split(',')

        return []

    @property
    def redis_key_prefix(self) -> Union[str, None]:
        return self.get_key('redis_key_prefix')

    @property
    def redis_host(self) -> Union[str, None]:
        return self.get_key('redis_host')

    @property
    def redis_port(self) -> Union[int, None]:
        value = self.get_key('redis_port')

        if value:
            return int(value)

        return None

    @property
    def redis_db(self) -> Union[int, None]:
        value = self.get_key('redis_db')

        if value:
            return int(value)

        return None

    def get_key(self, key: str) -> Union[str, None]:
        value = self._find_from_environment(key)
        if value is not None:
            return value

        value = self._find_from_config_file_using_environment_stage(key)

        if value is not None:
            return value

        value = self._find_from_config_file(key)

        if value is not None:
            return value

        print(f"Not found config key: {key}")

        return None

    def _find_from_environment(self, key: str) -> Union[str, None]:
        return os.environ.get(key.upper())

    def _find_from_config_file_using_environment_stage(self, key: str) -> Union[str, None]:
        try:
            return self.data[self.environment.value][key]
        except KeyError:
            return None

    def _find_from_config_file(self, key: str) -> Union[str, None]:
        try:
            return self.data[key]
        except KeyError:
            return None