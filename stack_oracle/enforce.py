"""Enforce manifest limits against pinned compose images."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from stack_oracle.compose import image_major, load_compose, service_image
from stack_oracle.manifest import iter_bindings, load_manifest

try:
    from yaml import YAMLError
except ImportError:  # pragma: no cover
    YAMLError = Exception  # type: ignore[misc, assignment]


@dataclass
class Violation:
    stack: str
    binding_id: str
    message: str


def check_manifest(repo_root: Path, manifest_path: Path) -> list[Violation]:
    manifest = load_manifest(manifest_path)
    violations: list[Violation] = []
    for stack_name, compose_rel, binding in iter_bindings(manifest):
        binding_id = str(binding.get("id") or "unknown")
        limits = binding.get("limits") or {}
        max_major = limits.get("dependency_max_major")
        if max_major is None:
            continue
        cap = int(max_major)
        dep_svc = str((binding.get("dependency") or {}).get("service") or "").strip()
        compose_path = repo_root / compose_rel
        if not compose_path.is_file():
            violations.append(
                Violation(stack_name, binding_id, f"missing compose file {compose_rel}")
            )
            continue
        try:
            services = (load_compose(compose_path).get("services") or {})
        except YAMLError as exc:
            violations.append(
                Violation(
                    stack_name,
                    binding_id,
                    f"invalid YAML in {compose_rel}: {exc}",
                )
            )
            continue
        img = service_image(services, dep_svc)
        if not img:
            violations.append(
                Violation(stack_name, binding_id, f"service {dep_svc!r} not found in {compose_rel}")
            )
            continue
        major = image_major(img)
        if major is None:
            violations.append(
                Violation(
                    stack_name,
                    binding_id,
                    f"cannot parse major from dependency image {img!r}",
                )
            )
            continue
        if major > cap:
            violations.append(
                Violation(
                    stack_name,
                    binding_id,
                    f"{dep_svc} uses major {major} but limit dependency_max_major={cap}",
                )
            )
    return violations
