from typing import Optional

from elasticsearch import exceptions

from common.errors import ApiError
from common.logging import get_logger
from gateways.block_api_gateway import BlockApiGateway

logger = get_logger()


class BlockApi:
    def __init__(self, block_api_gateway: Optional[BlockApiGateway] = None) -> Optional[None]:
        self.block_api_gateway = block_api_gateway or BlockApiGateway()

    def get_best_chain_height(self) -> dict:
        try:
            return self.block_api_gateway.get_best_chain_height()
        except exceptions.RequestError:
            logger.error('ElasticSearch request error')
            raise ApiError('invalid_parameters')
        except exceptions.AuthorizationException:
            logger.error('ElasticSearch authorization error')
            raise ApiError('not_authorized')
        except (exceptions.TransportError, KeyError):
            logger.error('ElasticSearch transport error')
            raise ApiError('internal_error')
