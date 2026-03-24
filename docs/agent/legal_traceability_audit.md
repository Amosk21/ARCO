# Legal-to-Ontology Traceability Audit

_Date: 2026-03-19 · Scope: Annex III 1(a) and 5(b) · Status: DRAFT — awaiting human review_

## Purpose

Determine whether ARCO's three-gate decomposition is a defensible encoding of the EU AI Act legal text, and name every interpretive move explicitly.

This is not an ontology quality review or a BFO alignment check. It is a legal-to-formal-encoding traceability audit.

---

## Legal Text Inventory (Verbatim Excerpts)

**Article 6(2):**
> "In addition to the high-risk AI systems referred to in paragraph 1, AI systems referred to in Annex III shall be considered to be high-risk."

**Article 6(3):**
> "By derogation from paragraph 2, an AI system referred to in Annex III shall not be considered to be high-risk where it does not pose a significant risk of harm to the health, safety or fundamental rights of natural persons, including by not materially influencing the outcome of decision making."
>
> Conditions: (a) narrow procedural task; (b) improve result of previously completed human activity; (c) detect decision-making patterns without replacing/influencing assessment; (d) preparatory task. Override: profiling of natural persons ALWAYS triggers high-risk.

**Article 3(12) — "intended purpose":**
> "'intended purpose' means the use for which an AI system is intended by the provider, including the specific context and conditions of use, as specified in the information supplied by the provider in the instructions for use, promotional or sales materials and statements, as well as in the technical documentation."

**Article 3(41) — "remote biometric identification system":**
_(Note: ARCO documentation previously cited this as Article 3(36). Corrected 2026-03-24 after backtest against Regulation 2024/1689. Article 3(35) defines "biometric identification"; Article 3(36) defines "biometric verification.")_
> "'remote biometric identification system' means an AI system for the purpose of identifying natural persons, without their active involvement, typically at a distance through the comparison of a person's biometric data with the biometric data contained in a reference database."

**Annex III 1 (chapeau):**
> "Biometrics, in so far as their use is permitted under relevant Union or national law:"

**Annex III 1(a):**
> "Remote biometric identification systems. This shall not include AI systems intended to be used for biometric verification the sole purpose of which is to confirm that a specific natural person is the person he or she claims to be."

**Annex III 5(b):**
> "AI systems intended to be used to evaluate the creditworthiness of natural persons or establish their credit score, with the exception of AI systems used for the purpose of detecting financial fraud."

**Recital 17** (definition of remote biometric identification):
> "The notion of 'remote biometric identification system' [...] should be defined functionally, as an AI system intended for the identification of natural persons without their active involvement, typically at a distance, through the comparison of a person's biometric data with the biometric data contained in a reference database [...] This excludes AI systems intended to be used for biometric verification, which includes authentication, the sole purpose of which is to confirm that a specific natural person is the person he or she claims to be."

**Recital 54** (biometrics as high-risk):
> "Remote biometric identification systems should therefore be classified as high-risk in view of the risks that they pose. Such a classification excludes AI systems intended to be used for biometric verification, including authentication, the sole purpose of which is to confirm that a specific natural person is who that person claims to be."

---

## Traceability Table

### Row 1: The Annex III listing mechanism itself

| Field | Content |
|---|---|
| **Legal Source** | Article 6(2) |
| **Exact Legal Text** | "In addition to the high-risk AI systems referred to in paragraph 1, AI systems referred to in Annex III shall be considered to be high-risk." |
| **ARCO Construct** | `HighRiskSystem` equivalentClass axiom (governance extension lines 156-177); `AnnexIII1aApplicableSystem` and `AnnexIII5bApplicableSystem` equivalentClass axioms |
| **Gate / Layer** | Classification layer. `HighRiskSystem` is entailed from Gate 1 alone. `AnnexIIIXApplicableSystem` is entailed from all three gates. |
| **Direct or Interpretive** | **Interpretive move.** Article 6(2) is a single-step conclusion: Annex III systems are high-risk. ARCO splits this into two classes: `HighRiskSystem` (capability-only, from Gate 1) and `AnnexIII1aApplicableSystem` (full three-gate). The law does not make this split. |
| **Why This Mapping** | `HighRiskSystem` captures "latent risk" — a system with a triggering capability is flagged even before intended use is documented. The category-specific class captures full Annex III applicability including intent and context. |
| **What It Infers** | A system with only Gate 1 satisfied is inferred as `HighRiskSystem` but NOT as `AnnexIII1aApplicableSystem`. All three gates yield both. |
| **What It Does Not Prove** | The law does not support a "latent risk" category separate from Annex III listing. Annex III includes the "intended to be used for" qualifier. A system not intended for that use is arguably not "referred to in Annex III" at all. `HighRiskSystem` based on capability alone is an ARCO policy position, not a legal requirement. |
| **Alternatives** | (A) No `HighRiskSystem` — only category-specific classes. (B) `HighRiskSystem` ≡ union of all category-specific classes (requiring all gates). (C) Two-tier with explicit labeling: `PotentiallyHighRiskSystem` (capability only) vs `HighRiskSystem` (all gates). |
| **Validation Status** | Tested (pipeline passes, gate-removal tests). Legal defensibility of capability-only `HighRiskSystem` is an unresolved interpretive assumption. |

---

### Row 2: Gate 1 — Reality-side capability requirement

| Field | Content |
|---|---|
| **Legal Source** | Annex III 1(a); Article 3(41); Recital 17 |
| **Exact Legal Text** | "Remote biometric identification systems." / "'remote biometric identification system' means an AI system for the purpose of identifying natural persons, without their active involvement, typically at a distance..." |
| **ARCO Construct** | Gate 1: `System AND has_part some (SystemComponent AND has_disposition some BiometricIdentificationCapability)` (governance extension lines 316-329) |
| **Gate / Layer** | Gate 1 / Classification layer |
| **Direct or Interpretive** | **Major interpretive move.** The law names a type of AI system defined by its purpose. It does NOT say "a system that has a hardware component bearing a biometric identification disposition." ARCO decomposes this into: (a) a material system with parts, (b) a hardware component specifically, (c) that component bearing a disposition, (d) that disposition typed as biometric identification capability. Each step is an ontological design choice. |
| **Why This Mapping** | BFO realism: dispositions inhere in independent continuants. The law's "for the purpose of identifying" is mapped to structural capability rather than functional state, because ARCO holds that regulatory classification should depend on what a system CAN do, not what it IS DOING. Stated in `ARCO_Regulatory_Determination_Case.md`: "Regulatory classification under the EU AI Act depends on capability, not intent or configuration." |
| **What It Infers** | A system is a candidate for 1(a) if and only if it has a material component bearing the right disposition. |
| **What It Does Not Prove** | (1) The law does not require a hardware component — a purely software-based biometric system would also be "referred to in Annex III." ARCO cannot classify such a system because `SoftwareArtifact ⊑ ICE`, not `SystemComponent`, and ICEs cannot bear dispositions. (2) The legal text's "for the purpose of" is about PURPOSE, not CAPABILITY. A camera module has the physical capability to capture faces but may never be intended for biometric identification. (3) Biometric identification is often an emergent capability of the whole system, not attributable to a single hardware module. |
| **Alternatives** | (A) Drop Gate 1 — let Gates 2 and 3 drive classification (closer to the literal legal text). (B) System-level disposition: `System has_disposition some BiometricIdentificationCapability`. (C) BFO Function instead of Disposition to capture "designed for" rather than "capable of." |
| **Validation Status** | Tested (gate-removal confirms independence). The interpretive assumptions are documented in CLAUDE.md but have not been validated against legal analysis. |

---

### Row 3: Gate 2 — "intended to be used for [process]"

| Field | Content |
|---|---|
| **Legal Source** | Annex III pattern; Article 3(12) |
| **Exact Legal Text** | Article 3(12): "'intended purpose' means the use for which an AI system is intended by the provider, including the specific context and conditions of use, as specified in the information supplied by the provider in the instructions for use, promotional or sales materials and statements, as well as in the technical documentation." |
| **ARCO Construct** | Gate 2: System is target of `IntendedUseSpecification` (via inverse `iao:0000136`) that `cco:prescribes some RemoteBiometricIdentificationProcess` (governance extension lines 337-349) |
| **Gate / Layer** | Gate 2 / Classification layer |
| **Direct or Interpretive** | **Two-step interpretive move.** **(A) Intent grounded in documentary artifact, not mental state.** Article 3(12) explicitly ties "intended purpose" to provider documentation. This is defensible — the law says "as specified in the information supplied by the provider." But ARCO treats a single `IntendedUseSpecification` as sufficient, while the law references multiple sources jointly (instructions, promotional materials, technical docs). **(B) "to be used for" mapped to `cco:prescribes`.** The law says the system has a purpose; ARCO says a documentary artifact prescribes a process. `cco:prescribes` imports prescriptive semantics — the document directs/governs the process, not merely describes it. This is stronger than `iao:is_about` and arguably matches the normative character of "intended purpose." |
| **Why This Mapping** | CCO's Directive/Descriptive ICE distinction: intended use is prescriptive (directs what the system should do), not descriptive (reports what it does). `iao:is_about` would be too weak. |
| **What It Infers** | If a documentary artifact typed as `IntendedUseSpecification`, about the system, prescribing a typed process instance, exists — Gate 2 fires. `owl:someValuesFrom` ensures genuine type-checking. |
| **What It Does Not Prove** | (1) The law's "intended purpose" is constituted by MULTIPLE documentary sources. ARCO uses one. A provider might claim different purposes in marketing vs technical docs. (2) Nothing enforces that the specification was authored by the provider (Article 3(12) says "intended by the provider"). (3) The process token is a placeholder for the process type, not an actual process occurrence. |
| **Alternatives** | (A) `iao:is_about` alone (weaker, loses prescriptive semantics). (B) Model multiple documentary sources and require consistency. (C) Ground intent in the system's BFO Function rather than a documentary artifact. |
| **Validation Status** | Tested (gate-removal, content-mutation). CCO alignment is stub-only. |

---

### Row 4: Gate 3 — "of natural persons"

| Field | Content |
|---|---|
| **Legal Source** | Article 3(41); Recital 17 |
| **Exact Legal Text** | "identifying natural persons, without their active involvement" |
| **ARCO Construct** | Gate 3: System is target of `UseScenarioSpecification` (via inverse `iao:0000136`) where specification `iao:0000136 :NaturalPersonRole` (`owl:hasValue`) (governance extension lines 357-370) |
| **Gate / Layer** | Gate 3 / Classification layer |
| **Direct or Interpretive** | **Three interpretive moves.** **(A) "Natural persons" modeled as a BFO Role.** The law means real human beings with legal personhood. ARCO models this as `NaturalPersonRole ⊑ bfo:0000023 (Role)`. Rationale: legal personhood is a role (externally contingent on the legal system), not a biological kind. **(B) Affected-entity constraint separated into a distinct documentary artifact.** The law says "of natural persons" as part of the same clause. ARCO splits it into a separate `UseScenarioSpecification` for independent testability. **(C) `owl:hasValue` punning on class IRI.** The specification is about the role CATEGORY (the universal), not a specific person. Class IRI used as concept-individual (OWL 2 punning). |
| **Why This Mapping** | Role vs Person avoids creating person instances. Separate document makes the gate independently testable. `hasValue` on universal: the regulation targets a category, not individuals. |
| **What It Infers** | Gate 3 fires if a `UseScenarioSpecification` about the system and about `:NaturalPersonRole` exists. |
| **What It Does Not Prove** | (1) Only checks that a document SAYS the system addresses natural persons — does not verify that the system actually interacts with them. (2) "Without their active involvement" (Article 3(41)) is NOT encoded. (3) "Typically at a distance" is NOT encoded. (4) The punning creates a fragility under CCO import (documented in alignment audit item 9). |
| **Alternatives** | (A) Merge Gate 3 into Gate 2 — affected role as a constraint on the process. (B) `owl:someValuesFrom` with typed individual (like Gate 2). (C) Model "without active involvement" and "at a distance" as additional gate conditions. |
| **Validation Status** | Tested (gate-removal). Punning dependency documented. |

---

### Row 5: Gate 2 / Gate 3 asymmetry (someValuesFrom vs hasValue)

| Field | Content |
|---|---|
| **Legal Source** | N/A — internal design asymmetry |
| **ARCO Construct** | Gate 2: `owl:someValuesFrom :RemoteBiometricIdentificationProcess`. Gate 3: `owl:hasValue :NaturalPersonRole`. |
| **Direct or Interpretive** | **Intentional design asymmetry.** Gate 2 needs a typed instance of a process (there are many possible remote biometric identification processes). Gate 3 points at the category itself (there is only one NaturalPersonRole universal). The asymmetry follows from BFO's particular/universal distinction. |
| **Why This Mapping** | Using `someValuesFrom` for Gate 3 would require minting a typed individual for the role — either an unnecessary placeholder or confusingly modeling "some natural person" rather than "natural persons as a category." |
| **What It Does Not Prove** | The asymmetry is not legally motivated — it is an OWL engineering decision. The law treats both "remote biometric identification" and "of natural persons" as parts of one clause. |
| **Alternatives** | (A) Both gates use `someValuesFrom` (requires role token). (B) Both use `hasValue` (would require process class IRI as individual — the pre-fix pattern that caused punning issues). (C) Accept asymmetry as principled (current). |
| **Validation Status** | Tested. SHACL punning dependency documented (alignment audit item 9). |

---

### Row 6: Annex III 5(b) — creditworthiness evaluation

| Field | Content |
|---|---|
| **Legal Source** | Annex III 5(b) |
| **Exact Legal Text** | "AI systems intended to be used to evaluate the creditworthiness of natural persons or establish their credit score, with the exception of AI systems used for the purpose of detecting financial fraud." |
| **ARCO Construct** | `AnnexIII5bApplicableSystem` equivalentClass (governance extension lines 393-457). Gate 1: `CreditworthinessEvaluationCapability`. Gate 2: `CreditworthinessEvaluationProcess`. Gate 3: `NaturalPersonRole`. |
| **Direct or Interpretive** | **Same three interpretive moves as 1(a), plus:** (1) The law says "evaluate the creditworthiness **or** establish their credit score" — a disjunction. ARCO collapses into `CreditworthinessEvaluationCapability`. Arguably defensible (credit scoring ⊂ creditworthiness evaluation) but the law presents them as alternatives. (2) **Fraud detection exclusion NOT modeled.** This is an explicit carve-out in the legal text, not a "nuance." (3) "For access to financial or public services" appears in the ARCO class comment but is NOT in the OWL axiom or gate structure. |
| **What It Does Not Prove** | (1) A fraud detection system that evaluates creditworthiness would be INCORRECTLY classified as high-risk. (2) The creditworthiness/credit-score distinction is collapsed. |
| **Alternatives** | (A) Separate `CreditScoreEstablishmentCapability` with a union gate. (B) Negation gate or exclusion mechanism for fraud detection. (C) Model fraud exclusion as a derogation claim that blocks classification. |
| **Validation Status** | Tested (cross-category isolation works). Fraud exclusion gap documented as deferred. |

---

### Row 7: AnnexIII_Condition_Q1 — dual role

| Field | Content |
|---|---|
| **Legal Source** | N/A — instance-level modeling question |
| **ARCO Construct** | `:AnnexIII_Condition_Q1` typed as `:RegulatoryContent` with `cco:prescribes :RemoteBiometricIdentificationProcess` and `iao:0000136` on capability, process, and role (instances_sentinel.ttl lines 23-28) |
| **Gate / Layer** | Audit/traceability only — does NOT participate in classification entailment |
| **Direct or Interpretive** | **Conflation of two roles.** This individual is both: (a) a representation of a piece of the regulation, and (b) a directive entity that prescribes a process type. The regulation itself doesn't prescribe the process — it describes what TRIGGERS classification. The `prescribes` triple is vestigial from an earlier design (Gate 2 now fires via `Sentinel_IntendedUse_001`). |
| **What It Does Not Prove** | The `prescribes` triple is misleading and is a known CCO-import blocker (class IRI as object of `prescribes`). |
| **Alternatives** | (A) Remove the vestigial `prescribes` triple. (B) Separate the regulatory content representation from the directive interpretation. |
| **Validation Status** | Known issue, documented in alignment audit v3 (lines 266-270). Does not affect classification. |

---

### Row 8: Article 6(3) derogation — not modeled

| Field | Content |
|---|---|
| **Legal Source** | Article 6(3) |
| **Exact Legal Text** | "By derogation from paragraph 2, an AI system referred to in Annex III shall not be considered to be high-risk where it does not pose a significant risk of harm..." Conditions (a)-(d). Override: profiling of natural persons ALWAYS triggers high-risk. |
| **ARCO Construct** | None. |
| **Direct or Interpretive** | **Omission.** The entire escape mechanism is missing. Every ARCO classification is potentially over-inclusive without this. |
| **Alternatives** | (A) Negation gate: `DerogationClaim` ICE that blocks classification (needs SHACL/SPARQL — OWL-RL lacks negation-as-failure). (B) Post-classification SPARQL audit check flagging when derogation might apply. (C) Post-classification review step outside the ontology. |
| **Validation Status** | Deferred. Documented in `eu_ai_act_rules.md`. |

---

### Row 9: Verification exclusion (1(a))

| Field | Content |
|---|---|
| **Legal Source** | Annex III 1(a) second sentence; Recitals 17 and 54 |
| **Exact Legal Text** | "This shall not include AI systems intended to be used for biometric verification the sole purpose of which is to confirm that a specific natural person is the person he or she claims to be." |
| **ARCO Construct** | `BiometricVerificationCapability` (core lines 77-81), `BiometricVerificationProcess` (governance extension lines 225-228). Disjointness axioms. NOT subclassed under `AnnexIIITriggeringCapability`. |
| **Direct or Interpretive** | **Partially direct.** Modeled via type disjointness: verification ≠ identification. Correct ontologically. However, the law's exclusion is conditional on "sole purpose" — a dual-purpose system might still be covered. ARCO's disjointness prevents a single disposition from being both, but a system could have TWO dispositions. Not explicitly tested. |
| **What It Does Not Prove** | "Sole purpose" condition not modeled. Purpose primacy for dual-purpose systems not addressed. |
| **Validation Status** | Tested (verification instances exist, cross-classification does not fire). |

---

### Row 10: "Without active involvement" and "at a distance" — not encoded

| Field | Content |
|---|---|
| **Legal Source** | Article 3(41); Recital 17 |
| **Exact Legal Text** | "without their active involvement, typically at a distance" |
| **ARCO Construct** | None. Not in any class, property, restriction, or gate. Not even in the `rdfs:comment` on `RemoteBiometricIdentificationProcess`. |
| **Direct or Interpretive** | **Omission.** These are defining characteristics of "remote" biometric identification. A biometric system used at close range with active subject participation would satisfy ARCO's gates but would NOT be a "remote biometric identification system" under Article 3(41). |
| **Alternatives** | (A) Properties on the process type: participation mode, range. (B) Constraints in `UseScenarioSpecification`. (C) Accept omission and document that "remote" is not formally verified. |
| **Validation Status** | Not modeled. Gap not documented in any existing file. |

---

### Row 11: Legality precondition — not modeled

| Field | Content |
|---|---|
| **Legal Source** | Annex III 1 (chapeau) |
| **Exact Legal Text** | "Biometrics, in so far as their use is permitted under relevant Union or national law" |
| **ARCO Construct** | None. |
| **Direct or Interpretive** | **Omission.** Biometric systems are listed as high-risk ONLY insofar as their use is permitted. If prohibited (e.g., Article 5), they are not merely high-risk — they are banned. ARCO cannot distinguish "high-risk but permitted" from "prohibited." |
| **Alternatives** | (A) Model Article 5 prohibitions as a pre-filter. (B) Add a legality precondition gate. (C) Document the limitation. |
| **Validation Status** | Not modeled. Not documented as a gap. |

---

## Named Interpretive Moves (Complete List)

| # | Move | Location | Defensibility |
|---|---|---|---|
| 1 | Intent grounded in documentary artifact, not mental state | Gate 2 | Strong — Article 3(12) ties intent to provider documentation |
| 2 | "To be used for" mapped to `cco:prescribes` | Gate 2 | Defensible — captures prescriptive/normative character |
| 3 | Reality-side capability requirement added | Gate 1 | **NOT in the literal legal text** — ARCO engineering addition |
| 4 | Capability attributed to hardware components | Gate 1 | BFO design choice — excludes pure-software systems |
| 5 | "Natural persons" modeled as Role, not Person | Gate 3 | Defensible — legal personhood is externally contingent |
| 6 | Affected-entity constraint in separate document | Gate 3 | ARCO design choice for testability — law embeds in same clause |
| 7 | `owl:hasValue` punning on class IRI | Gate 3 | OWL 2 permitted — creates CCO import fragility |
| 8 | `HighRiskSystem` as capability-only | Bridge axiom | **Goes beyond Article 6(2)** — ARCO policy position |
| 9 | Creditworthiness/credit-score disjunction collapsed | 5(b) | Arguable — law presents as alternatives |
| 10 | Fraud detection exclusion deferred | 5(b) | Known gap — explicit legal carve-out not modeled |
| 11 | Article 6(3) derogation not modeled | Global | Largest legal gap — every classification potentially over-inclusive |
| 12 | "Without active involvement" / "at a distance" not encoded | 1(a) | Gap — defining characteristics of "remote" absent |
| 13 | Legality precondition not modeled | 1(a) chapeau | Gap — not documented |

---

## What ARCO Proves vs. What the Law Requires

**ARCO proves:** Given a system description with (a) a hardware component bearing a typed capability disposition, (b) an intended-use document prescribing a typed process, and (c) a use-scenario document about the natural person role category — ARCO deterministically infers the system falls under its formal encoding of Annex III.

**The law requires:** That an AI system "intended to be used for" a listed purpose "of natural persons" in a permitted context is high-risk, subject to the Article 6(3) derogation, the fraud exclusion (5(b)), the verification exclusion (1(a)), and the legality precondition (1 chapeau).

**The gap:** ARCO's inference is a necessary-but-not-sufficient condition for legal compliance. If ARCO says no, the system probably is not high-risk under the modeled dimensions. But ARCO says yes does not mean the law says yes, because ARCO does not model derogations, does not model "remote" constraints, and treats capability as a gate the law does not explicitly require.

---

## The "Why These Three Gates?" Answer

- **Gate 1** answers: "Is this system structurally capable of the regulated activity?" NOT directly in the legal text. ARCO engineering addition grounded in BFO realism. Rationale: if a system lacks the physical capability, no documentation should trigger classification. Defensible as a safety margin. Must be disclosed as an addition.

- **Gate 2** answers: "Is this system documented as intended for the regulated process?" IS in the legal text. Article 3(12) grounds "intended purpose" in provider documentation. Mapping to `cco:prescribes` adds prescriptive semantics beyond mere aboutness.

- **Gate 3** answers: "Does the intended use target natural persons?" IS in the legal text. Both 1(a) (via Article 3(41)) and 5(b) explicitly name "natural persons."

---

## Highest-Priority Gaps for Legal Defensibility

1. **Article 6(3) derogation** — without this, every ARCO classification is potentially over-inclusive
2. **Fraud detection exclusion for 5(b)** — explicit carve-out that creates a known false-positive scenario
3. **"Remote" constraints** — without "without active involvement" and "at a distance," ARCO cannot distinguish remote from non-remote biometric identification
4. **HighRiskSystem capability-only** — needs clear labeling as an ARCO risk signal, not a legal determination
5. **Legality precondition** — "in so far as permitted" is a condition on the entire Annex III 1 section

---

_Sources: EU AI Act (Regulation 2024/1689) via EUR-Lex, AI Act Service Desk (ec.europa.eu), artificialintelligenceact.eu. ARCO files as of 2026-03-19._
