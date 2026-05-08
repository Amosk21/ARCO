# ARCO Competency Questions

ARCO is a BFO 2020 / RO / IAO / CCO-aligned OWL ontology that classifies AI systems against the EU AI Act (Regulation (EU) 2024/1689), with a specific focus on the Annex III high-risk categories. The classification is deterministic. No language model is involved at decision time. Three layers carry the work.

The first layer is OWL-RL entailment, which performs the actual classification. OWL operates under the Open World Assumption (OWA), meaning the absence of a fact does not entail its negation. This makes OWL the right tool for inference: a system enters the `:HighRiskSystem` extension only when its asserted facts satisfy an `equivalentClass` axiom. The second layer is SHACL, which validates documentary completeness. SHACL operates under the Closed World Assumption (CWA), meaning required structure must be present in the asserted graph or the shape fails. The third layer is SPARQL ASK, which runs after OWL-RL has materialized the entailed graph. Its job is post-reasoning audit: it confirms expected entailments fired, detects regulatory flags that classification alone does not surface, and provides traceability rows for the certificate.

Competency questions matter here because each question must be honest about which layer answers it. A question of the form "is this system high-risk?" is an entailment question and belongs to OWL-RL. A question of the form "is the intended use documented?" is a completeness question and belongs to SHACL. A question of the form "did the regulator-named exclusion apply?" is a pattern-detection question on the reasoned graph and belongs to SPARQL ASK. Conflating these layers is the most common modeling error in ontology-driven compliance, so each CQ below is tagged with its layer and the file that implements it.

---

## CQ1: Does this system have a component bearing an Annex III triggering capability?

**Regulator paraphrase.** Does this AI system contain any hardware part that can do something Annex III names as triggering high-risk classification?

**Motivation.** The EU AI Act treats high-risk capabilities as triggering even when the capability is latent, that is, not yet exercised in a deployed scenario. ARCO must surface latent risk so a provider does not avoid scrutiny by leaving a capability un-deployed.

**Layer.** OWL-RL (OWA) for the classification. SPARQL ASK (post-reasoning audit) for the flag row on the certificate.

**Regulatory anchor.** Article 6(2) and Annex III generally.

**Answered by.** `03_TECHNICAL_CORE/ontology/ARCO_governance_extension.ttl` (the `:HighRiskSystem` `equivalentClass` axiom), and `03_TECHNICAL_CORE/reasoning/detect_latent_risk.sparql` (audit flag).

**Expected answer.** OWL-RL entails `:HighRiskSystem` membership when the three gates are satisfied. The SPARQL audit returns `true` when a latent capability is present without a fully-specified deployment.

**Example.** A facial-recognition module shipped with a system but not yet wired into any use scenario is flagged latent. The certificate records a LATENT-RISK FLAG row.

---

## CQ2: Does this system meet all three gates for Annex III item 1(a)?

**Regulator paraphrase.** Is this system subject to Annex III 1(a) obligations as a remote biometric identification system?

**Motivation.** Annex III item 1(a) covers biometric identification. Classification is correct only when capability, process, and affected role all align. Any single gate failing means the system is not in the 1(a) extension.

**Layer.** OWL-RL (OWA) for entailment. SPARQL ASK (post-reasoning audit) for verification that the entailment fired.

**Regulatory anchor.** Annex III item 1(a) (biometric identification).

**Answered by.** `03_TECHNICAL_CORE/ontology/ARCO_governance_extension.ttl` (the `:AnnexIII1aApplicableSystem` `equivalentClass` axiom), and `03_TECHNICAL_CORE/reasoning/check_annex_iii_1a_entailment.sparql` (audit).

**Expected answer.** OWL-RL classifies the system into `:AnnexIII1aApplicableSystem` when Gate 1 (biometric identification capability), Gate 2 (biometric identification process prescribed), and Gate 3 (natural person role designated) all hold. The audit returns `true` when the entailment is present in the materialized graph.

**Example.** A border-control system with a biometric identification capability, a prescribed biometric identification process, and natural persons as the affected role enters the 1(a) extension.

---

## CQ3: Does this system meet all three gates for Annex III item 5(b)?

**Motivation.** Annex III item 5(b) covers creditworthiness assessment of natural persons. The same three-gate logic applies. Misclassification at this point can let a credit scorer escape Article 6(2) treatment.

**Layer.** OWL-RL (OWA) for entailment. SPARQL ASK (post-reasoning audit) for verification.

**Regulatory anchor.** Annex III item 5(b) (creditworthiness).

**Answered by.** `03_TECHNICAL_CORE/ontology/ARCO_governance_extension.ttl` (the `:AnnexIII5bApplicableSystem` `equivalentClass` axiom), and `03_TECHNICAL_CORE/reasoning/check_annex_iii_5b_entailment.sparql` (audit).

**Expected answer.** OWL-RL classifies the system into `:AnnexIII5bApplicableSystem` when the credit-scoring capability, a prescribed credit-scoring process, and natural persons as the affected role all hold.

**Example.** A bank's consumer-lending model with a credit-scoring capability, a prescribed credit-scoring process, and natural-person applicants as the affected role enters the 5(b) extension.

---

## CQ4: Is the system's intended use documented?

**Motivation.** Article 3(12) defines intended purpose as the use for which an AI system is intended by the provider. Without documented intended use, Gate 2 cannot be evaluated, and the regulator has nothing to compare against. This is a documentary precondition, not an entailment.

**Layer.** SHACL (CWA) for documentary validation. SPARQL ASK (post-reasoning audit) for the Gate 2 portion of the audit pipeline.

**Regulatory anchor.** Article 3(12) (intended purpose).

**Answered by.** `03_TECHNICAL_CORE/validation/assessment_documentation_shape.ttl` (`:IntendedUseSpecificationShape`), and `03_TECHNICAL_CORE/reasoning/check_intended_use.sparql` (Gate 2 portion).

**Expected answer.** SHACL conforms when the intended-use specification is present and well-formed. SPARQL ASK returns `true` when the typed-content checks for Gate 2 succeed on the reasoned graph.

**Example.** A provider asserts an intended-use specification that prescribes a `:RemoteBiometricIdentificationProcess` (the regulated process class for Annex III 1(a)). SHACL conforms. The Gate 2 audit confirms the prescribed process token is typed as the regulated class. Adversarial counter-example: the same instance file with the prescribed process retyped as `:BiometricVerificationProcess` causes Gate 2 to fail because verification is not identification.

---

## CQ5: Does the use scenario designate the regulated affected role universal?

**Motivation.** Annex III categories are scoped to specific affected roles, typically natural persons. A system that operates only on legal entities or non-personal data is not in the same extension. Gate 3 is the role-bearer check.

**Layer.** SHACL (CWA) for documentary validation. SPARQL ASK (post-reasoning audit) for the Gate 3 portion.

**Regulatory anchor.** Annex III items 1(a) and 5(b), affected-role scoping.

**Answered by.** `03_TECHNICAL_CORE/validation/assessment_documentation_shape.ttl` (`:UseScenarioSpecificationShape`, including the property shape `:PS_UseScenario_DesignatesRole`), and `03_TECHNICAL_CORE/reasoning/check_intended_use.sparql` (Gate 3 portion).

**Expected answer.** SHACL conforms when the use scenario designates the role universal expected by the regulation. The audit query confirms the role designation reaches the materialized graph.

**Example.** A credit scorer's use scenario designates `NaturalPersonRole`. SHACL conforms, the Gate 3 audit succeeds, and the 5(b) entailment is reachable.

---

## CQ6: Is the prescribed process aligned with the regulation-named regulated process?

**Motivation.** A provider can document an intended use that mentions a process by some local name. Classification requires that the prescribed process is the regulator-named process, not a similar-sounding one. Misalignment here is a common adversarial vector.

**Layer.** SPARQL ASK (post-reasoning audit).

**Regulatory anchor.** Annex III general (per-item process alignment).

**Answered by.** `03_TECHNICAL_CORE/reasoning/check_regulatory_alignment.sparql`.

**Expected answer.** Returns `true` when the prescribed process class on the reasoned graph matches the regulated-process class named by the applicable Annex III condition.

**Example.** A provider declares an intended use prescribing a process token typed as `:CreditworthinessEvaluationProcess` (the regulator-named process class for Annex III 5(b)). The audit confirms alignment between the regulatory ICE's prescribed process and the provider's intended use. Without that alignment (for example, the provider declares only a generic process), the audit returns `false` and the certificate records the gap.

---

## CQ7: Is there assessment documentation linking the system to applicable regulatory content?

**Motivation.** A regulator needs to follow a chain from system, to assessment, to regulation cited. Without this trace, classification is opaque.

**Layer.** SHACL (CWA) for documentary validation. SPARQL ASK (post-reasoning audit) for the traceability check.

**Regulatory anchor.** Article 6(2), supporting traceability.

**Answered by.** `03_TECHNICAL_CORE/validation/assessment_documentation_shape.ttl` (`:AssessmentDocumentationShape`), and `03_TECHNICAL_CORE/reasoning/check_assessment_traceability.sparql`.

**Expected answer.** SHACL conforms when the assessment documentation is present. SPARQL ASK returns `true` when the system, its assessment, and the cited regulatory content are connected on the reasoned graph.

**Example.** A credit scorer's assessment documentation cites `AnnexIII_Condition_5b`. SHACL conforms and the traceability audit succeeds.

---

## CQ8: Is there a compliance obligation specifying the provider's responsibilities?

**Motivation.** Annex III classification is not the end. The provider's obligations follow. ARCO requires that an obligation specification is linked to the classified system.

**Layer.** SHACL (CWA) for documentary validation. SPARQL ASK (post-reasoning audit) for the link audit.

**Regulatory anchor.** Article 6(2) and Articles 16 onward (provider obligations).

**Answered by.** `03_TECHNICAL_CORE/validation/assessment_documentation_shape.ttl` (`:ComplianceObligationSpecificationShape`), and `03_TECHNICAL_CORE/reasoning/check_obligation_link.sparql`.

**Expected answer.** SHACL conforms when the obligation specification is present. SPARQL ASK returns `true` when the obligation is linked to the system on the reasoned graph.

**Example.** A high-risk system has a linked `ComplianceObligationSpecification` recording the provider's documented duties. The obligation audit passes.

---

## CQ9: Has the provider asserted an Article 6(3) derogation claim for this system?

**Motivation.** Article 6(3) creates a narrow derogation from high-risk classification. A provider can claim it. ARCO does not adjudicate the claim. It surfaces the claim as an audit flag so the certificate records that human review is required.

**Layer.** SPARQL ASK (post-reasoning audit, flag).

**Regulatory anchor.** Article 6(3) (derogation).

**Answered by.** `03_TECHNICAL_CORE/reasoning/flag_derogation_candidate.sparql`.

**Expected answer.** Returns `true` when a derogation claim is asserted on the system. The certificate fires a FLAGGED row.

**Example.** A provider asserts an Article 6(3) derogation on a downstream-task system. The flag fires. The certificate documents the claim. Human review takes it from there.

---

## CQ10: Does the system have a fraud-detection process in scope (Annex III 5(b) exclusion candidate)?

**Motivation.** Annex III item 5(b) excludes fraud-detection processes. A system that scores credit but does so in a fraud-detection scope is a candidate for exclusion. As with derogation, ARCO surfaces the candidate, it does not finalize the exclusion.

**Layer.** SPARQL ASK (post-reasoning audit, flag).

**Regulatory anchor.** Annex III item 5(b), fraud-detection exclusion clause.

**Answered by.** `03_TECHNICAL_CORE/reasoning/flag_fraud_exclusion_candidate.sparql`.

**Expected answer.** Returns `true` when a `FraudDetectionProcess` is in the system's scope on the reasoned graph. The certificate records a FLAGGED row.

**Example.** A retail bank's transaction-monitoring scorer is flagged. Human review then determines whether the fraud-detection scope is exclusive or partial.

---

## CQ11: Does each ProviderRole instance correctly inhere in a single bearer?

**Regulator paraphrase.** Is each provider-role record bound to exactly one provider, so the obligations attached to that role can be attributed unambiguously?

**Motivation.** BFO roles are specifically dependent continuants; they inhere in an independent continuant bearer. A `ProviderRole` instance with no bearer (or with multiple bearers) violates BFO and breaks downstream obligation attribution.

**Layer.** SHACL (CWA) for cardinality validation of the inherence path. SPARQL ASK (post-reasoning) for the named-instance smoke test that ships with the sentinel fixture.

**Regulatory anchor.** Indirect. This is an ontological-soundness check that supports Article 16 obligation attribution.

**Answered by.** `03_TECHNICAL_CORE/validation/assessment_documentation_shape.ttl` (`:ProviderRoleShape` / `:PS_ProviderRole_InheresIn` enforces `ro:0000052` minCount 1, maxCount 1). `03_TECHNICAL_CORE/reasoning/ask_provider_role_inheres_in_org.sparql` is a sentinel smoke test asserting the named-instance pattern; it is not parameterized by system and is not a generalized "check this system's provider role" query.

**Expected answer.** SHACL conforms when every `:ProviderRole` instance has exactly one `ro:0000052` link. The shape does not check the type of the bearer; type-checking the bearer as `:ProviderOrganization` would be a stronger invariant and is a candidate refinement. The SPARQL smoke test returns `true` for the sentinel fixture.

**Example.** A `:ProviderRole` instance realized by an organization. SHACL passes when the cardinality holds. A future refinement would either tighten the SHACL shape with `sh:qualifiedValueShape [ sh:class :ProviderOrganization ]` or extend the SPARQL audit to bind the system and walk to the role-organization pair, removing the sentinel-only hardcoding.

---

## CQ12: Did the latent-risk OWL-RL entailment fire correctly?

**Regulator paraphrase.** Did the system end up flagged as carrying an Annex III triggering capability when its facts say it should be?

**Motivation.** The certificate's PRIMARY classification depends on entailments that should have fired. A regression in the ontology, the imports, or the reasoner could leave a system uncategorized. This audit confirms the entailment reached the materialized graph.

**Layer.** SPARQL ASK (post-reasoning audit).

**Regulatory anchor.** Article 6(2). Cross-check on classification soundness.

**Answered by.** `03_TECHNICAL_CORE/reasoning/check_high_risk_inference.sparql`.

**Expected answer.** Returns `true` when an expected `:HighRiskSystem` membership is present in the reasoned graph for systems whose facts satisfy the gates.

**Example.** The sentinel credit scorer's `:HighRiskSystem` membership is present after OWL-RL runs. The audit confirms classification fired and the certificate's VERIFIED state is consistent with the audit row.

---

## How this doc is used

The twelve competency questions enumerated above are the contract between ARCO's regulatory ambition and its implementation. Each question maps to one and only one layer (OWL-RL, SHACL, or SPARQL ASK), and each maps to a specific file in the repository. If a future change adds a new SPARQL query, a new SHACL shape, or a new entailment axiom, this document is updated in the same patch so that CQ-to-implementation traceability is preserved. A reviewer should be able to read this document and, for any question a regulator might ask, find the file that answers it.
