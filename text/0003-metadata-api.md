- Feature Name: metadata_api
- Start Date: 2021-07-13
- RFC PR: (leave this empty)
- Hathor Issue: (leave this empty)
- Author: Giovane Costa <gigio.coder@gmail.com>

# Summary
[summary]: #summary

Metadata API will provide metadata information about Transactions, Tokens, Blocks and other things on Network.
It will start with Transactions and Tokens

# Motivation
[motivation]: #motivation

We need to have some data to be used on Public Explore and Wallets that can't be stored on the blockchain about
Transactions, Tokens, Blocks and other things on Network. 
So, we store somewhere else and retrieve them through MetadataAPI.
This data can also be used by community as they please.

# Guide-level explanation
[guide-level-explanation]: #guide-level-explanation

Information will be stored in S3 in format `(token|transaction)/[hash].json` inside the metadata bucket.

A request made to the API passing `hash` and `type` will retrieve the information or `404` if not found.

Types can be: `token` and `transaction` for now.  

# Reference-level explanation
[reference-level-explanation]: #reference-level-explanation

**Endpoint:**

GET `/metadata/:type/:hash` return `200` | `404`

- `type` - type of the data (`token` or `transaction`)
- `hash` - hash of the token or transaction


`metadata-handler` return the stored metadata in the following json format

```
{
  "id": string,
  "type": string,
  "data": (TokenMeta|TransactionMeta)
}
```

```
TokenMeta {
  id: string,
  verified: boolean,
  banned: boolean,
  reason: boolean,
  nft: boolean,
  nft_media: {
    type: enum(VIDEO|IMAGE|AUDIO),
    file: string,
    loop: boolean
  }
}

TransactionMeta {
  id: string,
  context: string, // a message to be shown on transaction page
  genesis: boolean
}

```

Examples:

** Token Metadata **
```
{
  "id": "00003aa356c9493464c657873b115c5e8667adf58cceeb4b37a1cdae0ddc9536",
  "data": {
    "id": "00003aa356c9493464c657873b115c5e8667adf58cceeb4b37a1cdae0ddc9536",
    "verified": false,
    "banned": false,
    "reason": null,
    "nft": true,
    "nft_media": {
      "type": "IMAGE",
      "file": "http://curtis-white.com/mean/officer.png",
      "loop": false
    }
  },
  "type": "TOKEN"
}

```

** Transaction Metadata **
```
{
  "id": "0000ecc7836621f5ee656695f96f561e59d8435904fb989a6b8de62bd2182888",
  "data": {
    "id": "0000ecc7836621f5ee656695f96f561e59d8435904fb989a6b8de62bd2182888",
    "context": "Whose citizen rate lose bar.",
    "genesis": false
  },
  "type": "TRANSACTION"
}

```

# Drawbacks
[drawbacks]: #drawbacks

We still store data manually in S3. It would be good to have a better way to do it, like a CMS or something like that.

# Rationale and alternatives
[rationale-and-alternatives]: #rationale-and-alternatives

Store in S3 in JSON format was the fastest we could do when we needed to have metadata for Token.
We could store in a database too.

# Unresolved questions
[unresolved-questions]: #unresolved-questions

Every entity that potentialy have some metadata will make a request and only a few will have, so, the massive majority of requests will return `404`. 

# Future possibilities
[future-possibilities]: #future-possibilities

We can store it in a database and have some tool to manage it like a CMS.
