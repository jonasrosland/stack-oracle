# LinuxServer BookStack + MariaDB (example)

[BookStack](https://docs.linuxserver.io/images/docker-bookstack/) on LinuxServer.io **depends on an external MariaDB** (same pattern as UniFi + Mongo in homelab-config).

Use this tree for Stack Oracle smoke tests (`tests/test_lsio_bookstack_smoke.py`):

- Valid pins: `mariadb:10.11` with `dependency_max_major: 10`
- Failure cases: MariaDB 11+, wrong manifest compose path, invalid compose YAML

Not deployed in homelab-config; for tooling demos and CI only.
