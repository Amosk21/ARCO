# Guard-test fixtures

`probe_ice_subfamily_trap.ttl` is the one committed probe fixture: a
standalone minimal fixture in which a single Information Content Entity
individual asserts both `cco:designates` and `cco:prescribes`, which the
pinned CCO disjointness makes unsatisfiable. `test_ice_subfamily_trap.py`
in `03_TECHNICAL_CORE/scripts/` asserts the pipeline fails closed on it
(exit 1, naming the disjoint pair). It lives in `probes/`, outside the
`ARCO_instances_*` glob the fixture batteries sweep, because it is
deliberately inconsistent and must never enter a merged inventory or
reasoning battery.

The Gate-2 mistype cases need no fixture files: `test_gate2_mistype.py`
mutates the committed sentinel fixture programmatically (one rdf:type swap
in memory), so the mutants can never drift from the sentinel.
