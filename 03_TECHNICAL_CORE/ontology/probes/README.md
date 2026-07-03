# Guard-test fixtures — intended repo location

These three TTL files are the committed-fixture versions of the P3.3 probes
whose test promotion was recommended unconditionally
(`../../P3_3_adversarial_probes.md`, probes 2, 3a, 3b). They are inputs to
`test_ice_subfamily_trap.py` and `test_gate2_mistype.py` in the parent
directory.

## Recommended location: `03_TECHNICAL_CORE/ontology/probes/`

Recommendation between the two candidates named in the P7 brief
(`03_TECHNICAL_CORE/ontology/probes/` vs scripts-adjacent):
**`03_TECHNICAL_CORE/ontology/probes/`**, for three reasons:

1. **Battery isolation is structural, not name-based.** Every existing sweep
   over the fixture set is a non-recursive glob rooted at
   `03_TECHNICAL_CORE/ontology/`: `test_tbox_guard.py:81` and
   `test_canonical_iris.py:38` glob `ARCO_instances_*.ttl`; the program's own
   `p21_iri_audit.py` and `p24_punning_inventory.py` glob `*.ttl` in that
   directory. A `probes/` subdirectory is invisible to all of them (verified
   against the four scripts named). That matters most for the trap fixture,
   which is deliberately inconsistent and must never enter a merged
   inventory or fixture battery. The fixtures also avoid the
   `ARCO_instances_*` name prefix as a second layer of glob protection.
2. **They are ontology data, not code.** The pipeline consumes them via
   `--instances`; keeping them under `ontology/` keeps the data/code split
   clean, and `run_pipeline.py --instances` accepts the relative path
   directly.
3. **Scripts-adjacent placement buys nothing:** the tests resolve paths from
   `REPO_ROOT` either way, and a TTL file sitting in `scripts/` would be the
   only ontology artifact outside `ontology/`.

Cost of the choice, disclosed: fixtures in `probes/` are NOT covered by
`test_canonical_iris.py`'s IRI-pin sweep. The two mistype fixtures are
single-triple mutants of the already-swept sentinel fixture, and the trap
fixture's IRIs are pipeline-verified by its own guard test, so the exposure is
small; extending the canonical-IRI glob to `probes/` (excluding the
deliberately inconsistent trap from any *reasoning* battery, not from text
checks) is a cheap optional follow-on.

## Files

| File | Origin probe | Delta from committed fixture | Guard test |
|---|---|---|---|
| `probe_ice_subfamily_trap.ttl` | P3.3 probe 2 (individuals renamed `Probe2_*` → `ICETrap_*`; committed-guard header with the F-053 authoring warning) | standalone minimal fixture | `test_ice_subfamily_trap.py` |
| `probe_gate2_mistyped_kind.ttl` | P3.3 probe 3a (header updated; body unchanged) | sentinel + 1 triple: Gate-2 token typed `:BiometricVerificationProcess` | `test_gate2_mistype.py` |
| `probe_gate2_neither_kind.ttl` | P3.3 probe 3b (header updated; body unchanged) | sentinel + 1 triple: Gate-2 token typed `:OperationalProcess` | `test_gate2_mistype.py` |

The tests in the parent directory hardcode
`ONTOLOGY_DIR / "probes" / <name>` and are written for their intended home,
`03_TECHNICAL_CORE/scripts/`. Landing = copy the two test files to
`03_TECHNICAL_CORE/scripts/`, the three fixtures to
`03_TECHNICAL_CORE/ontology/probes/`, and add the two smoke-test workflow
steps (see `../ci_guards/workflows/arco-smoke-test.additions.diff`).
