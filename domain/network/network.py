from dataclasses import asdict, dataclass
from typing import List, Set

from dacite import Config, from_dict

from domain.network.node import Node, NodeState, Peer


@dataclass
class AggregatedPeer:
    """Aggregated data of a Peer retrieved by requesting a Node

    :param id: id of peer
    :type id: str

    :param app_version: version of hathor-core running on peer
    :type app_version: str

    :param uptime: time of activity
    :type uptime: float

    :param address: ip address of peer
    :type address: str

    :param state: state of peer
    :type state: :py:class:`domain.network.node.NodeState`

    :param last_message: timestamp of last message
    :type last_message: int

    :param latest_timestamp: latest timestamp
    :type latest_timestamp: int

    :param sync_timestamp: timestamp of last sychronized block
    :type sync_timestamp: int

    :param warning_flags: list of warning flags, if any
    :type warning_flags: List[str]

    :param entrypoints: list entrypoints, if any
    :type entrypoints: List[str]

    :param connected_to: list of ids of nodes that peer is conected to
    :type connected_to: Set[str]

    """
    id: str
    app_version: str
    uptime: float
    address: str
    state: NodeState
    last_message: int
    latest_timestamp: int
    sync_timestamp: int
    warning_flags: List[str]
    entrypoints: List[str]
    connected_to: Set[str]

    @classmethod
    def from_peer(cls, peer: Peer) -> 'AggregatedPeer':
        """Create an AggregatedPeer from a Peer

        :param peer: Peer instance
        :type peer: :py:class:`domain.network.node.Peer`

        :return: AggregatedPeer instance
        :rtype: :py:class:`domain.network.network.AggregatedPeer`
        """
        return cls(
            id=peer.id,
            app_version=peer.app_version,
            uptime=peer.uptime,
            address=peer.address,
            state=peer.state,
            last_message=int(peer.last_message),
            latest_timestamp=peer.latest_timestamp,
            sync_timestamp=peer.sync_timestamp,
            warning_flags=peer.warning_flags,
            entrypoints=peer.entrypoints,
            connected_to=set()
        )

    def to_dict(self) -> dict:
        """ Convert a AggregatedPeer instance into dict

        :return: The dict representation of the AggregatedPeer
        :rtype: dict
        """
        obj = asdict(self)
        obj['connected_to'] = list(obj['connected_to'])
        return obj

    def add_connected_to(self, node_id: str) -> None:
        """Add id of a node that peer is connected to list of connected nodes

        :param node_id: id of the node
        :type node_id: str
        """
        self.connected_to.add(node_id)


@dataclass
class AggregatedNode:
    """Aggregated data of a Node retrived by requesting a full-node

    :param id: id of Node
    :type id: str

    :param app_version: version of hathor-core running on node
    :type app_version: str

    :param uptime: time of activity
    :type uptime: float

    :param state: state of node
    :type state: :py:class:`domain.network.node.NodeState`

    :param latest_timestamp: latest timestamp
    :type latest_timestamp: int

    :param entrypoints: list of entrypoints if any
    :type entrypoints: List[str]

    :param connected_peers: list of connected peers
    :type connected_peers: List[str]

    """
    id: str
    app_version: str
    uptime: float
    state: NodeState
    latest_timestamp: int
    entrypoints: List[str]
    connected_peers: List[str]

    @classmethod
    def from_node(cls, node: Node) -> 'AggregatedNode':
        """Create an AggregatedNode from a Node

        :param peer: Node instance
        :type peer: :py:class:`domain.network.node.Node`

        :return: AggregatedNode instance
        :rtype: :py:class:`domain.network.network.AggregatedNode`
        """
        return cls(
            id=node.id,
            app_version=node.app_version,
            uptime=node.uptime,
            state=node.state,
            latest_timestamp=node.latest_timestamp,
            entrypoints=node.entrypoints,
            connected_peers=[peer.id for peer in node.connected_peers]
        )

    def to_dict(self) -> dict:
        """ Convert a AggregatedNode instance into dict

        :return: The dict representation of the AggregatedNode
        :rtype: dict
        """
        return asdict(self)


@dataclass
class Network:
    """Aggregated Network data

    :param nodes: List of network nodes
    :type nodes: List[:py:class:`domain.network.network.AggregatedNode`]

    :param peers: List of network peers
    :type peers: List[:py:class:`domain.network.network.AggregatedPeer`]
    """
    nodes: List[AggregatedNode]
    peers: List[AggregatedPeer]

    def to_dict(self) -> dict:
        """ Convert a Network instance into dict

        :return: The dict representation of the Network
        :rtype: dict
        """
        return {
            'nodes': [node.to_dict() for node in self.nodes],
            'peers': [peer.to_dict() for peer in self.peers],
        }

    @classmethod
    def from_dict(cls, dikt: dict) -> 'Network':
        return from_dict(
            data_class=cls,
            data=dikt,
            config=Config(
                type_hooks={Set[str]: set},
                cast=[NodeState],
            ),
        )
