# Oracle requirements (POL-*)

| ID | MUST (summary) | Test(s) | Code |
|----|----------------|---------|------|
| POL-001 | `check` uses only manifest + compose on disk (no network) | `tests/test_enforce.py`, `tests/test_lsio_bookstack_smoke.py` | `stack_oracle/enforce.py`, `cli.py` |
| POL-002 | `research` MUST NOT change manifest limits or exit codes of `check` | Manual / CI artifact only | `stack_oracle/research/run.py` |
| POL-003 | `research` fetches only manifest `research` entries (`https://` doc URLs, `github_releases` repos) | Code review + `research/run.py` | `stack_oracle/research/run.py` |
| POL-004 | Image majors parsed consistently for enforce | `tests/test_compose.py` | `stack_oracle/compose.py` |
| POL-005 | `inventory` scans compose only (no network) | `tests/test_lsio_bookstack_smoke.py` (`inventory_repo`) | `stack_oracle/inventory.py` |

Deep dives: linked from [README.md](./README.md).
