- Feature Name: data_collector
- Start Date: 2021-05-11
- RFC PR: (leave this empty)
- Hathor Issue: (leave this empty)
- Author: Giovane Costa <gigio.coder@gmail.com>

# Summary
[summary]: #summary

Data ccollector will make polling and connect to `full-node` in order to send messages to SNS's with updates

# Motivation
[motivation]: #motivation

Explorer needs these updates and lambdas can't stay connected to a WebSocket. Also we can't modify the `full-node` to send message to SNS. 

# Guide-level explanation
[guide-level-explanation]: #guide-level-explanation

![image](https://user-images.githubusercontent.com/698586/117846564-f0fddd00-b257-11eb-869f-38b2f3d6a6b9.png)

Data collector will get data from `full-node` by the following ways

**WebSocket:**

- `/v1a/ws` - Listen to the following events:
    - `'dashboard:metrics'` - for statistics
    - `'network:new_tx_accepted'` - for transactions an DAG

**Polling:**

- `/v1a/status` - Fetch Network information 

Every update will be sent to respective SNS.


# Reference-level explanation
[reference-level-explanation]: #reference-level-explanation


**Messages from `hathor-core`:**


```

```


```
Network {
    id: string
    uptime: int // in seconds
    version: string
    latest_timestamp: timestamp // (ISO 8601)
    peers: [
        {
            id: string
            uptime: int // in seconds
            version: string
            address: string
            entrypoints: string
            state: string
            sync_timestamp: timestamp // (ISO 8601)
            latest_timestamp: timestamp // (ISO 8601)
        },
        ...
    ]
    timestamp: timestamp // (ISO 8601)
}
```

This is the technical portion of the RFC. Explain the design in sufficient
detail that:

- Its interaction with other features is clear.
- It is reasonably clear how the feature would be implemented.
- Corner cases are dissected by example.

The section should return to the examples given in the previous section, and
explain more fully how the detailed proposal makes those examples work.

# Drawbacks
[drawbacks]: #drawbacks

Why should we *not* do this?

# Rationale and alternatives
[rationale-and-alternatives]: #rationale-and-alternatives

- Why is this design the best in the space of possible designs?
- What other designs have been considered and what is the rationale for not
  choosing them?
- What is the impact of not doing this?

# Prior art
[prior-art]: #prior-art

Discuss prior art, both the good and the bad, in relation to this proposal.
A few examples of what this can include are:

- For protocol, network, algorithms and other changes that directly affect the
  code: Does this feature exist in other blockchains and what experience have
  their community had?
- For community proposals: Is this done by some other community and what were
  their experiences with it?
- For other teams: What lessons can we learn from what other communities have
  done here?
- Papers: Are there any published papers or great posts that discuss this? If
  you have some relevant papers to refer to, this can serve as a more detailed
  theoretical background.

This section is intended to encourage you as an author to think about the
lessons from other blockchains, provide readers of your RFC with a fuller
picture. If there is no prior art, that is fine - your ideas are interesting to
us whether they are brand new or if it is an adaptation from other blockchains.

Note that while precedent set by other blockchains is some motivation, it does
not on its own motivate an RFC. Please also take into consideration that Hathor
sometimes intentionally diverges from common blockchain features.

# Unresolved questions
[unresolved-questions]: #unresolved-questions

- What parts of the design do you expect to resolve through the RFC process
  before this gets merged?
- What parts of the design do you expect to resolve through the implementation
  of this feature before stabilization?
- What related issues do you consider out of scope for this RFC that could be
  addressed in the future independently of the solution that comes out of this
  RFC?

# Future possibilities
[future-possibilities]: #future-possibilities

Think about what the natural extension and evolution of your proposal would be
and how it would affect the network and project as a whole in a holistic way.
Try to use this section as a tool to more fully consider all possible
interactions with the project and network in your proposal. Also consider how
this all fits into the roadmap for the project and of the relevant sub-team.

This is also a good place to "dump ideas", if they are out of scope for the
RFC you are writing but otherwise related.

If you have tried and cannot think of any future possibilities,
you may simply state that you cannot think of anything.

Note that having something written down in the future-possibilities section
is not a reason to accept the current or a future RFC; such notes should be
in the section on motivation or rationale in this or subsequent RFCs.
The section merely provides additional information.
