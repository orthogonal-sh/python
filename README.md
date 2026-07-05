<div align="center">

# Orthogonal Python SDK

**Python SDK for calling APIs on the [Orthogonal](https://orthogonal.com) platform.**

Call any API on the Orthogonal platform through one client and one credit balance — authentication, routing, and billing are handled for you.

[![python](https://img.shields.io/badge/python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![license](https://img.shields.io/badge/license-MIT-blue)](./LICENSE)

</div>

## Table of Contents

- [Why Orthogonal](#why-orthogonal)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Authentication](#authentication)
- [Usage](#usage)
- [Async Usage](#async-usage)
- [Error Handling](#error-handling)
- [API Reference](#api-reference)
- [Related](#related)
- [License](#license)

## Why Orthogonal

Orthogonal puts a catalog of APIs behind one account and one balance:

- **One integration** — call any API on the platform through a single `run()` method.
- **Pay per use** — a single credit balance instead of juggling dozens of provider subscriptions.
- **Sync and async** — a blocking `Orthogonal` client and an `await`-able `AsyncOrthogonal`, both usable as context managers.
- **Typed** — `RunOptions` / `RunResponse` typed dicts and full type hints.

## Installation

Requires **Python 3.9+**.

```bash
pip install orthogonal-sdk
```

## Quick Start

```python
import os
from orthogonal import Orthogonal

with Orthogonal(api_key=os.environ["ORTHOGONAL_API_KEY"]) as orthogonal:
    res = orthogonal.run(
        api="tavily",
        path="/search",
        query={"query": "latest AI news"},
    )

print(res["data"])   # the upstream API's response
print(res["price"])  # amount charged, e.g. "0.01"
```

Get an API key from your [Orthogonal dashboard](https://orthogonal.com/dashboard).

## Authentication

Pass your key to the constructor (reading it from the environment keeps keys out of source):

```python
orthogonal = Orthogonal(api_key=os.environ["ORTHOGONAL_API_KEY"])
```

## Usage

### GET request (query params)

```python
res = orthogonal.run(
    api="fantastic-jobs",
    path="/v1/active-ats",
    query={"time_frame": "1h", "limit": 10},
)
```

### POST request (JSON body)

```python
res = orthogonal.run(
    api="some-api",
    path="/v1/generate",
    body={"prompt": "a red bicycle"},
)
```

### Options dict instead of keyword arguments

```python
res = orthogonal.run({
    "api": "tavily",
    "path": "/search",
    "query": {"query": "hello world"},
})
```

### Custom headers

Headers passed to the constructor are sent on every request:

```python
orthogonal = Orthogonal(
    api_key=os.environ["ORTHOGONAL_API_KEY"],
    headers={"x-my-trace-id": "abc123"},
)
```

## Async Usage

`AsyncOrthogonal` mirrors the sync client with `await` and `async with`:

```python
import asyncio
from orthogonal import AsyncOrthogonal

async def main():
    async with AsyncOrthogonal(api_key=os.environ["ORTHOGONAL_API_KEY"]) as orthogonal:
        res = await orthogonal.run(
            api="tavily",
            path="/search",
            query={"query": "orthogonal"},
        )
        print(res["data"])

asyncio.run(main())
```

## Error Handling

`run()` returns the response on success and raises **`OrthogonalError`** on any non-2xx response (invalid key, insufficient credits, or an upstream/validation error). The message describes what went wrong.

```python
from orthogonal import Orthogonal, OrthogonalError

try:
    res = orthogonal.run(api="tavily", path="/search", query={"query": "x"})
except OrthogonalError as err:
    print(f"request failed: {err}")
```

## API Reference

### `Orthogonal(api_key, *, headers=None, base_url=...)`

| Argument | Type | Description |
| --- | --- | --- |
| `api_key` | `str` | **Required.** Your Orthogonal API key (`orth_live_…` / `orth_test_…`). |
| `headers` | `Mapping[str, str] \| None` | Optional headers sent on every request. |
| `base_url` | `str` | Override the API base URL (advanced). |

### `orthogonal.run(options=None, *, api, path, query=None, body=None)` → `RunResponse`

Call an endpoint. Pass **either** an `options` dict **or** keyword arguments (not both).

| Argument | Type | Description |
| --- | --- | --- |
| `api` | `str` | **Required.** The API slug (e.g. `"tavily"`). |
| `path` | `str` | **Required.** The endpoint path (e.g. `"/search"`). |
| `query` | `Mapping[str, JSONValue]` | Query parameters. |
| `body` | `Mapping[str, JSONValue]` | Request body for POST/PUT/PATCH. |

**`RunResponse`** (a `TypedDict`)

| Key | Type | Description |
| --- | --- | --- |
| `success` | `bool` | Whether the call succeeded. |
| `price` | `str` | Amount charged in USD (e.g. `"0.01"`). |
| `data` | `JSONValue` | The upstream API's response. |

### `AsyncOrthogonal(...)`

Same constructor and `run(...)` signature as `Orthogonal`, but `run()` is a coroutine (`await`) and the client supports `async with` / `await client.close()`.

### `OrthogonalError`

Raised by `run()` on a non-2xx response. Subclass of `Exception`; `str(err)` is a human-readable message.

Both clients are context managers — use `with` / `async with` (or call `close()`) so the underlying HTTP connection is released.

## Related

- **[`@orth/cli`](https://www.npmjs.com/package/@orth/cli)** — the Orthogonal command-line tool.
- **[`@orth/sdk`](https://www.npmjs.com/package/@orth/sdk)** — the official TypeScript/JavaScript SDK.

## License

[MIT](./LICENSE) © Orthogonal
