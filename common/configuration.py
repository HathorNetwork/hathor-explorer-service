from enum import Enum

from decouple import Csv, config


class Environment(Enum):
    """List of possible environments"""

    PROD = 'PROD'
    DEV = 'DEV'
    TEST = 'TEST'

    @property
    def is_prod(self) -> bool:
        """Check if current value is prod

        :return: if is prod or not
        :rtype: bool
        """
        return self is self.PROD

    @property
    def is_dev(self) -> bool:
        """Check if current value is dev

        :return: if is dev or not
        :rtype: bool
        """
        return self is self.DEV

    @property
    def is_test(self) -> bool:
        """Check if current value is test

        :return: if is test or not
        :rtype: bool
        """
        return self is self.TEST

    @classmethod
    def default(cls) -> 'Environment':
        """Return default environment

        :return: dev environment
        :rtype: :py:class:`common.configuration.Environment`
        """
        return cls.DEV


ENVIRONMENT = Environment(config('ENVIRONMENT', default=Environment.default().value).upper())

API_PORT = config('API_PORT', default=None)

LAMBDA_INVOKE_URL = config('LAMBDA_INVOKE_URL', default=None)
S3_ENDPOINT = config('S3_ENDPOINT', default=None)

DATA_AGGREGATOR_LAMBDA_NAME = config('DATA_AGGREGATOR_LAMBDA_NAME', default=None)

HATHOR_CORE_DOMAIN = config('HATHOR_CORE_DOMAIN', default=None)

HATHOR_NODES = config('HATHOR_NODES', default='', cast=Csv())

REDIS_KEY_PREFIX = config('REDIS_KEY_PREFIX', default=None)
REDIS_HOST = config('REDIS_HOST', default=None)
REDIS_PORT = config('REDIS_PORT', default=None)
REDIS_DB = config('REDIS_DB', default='0', cast=int)

TOKEN_METADATA_BUCKET = config('TOKEN_METADATA_BUCKET', default=None)

CORS_ALLOWED_ORIGIN = config('CORS_ALLOWED_ORIGIN', default=None)
