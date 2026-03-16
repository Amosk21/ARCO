# EU AI Act Rules

> **Scope of this file:** Regulatory background and accuracy reference only. Do not act on anything here unless a task explicitly calls for it. Do not add ontology classes, instances, SHACL shapes, or SPARQL queries based solely on content in this file. Current implemented scope is Annex III 1(a) (biometrics/Sentinel-ID) and Annex III 5(b) (creditworthiness). Everything else is context.

## Annex III Structure
Every item follows: "AI systems **intended to be used** for [capability/process] **of** [affected entities] in [domain context]".

Full classification requires:
- System bears the relevant capability disposition (reality-side)
- Intended use specification prescribes the regulated process type (directive ICE)
- Use scenario specification constrains realization context to affected entities (directive ICE)

## Article 6(1) — Background only, not in scope
AI systems that are safety components of products governed by EU harmonised legislation listed in Annex I (medical devices, machinery, vehicles, aviation, etc.) are classified as high-risk under Article 6(1). Distinct from Annex III. Not modelled in ARCO. Recorded here so the boundary is explicit — do not build toward this without a deliberate scoping decision.

## Article 6(2) — Current ARCO scope
AI systems listed in Annex III are high-risk by default, subject to the Article 6(3) derogation below.

## Article 6(3) Derogation
An Annex III system is NOT high-risk if it does not pose a significant risk of harm to health, safety, or fundamental rights of natural persons (including by not materially influencing the outcome of decision-making). Applies where **any** of the following conditions is met:
- (a) narrow procedural task
- (b) improve the result of a previously completed human activity
- (c) detect decision-making patterns or deviations from prior decision-making patterns — where the system is not meant to replace or influence the previously completed human assessment **without proper human review** (the "without proper human review" qualifier is part of the statutory text; do not drop it)
- (d) preparatory task to an assessment relevant for Annex III use cases

**Exception**: an Annex III system that performs profiling of natural persons is ALWAYS high-risk, regardless of the above.

## Article 6(4) — Background only, not yet modelled
A provider who considers their Annex III system is NOT high-risk must document that assessment before placing the system on the market or putting it into service. Pre-market timing is legally significant. Recorded here for accuracy — derogation modelling is not currently in scope and should not be built unless explicitly tasked.

## Annex III Category 1 — Biometrics (Current Focus)
- 1(a): Remote biometric identification (NOT verification-only)
- 1(b): Biometric categorisation by sensitive attributes
- 1(c): Emotion recognition

Sentinel-ID demo covers 1(a). The verification-only exclusion should eventually be modelable.

## Current State

Pipeline is working. All previously known issues resolved as of 2026-03-08:

- `HighRisk_Determination_001` typed as `:HighRiskDetermination` ✓
- Three-gate `AnnexIII1aApplicableSystem` equivalentClass axiom implemented and tested ✓
  - Gate 2: `owl:someValuesFrom :RemoteBiometricIdentificationProcess` — prescribes a *typed* process token, not just any process; a system documented as on-site fingerprint enrollment fails Gate 2
  - Gate 3: `owl:hasValue :NaturalPersonRole` — checks role category (universal), not a role-bearer instance; intentional design for extensibility
- SHACL `SystemShape` targets `SystemComponent` (not hardware-only) ✓
- Two-layer architecture in place: OWL-RL classification + SPARQL ASK audit layer, explicitly separated in pipeline and certificate output ✓
- Gate-removal regression tests (`test_gate_removal.py`) pass: each gate is independently necessary ✓

Current pipeline counts: ~324 asserted → ~1066 entailed (+742).
