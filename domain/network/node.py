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
    """ Information about a Peer connected to a node

    :param id: Peer id hash
    :type id: str

    :param app_version: The current version of app running on node
    :type app_version: str

    :param uptime: Time of node activity in seconds
    :type uptime: float

    :param address: Ip address and port of the peer
    :type address: str

    :param state: Current state of the peer
    :type state: :py:class:`domain.network.node.NodeState`

    :param last_message: Time passed since the last message that node received in seconds
    :type last_message: float

    :param latest_timestamp: Timestamp of the latest block of the node
    :type latest_timestamp: int

    :param sync_timestamp: Timestamp of the last synchronized block of the node
    :type sync_timestamp: int

    :param warning_flags: List of node warnings, if any
    :type warning_flags: List[str]

    :param entrypoints: List of entrypoints, if any
    :type entrypoints: List[str]
    """
    id: str
    app_version: str
    uptime: float
    address: str
    state: NodeState
    last_message: float
    latest_timestamp: int
    sync_timestamp: int
    warning_flags: List[str]
    entrypoints: List[str]


@dataclass
class Node:
    """ Node information of a given node

    :param id: Node id hash
    :type id: str

    :param app_version: The current version of app running on node
    :type app_version: str

    :param state: Current state of the node
    :type state: :py:class:`domain.network.node.NodeState`

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

    def to_dict(self) -> dict:
        """ Convert a Node instance into dict

        :return: The dict representation of the Node
        :rtype: dict
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, dikt: dict) -> 'Node':
        """ Creates a new Node instance from a given dict (inverse operation of `to_dict`)

        :param dikt: Dict with Node structure and data
        :type dikt: dict

        :return: The new instance
        :rtype: :py:class:`domain.network.node.Node`
        """
        dikt['state'] = NodeState(dikt['state'])

        connected_peers = []

        for peer in dikt['connected_peers']:
            peer['state'] = NodeState(peer['state'])
            connected_peers.append(Peer(**peer))

        dikt['connected_peers'] = connected_peers

        return Node(**dikt)

    @classmethod
    def from_status_dict(cls, status: dict) -> 'Node':
        """Convenience method to parse response to domain object

        :param dikt: Dict response of a request to node status endpoint
        :type dikt: dict

        :return: A new Node class built from status data
        :rtype: Node
        """
        peer_entrypoints = {peer['id']: peer['entrypoints'] for peer in status['known_peers']}

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
                warning_flags=peer['warning_flags'],
                entrypoints=peer_entrypoints[peer['id']]
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
            known_peers=[id for id in peer_entrypoints.keys()],
            connected_peers=connected_peers
        )
