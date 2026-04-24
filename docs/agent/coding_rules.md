# Coding Rules

## Tech Stack
- Python 3.10+, rdflib, pyshacl, owlrl
- OWL 2 (Turtle syntax), SHACL, SPARQL ASK
- OWL-RL reasoning via owlrl
- GitHub Actions CI: `.github/workflows/arco-demo.yml`

## Repository Structure
```
03_TECHNICAL_CORE/
  ontology/
    ARCO_core.ttl — Core ontology (BFO-aligned, bridge axioms)
    ARCO_governance_extension.ttl — Provider roles, doc workflow
    ARCO_instances_sentinel.ttl — Sentinel-ID demo
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
    run_pipeline.py — Main execution
    test_gate_removal.py — Gate-removal regression
    test_scenarios.py — Multi-scenario classification regression
```

## Regression Testing
Run `python 03_TECHNICAL_CORE/scripts/run_pipeline.py` after every coherent change.

Pass criteria (two-layer):
- **Classification** (OWL-RL + SHACL): OWL-RL succeeds, SHACL conforms, `HighRiskSystem` latent-risk flag entails when Gate 1 is present, and category-specific classes such as `AnnexIII1aApplicableSystem` / `AnnexIII5bApplicableSystem` entail only when all applicable gates are present
- **Audit** (SPARQL ASK on reasoned graph): all queries return True
- Certificate emits with correct field values
- Both layers PASS, "ALL CHECKS PASSED" prints, exit 0

SPARQL queries inspect documentary completeness post-reasoning. They document, not produce classification. Audit failure = incomplete documentation, not wrong classification.

Don't batch changes to triples, restrictions, or shapes — test immediately.

## Pipeline
Load ontology + instances → OWL-RL reasoning → SHACL validation → SPARQL ASK → emit ARCO CONDITION ASSESSMENT CERTIFICATE → write artifacts to `runs/demo/`
