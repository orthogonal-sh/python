"""HTTP clients for the Orthogonal API."""

from __future__ import annotations

import json
import math
from typing import Any, Dict, Mapping, Optional, Union, cast

import httpx

from ._exceptions import OrthogonalError
from ._types import JSONValue, RunOptions, RunResponse

VERSION = "0.1.0"
BASE_URL = "https://api.orth.sh"
_RUN_PATH = "/v1/run"
_INVALID_API_KEY = "Invalid API key. Visit https://orthogonal.sh to get one!"
_INSUFFICIENT_FUNDS = "Insufficient funds. Add USDC at https://orthogonal.sh"


def _js_truthy(value: Any) -> bool:
    """Return JavaScript-like truthiness for values found in API responses."""

    if value is None or value is False:
        return False
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value != 0 and not (isinstance(value, float) and math.isnan(value))
    if isinstance(value, str):
        return bool(value)
    return True


def _format_error(raw: Any, status: int) -> str:
    fallback = f"Request failed with status {status}"
    if raw is None:
        return fallback
    if isinstance(raw, str):
        return raw or fallback
    if isinstance(raw, Mapping):
        message = raw.get("message")
        if isinstance(message, str) and message:
            return message
        error = raw.get("error")
        if isinstance(error, str) and error:
            return error
    if isinstance(raw, (Mapping, list)):
        try:
            encoded = json.dumps(raw, separators=(",", ":"), ensure_ascii=False)
        except (TypeError, ValueError, OverflowError):
            return fallback
        return encoded if encoded not in {"{}", "[]", "null"} else fallback
    if isinstance(raw, bool):
        return "true" if raw else "false"
    return str(raw)


def _error_from_response(response: httpx.Response, data: Any) -> OrthogonalError:
    if response.status_code == 401:
        return OrthogonalError(_INVALID_API_KEY)
    if response.status_code == 402:
        return OrthogonalError(_INSUFFICIENT_FUNDS)

    nested_error: Any = None
    top_level_error: Any = None
    if isinstance(data, Mapping):
        nested = data.get("data")
        if isinstance(nested, Mapping):
            nested_error = nested.get("error")
        top_level_error = data.get("error")

    raw_error = nested_error if _js_truthy(nested_error) else top_level_error
    return OrthogonalError(_format_error(raw_error, response.status_code))


def _headers(api_key: str, custom_headers: Optional[Mapping[str, str]]) -> Dict[str, str]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": f"orthogonal-python/{VERSION}",
        "X-Orthogonal-Source": "sdk",
    }
    if custom_headers:
        headers.update(custom_headers)
    return headers


def _payload(
    api: str,
    path: str,
    query: Optional[Mapping[str, JSONValue]],
    body: Optional[Mapping[str, JSONValue]],
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {"api": api, "path": path}
    if query is not None:
        payload["query"] = dict(query)
    if body is not None:
        payload["body"] = dict(body)
    return payload


class Orthogonal:
    """Synchronous client for calling APIs on the Orthogonal platform."""

    def __init__(
        self,
        api_key: str,
        *,
        headers: Optional[Mapping[str, str]] = None,
        base_url: str = BASE_URL,
        timeout: Union[float, httpx.Timeout, None] = 30.0,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        if not api_key:
            raise ValueError("Orthogonal API key is required")
        self._owns_client = http_client is None
        self._client = http_client or httpx.Client(timeout=timeout)
        self._url = f"{base_url.rstrip('/')}{_RUN_PATH}"
        self._headers = _headers(api_key, headers)

    def run(
        self,
        options: Optional[RunOptions] = None,
        *,
        api: Optional[str] = None,
        path: Optional[str] = None,
        query: Optional[Mapping[str, JSONValue]] = None,
        body: Optional[Mapping[str, JSONValue]] = None,
    ) -> RunResponse:
        """Call an API through Orthogonal."""

        if options is not None:
            if api is not None or path is not None or query is not None or body is not None:
                raise TypeError("Pass either options or keyword arguments, not both")
            api = options["api"]
            path = options["path"]
            query = options.get("query")
            body = options.get("body")
        if api is None or path is None:
            raise TypeError("run() requires 'api' and 'path'")

        response = self._client.post(
            self._url,
            headers=self._headers,
            json=_payload(api, path, query, body),
        )
        data = response.json()
        if not response.is_success:
            raise _error_from_response(response, data)
        return cast(RunResponse, data)

    def close(self) -> None:
        """Close the underlying HTTP client when it is SDK-owned."""

        if self._owns_client:
            self._client.close()

    def __enter__(self) -> Orthogonal:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


class AsyncOrthogonal:
    """Asynchronous client for calling APIs on the Orthogonal platform."""

    def __init__(
        self,
        api_key: str,
        *,
        headers: Optional[Mapping[str, str]] = None,
        base_url: str = BASE_URL,
        timeout: Union[float, httpx.Timeout, None] = 30.0,
        http_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        if not api_key:
            raise ValueError("Orthogonal API key is required")
        self._owns_client = http_client is None
        self._client = http_client or httpx.AsyncClient(timeout=timeout)
        self._url = f"{base_url.rstrip('/')}{_RUN_PATH}"
        self._headers = _headers(api_key, headers)

    async def run(
        self,
        options: Optional[RunOptions] = None,
        *,
        api: Optional[str] = None,
        path: Optional[str] = None,
        query: Optional[Mapping[str, JSONValue]] = None,
        body: Optional[Mapping[str, JSONValue]] = None,
    ) -> RunResponse:
        """Call an API through Orthogonal."""

        if options is not None:
            if api is not None or path is not None or query is not None or body is not None:
                raise TypeError("Pass either options or keyword arguments, not both")
            api = options["api"]
            path = options["path"]
            query = options.get("query")
            body = options.get("body")
        if api is None or path is None:
            raise TypeError("run() requires 'api' and 'path'")

        response = await self._client.post(
            self._url,
            headers=self._headers,
            json=_payload(api, path, query, body),
        )
        data = response.json()
        if not response.is_success:
            raise _error_from_response(response, data)
        return cast(RunResponse, data)

    async def close(self) -> None:
        """Close the underlying HTTP client when it is SDK-owned."""

        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self) -> AsyncOrthogonal:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()
