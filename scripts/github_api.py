"""Cliente mínimo da API REST do GitHub, só com a biblioteca padrão."""
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request

API = "https://api.github.com"


class GitHub:
    def __init__(self, repo: str | None = None, token: str | None = None) -> None:
        self.repo = repo or os.environ["GITHUB_REPOSITORY"]
        self.token = token or os.environ.get("GITHUB_TOKEN")

    def _request(self, method: str, path: str, body: dict | None = None):
        url = path if path.startswith("http") else f"{API}{path}"
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("X-GitHub-Api-Version", "2022-11-28")
        if self.token:
            req.add_header("Authorization", f"Bearer {self.token}")
        if data is not None:
            req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = resp.read()
            link = resp.headers.get("Link", "")
        return (json.loads(payload) if payload else None), link

    def get(self, path: str):
        return self._request("GET", path)[0]

    def post(self, path: str, body: dict):
        return self._request("POST", path, body)[0]

    def paginate(self, path: str, params: dict | None = None) -> list:
        query = urllib.parse.urlencode({"per_page": 100, **(params or {})})
        url = f"{API}{path}?{query}"
        items: list = []
        while url:
            page, link = self._request("GET", url)
            items.extend(page)
            url = _next_link(link)
        return items


def _next_link(link_header: str) -> str | None:
    for part in link_header.split(","):
        if 'rel="next"' in part:
            return part[part.index("<") + 1 : part.index(">")]
    return None
