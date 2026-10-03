#!/usr/bin/env python3
"""CLI entrypoint for stack-oracle."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

from stack_oracle.enforce import check_manifest
from stack_oracle.inventory import inventory_repo
from stack_oracle.research.run import research_manifest, write_report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Discover compose dependencies, enforce limits, research vendor docs.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    inv = sub.add_parser("inventory", help="Print draft manifest from compose files")
    inv.add_argument("--root", type=Path, default=Path("."))
    inv.add_argument("--glob", default="**/docker-compose.yml")

    chk = sub.add_parser("check", help="Fail if compose pins exceed manifest limits")
    chk.add_argument("--root", type=Path, default=Path("."))
    chk.add_argument(
        "--manifest",
        type=Path,
        default=Path("stack-compatibility.yml"),
    )

    res = sub.add_parser("research", help="Fetch allowlisted docs/releases (network)")
    res.add_argument("--manifest", type=Path, default=Path("stack-compatibility.yml"))
    res.add_argument("--out", type=Path, default=Path(".generated/stack-oracle-research.json"))

    args = parser.parse_args()

    if args.cmd == "inventory":
        doc = inventory_repo(args.root.resolve(), args.glob)
        print(yaml.safe_dump(doc, sort_keys=False))
        return 0

    if args.cmd == "check":
        violations = check_manifest(args.root.resolve(), args.manifest.resolve())
        if violations:
            for v in violations:
                print(f"{v.stack}/{v.binding_id}: {v.message}", file=sys.stderr)
            return 1
        print("stack-oracle check OK")
        return 0

    if args.cmd == "research":
        findings = research_manifest(args.manifest.resolve())
        write_report(findings, args.out.resolve())
        print(json.dumps([f.__dict__ for f in findings], indent=2))
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
