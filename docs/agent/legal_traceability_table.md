# Legal Traceability Table — ARCO v1 Implemented Scope

_Date: 2026-03-24 · Status: DRAFT — backtested against EU AI Act (Regulation 2024/1689) via EC AI Act Service Desk; awaiting external legal review_
_Source precedence: current TTL > eu_ai_act_rules.md > legal_traceability_audit.md > deep_alignment_audit.md > adr_002_honest_assessment.md_
_Backtest source: AI Act Service Desk (ai-act-service-desk.ec.europa.eu), verified 2026-03-24_

## Backtest Citation Correction

ARCO documentation (legal_traceability_audit.md, deep_alignment_audit.md) previously cited **Article 3(36)** for "remote biometric identification system." This is **wrong** — now corrected. The actual Article 3 numbering in Regulation 2024/1689 is:

| Point | Actual definition |
|---|---|
| Article 3(35) | 'biometric data' |
| Article 3(36) | 'biometric identification' |
| Article 3(37) | 'biometric verification' |
| Article 3(41) | 'remote biometric identification system' |

All references below use corrected numbering. Upstream ARCO docs (`legal_traceability_audit.md`, `deep_alignment_audit.md`) have been fixed.

---

## Traceability Table

| Legal source | Exact legal condition | ARCO gate / class | Ontology pattern | Interpretive move | Known limitation |
|---|---|---|---|---|---|
| Article 6(2) | "In addition to the high-risk AI systems referred to in paragraph 1, AI systems referred to in Annex III shall be considered to be high-risk." | `AnnexIII1aApplicableSystem`, `AnnexIII5bApplicableSystem` | Three-gate `owl:equivalentClass` axiom per category-specific class, entailed by OWL-RL | Direct legal trigger encoded as per-category entailment classes rather than one unified class | ARCO splits this into category-specific classes plus a separate capability-only `HighRiskSystem`; the law does not make this split |
| HighRiskSystem bridge inference | No standalone legal condition — derived from Article 6(2) plus ARCO engineering policy | `HighRiskSystem` | `HighRiskSystem ≡ System ∩ has_part some (SystemComponent ∩ has_disposition some AnnexIIITriggeringCapability)` | ARCO-specific decomposition: fires on capability alone as a latent-risk signal; the law requires "intended to be used for" | Capability-only classification goes beyond Article 6(2); must be labeled as ARCO risk signal, not a legal determination |
| Article 3(12) | "'intended purpose' means the use for which an AI system is intended by the provider, including the specific context and conditions of use, as specified in the information supplied by the provider in the instructions for use, promotional or sales materials and statements, as well as in the technical documentation." | Gate 2: `IntendedUseSpecification` + `cco:prescribes` | Directive ICE with `cco:prescribes some [ProcessType]` and inverse `iao:0000136` linking to the system | Legally implied: intent grounded in documentary artifact (defensible per Article 3(12)), but `cco:prescribes` adds prescriptive semantics beyond mere aboutness | Law references multiple documentary sources jointly (instructions, marketing, technical docs); ARCO uses a single `IntendedUseSpecification` |
| Article 3(41) / remote biometric identification definition | "'remote biometric identification system' means an AI system for the purpose of identifying natural persons, without their active involvement, typically at a distance through the comparison of a person's biometric data with the biometric data contained in a reference database." | `BiometricIdentificationCapability` (Gate 1), `RemoteBiometricIdentificationProcess` (Gate 2) | Capability as BFO Disposition in `SystemComponent`; process as BFO Process subclass | ARCO-specific decomposition: definition split into a capability disposition and a typed process class; "remote" qualifying conditions and database-comparison element not encoded | "Without active involvement," "at a distance," and "comparison with a reference database" are all definitional but not modeled (see row 10) |
| Annex III 1(a) | "Remote biometric identification systems. This shall not include AI systems intended to be used for biometric verification the sole purpose of which is to confirm that a specific natural person is the person he or she claims to be." | `AnnexIII1aApplicableSystem` | Gate 1: `has_part some (SystemComponent ∩ has_disposition some BiometricIdentificationCapability)`. Gate 2: `someValuesFrom RemoteBiometricIdentificationProcess`. Gate 3: `hasValue NaturalPersonRole`. | ARCO-specific decomposition: single legal clause decomposed into three independently necessary gates; Gate 1 (capability) is ARCO-added and not in the literal legal text | Legality precondition (Annex III 1 chapeau "in so far as permitted") and "sole purpose" condition on the verification exclusion are not modeled |
| Biometric verification exclusion | "This shall not include AI systems intended to be used for biometric verification the sole purpose of which is to confirm that a specific natural person is the person he or she claims to be." (Annex III 1(a) second sentence; Recitals 17, 54) | `BiometricVerificationCapability` (NOT under `AnnexIIITriggeringCapability`); `BiometricVerificationProcess` | Type disjointness: verification ≠ identification; `BiometricVerificationCapability` not subclassed under `AnnexIIITriggeringCapability` | Legally implied exclusion modeled via type disjointness rather than negation — correct for pure-verification systems | "Sole purpose" condition not modeled; Recital 17 broadens exclusion scope to include authentication for service access, device unlock, and premises security — not captured |
| Annex III 5(b) | "AI systems intended to be used to evaluate the creditworthiness of natural persons or establish their credit score, with the exception of AI systems used for the purpose of detecting financial fraud." | `AnnexIII5bApplicableSystem` | Gate 1: `CreditworthinessEvaluationCapability`. Gate 2: `someValuesFrom CreditworthinessEvaluationProcess`. Gate 3: `hasValue NaturalPersonRole`. | ARCO-specific decomposition: "evaluate creditworthiness or establish credit score" disjunction collapsed into single capability class | Fraud detection exclusion not modeled — creates known false positive; "or establish their credit score" treated as same capability |
| Article 6(3) derogation | "By derogation from paragraph 2, an AI system referred to in Annex III shall not be considered to be high-risk where it does not pose a significant risk of harm to the health, safety or fundamental rights of natural persons, including by not materially influencing the outcome of decision making." Conditions (a)-(d); profiling override: "always... high-risk where the AI system performs profiling of natural persons." | Not modeled | None | Omission — entire derogation escape mechanism is absent; every ARCO classification is potentially over-inclusive | OWL-RL lacks negation-as-failure; Article 6(4) requires providers claiming derogation to document the assessment — aligns with planned ICE approach but not yet implemented |
| 5(b) fraud exclusion | "with the exception of AI systems used for the purpose of detecting financial fraud" (Annex III 5(b)) | Not modeled | None | Omission — explicit legal carve-out deferred; a fraud-detection system with creditworthiness capability would be incorrectly classified as `AnnexIII5bApplicableSystem` | OWL-RL cannot express negation gates; requires either post-classification SPARQL/SHACL check or negation-aware reasoning |
| "without active involvement / at a distance" | "without their active involvement, typically at a distance" (Article 3(41); Recital 17) | Not modeled — no class, property, restriction, or gate | None | Omission — defining characteristics of "remote" in the legal definition are entirely absent from the ontology | A biometric system used at close range with active subject participation would satisfy ARCO's gates but would NOT be a "remote biometric identification system" under Article 3(41) |

---

## Backtest Findings (verified against Regulation 2024/1689)

### Finding 1 — CRITICAL: Article 3 citation numbering error

All ARCO documentation cited "Article 3(36)" for the definition of "remote biometric identification system." The actual regulation numbers this as **Article 3(41)**. Article 3(36) actually defines "biometric identification" (the general concept, not remote). Article 3(37) defines "biometric verification." This error appeared in: `legal_traceability_audit.md` (6 occurrences, now fixed) and `deep_alignment_audit.md` (1 occurrence, now fixed). The table above uses corrected numbering.

### Finding 2 — Article 6(2) excerpt was truncated

ARCO's `legal_traceability_audit.md` quotes Article 6(2) as: "AI systems referred to in Annex III shall be considered to be high-risk." The full text begins: "**In addition to** the high-risk AI systems referred to in paragraph 1, AI systems referred to in Annex III shall be considered to be high-risk." The omitted prefix ("In addition to...paragraph 1") establishes that Annex III listing is a second, independent pathway — distinct from the product-safety-component pathway in Article 6(1). This framing is relevant but the omission does not change the operative meaning for ARCO's scope.

### Finding 3 — Article 3(36) "biometric identification" definition not separately traced

The actual Article 3(36) defines "biometric identification" as: "the automated recognition of physical, physiological, behavioural, or psychological human features for the purpose of establishing the identity of a natural person by comparing biometric data of that individual to biometric data of individuals stored in a database." ARCO's `BiometricIdentificationCapability` maps to this but does not encode the "comparing... to... database" element. A system that identifies persons without database comparison (e.g., de novo clustering) might not meet the legal definition but would satisfy ARCO's gate.

### Finding 4 — Recital 17 verification exclusion is broader than ARCO quotes

ARCO's `legal_traceability_audit.md` truncates Recital 17's verification exclusion. The full text adds: "and to confirm the identity of a natural person for the sole purpose of having access to a service, unlocking a device or having security access to premises." These specific use-case boundaries (service access, device unlock, premises security) are part of the regulatory context for the exclusion but are not captured by ARCO's type-disjointness model.

### Finding 5 — Recital 17 supports technology-neutral approach

Recital 17 states the definition applies "irrespectively of the particular technology, processes or types of biometric data used." This supports ARCO's abstract capability-based modeling rather than encoding specific biometric modalities (facial, fingerprint, iris, etc.).

### Finding 6 — Article 6(3) profiling override is a distinct unmodeled element

Article 6(3) final subparagraph: "an AI system referred to in Annex III shall **always** be considered to be high-risk where the AI system performs profiling of natural persons." This is not merely part of the derogation — it is a blanket override that eliminates the derogation pathway for profiling systems. ARCO models neither the derogation nor the profiling override.

### Finding 7 — Article 6(4) creates provider documentation obligation for derogation

"A provider who considers that an AI system referred to in Annex III is not high-risk shall document its assessment before that system is placed on the market or put into service." This aligns with ARCO's planned approach of modeling derogation claims as Descriptive ICE artifacts, but is not yet implemented.

### Finding 8 — All Annex III legal excerpts verified accurate

Annex III 1(a) text, Annex III 1 chapeau text, Annex III 5(b) text, and Article 3(12) "intended purpose" definition all match the official text verbatim. No content errors found in ARCO's legal excerpts beyond the citation numbering issue.

---

## Worked Example: Sentinel-ID Annex III 1(a) Positive Path

**Legal sources:** Article 6(2) ("Annex III systems are high-risk") + Annex III 1(a) ("Remote biometric identification systems") + Article 3(41) (definition of remote biometric identification) + Article 3(36) (definition of biometric identification) + Article 3(12) (intended purpose grounded in provider documentation).

**Gates fired:**
- Gate 1: Sentinel-ID `has_part` a `SystemComponent` (`Sentinel_FacialRecognitionModule_001`) that `has_disposition` a `BiometricIdentificationCapability` instance.
- Gate 2: `Sentinel_IntendedUse_001` (an `IntendedUseSpecification`) `is_about` Sentinel-ID and `cco:prescribes` a `RemoteBiometricIdentificationProcess` instance.
- Gate 3: `Sentinel_UseScenario_001` (a `UseScenarioSpecification`) `is_about` Sentinel-ID and `is_about` `:NaturalPersonRole`.

**Class inferred:** `AnnexIII1aApplicableSystem` (via OWL-RL equivalentClass entailment) and `HighRiskSystem` (via capability-only bridge axiom).

**Limitations:** Classification does not verify "without active involvement" or "at a distance" (Article 3(41) definitional elements). Does not verify "comparison with a reference database" (Article 3(36) definitional element). Article 6(3) derogation cannot exempt the system even if applicable. Gate 1 (capability in hardware component) is ARCO-added — the law does not separately require a hardware capability gate. The Annex III 1 chapeau legality precondition is not checked.

---

## Assessment (3 bullets)

- **Strongest:** Gate 2's grounding of "intended purpose" in a documentary artifact with typed process prescription has direct support in Article 3(12) and correctly captures the prescriptive character of "intended to be used for."
- **Weakest:** The absence of "without active involvement" and "at a distance" means ARCO cannot distinguish remote from non-remote biometric identification — the central legal distinction in Article 3(41) that defines the scope of 1(a).
- **Question for external legal review:** Does the three-gate decomposition (capability + prescribed process type + affected party category) capture conditions that are individually necessary and jointly sufficient for Annex III applicability, or does the legal text operate as an undivided description that resists formal decomposition into independent gates?
