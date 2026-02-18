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
```

## Regression Testing
Run `python 03_TECHNICAL_CORE/scripts/run_pipeline.py` after every coherent unit of change.

Pass criteria:
- OWL-RL reasoning runs
- All SPARQL queries return True
- SHACL conforms
- Certificate emits
- "ALL CHECKS PASSED" prints
- Exit 0

Do not batch changes that touch existing triples, restrictions, or shapes — test immediately.

## Pipeline
Load ontology + instances → OWL-RL reasoning → SHACL validation → SPARQL ASK queries → emit REGULATORY DETERMINATION CERTIFICATE → write artifacts to `runs/demo/`
