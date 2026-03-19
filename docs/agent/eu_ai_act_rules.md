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

## Annex III Category 1 — Biometrics
- 1(a): Remote biometric identification (NOT verification-only) — **implemented**
- 1(b): Biometric categorisation by sensitive attributes — not yet modeled
- 1(c): Emotion recognition — not yet modeled

Sentinel-ID demo covers 1(a). The verification-only exclusion is modeled (BiometricVerificationCapability exists but is NOT subclassed under AnnexIIITriggeringCapability).

## Annex III Category 5 — Access to Essential Services
- 5(b): Creditworthiness evaluation of natural persons — **implemented**

CreditScorer demo covers 5(b). Cross-category isolation is enforced by the ontology: a biometric system is NOT entailed as 5(b), and a credit scorer is NOT entailed as 1(a).

## Current State

Pipeline is working. All previously known issues resolved as of 2026-03-18:

- `HighRisk_Determination_001` typed as `:HighRiskDetermination` ✓
- Three-gate `AnnexIII1aApplicableSystem` equivalentClass axiom implemented and tested ✓
- Three-gate `AnnexIII5bApplicableSystem` equivalentClass axiom implemented and tested ✓
  - Gate 2: `owl:someValuesFrom` on category-specific process class — prescribes a *typed* process token, not just any process
  - Gate 3: `owl:hasValue :NaturalPersonRole` — checks role category (universal), not a role-bearer instance
- `HighRiskSystem` bridge axiom requires `SystemComponent` in the has_part chain ✓
- SHACL `SystemShape` targets `SystemComponent` (not hardware-only) ✓
- Two-layer architecture in place: OWL-RL classification + SPARQL ASK audit layer, explicitly separated in pipeline and certificate output ✓
- Classification pass and audit pass computed independently ✓
- Gate-removal regression tests (`test_gate_removal.py`) pass: each gate is independently necessary, including content-mutation tests ✓

Current pipeline counts (sentinel): 1423 asserted → 4865 entailed (+3442, includes BFO 2020 import).
