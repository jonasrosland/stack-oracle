# Using Stack Oracle with AI coding agents

Stack Oracle is built for **human-in-the-loop** automation: machines enforce numeric caps; **agents interpret** research snippets and vendor docs when limits need to change.

## Roles

| Actor | Responsibility |
|-------|----------------|
| **Inventory / check** | Deterministic; run in CI; agents should not weaken without user intent |
| **Research JSON** | Evidence for the agent; not auto-applied |
| **Agent (Cursor, Claude Code, Codex, etc.)** | Read research + official docs; propose manifest/Renovate updates; open PR |
| **You (admin)** | Approve limit changes; merge via your normal PR + CI flow |

## Agent workflow (copy into your repo `AGENTS.md`)

```markdown
### Stack compatibility (Stack Oracle)

When a PR changes Docker Compose images or `stack-compatibility.yml`:

1. Run `stack-oracle check --root . --manifest <path>` (must pass before merge).
2. If the PR is from Renovate or bumps an **application** image (not only digest):
   - Run `stack-oracle research --manifest <path> --out .generated/stack-oracle-research.json`
   - Read `evidence` and research snippets for postgres/mongo/database mentions.
   - Compare with `limits.dependency_max_major` for each binding.
3. If official docs require a **higher** supported DB major:
   - Update `limits`, `evidence`, and matching `renovate.allowedVersions` in one PR.
   - Document migration steps (DB major upgrades are rarely a single tag bump).
4. If research is silent: **no news is not proof** — do not raise limits without a cited doc line or release note.
5. Never disable `stack-oracle check` in CI to green a Renovate PR.
```

## Prompt template for review (paste into agent chat)

```text
Context: Pull request may upgrade container images in docker-compose.

Tasks:
1. Summarize which bindings in stack-compatibility.yml apply to changed files.
2. Read .generated/stack-oracle-research.json if present; quote snippets that mention database versions.
3. State whether current dependency_max_major limits are still valid.
4. If invalid, draft a minimal YAML diff for stack-compatibility.yml and renovate.json with citations (URL + quote).

Do not merge if stack-oracle check fails. Do not invent vendor support matrix numbers without a citation.
```

## Cursor / Claude Code / Codex specifics

- **Cursor**: add the workflow above to `.cursor/rules/` or root `AGENTS.md`; use `@stack-compatibility.yml` and research artifact in context.
- **Claude Code / Codex**: same rules in `AGENTS.md`; run CLI via sandbox before suggesting merge.
- **No agent should auto-merge** dependency limit changes without explicit user approval and green CI.

## What agents are good / bad at

| Good | Bad |
|------|-----|
| Summarizing release notes already fetched by `research` | Replacing allowlisted research with random web search |
| Proposing YAML + Renovate diffs with citations | Silently bumping `dependency_max_major` because "latest exists" |
| Explaining UniFi-style multi-hop DB migrations | Guaranteeing compose-only repos without sidecar limits |

## Optional: LLM inside your infra

You may send **only** research snippets (not whole repos) to your LiteLLM/OpenAI endpoint with a JSON schema output `{ "recommendation", "citations" }`. Stack Oracle intentionally stays LLM-free so CI stays reproducible; LLM belongs in the **agent or optional wrapper script** in your repo, not in the required check.
