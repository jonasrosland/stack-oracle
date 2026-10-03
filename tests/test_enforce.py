from pathlib import Path

import yaml

from stack_oracle.enforce import check_manifest


def test_enforce_ok(tmp_path: Path):
    compose_dir = tmp_path / "stacks" / "demo"
    compose_dir.mkdir(parents=True)
    (compose_dir / "docker-compose.yml").write_text(
        """
services:
  app:
    image: example/app:1.0
    depends_on: [db]
  db:
    image: mongo:7.0
"""
    )
    manifest = tmp_path / "stack-compatibility.yml"
    manifest.write_text(
        yaml.safe_dump(
            {
                "version": 1,
                "stacks": {
                    "demo": {
                        "compose": "stacks/demo/docker-compose.yml",
                        "bindings": [
                            {
                                "id": "app-mongo",
                                "dependency": {"service": "db"},
                                "limits": {"dependency_max_major": 7},
                            }
                        ],
                    }
                },
            }
        )
    )
    assert check_manifest(tmp_path, manifest) == []


def test_enforce_violation(tmp_path: Path):
    compose_dir = tmp_path / "stacks" / "demo"
    compose_dir.mkdir(parents=True)
    (compose_dir / "docker-compose.yml").write_text(
        "services:\n  db:\n    image: mongo:9.0\n"
    )
    manifest = tmp_path / "stack-compatibility.yml"
    manifest.write_text(
        yaml.safe_dump(
            {
                "version": 1,
                "stacks": {
                    "demo": {
                        "compose": "stacks/demo/docker-compose.yml",
                        "bindings": [
                            {
                                "id": "x",
                                "dependency": {"service": "db"},
                                "limits": {"dependency_max_major": 7},
                            }
                        ],
                    }
                },
            }
        )
    )
    v = check_manifest(tmp_path, manifest)
    assert len(v) == 1
    assert "major 9" in v[0].message
