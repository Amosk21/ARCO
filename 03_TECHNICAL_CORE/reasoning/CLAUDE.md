# SPARQL Audit Rules — `03_TECHNICAL_CORE/reasoning/`

Governs: all `*.sparql` files

Full EU AI Act classification logic: `docs/agent/eu_ai_act_rules.md`

## What These Queries Are

These are AUDIT queries. They run on the post-OWL-RL-reasoning graph. They inspect what the reasoner produced; they do not produce the classification.

- **Classification** = OWL-RL entailment. The reasoner infers `rdf:type AnnexIII1aApplicableSystem` (or `HighRiskSystem`) from bridge axioms and instance data. This is in the graph.
- **Audit** = SPARQL ASK confirming that the right documentary content is explicitly declared and aligned with what the classification requires.

Never describe a SPARQL ASK query as "the system that classifies" or "the check that determines if a system is high-risk." That is the OWL reasoner's job. The SPARQL layer confirms; it does not determine.

## Pre-Edit Checklist

- [ ] New query is ASK (boolean), not SELECT
- [ ] Query target is the post-reasoning graph (entailed triples are available)
- [ ] Query is audit-layer: it checks declared documentary content, not re-derives OWL entailment
- [ ] Query result is consistent with what OWL-RL already entailed — no certificate contradiction possible
- [ ] Query labelled correctly in `run_pipeline.py` (classification layer vs. audit layer)
- [ ] Certificate line for the query does not overstate the layer (audit PASS ≠ classification VERIFIED)
- [ ] Pipeline passes: `python 03_TECHNICAL_CORE/scripts/run_pipeline.py`

## Hard Stops

**Audit ≠ classification** — A SPARQL ASK returning TRUE does not mean the system is classified. A SPARQL ASK returning FALSE does not mean the OWL classification is wrong. Each layer has its own semantics. If they contradict, diagnose — don't patch one to match the other.

**No certificate contradiction** — If OWL says `AnnexIII1aApplicableSystem = ENTAILED` and a SPARQL query returns FALSE for the same condition, that is a design error in the query or the gate. Fix the source of the contradiction; do not suppress the check.

**No IRI-matching where type-level is correct** — Use `rdf:type/rdfs:subClassOf*` pattern queries when the condition is about class membership, not individual IRI equality.

**No re-implementing OWL gates in SPARQL** — If a SPARQL query duplicates the three-gate OWL equivalentClass condition, you have two classification engines. The OWL gate is authoritative; SPARQL audits its documentary inputs.

## Good / Bad Examples

```
Bad:  "The check_annex_iii_1a_entailment.sparql query classifies the system as high-risk."
Good: "The check_annex_iii_1a_entailment.sparql query verifies that the OWL reasoner entailed
      AnnexIII1aApplicableSystem — it reads a classification already in the graph."

Bad:  ASK WHERE { :Sentinel_ID_System :hasRisk :HighRisk . }  (IRI-matching a custom property)
Good: ASK WHERE { :Sentinel_ID_System rdf:type :HighRiskSystem . }  (type membership)

Bad:  Certificate prints "ANNEX III 1(a): VERIFIED" while check_regulatory_alignment returns FAIL
      for the same condition — contradiction to an auditor reading the certificate.
Good: Investigate which layer is wrong; fix the gate content or the audit query to eliminate
      the contradiction before emitting the certificate.
```
