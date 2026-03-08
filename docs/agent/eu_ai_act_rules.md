# EU AI Act Rules

## Annex III Structure
Every item follows: "AI systems **intended to be used** for [capability/process] **of** [affected entities] in [domain context]".

Full classification requires:
- System bears the relevant capability disposition (reality-side)
- Intended use specification prescribes the regulated process type (directive ICE)
- Use scenario specification constrains realization context to affected entities (directive ICE)

## Article 6(3) Derogation
An Annex III system may NOT be high-risk if it "does not pose a significant risk of harm":
- (a) narrow procedural task
- (b) improve result of previously completed human activity
- (c) detect decision-making patterns without replacing/influencing assessment
- (d) preparatory task

**Exception**: profiling of natural persons ALWAYS triggers high-risk.

Model derogation claims as ICE artifacts (descriptive, asserting non-significance) that can be queried.

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
