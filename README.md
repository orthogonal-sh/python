# orthogonal-sdk

Python SDK to call any API on the Orthogonal platform.

## Installation

```bash
pip install orthogonal-sdk
```

## Quick Start

```python
import os

from orthogonal import Orthogonal

with Orthogonal(api_key=os.environ["ORTHOGONAL_API_KEY"]) as orthogonal:
    response = orthogonal.run(
        api="andi",
        path="/api/v1/search",
        query={"q": "what is the weather today"},
    )

print(response["data"])
print(response["price"])  # e.g. "0.01"
```

The `run` method also accepts an options dictionary:

```python
response = orthogonal.run(
    {
        "api": "andi",
        "path": "/api/v1/search",
        "query": {"q": "hello world"},
    }
)
```

## Async Usage

```python
import asyncio
import os

from orthogonal import AsyncOrthogonal


async def main() -> None:
    async with AsyncOrthogonal(
        api_key=os.environ["ORTHOGONAL_API_KEY"]
    ) as orthogonal:
        response = await orthogonal.run(
            api="andi",
            path="/api/v1/search",
            query={"q": "hello world"},
        )
        print(response["data"])


asyncio.run(main())
```

## Custom Headers

Custom headers are included in every request. As in the TypeScript SDK, they
take precedence over SDK defaults.

```python
client = Orthogonal(
    api_key="orth_live_...",
    headers={"X-Request-ID": "request-123"},
)
```

## Response

Successful calls return the decoded API response:

```json
{
  "success": true,
  "price": "0.01",
  "data": {}
}
```

HTTP errors raise `OrthogonalError`. Authentication and insufficient-funds
errors include direct instructions, while upstream API errors preserve the
most useful available message.

## License

MIT

