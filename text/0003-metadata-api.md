- Feature Name: metadata_api
- Start Date: 2021-07-13
- RFC PR: (leave this empty)
- Hathor Issue: (leave this empty)
- Author:
    - Giovane Costa <gigio.coder@gmail.com>
    - André Carneiro <andreluizmrcarneiro@gmail.com>

# Summary
[summary]: #summary

Metadata API will provide metadata information about Transactions, Tokens, Blocks and other things on Network.

# Motivation
[motivation]: #motivation

We need to have some data to be used on Public Explorer and Wallets that can't be stored on the blockchain about
Transactions, Tokens, Blocks and other things on Network.
So, we store somewhere else and retrieve them through MetadataAPI.
This data can also be used by community as they please.

# Guide-level explanation
[guide-level-explanation]: #guide-level-explanation

## **Endpoint**

Get dag entity metadata

GET `/metadata/dag` return `200` | `404`

**Query params**

- `id` - id of the dag entity

**Success Response**

- **Code** 200 <br/>
  **Content** `{"<id>": <metadata content>}`

**Error Response**

- **Code** 404 NOT FOUND <br/>
  **Content** `{"error": "not_found"}` <br/>
  **Meaning**: no metadata for this entity.

## **Content format**

Different dag elements may have different metadata associated with them.
For now we will describe the transaction and token metadata structures.
If any fields are missing from the actual response the caller should interpret as the "falsy" value for the field (bool is `false`, string is `""` and dict is `{}`) or null when applicable.


**Transaction**

| Field name | type | Description |
| --- | --- | --- |
| id      | str   | Transaction id |
| context | str   | Message to be shown on frontend |
| genesis | bool  | If this transaction is genesis |

Example:

```json
{
  "id": "000000005e4849855eeb967c6891162cc6a185f7ba68fe47ee4cecbe3e590bad",
  "context": "First transaction made with the hathor ledger app"
}
```

**Token**

| Field name | type | Description |
| --- | --- | --- |
| id | str | Token unique id |
| verified | bool | If token is verified |
| banned | bool | If token is banned |
| reason | str | Ban reason |
| nft | bool | If token is a nft or not |
| nft_media | dict | NFT media data, if any |

`nft_media` structure:

| Field name | type | Description |
| --- | --- | --- |
| type | enum(video\|image\|audio\|pdf) | NFT media type |
| file | str | Media file of the NFT |
| loop | bool | If media will play in loop |
| autoplay | bool | If media will play automatically |

Example:

```json
{
  "id": "00003aa356c9493464c657873b115c5e8667adf58cceeb4b37a1cdae0ddc9536",
  "verified": false,
  "banned": true,
  "reason": "some reason",
  "nft": true,
  "nft_media": {
    "type": "video",
    "file": "https://vimeo.com/68231446",
    "loop": false,
    "autoplay": true
  }
}
```

# Reference-level explanation
[reference-level-explanation]: #reference-level-explanation

Information will be stored on a file `dag/[id].json` inside an S3 bucket.

The endpoint will read the json from the file and return it as described on the guide-level.

If the file was not found, `404` will be returned.

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

The API could be more complex, allowing the caller to request a list of ids instead of a single one, or a more complex search like retrieve verified tokens with pagination.

We could store metadata on a database like mongodb or AWS DocumentDB and have a CronJob read the database, validate the data and compute any aggregations then write the S3 files.
This would allow a simple service to manage and interact with the database (maybe with an API) and we would still have the benefits of the public S3 with the metadata.
