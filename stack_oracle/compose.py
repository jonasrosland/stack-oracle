"""Parse Docker Compose files for images and depends_on edges."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

_IMAGE_MAJOR = re.compile(r"^(?:docker\.io/library/|[^/]+/)?(?P<name>[^:@/]+)(?::(?P<tag>[^@]+))?")


def load_compose(path: Path) -> dict[str, Any]:
    raw = yaml.safe_load(path.read_text()) or {}
    return raw if isinstance(raw, dict) else {}


def service_image(services: dict[str, Any], service: str) -> str | None:
    spec = services.get(service) or {}
    if not isinstance(spec, dict):
        return None
    img = str(spec.get("image") or "").strip()
    return img or None


def image_major(image: str) -> int | None:
    """Best-effort major version from tag (e.g. mongo:7.0, postgres:18-alpine)."""
    m = _IMAGE_MAJOR.match(image.split("@", 1)[0])
    if not m:
        return None
    tag = (m.group("tag") or "").strip()
    if not tag or tag in ("latest", "stable"):
        return None
    head = tag.split("-", 1)[0]
    parts = head.split(".")
    if parts and parts[0].isdigit():
        return int(parts[0])
    return None


def image_base_name(image: str) -> str:
    m = _IMAGE_MAJOR.match(image.split("@", 1)[0])
    if not m:
        return image
    name = m.group("name") or image
    if "/" in name:
        return name.rsplit("/", 1)[-1]
    return name


def depends_on_targets(spec: dict[str, Any]) -> list[str]:
    dep = spec.get("depends_on")
    if dep is None:
        return []
    if isinstance(dep, list):
        return [str(x) for x in dep if x]
    if isinstance(dep, dict):
        return [str(k) for k in dep.keys()]
    return []
