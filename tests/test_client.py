import json

import httpx
import pytest

from orthogonal import AsyncOrthogonal, Orthogonal, OrthogonalError


def response(status: int, payload: object) -> httpx.Response:
    return httpx.Response(status, json=payload)


def sync_client(handler, **kwargs) -> Orthogonal:
    transport = httpx.MockTransport(handler)
    return Orthogonal("orth_live_test123", http_client=httpx.Client(transport=transport), **kwargs)


def test_requires_api_key() -> None:
    with pytest.raises(ValueError, match="Orthogonal API key is required"):
        Orthogonal("")


def test_successful_request_with_query_and_headers() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == "https://api.orth.sh/v1/run"
        assert request.method == "POST"
        assert request.headers["authorization"] == "Bearer orth_live_test123"
        assert request.headers["user-agent"] == "orthogonal-python/0.1.0"
        assert request.headers["x-orthogonal-source"] == "sdk"
        assert json.loads(request.content) == {
            "api": "andi",
            "path": "/api/v1/search",
            "query": {"q": "test"},
        }
        return response(
            200,
            {"success": True, "price": "0.01", "data": {"results": [{"title": "Test"}]}},
        )

    client = sync_client(handler)
    result = client.run(api="andi", path="/api/v1/search", query={"q": "test"})
    assert result["price"] == "0.01"


def test_options_dictionary_and_body() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert json.loads(request.content)["body"] == {"prompt": "Hello"}
        return response(200, {"success": True, "price": "0.05", "data": {}})

    client = sync_client(handler)
    result = client.run(
        {"api": "some-api", "path": "/api/v1/generate", "body": {"prompt": "Hello"}}
    )
    assert result["success"] is True


@pytest.mark.parametrize(
    ("status", "message"),
    [
        (401, "Invalid API key. Visit https://orthogonal.sh to get one!"),
        (402, "Insufficient funds. Add USDC at https://orthogonal.sh"),
    ],
)
def test_helpful_auth_and_funds_errors(status: int, message: str) -> None:
    client = sync_client(lambda request: response(status, {"error": "ignored"}))
    with pytest.raises(OrthogonalError, match=message):
        client.run(api="andi", path="/search")


@pytest.mark.parametrize(
    ("payload", "status", "message"),
    [
        (
            {"data": {"error": "Missing required parameter: q"}},
            400,
            "Missing required parameter: q",
        ),
        (
            {
                "data": {
                    "error": {
                        "type": ["invalid_request_error"],
                        "message": "Does not meet minimum combination of required data points.",
                    }
                }
            },
            400,
            "Does not meet minimum combination of required data points.",
        ),
        (
            {"data": {"error": {"code": "bad_input", "field": "q"}}},
            422,
            '{"code":"bad_input","field":"q"}',
        ),
        ({"success": False}, 503, "Request failed with status 503"),
        (
            {"data": {"error": {"type": "invalid_request_error", "message": ""}}},
            400,
            '{"type":"invalid_request_error","message":""}',
        ),
        (
            {"data": {"error": ""}, "error": "upstream unavailable"},
            500,
            "upstream unavailable",
        ),
        (
            {"data": {"error": ""}, "error": ""},
            500,
            "Request failed with status 500",
        ),
        ({"data": {"error": []}}, 500, "Request failed with status 500"),
    ],
)
def test_error_shapes(payload: object, status: int, message: str) -> None:
    client = sync_client(lambda request: response(status, payload))
    with pytest.raises(OrthogonalError) as exc:
        client.run(api="x", path="/y")
    assert str(exc.value) == message
    assert "[object Object]" not in str(exc.value)


def test_custom_headers_override_defaults() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Custom token"
        assert request.headers["x-request-id"] == "request-123"
        return response(200, {"success": True, "price": "0", "data": {}})

    client = sync_client(
        handler,
        headers={"Authorization": "Custom token", "X-Request-ID": "request-123"},
    )
    client.run(api="test", path="/test")


def test_rejects_mixed_options_and_keywords() -> None:
    client = sync_client(lambda request: response(200, {}))
    with pytest.raises(TypeError, match="either options or keyword arguments"):
        client.run({"api": "x", "path": "/y"}, api="x")


async def test_async_client() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert json.loads(request.content) == {"api": "andi", "path": "/search"}
        return response(200, {"success": True, "price": "0.01", "data": {"ok": True}})

    transport = httpx.MockTransport(handler)
    http_client = httpx.AsyncClient(transport=transport)
    client = AsyncOrthogonal("test", http_client=http_client)
    result = await client.run(api="andi", path="/search")
    assert result["data"] == {"ok": True}
    await http_client.aclose()
