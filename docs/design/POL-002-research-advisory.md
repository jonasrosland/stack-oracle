# POL-002 — `research` is advisory

**MUST:** `stack-oracle research` outputs keyword snippets for humans and agents. It MUST NOT write back to `stack-compatibility.yml` or modify compose.

**MUST NOT:** CI treat `research` success as permission to merge a higher `dependency_max_major` without a human/agent PR that updates the manifest and evidence.

**SHOULD:** Consumer repos run `research` on Renovate branches and attach artifacts (see homelab `stack-oracle.yml` `run-research`).

## Enforcement

- Design + code review (`stack_oracle/research/run.py` has no manifest write path)
- Homelab [AGENTS.md](https://github.com/jonasrosland/homelab-config/blob/main/AGENTS.md) cap-bump workflow
