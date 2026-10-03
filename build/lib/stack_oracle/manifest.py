"""Load and validate stack-compatibility.yml."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_manifest(path: Path) -> dict[str, Any]:
    raw = yaml.safe_load(path.read_text()) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: root must be a mapping")
    if int(raw.get("version") or 0) != 1:
        raise ValueError(f"{path}: supported version is 1")
    return raw


def iter_bindings(manifest: dict[str, Any]):
    for stack_name, stack in (manifest.get("stacks") or {}).items():
        if not isinstance(stack, dict):
            continue
        compose = str(stack.get("compose") or "").strip()
        for binding in stack.get("bindings") or []:
            if not isinstance(binding, dict):
                continue
            yield stack_name, compose, binding
