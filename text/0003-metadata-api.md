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

We need to have some data about Transactions, Tokens, Blocks and other things on Network that can't be stored on the
blockchain. So, we store somewhere else and retrieve them through MetadataAPI

# Guide-level explanation
[guide-level-explanation]: #guide-level-explanation

Information will be stored in S3 in format `(token|transaction)/[id_hash].json` inside the metadata bucket.

A request made to the API passing `id` and `type` will retrieve the information or `404` if not found. 

# Reference-level explanation
[reference-level-explanation]: #reference-level-explanation

**Endpoint:**

GET `/metadata/:type/:id` return `200` | `404`

`metadata-handler` return the stored data

```
{
  "id": string,
  "type": string,
  "data": object
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
