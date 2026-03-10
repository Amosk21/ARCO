# ARCO Post-Change Validation Memo

**Date:** 2026-03-10
**Branch:** `claude/sql-ontology-graphrag-s4DIH`
**Pipeline:** ALL CHECKS PASSED · ALL GATE-REMOVAL TESTS PASSED
**Cross-system entailment checks:** 9/9 PASSED

---

## What changed

**Architecture — no semantic change to Sentinel:**

- `AnnexIIITriggeringCapability` and `HighRiskSystem` moved from `ARCO_core.ttl` → `ARCO_governance_extension.ttl`. Rationale: both are regulatory grouping concepts, not BFO natural kinds; what makes a capability "triggering" is the legal text, not a mind-independent property in reality.
- `AnnexIIITriggeringCapability` definition changed from `owl:equivalentClass [owl:unionOf (:BiometricIdentificationCapability)]` to `rdfs:subClassOf :CapabilityDisposition` with a direct `BiometricIdentificationCapability rdfs:subClassOf :AnnexIIITriggeringCapability` assertion. Semantically equivalent for the prior Sentinel path and current triggering-capability cases; scales by adding subclass assertions rather than editing a union.

**New reality-side classes (`ARCO_core.ttl`, section 1):**

- `BiometricVerificationCapability` — sibling of `BiometricIdentificationCapability`, not a subclass. Models the 1:1 vs 1:N legal distinction structurally.
- `CreditworthinessEvaluationCapability` — new domain universal (hardware genuinely has or lacks this capacity).

**New governance-layer content (`ARCO_governance_extension.ttl`):**

- `CreditworthinessEvaluationCapability rdfs:subClassOf :AnnexIIITriggeringCapability` — regulatory grouping assertion; `BiometricVerificationCapability` is explicitly not subclassed here.
- `BiometricVerificationProcess`, `CreditworthinessEvaluationProcess` — process classes used as Gate 2 type-check targets.
- `AnnexIII5bApplicableSystem` — three-gate `owl:equivalentClass` following the exact 1(a) structural pattern. Gate 2 requires an `IntendedUseSpecification` that `cco:prescribes` a typed `CreditworthinessEvaluationProcess` token — genuine type-check, not existence-only.
- `cco:DescriptiveInformationContentEntity` stub + Three D's subtyping of existing ICE classes. Supporting alignment only; no classification logic depends on it.

**New instance files:**

- `ARCO_instances_verification.ttl` — VerificationKiosk_001 (negative case)
- `ARCO_instances_creditscoring.ttl` — CreditScorer_001 (second positive case)

---

## What stayed invariant

- Sentinel classification outcomes and total reasoning delta are unchanged from the pre-merge baseline.
- Sentinel reasoning delta: 400 asserted → 1291 total (+891 inferred) — confirmed identical post-merge.
- All gate-removal tests for `AnnexIII1aApplicableSystem` pass identically (8/8 mutations).
- No existing class, instance, property, or inference chain was deleted or modified. All changes are additions.
- `BiometricVerificationCapability` has no subclass path to `AnnexIIITriggeringCapability` — this is structural, not asserted.

---

## What new positive entailments now exist

Cross-system checks run against all three instance files loaded together (1622 total triples post-reasoning, strictest condition):

| System | Class | Entailed |
|---|---|---|
| Sentinel_ID_System | HighRiskSystem | YES |
| Sentinel_ID_System | AnnexIII1aApplicableSystem | YES |
| CreditScorer_001 | HighRiskSystem | YES |
| CreditScorer_001 | AnnexIII5bApplicableSystem | YES |

---

## What new non-entailments now exist

All verified against the fully populated graph (all three instance files):

| System | Class | Entailed | Why not |
|---|---|---|---|
| VerificationKiosk_001 | HighRiskSystem | NO | `BiometricVerificationCapability` not in `AnnexIIITriggeringCapability`; Gate 1 fails |
| VerificationKiosk_001 | AnnexIII1aApplicableSystem | NO | Same; Gate 1 fails |
| VerificationKiosk_001 | AnnexIII5bApplicableSystem | NO | No creditworthiness capability |
| CreditScorer_001 | AnnexIII1aApplicableSystem | NO | No biometric identification capability; Gate 1 of 1(a) fails |
| Sentinel_ID_System | AnnexIII5bApplicableSystem | NO | No creditworthiness capability; Gate 1 of 5(b) fails |

All non-entailment claims hold under OWA. No closed-world assertion is made.

---

## What legal scope is still deferred

- Annex III 5(b) micro-enterprise exclusions
- Annex III 5(b) fraud-detection exception
- All other Annex III categories beyond 1(a) and the 5(b) pattern demonstrated here
- Multi-system deployments and shared-component scenarios
- Article 6(2) and Annex II (harmonised standards path to high-risk)
- Prohibited AI systems (Article 5)

---

## What public claims are now safe

**Safe:**

- "ARCO demonstrates two Annex III classification patterns under the same deterministic OWL-RL architecture."
- "Biometric verification (1:1) is structurally excluded from Annex III 1(a) under the current model — the non-entailment is enforced by class structure, not by assertion."
- "Creditworthiness evaluation triggers a second high-risk / Annex III applicable-system path under the current positive-path model."
- "All classifications are inferred by the OWL-RL reasoner, not asserted or pattern-matched."
- "Sentinel pipeline: 400 asserted triples → +891 inferred, all checks pass, unchanged from the pre-merge baseline."

**Not safe yet:**

- "ARCO covers Annex III 5(b)." — exclusions not modeled.
- "ARCO handles creditworthiness evaluation fully." — same reason.
- Any claim that the Three D's ICE typing adds to classification correctness.
- Any claim about systems not explicitly modeled in the three instance files.

---

## Operational status

- Certificate generation remains single-system per pipeline invocation (`SYSTEM_LOCAL` in `run_pipeline.py`).
- Cross-system entailment checks were run on the merged validation graph as a separate validation step; they are not part of the certificate workflow.
- Multi-system artifact generation is deferred.

---

## What not to do next

- Do not add more Annex III categories immediately.
- Do not build intake automation or multi-system pipeline mode.
- Do not refactor the certificate workflow.

Freeze, review, pressure-test claims.
