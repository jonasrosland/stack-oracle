"""Discover compose sidecars and suggest manifest skeleton."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from stack_oracle.compose import depends_on_targets, image_base_name, load_compose, service_image


def discover_compose_file(path: Path) -> list[dict[str, Any]]:
    """Return binding-shaped dicts inferred from one compose file."""
    data = load_compose(path)
    services = data.get("services") or {}
    if not isinstance(services, dict):
        return []
    out: list[dict[str, Any]] = []
    for consumer, spec in services.items():
        if not isinstance(spec, dict):
            continue
        for dep_service in depends_on_targets(spec):
            dep_spec = services.get(dep_service) or {}
            if not isinstance(dep_spec, dict):
                continue
            consumer_img = service_image(services, consumer) or ""
            dep_img = service_image(services, dep_service) or ""
            if not dep_img:
                continue
            out.append(
                {
                    "id": f"{consumer}-{dep_service}",
                    "consumer": {"service": consumer, "image": consumer_img},
                    "dependency": {
                        "service": dep_service,
                        "image": image_base_name(dep_img),
                    },
                    "limits": {},
                    "research": [],
                }
            )
    return out


def inventory_repo(repo_root: Path, glob_pattern: str = "**/docker-compose.yml") -> dict[str, Any]:
    stacks: dict[str, Any] = {}
    for compose_path in sorted(repo_root.glob(glob_pattern)):
        if ".git" in compose_path.parts:
            continue
        rel = compose_path.relative_to(repo_root).as_posix()
        stack_key = compose_path.parent.name
        bindings = discover_compose_file(compose_path)
        if bindings:
            stacks[stack_key] = {"compose": rel, "bindings": bindings}
    return {"version": 1, "stacks": stacks}
