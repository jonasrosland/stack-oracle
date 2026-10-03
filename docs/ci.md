# CI integration

## Recommended split: hard gate + soft research

| Job | Blocks merge? | When |
|-----|----------------|------|
| **`stack-oracle check`** | **Yes** | Every PR that touches compose or manifest |
| **`stack-oracle research`** | **No** (artifact / comment) | Renovate PRs, weekly cron, or manual |

Renovate proposes image bumps; **check** ensures nobody merges a Postgres/Mongo major above your documented cap. **Research** collects fresh doc/release lines containing `postgres`, `mongo`, etc., for review.

## GitHub Actions (composite action)

```yaml
# .github/workflows/stack-oracle.yml
name: stack-oracle

on:
  pull_request:
    paths:
      - "**/docker-compose.yml"
      - "**/compose.yml"
      - stack-compatibility.yml
      - config/stack-compatibility.yml

jobs:
  enforce:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v5
      - uses: jonasrosland/stack-oracle/action@v0.1.0
        with:
          manifest: stack-compatibility.yml
          run-research: ${{ startsWith(github.head_ref, 'renovate/') }}
```

Point `manifest` at your path (`config/stack-compatibility.yml` in homelab-config).

## Homelab / self-hosted

```bash
pip install "stack-oracle[research] @ git+https://github.com/jonasrosland/stack-oracle@main"
stack-oracle check --root /path/to/repo --manifest config/stack-compatibility.yml
```

Run weekly research on a scheduler; attach `.generated/stack-oracle-research.json` to Telegram or SRE.

## With existing test suites

Consumer repos can wrap `check` in pytest:

```python
from stack_oracle.enforce import check_manifest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_stack_compatibility():
    v = check_manifest(ROOT, ROOT / "stack-compatibility.yml")
    assert not v, [f"{x.stack}/{x.binding_id}: {x.message}" for x in v]
```

## Renovate

Keep database `automerge: false` and `allowedVersions` aligned with manifest `renovate` blocks. Oracle **check** catches merges that Renovate or hand-edits get wrong.
