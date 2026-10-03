# POL-003 — Allowlisted fetch only

**MUST:** `research` only requests URLs explicitly listed under a binding’s `research` array in the manifest.

**MUST:** `kind: doc` entries use `https://` URLs only (non-HTTPS skipped).

**MUST:** `kind: github_releases` entries use `repo: org/name` and call the GitHub releases API (no generic HTML crawl).

**MUST NOT:** Generic web search, arbitrary domains, or following links discovered in page bodies.

## Enforcement

- `stack_oracle/research/run.py` — `iter_bindings` + per-kind handlers
- Extend with tests when adding new `kind` values
