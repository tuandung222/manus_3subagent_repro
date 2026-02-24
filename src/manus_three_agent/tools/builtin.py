from __future__ import annotations

import math
import re
from typing import Any

import requests

_SAFE_EXPR = re.compile(r"^[0-9\s\+\-\*\/\(\)\.,a-zA-Z_]+$")


def calculator_tool(arguments: dict[str, Any]) -> dict[str, Any]:
    expression = str(arguments.get("expression", "")).strip()
    if not expression:
        return {"ok": False, "error": "empty_expression"}

    if not _SAFE_EXPR.match(expression):
        return {"ok": False, "error": "unsupported_expression"}

    value = eval(expression, {"__builtins__": {}}, {"sqrt": math.sqrt, "pow": pow})
    return {"ok": True, "expression": expression, "value": value}


def fetch_url_tool(arguments: dict[str, Any]) -> dict[str, Any]:
    url = str(arguments.get("url", "")).strip()
    max_chars = int(arguments.get("max_chars", 1200))
    if not url:
        return {"ok": False, "error": "empty_url"}

    response = requests.get(url, timeout=12)
    content_type = response.headers.get("content-type", "")
    text = response.text[:max_chars]
    title = ""

    title_match = re.search(r"<title>(.*?)</title>", response.text, flags=re.IGNORECASE | re.DOTALL)
    if title_match:
        title = re.sub(r"\\s+", " ", title_match.group(1)).strip()

    return {
        "ok": response.ok,
        "status": response.status_code,
        "url": str(response.url),
        "content_type": content_type,
        "title": title,
        "content_preview": re.sub(r"\\s+", " ", text).strip(),
    }
