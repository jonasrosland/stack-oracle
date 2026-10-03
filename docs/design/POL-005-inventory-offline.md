# POL-005 — `inventory` is offline

**MUST:** `stack-oracle inventory` walks compose files under `--root` and prints a draft manifest from `depends_on` and service images. No network.

**SHOULD:** Operators diff inventory output against committed manifest; Oracle does not auto-commit drafts.

## Enforcement

- `stack_oracle.inventory.inventory_repo`
- `tests/test_lsio_bookstack_smoke.py::test_example_inventory_finds_bookstack_mariadb_edge`
