# Pipeline and Scripting Rules — `03_TECHNICAL_CORE/scripts/`

Governs: `run_pipeline.py`, `test_gate_removal.py`, `.github/workflows/`

Full coding rules: `docs/agent/coding_rules.md`

## Pass Criteria

Every pipeline run must satisfy both layers:
- **Classification layer**: OWL-RL reasoning executes without exception, SHACL conforms (zero violations), HighRiskSystem entailment succeeds
- **Audit layer**: All SPARQL ASK queries return True (documentary completeness on the reasoned graph)
- Certificate emits with correct field values
- Both layers report PASS, "ALL CHECKS PASSED" prints, exit 0

SPARQL audit queries do not produce or affect the classification result. An audit failure indicates incomplete documentation, not a wrong classification.

## Pre-Edit Checklist

- [ ] New pipeline check is labelled by layer: classification (OWL-RL entailment) or audit (SPARQL ASK on reasoned graph)
- [ ] Certificate output does not display "VERIFIED" for a result unless OWL entailment for that result is in the graph
- [ ] If a new SPARQL query is added, it is wired into the pipeline's query list and has a labelled certificate line
- [ ] `test_gate_removal.py` updated if any gate axiom changes (each gate must independently break the entailment when removed)
- [ ] CI workflow not modified unless the pipeline output format has changed
- [ ] Pipeline passes end-to-end after the change

## Hard Stops

**Certificate must not overstate entailment** — If `AnnexIII1aApplicableSystem` is not entailed by OWL-RL, the certificate must not print "VERIFIED" for it. The certificate reflects the graph, not assumptions.

**Two-layer labelling** — Classification outputs (OWL-RL) and audit outputs (SPARQL) must be visually distinguishable in the certificate. Do not merge them into a single flat list that obscures which layer produced which result.

**Gate regression must stay wired** — `test_gate_removal.py` must always test each gate independently. If gate axioms change, update the test. Never remove gate tests.

**No hardcoded expected values** — Pipeline assertions about entailed triple counts should use a minimum threshold (e.g., `> asserted_count`), not an exact expected value that silently passes on a wrong reasoner run.

**Certificate field integrity** — Every certificate field must reflect a specific formal result from a specific layer. No field may be hardcoded, approximated, or inferred from another field:
- Classification fields (`HighRiskSystem`, `AnnexIII1a`) → presence in OWL-RL graph post-reasoning
- Validation field (`SHACL`) → pyshacl conformance return value
- Audit fields (`Traceability`, `Latent Risk`, `Intended Use`, `Obligation`, `Reg. Aligned`) → individual SPARQL ASK return values
- Triple counts → actual reasoner output, not a stored constant
