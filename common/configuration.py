from enum import Enum
from decouple import config, Csv


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


ENVIRONMENT = Environment(config('ENVIRONMENT', default=Environment.default().value).upper())

API_PORT = config('API_PORT', default=None)

LAMBDA_INVOKE_URL = config('LAMBDA_INVOKE_URL', default=None)

DATA_AGGREGATOR_LAMBDA_NAME = config('DATA_AGGREGATOR_LAMBDA_NAME', default=None)

HATHOR_CORE_DOMAIN = config('HATHOR_CORE_DOMAIN', default=None)

HATHOR_NODES = config('HATHOR_NODES', default='', cast=Csv())

REDIS_KEY_PREFIX = config('REDIS_KEY_PREFIX', default=None)
REDIS_HOST = config('REDIS_HOST', default=None)
REDIS_PORT = config('REDIS_PORT', default=None)
REDIS_DB = config('REDIS_DB', default='0', cast=int)
