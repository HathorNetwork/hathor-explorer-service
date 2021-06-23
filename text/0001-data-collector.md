- Feature Name: data_collector
- Start Date: 2021-05-11
- RFC PR: (leave this empty)
- Hathor Issue: (leave this empty)
- Author: Giovane Costa <gigio.coder@gmail.com>

# Summary
[summary]: #summary

Data collector will make polling to `full-node` in order to store network data into Redis cache.

# Motivation
[motivation]: #motivation

In order to reduce `full-node` overloads, instead of have each open explorer app polling, we create a daemon that will alone make the polling, reducing it to 1 req/s no matter how much explorer Apps are open. 

# Guide-level explanation
[guide-level-explanation]: #guide-level-explanation

![image](https://raw.githubusercontent.com/HathorNetwork/hathor-explorer-service/main/text/img/data-collector.png)

Data collector will get data from `full-node` by the following way

**Polling:**

- `/v1a/status` - Fetch Network information 

Every response will be sent to `network-data-aggregator` that will save it on Redis.


# Reference-level explanation
[reference-level-explanation]: #reference-level-explanation

`data_collector.py` run inside a Docker container, polling asychronously a fixed list of nodes each second. The endpoint to be polled is 

> GET `/v1a/status`

For each request, part of the response is sent to `network-data-aggregator`:

**Response from `hathor-core`:**
```
{
  "server": {
    "id": string,
    "app_version": string,
    "state": string,
    "network": string,
    "uptime": float,
    "entrypoints": [string, ...]
  },
  "peers_whitelist": [string, ...],
  "known_peers": [
    {
      "id": string,
      "entrypoints": [string, ...],
      "flags": [string, ...]
    },
    ...
  ],
  "connections": {
    "connected_peers": [
      {
        "id": string,
        "app_version": string,
        "uptime": float,
        "address": string,
        "state": string,
        "last_message": float,
        "plugins": {
          "node-sync-timestamp": {
            "latest_timestamp": int,
            "synced_timestamp": int
          }
        },
        "warning_flags": [ string, ...]
      },
      ...
    ],
    "handshaking_peers": [],
    "connecting_peers": [
      {
        "deferred": string,
        "address": string
      },
      ...
    ]
  },
  "dag": {
    "first_timestamp": int,
    "latest_timestamp": int
  }
}
```

**Data sent to `network-data-aggregator`:**
```
{
  "server": {
    "id": string,
    "app_version": string,
    "state": string,
    "network": string,
    "uptime": float,
    "entrypoints": [string, ...]
  },
  "known_peers": [string, ...],
  "connected_peers": [
    {
      "id": string,
      "app_version": string,
      "uptime": float,
      "address": string,
      "state": string,
      "last_message": float,
      "latest_timestamp": int,
      "sync_timestamp": int
      "warning_flags": [ string, ...]
    },
    ...
  ]
}
```

`network-data-aggregator` then saves it into Redis under the following keys:

> `'hathor-explorer-service.network.${server.id}'`

**Endpoint:**

GET `/v1a/network/`

`network-handler` return a list of available nodes PoV (Redis keys)

```
[string, ...]
```

**Endpoint:**

GET `/v1a/network/:hash`

`network-handler` fecth data of given node from Redis and return 

```
{
  "server": {
    "id": string,
    "app_version": string,
    "state": string,
    "network": string,
    "uptime": float,
    "entrypoints": [string, ...]
  },
  "known_peers": [string, ...],
  "connected_peers": [
    {
      "id": string,
      "app_version": string,
      "uptime": float,
      "address": string,
      "state": string,
      "last_message": float,
      "latest_timestamp": int,
      "sync_timestamp": int
      "warning_flags": [ string, ...]
    },
    ...
  ]
}

```

*Note:* If a invalid hash is sent, 404 is returned.

# Drawbacks
[drawbacks]: #drawbacks

Polling is still bad specially with data that will not be modified constantly. However, WebSocket is intended to be implemented soon.

# Rationale and alternatives
[rationale-and-alternatives]: #rationale-and-alternatives

This design is the best for the moment when we want things working as soon as possible. Although WebSocket solution is a more elegant one, it takes more effort to build and the benefits for `full-node` are the same.

# Unresolved questions
[unresolved-questions]: #unresolved-questions

- `network-data-aggregator` still just save the data received. It would be good to make some checks to avoid saving data that is the same already saved.

# Future possibilities
[future-possibilities]: #future-possibilities

WebSocket. `network-data-aggregator` will check if network data received is new, and trigger handler to broadcast new data to connected clients.