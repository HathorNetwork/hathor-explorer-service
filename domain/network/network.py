from dataclasses import asdict, dataclass
from typing import List
from datetime import datetime, timedelta
from dacite import from_dict

from domain.network.node import NodeState, Peer, Node


def uptime_to_up_since(uptime: float) -> int:
    up_since_date = datetime.now() - timedelta(seconds=uptime)
    return int(datetime.timestamp(up_since_date))


@dataclass
class AggregatedPeer:
    id: str
    app_version: str
    up_since: int
    address: str
    state: NodeState
    last_message: int
    latest_timestamp: int
    sync_timestamp: int
    warning_flags: List[str]
    entrypoints: List[str]
    connected_to: List[str]

    @classmethod
    def from_peer(cls, peer: Peer) -> 'AggregatedPeer':
        return cls(
            id=peer.id,
            app_version=peer.app_version,
            up_since=uptime_to_up_since(peer.uptime),
            address=peer.address,
            state=peer.state,
            last_message=int(peer.last_message),
            latest_timestamp=peer.latest_timestamp,
            sync_timestamp=peer.sync_timestamp,
            warning_flags=peer.warning_flags,
            entrypoints=[],  # TODO: add when Peer entrypoints is fixed HathorNetwork/hathor-explorer-service#28
            connected_to=[]
        )

    def to_dict(self) -> dict:
        """ Convert a AggregatedPeer instance into dict

        :return: The dict representation of the AggregatedPeer
        :rtype: dict
        """
        return asdict(self)

    def add_connected_to(self, node_id: str) -> None:
        self.connected_to.append(node_id)

    def remove_connected_to(self, node_id: str) -> None:
        self.connected_to.remove(node_id)


@dataclass
class AggregatedNode:
    id: str
    app_version: str
    up_since: int
    state: NodeState
    latest_timestamp: int
    entrypoints: List[str]
    connected_peers: List[str]

    @classmethod
    def from_node(cls, node: Node) -> 'AggregatedNode':
        return cls(
            id=node.id,
            app_version=node.app_version,
            up_since=uptime_to_up_since(node.uptime),
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
    nodes: List[AggregatedNode]
    peers: List[AggregatedPeer]

    def to_dict(self) -> dict:
        """ Convert a Network instance into dict

        :return: The dict representation of the Network
        :rtype: dict
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, dikt: dict) -> 'Network':
        return from_dict(data_class=cls, data=dikt)
