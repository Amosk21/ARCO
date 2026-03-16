# EU AI Act Rules

## Annex III Structure
Every item follows: "AI systems **intended to be used** for [capability/process] **of** [affected entities] in [domain context]".

Full classification requires:
- System bears the relevant capability disposition (reality-side)
- Intended use specification prescribes the regulated process type (directive ICE)
- Use scenario specification constrains realization context to affected entities (directive ICE)

## Article 6(1) — Separate High-Risk Pathway (Not Currently in ARCO Scope)
AI systems that are safety components of products governed by EU harmonised legislation listed in Annex I (medical devices, machinery, vehicles, aviation, etc.) are classified as high-risk under Article 6(1). This pathway is distinct from Annex III and is not currently modelled in ARCO. Any extension to safety-component classification must track this separately.

## Article 6(2) — Annex III Pathway (Current ARCO Scope)
AI systems listed in Annex III are high-risk by default, subject to the Article 6(3) derogation below.

## Article 6(3) Derogation
An Annex III system is NOT high-risk if it does not pose a significant risk of harm to health, safety, or fundamental rights of natural persons (including by not materially influencing the outcome of decision-making). Applies where **any** of the following conditions is met:
- (a) narrow procedural task
- (b) improve the result of a previously completed human activity
- (c) detect decision-making patterns or deviations from prior decision-making patterns — where the system is not meant to replace or influence the previously completed human assessment **without proper human review** (the "without proper human review" qualifier is part of the statutory text; do not drop it)
- (d) preparatory task to an assessment relevant for Annex III use cases

**Exception**: an Annex III system that performs profiling of natural persons is ALWAYS high-risk, regardless of the above.

## Article 6(4) — Documentation Obligation for Derogation Claims
A provider who considers their Annex III system is NOT high-risk must **document that assessment before placing the system on the market or putting it into service**. Model derogation claims as ICE artifacts (descriptive, asserting non-significance) that can be queried. The pre-market timing of the documentation obligation is legally significant — post-hoc derogation claims are not compliant.

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
