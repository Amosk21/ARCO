# Ontology Rules — `03_TECHNICAL_CORE/ontology/`

Governs: `ARCO_core.ttl`, `ARCO_governance_extension.ttl`, `ARCO_instances_sentinel.ttl`

Full hard constraints and patterns: `docs/agent/ontology_rules.md` — read before any substantive edit.
EU AI Act classification logic: `docs/agent/eu_ai_act_rules.md` — read for Annex III work.

## Pre-Edit Checklist

- [ ] Architectural Memory in root `CLAUDE.md` consulted — do not read TTL to answer conceptual questions
- [ ] Every new class traces to a named BFO 2020 universal (state which one explicitly)
- [ ] Every relation uses a BFO/RO/IAO/CCO IRI — no custom object properties
- [ ] Subsumption is defensible: every instance of the subclass IS necessarily an instance of the superclass (the Barry Smith test)
- [ ] Removed-enabling-axiom test run: if the axiom is removed, does the inference break? If not, it is not doing reasoning work — it is lookup
- [ ] Reality/representation boundary maintained: dispositions in independent continuants; determinations/specs in ICEs
- [ ] New Annex III capability categories extend `AnnexIIITriggeringCapability` via direct subclassing only (no union axioms); `AnnexIIITriggeringCapability` and `HighRiskSystem` live in governance extension, not core
- [ ] Gate 2 `owl:someValuesFrom :RemoteBiometricIdentificationProcess` not relaxed to existence-only
- [ ] Gate 3 `owl:hasValue :NaturalPersonRole` not changed to a role-bearer instance
- [ ] Pipeline passes after change: `python 03_TECHNICAL_CORE/scripts/run_pipeline.py`

## Hard Stops

**False subsumption** — The canonical error: VisionCapability ⊑ BiometricIdentificationCapability. Vision is not a species of biometric identification. Subsumption means every-instance-is, necessarily. If you cannot state that universally and defend it empirically, do not create the subsumption.

**Scope boundary** — Currently Annex III 1(a) (biometrics) and 5(b) (creditworthiness). Do not add other Annex III categories without an explicit instruction to do so. Each category requires separate instance data, SPARQL tests, gate-removal regression coverage, and business traceability. Follow `docs/agent/extension_protocol.md`.

**Model/software typing** — Trained models are `SoftwareArtifact ⊑ ICE`. They cannot bear dispositions (BFO: dispositions inhere in independent continuants). Dispositions inhere in the hardware infrastructure that concretizes the model.

**No future particulars** — Intent = DirectiveICEs about universals (classes). Do not instantiate unoccurred processes.

**NaturalPerson is a role** — `NaturalPersonRole ⊑ bfo:0000023 (Role)`. Not a biological subclass of Person/Object. No person instances. Use `iao:0000136` aboutness only.

## Ontology Stability Contract

Every ontology edit must preserve all of the following. If any is violated, the edit is not complete:

- **Bucket discipline** — every instance stays in its correct BFO category (Disposition, Process, ICE, Role, Object, etc.). An instance cannot migrate between categories as a side effect of a "refactor."
- **Entailment behavior** — existing inferences must still fire after the change; no new inferences fire from unchanged instance data
- **Gate integrity** — the three-gate `AnnexIII1aApplicableSystem` equivalentClass axiom must fire if and only if all three conditions are independently satisfied; no change may make it fire with fewer
- **Semantics stability** — changes that appear stylistic (reordering axioms, renaming blank nodes, reformatting Turtle) must not alter what the reasoner produces; verify by comparing triple counts before and after

Before finalizing any TTL edit: run `python 03_TECHNICAL_CORE/scripts/run_pipeline.py` and `python 03_TECHNICAL_CORE/scripts/test_gate_removal.py`. Entailed triple count must be ≥ the pre-edit count. Gate tests must all pass independently.

Axiom edits that look cosmetic are often not. When uncertain whether a change alters entailment behavior, compare triple counts with and without the change.

## Good / Bad Examples

```
Bad:  :VisionCapability rdfs:subClassOf :BiometricIdentificationCapability .
Good: Assert both dispositions independently on the instance if the evidence supports both.

Bad:  :ModelComponent rdf:type owl:Class ; rdfs:subClassOf bfo:0000030 .
Good: :SoftwareArtifact rdf:type owl:Class ; rdfs:subClassOf iao:0000030 .

Bad:  Gate 2 checks existence of any IntendedUseSpecification is_about system.
Good: Gate 2 requires owl:someValuesFrom :RemoteBiometricIdentificationProcess — the token must be typed.

Bad:  :hasSystemicRiskIndicator rdf:type owl:ObjectProperty .
Good: :SystemicRiskIndicator iao:0000136 :SomeCapability .  (is_about, no custom property)
```
