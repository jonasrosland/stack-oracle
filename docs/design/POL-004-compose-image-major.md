# POL-004 — Compose image major parsing

**MUST:** `image_major()` extract the numeric major from common Docker tag forms (`mongo:7.0`, `postgres:18-alpine`, digest suffix `@sha256:…`).

**MUST:** `image_base_name()` normalize registry paths for inventory/docs (`docker.io/library/postgres` → `postgres`).

Enforcement failures in `check` depend on this parser; regressions are caught by `tests/test_compose.py`.
