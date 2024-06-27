from enum import Enum
from typing import Any

from decouple import Csv, config


class Environment(Enum):
    PROD = "PROD"
    DEV = "DEV"
    TEST = "TEST"

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
    def default(cls) -> "Environment":
        return cls.DEV


class LogRenderer(Enum):
    JSON = "json"
    CONSOLE = "console"

    @property
    def renderer_class(self) -> Any:
        import structlog

        class_mapping = {
            "json": structlog.processors.JSONRenderer,
            "console": structlog.dev.ConsoleRenderer,
        }
        return class_mapping[self.value]

    @classmethod
    def default(cls) -> "LogRenderer":
        return cls.JSON


ENVIRONMENT = Environment(
    config("ENVIRONMENT", default=Environment.default().value).upper()
)

API_PORT = config("API_PORT", default=None)

LAMBDA_INVOKE_URL = config("LAMBDA_INVOKE_URL", default=None)
S3_ENDPOINT = config("S3_ENDPOINT", default=None)

DATA_AGGREGATOR_LAMBDA_NAME = config("DATA_AGGREGATOR_LAMBDA_NAME", default=None)

HATHOR_CORE_URL = config("HATHOR_CORE_URL", default=None)

HATHOR_NODES = config("HATHOR_NODES", default="", cast=Csv())
NODE_CACHE_TTL = config("NODE_CACHE_TTL", default=30)

REDIS_KEY_PREFIX = config("REDIS_KEY_PREFIX", default=None)
REDIS_HOST = config("REDIS_HOST", default=None)
REDIS_PORT = config("REDIS_PORT", default=None)
REDIS_DB = config("REDIS_DB", default="0", cast=int)
REDIS_TIMEOUT = config("REDIS_TIMEOUT", default="2", cast=int)

METADATA_BUCKET = config("METADATA_BUCKET", default=None)

CORS_ALLOWED_REGEX = config(
    "CORS_ALLOWED_REGEX", default=r"https?://([a-z0-9]*\.){0,5}hathor\.network"
)

LOG_RENDERER = LogRenderer(config("LOG_RENDERER", default=LogRenderer.default().value))

ELASTIC_CLOUD_ID = config("ELASTIC_CLOUD_ID", default=None)
ELASTIC_USER = config("ELASTIC_USER", default=None)
ELASTIC_PASSWORD = config("ELASTIC_PASSWORD", default=None)
ELASTIC_RESULTS_PER_PAGE = config("ELASTIC_RESULTS_PER_PAGE", default=10)
ELASTIC_SEARCH_TIMEOUT = config("ELASTIC_SEARCH_TIMEOUT", default=25)

ELASTIC_INDEX = config("ELASTIC_INDEX", default=None)
ELASTIC_TOKEN_BALANCES_INDEX = config("ELASTIC_TOKEN_BALANCES_INDEX", default=None)
ELASTIC_TX_INDEX = config("ELASTIC_TX_INDEX", default=None)

WALLET_SERVICE_DB_USERNAME = config("WALLET_SERVICE_DB_USERNAME", default=None)
WALLET_SERVICE_DB_PASSWORD = config("WALLET_SERVICE_DB_PASSWORD", default=None)
WALLET_SERVICE_DB_HOST = config("WALLET_SERVICE_DB_HOST", default=None)
WALLET_SERVICE_DB_NAME = config("WALLET_SERVICE_DB_NAME", default=None)

# Daemon Healthcheck
# This ping functionality will be used by the data collector daemon to send pings to a health monitor service
HEALTHCHECK_PING_ENABLED = config("HEALTHCHECK_PING_ENABLED", default=False, cast=bool)
HEALTHCHECK_PING_INTERVAL = config("HEALTHCHECK_PING_INTERVAL", default=30, cast=int)
HEALTHCHECK_SERVICE_API_KEY = config("HEALTHCHECK_SERVICE_API_KEY", default="")
HEALTHCHECK_DATA_COLLECTOR_URL = config("HEALTHCHECK_DATA_COLLECTOR_URL", default=None)

# API Healthcheck
HEALTHCHECK_HATHOR_CORE_ENABLED = config(
    "HEALTHCHECK_HATHOR_CORE_ENABLED", default=True, cast=bool
)
HEALTHCHECK_WALLET_SERVICE_DB_ENABLED = config(
    "HEALTHCHECK_WALLET_SERVICE_DB_ENABLED", default=False, cast=bool
)
HEALTHCHECK_ELASTICSEARCH_ENABLED = config(
    "HEALTHCHECK_ELASTICSEARCH_ENABLED", default=False, cast=bool
)
HEALTHCHECK_REDIS_ENABLED = config(
    "HEALTHCHECK_REDIS_ENABLED", default=False, cast=bool
)
