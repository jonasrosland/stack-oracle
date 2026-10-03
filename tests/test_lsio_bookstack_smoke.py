"""Smoke scenarios: LinuxServer BookStack + MariaDB (multi-service LSIO pattern)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

from stack_oracle.cli import main as oracle_cli_main
from stack_oracle.enforce import check_manifest
from stack_oracle.inventory import inventory_repo

REPO = Path(__file__).resolve().parents[1]
EXAMPLE = REPO / "examples" / "linuxserver-bookstack"
MANIFEST = EXAMPLE / "stack-compatibility.yml"
COMPOSE = EXAMPLE / "docker-compose.yml"


def test_example_bookstack_check_ok():
    violations = check_manifest(REPO, MANIFEST)
    assert violations == []


def test_example_inventory_finds_bookstack_mariadb_edge():
    doc = inventory_repo(EXAMPLE)
    stacks = doc.get("stacks") or {}
    assert "linuxserver-bookstack" in stacks
    bindings = stacks["linuxserver-bookstack"]["bindings"]
    assert any(b.get("dependency", {}).get("image") == "mariadb" for b in bindings)


def test_mariadb_major_above_cap(tmp_path: Path):
    _write_bookstack_stack(tmp_path, mariadb_image="mariadb:11.4")
    manifest = _manifest(tmp_path)
    v = check_manifest(tmp_path, manifest)
    assert len(v) == 1
    assert "major 11" in v[0].message


def test_manifest_compose_path_wrong(tmp_path: Path):
    _write_bookstack_stack(tmp_path, mariadb_image="mariadb:10.11")
    manifest = _manifest(tmp_path, compose="stacks/wrong/docker-compose.yml")
    v = check_manifest(tmp_path, manifest)
    assert any("missing compose" in x.message for x in v)


def test_compose_invalid_yaml(tmp_path: Path):
    stack_dir = tmp_path / "stacks" / "bookstack"
    stack_dir.mkdir(parents=True)
    (stack_dir / "docker-compose.yml").write_text("services:\n  bad: [unclosed\n")
    manifest = _manifest(tmp_path)
    v = check_manifest(tmp_path, manifest)
    assert len(v) == 1
    assert "invalid YAML" in v[0].message


def test_dependency_service_name_mismatch(tmp_path: Path):
    _write_bookstack_stack(tmp_path, mariadb_image="mariadb:10.11")
    manifest = _manifest(tmp_path, dependency_service="mysql")
    v = check_manifest(tmp_path, manifest)
    assert any("not found" in x.message for x in v)


def test_cli_check_ok_and_fail_on_bad_major(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _write_bookstack_stack(tmp_path, mariadb_image="mariadb:10.11")
    manifest = _manifest(tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        ["stack-oracle", "check", "--root", str(tmp_path), "--manifest", str(manifest)],
    )
    assert oracle_cli_main() == 0

    _write_bookstack_stack(tmp_path, mariadb_image="mariadb:11.0")
    assert oracle_cli_main() == 1


def _manifest(tmp_path: Path, *, compose: str | None = None, dependency_service: str = "mariadb") -> Path:
    rel = compose or "stacks/bookstack/docker-compose.yml"
    path = tmp_path / "stack-compatibility.yml"
    path.write_text(
        yaml.safe_dump(
            {
                "version": 1,
                "stacks": {
                    "bookstack": {
                        "compose": rel,
                        "bindings": [
                            {
                                "id": "bookstack-mariadb",
                                "dependency": {"service": dependency_service},
                                "limits": {"dependency_max_major": 10},
                            }
                        ],
                    }
                },
            }
        )
    )
    return path


def _write_bookstack_stack(tmp_path: Path, *, mariadb_image: str) -> None:
    stack_dir = tmp_path / "stacks" / "bookstack"
    stack_dir.mkdir(parents=True, exist_ok=True)
    (stack_dir / "docker-compose.yml").write_text(
        f"""
services:
  bookstack:
    image: lscr.io/linuxserver/bookstack:latest
    depends_on: [mariadb]
  mariadb:
    image: {mariadb_image}
"""
    )
