# Guard-test fixtures

These three TTL files are committed adversarial probe fixtures. They are the
inputs to `test_ice_subfamily_trap.py` and `test_gate2_mistype.py` in
`03_TECHNICAL_CORE/scripts/`, which run in the smoke-test workflow on every
push and pull request to main.

## Why they live in `ontology/probes/`

1. Battery isolation is structural, not name-based. The existing sweeps over
   the fixture set are non-recursive globs rooted at
   `03_TECHNICAL_CORE/ontology/`: `test_tbox_guard.py:81` and
   `test_canonical_iris.py:38` glob `ARCO_instances_*.ttl`. A `probes/`
   subdirectory is invisible to both, and the files also avoid the
   `ARCO_instances_*` name prefix as a second layer of protection. That
   matters most for the trap fixture, which is deliberately inconsistent and
   must never enter a merged inventory or reasoning battery.
2. They are ontology data, not code. The pipeline consumes them via
   `--instances`; keeping them under `ontology/` keeps the data/code split
   clean.
3. Scripts-adjacent placement buys nothing: the tests resolve paths from the
   repo root either way.

Cost of the choice, disclosed: fixtures in `probes/` are not covered by
`test_canonical_iris.py`'s IRI-pin sweep. The two mistype fixtures differ from
the already-swept sentinel fixture by one logic triple each (see below), and
the trap fixture's IRIs are exercised by its own guard test, so the exposure
is small. Extending the canonical-IRI glob to `probes/` is a cheap optional
follow-on.

## Files

| File | What it is | Guard test |
|---|---|---|
| `probe_ice_subfamily_trap.ttl` | Standalone minimal fixture: one ICE individual asserting both `cco:designates` and `cco:prescribes`, which the pinned CCO disjointness makes unsatisfiable. The guard asserts the pipeline fails closed (exit 1, naming the disjoint pair). | `test_ice_subfamily_trap.py` |
| `probe_gate2_mistyped_kind.ttl` | Sentinel-derived mutant: the Gate-2 prescribed-process token is typed `:BiometricVerificationProcess` instead of the regulated kind. Logic delta from the sentinel fixture is exactly one `rdf:type` triple; header text and some explanatory annotation triples differ. The guard asserts 1(a) is not entailed while the latent flag stays on. | `test_gate2_mistype.py` |
| `probe_gate2_neither_kind.ttl` | Same construction with the token typed only `:OperationalProcess` (neither regulated kind). | `test_gate2_mistype.py` |
