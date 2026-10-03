# POL-001 — `check` is deterministic and offline

**MUST:** `stack-oracle check` evaluates only files present at `--root` and the manifest path. It MUST NOT perform network I/O.

**MUST:** For each binding with `limits.dependency_max_major`, the dependency service image major in the referenced compose file MUST be ≤ that limit.

**MUST:** Missing compose, invalid YAML, missing dependency service, or unparsable image tag MUST produce a violation (non-zero CLI exit).

## Enforcement

- `stack_oracle.enforce.check_manifest`
- `tests/test_enforce.py` — pass/fail majors
- `tests/test_lsio_bookstack_smoke.py` — BookStack example, YAML errors, CLI exit codes

## Non-goals

- Raising limits from the internet
- Validating Renovate JSON (consumer repo responsibility, e.g. homelab CFG-003)
