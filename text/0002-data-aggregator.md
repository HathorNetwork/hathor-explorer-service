- Feature Name: data_collector
- Start Date: 2021-07-05
- RFC PR: (leave this empty)
- Hathor Issue: (leave this empty)
- Author: Giovane Costa <gigio.coder@gmail.com>

# Summary
[summary]: #summary

Data aggregator will aggregate all network data from Redis, check if something changed and update if necessary.

# Motivation
[motivation]: #motivation

We want to have an overview of all the hathor network. Today we have only a single node point of view. 

# Guide-level explanation
[guide-level-explanation]: #guide-level-explanation

Data aggregator will get data collected by `data-collector`, aggregate them into a Network dataclass, compare with saved data and save it if different.

# Reference-level explanation
[reference-level-explanation]: #reference-level-explanation

Three new dataclasses will be created: `AggregatedNode`, `AggregatedPeer` and `Network`.

- `AggregatedNode` and `AggregatedPeer` will be a bit smaller version of `Node` and `Peer` respectively, having `up_since` as the main change.
  As `uptime` is always changing as time goes by, `up_since` remains the same. 
  Also, `up_since` is an integer to avoid problems with microseconds calculations (`/v1a/status` returns only `uptime` and we have to calculate everytime).
- `AggregatedPeer` also have a list of nodes that it is connected to.
- `Network` have the list of `AggregatedNode` and `AggregatedPeer`

`AggregateNodeData` usecase is called along with `SaveNodeData` inside `aggregate_node_handler`.

`Network` is saved into Redis under the following key:

> `'hathor-explorer-service.network.v1'`

**Endpoint:**

GET `/network`

`network-handler` return current network stored in Redis

```
{
  nodes: [AggregatedNode, ...],
  peers: [AggregatedPeer, ...]
}
```

# Drawbacks
[drawbacks]: #drawbacks

Polling is still bad specially with data that will not be modified constantly. However, WebSocket is intended to be implemented soon.

# Rationale and alternatives
[rationale-and-alternatives]: #rationale-and-alternatives

We could do the aggregation on client side. However, more requests must be made every second, or always return everyhthing.

The disadvantage of this approach is that we must keep polling. 

# Unresolved questions
[unresolved-questions]: #unresolved-questions

- Nodes are still manually setted by us. It would be good to discover new http responding nodes automatically as they join the network.

# Future possibilities
[future-possibilities]: #future-possibilities

WebSocket. Everytime `Network` have new content and is saved, a handler can be triggered to broadcast new data to connected clients.
