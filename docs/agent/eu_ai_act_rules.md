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

## Current Known Issues

**Pipeline is working.** These remain:

1. **Instance typing**: `HighRisk_Determination_001` typed as `:ComplianceDetermination` — should be `:HighRiskDetermination`
2. **No intended use modeling**: Bridge axiom fires on capability alone without intended use context — ontologically incomplete per Annex III
3. **Hardware-only component constraint**: `SystemShape` SHACL requires hardware components only — should allow broader `SystemComponent`
