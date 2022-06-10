from typing import Optional

from elasticsearch import exceptions

from gateways.block_api_gateway import BlockApiGateway


class BlockApi:
    def __init__(self, block_api_gateway: Optional[BlockApiGateway] = None) -> Optional[None]:
        self.block_api_gateway = block_api_gateway or BlockApiGateway()

    def get_best_chain_height(self) -> dict:
        try:
            return self.block_api_gateway.get_best_chain_height()
        except exceptions.RequestError:
            return {'error': 'bad_request', 'status': 400}
        except exceptions.AuthorizationException:
            return {'error': 'not_authorized', 'status': 403}
        except exceptions.TransportError:
            return {'error': 'elasticsearch_transport_error',  'status': 500}
        except KeyError:
            return {'error': 'elasticsearch_document_missing_information',  'status': 500}
