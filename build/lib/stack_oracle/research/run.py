"""Fetch allowlisted sources and extract dependency version hints."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

from stack_oracle.manifest import iter_bindings, load_manifest

DEFAULT_KEYWORDS = (
    "postgres",
    "postgresql",
    "mongo",
    "mongodb",
    "mysql",
    "mariadb",
    "redis",
    "database",
    "migration",
)


@dataclass
class Finding:
    stack: str
    binding_id: str
    source: str
    kind: str
    snippets: list[str] = field(default_factory=list)


def _fetch_text(url: str, timeout: int = 30) -> str:
    req = Request(url, headers={"User-Agent": "stack-oracle/0.1"})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _grep_keywords(text: str, keywords: tuple[str, ...]) -> list[str]:
    lines = text.splitlines()
    hits: list[str] = []
    for line in lines:
        low = line.lower()
        if any(k in low for k in keywords):
            stripped = line.strip()
            if stripped and stripped not in hits:
                hits.append(stripped[:500])
    return hits[:25]


def _github_release_bodies(repo: str, limit: int = 5) -> str:
    url = f"https://api.github.com/repos/{repo}/releases?per_page={limit}"
    req = Request(url, headers={"User-Agent": "stack-oracle/0.1", "Accept": "application/vnd.github+json"})
    with urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
    parts: list[str] = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                parts.append(str(item.get("body") or ""))
    return "\n\n".join(parts)


def research_manifest(
    manifest_path: Path,
    keywords: tuple[str, ...] = DEFAULT_KEYWORDS,
) -> list[Finding]:
    manifest = load_manifest(manifest_path)
    findings: list[Finding] = []
    for stack_name, _compose, binding in iter_bindings(manifest):
        binding_id = str(binding.get("id") or "unknown")
        for src in binding.get("research") or []:
            if not isinstance(src, dict):
                continue
            kind = str(src.get("kind") or "").strip()
            if kind == "doc":
                url = str(src.get("url") or "").strip()
                if not url.startswith("https://"):
                    continue
                text = _fetch_text(url)
                snippets = _grep_keywords(text, keywords)
                if snippets:
                    findings.append(Finding(stack_name, binding_id, url, "doc", snippets))
            elif kind == "github_releases":
                repo = str(src.get("repo") or "").strip()
                if not repo or "/" not in repo:
                    continue
                text = _github_release_bodies(repo, int(src.get("limit") or 5))
                snippets = _grep_keywords(text, keywords)
                if snippets:
                    findings.append(
                        Finding(stack_name, binding_id, f"github:{repo}", "github_releases", snippets)
                    )
    return findings


def write_report(findings: list[Finding], out_path: Path) -> None:
    payload = [
        {
            "stack": f.stack,
            "binding_id": f.binding_id,
            "source": f.source,
            "kind": f.kind,
            "snippets": f.snippets,
        }
        for f in findings
    ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2) + "\n")
