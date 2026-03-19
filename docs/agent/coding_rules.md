# Coding Rules

## Tech Stack
- Python 3.10+, rdflib, pyshacl, owlrl
- OWL 2 (Turtle syntax), SHACL, SPARQL ASK queries
- OWL-RL reasoning profile via owlrl
- GitHub Actions CI (`.github/workflows/arco-demo.yml`)

## Repository Structure
```
03_TECHNICAL_CORE/
  ontology/
    ARCO_core.ttl              — Core ontology (BFO-aligned classes, bridge axioms)
    ARCO_governance_extension.ttl — Provider roles, documentation workflow
    ARCO_instances_sentinel.ttl   — Sentinel-ID demo instances
  validation/
    assessment_documentation_shape.ttl — SHACL shapes
  reasoning/
    check_high_risk_inference.sparql
    check_assessment_traceability.sparql
    detect_latent_risk.sparql
    ask_provider_role_inheres_in_org.sparql
    check_annex_iii_1a_entailment.sparql
    check_intended_use.sparql
    check_obligation_link.sparql
  scripts/
    run_pipeline.py            — Main execution pipeline
    test_gate_removal.py       — Gate-removal regression test
    test_scenarios.py          — Multi-scenario classification regression test
```

## Regression Testing
Run `python 03_TECHNICAL_CORE/scripts/run_pipeline.py` after every coherent unit of change.

Pass criteria (two-layer):
- **Classification layer** (OWL-RL + SHACL): OWL-RL reasoning runs without exception, SHACL conforms, HighRiskSystem entailment succeeds
- **Audit layer** (SPARQL ASK on reasoned graph): all SPARQL audit queries return True
- Certificate emits with correct field values
- Both layers report PASS, "ALL CHECKS PASSED" prints, exit 0

SPARQL audit queries inspect documentary completeness on the reasoned graph. They do not produce or affect the classification result. An audit failure means incomplete documentation, not a wrong classification.

Do not batch changes that touch existing triples, restrictions, or shapes — test immediately.

## Pipeline
Load ontology + instances → OWL-RL reasoning → SHACL validation → SPARQL ASK queries → emit REGULATORY DETERMINATION CERTIFICATE → write artifacts to `runs/demo/`
