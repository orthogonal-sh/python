"""Public type definitions for the Orthogonal SDK."""

from typing import Dict, List, TypedDict, Union

JSONPrimitive = Union[str, int, float, bool, None]
JSONValue = Union[JSONPrimitive, List["JSONValue"], Dict[str, "JSONValue"]]


class _RequiredRunOptions(TypedDict):
    api: str
    path: str


class RunOptions(_RequiredRunOptions, total=False):
    """Options accepted by :meth:`Orthogonal.run`."""

    query: Dict[str, JSONValue]
    body: Dict[str, JSONValue]


class RunResponse(TypedDict):
    """Response returned by the Orthogonal API."""

    success: bool
    price: str
    data: JSONValue
