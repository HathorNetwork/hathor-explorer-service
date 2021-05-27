from dataclasses import asdict, dataclass
from enum import Enum
from typing import List


class NodeState(str, Enum):
    # Node is still initializing
    INITIALIZING = 'INITIALIZING'

    # Node is ready to establish new connections, sync, and exchange transactions.
    READY = 'READY'


@dataclass
class Peer:
    id: str
    app_version: str
    uptime: float
    address: str
    state: NodeState
    last_message: float
    latest_timestamp: int
    sync_timestamp: int
    warning_flags: List[str]


@dataclass
class Network:
    """ Network information of a given node

    :param id: Node id hash
    :type id: str

    :param app_version: The current version of app running on node
    :type app_version: str

    :param state: Current state of the node
    :type state: :py:class:`domain.network.network.NodeState`

    :param network: Current network. Can be `mainnet`, any version of `testnet` or other
    :type network: str

    :param uptime: Time of node activity in seconds
    :type uptime: float

    :param first_timestamp: Timestamp of the first block of the node
    :type first_timestamp: int

    :param latest_timestamp: Timestamp of the latest block of the node
    :type latest_timestamp: int

    :param entrypoints: List of node entrypoints
    :type entrypoints: List[str]

    :param known_peers: List of ids of peers known by the node
    :type known_peers: List[str]

    :param connected_peers: List of peers connected with the node
    :type connected_peers: List[Peer]

    """
    id: str
    app_version: str
    state: NodeState
    network: str
    uptime: float
    first_timestamp: int
    latest_timestamp: int
    entrypoints: List[str]
    known_peers: List[str]
    connected_peers: List[Peer]

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, dikt: dict) -> 'Network':
        dikt['state'] = NodeState(dikt['state'])

        connected_peers = []

        for peer in dikt['connected_peers']:
            peer['state'] = NodeState(peer['state'])
            connected_peers.append(Peer(**peer))

        dikt['connected_peers'] = connected_peers

        return Network(**dikt)

    @classmethod
    def from_status_dict(cls, status: dict) -> 'Network':
        """Convenience method to parse response to domain object

        :return: A new Network class built from status data
        :rtype: Network
        """
        known_peers = [peer['id'] for peer in status['known_peers']]

        connected_peers = []

        for peer in status['connections']['connected_peers']:
            connected_peers.append(Peer(
                id=peer['id'],
                app_version=peer['app_version'],
                uptime=peer['uptime'],
                address=peer['address'],
                state=NodeState(peer['state']),
                last_message=peer['last_message'],
                latest_timestamp=peer['plugins']['node-sync-timestamp']['latest_timestamp'],
                sync_timestamp=peer['plugins']['node-sync-timestamp']['synced_timestamp'],
                warning_flags=peer['warning_flags']
            ))

        return cls(
            id=status['server']['id'],
            app_version=status['server']['app_version'],
            state=NodeState(status['server']['state']),
            network=status['server']['network'],
            uptime=status['server']['uptime'],
            first_timestamp=status['dag']['first_timestamp'],
            latest_timestamp=status['dag']['latest_timestamp'],
            entrypoints=status['server']['entrypoints'],
            known_peers=known_peers,
            connected_peers=connected_peers
        )
