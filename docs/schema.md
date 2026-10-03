# stack-compatibility.yml (version 1)

Place this file in **your** deployment repo (monorepo, homelab-config, etc.). Stack Oracle does not ship vendor limits—you define them after reading docs or running `research`.

```yaml
version: 1
stacks:
  <stack-id>:
    compose: path/to/docker-compose.yml   # relative to repo root
    bindings:
      - id: unique-binding-id
        consumer:
          service: app-service-name
          image: optional/pinned-image-for-docs
        dependency:
          service: db-service-name
          image: mongo | postgres | redis   # logical name for Renovate
        limits:
          dependency_max_major: 7           # enforced by `stack-oracle check`
        evidence:                           # audit trail (human + agents)
          - kind: doc
            url: https://...
            refreshed_at: "YYYY-MM-DD"
            summary: One-line why the limit exists
        research:                           # allowlisted fetch targets only
          - kind: doc
            url: https://official-vendor-doc
          - kind: github_releases
            repo: org/repo
            limit: 5
        renovate:                           # copy into renovate.json (manual or script)
          matchPackageNames: [mongo]
          matchFileNames: [stacks/foo/**]
          allowedVersions: "<8"
```

## Commands

| Command | Network | Purpose |
|---------|---------|---------|
| `stack-oracle inventory` | No | Draft manifest from `depends_on` + images |
| `stack-oracle check` | No | **CI gate**: compose major ≤ `dependency_max_major` |
| `stack-oracle research` | Yes | Keyword snippets from `research` sources |

## Design rules

1. **Limits are yours** — Oracle enforces what you committed; it does not auto-raise limits from the internet on first sight.
2. **Research is advisory** — Outputs snippets for humans/agents; wire `research` in CI as artifact or PR comment, not as silent limit changes.
3. **Allowlisted URLs only** — No generic web search (brittle, untrustworthy).
4. **Renovate is separate** — Duplicate `renovate` blocks into `renovate.json` until a sync script exists in your repo.
