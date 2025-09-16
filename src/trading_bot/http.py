"""Lightweight HTTP utilities to avoid external dependencies."""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class HTTPResponse:
    status_code: int
    text: str
    data: Optional[Any]

    def json(self) -> Any:
        if self.data is None:
            raise ValueError("Response did not contain JSON data")
        return self.data


def post_json(url: str, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None, timeout: int = 30) -> HTTPResponse:
    headers = {"Content-Type": "application/json", **(headers or {})}
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url=url, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            status = response.getcode()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return HTTPResponse(status_code=exc.code, text=body, data=None)
    except urllib.error.URLError as exc:  # pragma: no cover - network failures vary
        raise RuntimeError(f"HTTP request failed: {exc.reason}") from exc

    try:
        parsed = json.loads(body) if body else None
    except json.JSONDecodeError:
        parsed = None

    return HTTPResponse(status_code=status, text=body, data=parsed)
