- Feature Name: send_report_api
- Start Date: 2021-08-02
- RFC PR: (leave this empty)
- Hathor Issue: (leave this empty)
- Author: Giovane Costa <gigio.coder@gmail.com>

# Summary
[summary]: #summary

Report API will receive reports from users about tokens, transactions, etc.

# Motivation
[motivation]: #motivation

We are concerned about scammers, abuses, etc. As we have a metadata API that will carry information about tokens and
transactions, we need a way where users can report tokens used in scams and respective transactions.

# Guide-level explanation
[guide-level-explanation]: #guide-level-explanation

Report will be received as a POST and sent to a special email from hathor.

# Reference-level explanation
[reference-level-explanation]: #reference-level-explanation

**Endpoint:**

POST `/report` return `200` | `500`

```
body:
{
    type: str, // 'token' or 'transaction'
    id: str,
    decription: str

}
```

`send-report-handler` return success

```
{
  "ok": bool
}
```

# Drawbacks
[drawbacks]: #drawbacks

None

# Rationale and alternatives
[rationale-and-alternatives]: #rationale-and-alternatives

We can use other way to receive reports instead of an email

# Unresolved questions
[unresolved-questions]: #unresolved-questions

None

# Future possibilities
[future-possibilities]: #future-possibilities

We can store it in a database and have some automation as the volume can increase.
It can be hard to us to manage all reports as it grows.
