- Feature Name: data_collector
- Start Date: 2021-07-05
- RFC PR: (leave this empty)
- Hathor Issue: (leave this empty)
- Author:
    - Giovane Costa <gigio.coder@gmail.com>
    - André Carneiro <andre.carneiro@hathor.network>

# Summary
[summary]: #summary

Data aggregator will aggregate all network data from Redis, check if something changed and update if necessary.

# Motivation
[motivation]: #motivation

We want to have an overview of all the hathor network. Today we have only a single node point of view.

# Guide-level explanation
[guide-level-explanation]: #guide-level-explanation

Data aggregator will get data collected by `data-collector`, aggregate them into a Network dataclass, compare with saved data and save it if different.
The aggregated data will be available through a simple HTTP API

## **Endpoint**

Get network data.

GET `/network` return `200`|`404`

### **Success Response**

**Code** 200

**Content**

```js
{
  "nodes": [AggregatedNode, ...],
  "peers": [AggregatedPeer, ...]
}
```

AggregatedNode:

```js
{
  "id": str,
  "app_version": str,
  "uptime": float,
  "state": ("INITIALIZING"|"READY"),
  "latest_timestamp": number,
  "entrypoints": [str],
  "connected_peers": [str]
}
```

Obs: `connected_peers` will be a list of peer id (hence str).

AggregatedPeer:

```js
{
  "id": str,
  "app_version": str,
  "uptime": float,
  "address": str
  "state": ("INITIALIZING"|"READY"),
  "last_message": number,
  "latest_timestamp": number,
  "sync_timestamp": number,
  "warning_flags": [str],
  "entrypoints": [str],
  "connected_to": [str]
}
```

# Reference-level explanation
[reference-level-explanation]: #reference-level-explanation

Three new dataclasses will be created: `AggregatedNode`, `AggregatedPeer` and `Network`.

- `AggregatedNode` and `AggregatedPeer` will be a bit smaller version of `Node` and `Peer` respectively.
- `AggregatedPeer` also have a list of nodes that it is connected to.
- `Network` have the list of `AggregatedNode` and `AggregatedPeer`

`AggregateNodeData` usecase is called along with `SaveNodeData` inside `node_data_aggregator_handler`.

`Network` is saved into Redis under the following key:

> `'hathor-explorer-service.network.v1'`

The data will be exposed through an API described on the [Guide-Level](#guide-level-explanation)

# Drawbacks
[drawbacks]: #drawbacks

Polling is still bad specially with data that will not be modified constantly. However, WebSocket is intended to be implemented soon.

# Rationale and alternatives
[rationale-and-alternatives]: #rationale-and-alternatives

We could do the aggregation on client side. However, more requests must be made every second, or always return everything.

The disadvantage of this approach is that we must keep polling.

# Unresolved questions
[unresolved-questions]: #unresolved-questions

- Nodes are still manually setted by us. It would be good to discover new http responding nodes automatically as they join the network.

# Future possibilities
[future-possibilities]: #future-possibilities

- WebSocket. Everytime `Network` have new content and is saved, a handler can be triggered to broadcast new data to connected clients.
- World map. We can get all peers and nodes locations and show on map.
