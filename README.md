# Stack Oracle

**Discover** sidecar dependencies in Docker Compose, **enforce** version limits you define from vendor docs, and **research** allowlisted official docs/releases for database-related keywords.

Renovate bumps `mongo` and `litellm` independently—it does not know UniFi needs MongoDB ≤7 or that LiteLLM release notes might mention Postgres. Stack Oracle closes the gap for **co-deployed** services (app + DB/cache in the same compose stack).

## Quick start

```bash
pip install "stack-oracle[research] @ git+https://github.com/jonasrosland/stack-oracle@main"

# Draft manifest from depends_on edges (review and add limits)
stack-oracle inventory --root . > stack-compatibility.yml

# CI gate after you set dependency_max_major
stack-oracle check --root . --manifest stack-compatibility.yml

# Optional: fetch doc/release snippets (HTTPS allowlist only)
stack-oracle research --manifest stack-compatibility.yml
```

## Manifest

See [docs/schema.md](docs/schema.md). Example: [examples/homelab-unifi/stack-compatibility.yml](examples/homelab-unifi/stack-compatibility.yml).

## CI on pull requests

**Yes — use Oracle in CI**, but split responsibilities:

- **Required:** `stack-oracle check` (deterministic, no network).
- **Optional:** `stack-oracle research` on Renovate branches or schedule (artifact for humans/agents).

Details: [docs/ci.md](docs/ci.md).

## AI agents (Cursor, Claude, Codex, …)

Oracle does not replace an agent; it **feeds** one:

1. CI proves pins respect committed limits.
2. Research produces snippets for “does this release mention Postgres?”
3. Your agent proposes limit/Renovate updates **with citations**; you merge via PR.

Guide: [docs/agents.md](docs/agents.md).

## GitHub Action

```yaml
- uses: jonasrosland/stack-oracle/action@v0.1.0
  with:
    manifest: stack-compatibility.yml
    run-research: "false"
```

## Philosophy

| Layer | Tool |
|-------|------|
| Bump proposals | Renovate / Dependabot |
| **Your policy** | `stack-compatibility.yml` |
| **Hard enforcement** | Stack Oracle `check` in CI |
| **Doc hints** | Stack Oracle `research` |
| **Judgment** | You + AI agent |

Limits change only through **git**, with evidence fields for audit.

## Status

Early **0.1.x** — API may evolve. Homelab dogfooding: [homelab-config](https://github.com/jonasrosland/homelab-config).

## License

MIT
