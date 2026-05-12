# Reference Use Case: Bank Deploying a Third-Party Credit-Scoring Model

This document walks through one specific use case to make ARCO's scope, strengths, and gaps concrete. It is the worked example referenced from the README's "What ARCO is, and what it is not" section. The purpose is not to ship a deployable client tool. The purpose is to show, against a realistic scenario, where ARCO's current architecture supports a defensible determination and where it does not.

The scenario is hypothetical but plausible. The artifact landscape (vendor documentation, bank deployment policy, regulatory text) is described concretely so a reviewer can verify each gap claim.

---

## The scenario

A consumer bank in Germany ("Bank Y") wants to deploy a third-party gradient-boosted credit-scoring model ("Vendor X's Credit Score API") to support personal loan decisions for unsecured loans up to €25,000 to EU resident adult applicants. The model returns a score; Bank Y's loan officers use the score as one input in a decision they make. Bank Y wants to know:

1. Does this deployment fall under EU AI Act Annex III 5(b) (creditworthiness evaluation)?
2. If yes, what obligations attach to Bank Y as the deployer, and to Vendor X as the provider?
3. Does the Article 6(3) derogation apply (e.g., because human loan officers always decide)?

Bank Y's compliance team needs a determination they can defend in a regulatory audit, traceable to specific clauses in specific documents.

---

## The artifact landscape

For a defensible determination, the following artifacts must exist and be accessible:

**Vendor X side:**
- Product documentation describing the model's capability (input features, output scores, intended uses)
- Technical documentation per Annex IV (model architecture, training data summary, performance metrics, limitations)
- A model card or equivalent published artifact stating the intended purpose
- Promotional or sales material making capability claims

**Bank Y side:**
- Deployment specification (which loan products, which customer segments, which decision flow)
- Policy stating how scores are used in decisions (input, advisory, automated)
- Risk management plan if Annex III applies (Article 9)
- Data governance plan covering applicant data (Article 10)
- Human oversight plan (Article 14): the loan officer review process
- Transparency plan (Article 13): disclosure to the applicant

**Regulatory side:**
- Regulation (EU) 2024/1689 Article 6, Annex III item 5(b), Article 6(3), Article 16 (provider obligations), Article 26 (deployer obligations)
- Recitals relevant to creditworthiness (Recital 58)

A defensible determination cites specific clauses from each of these. The certificate ARCO produces today does not.

---

## What ARCO produces today for this case

The repository ships `03_TECHNICAL_CORE/ontology/ARCO_instances_creditscoring.ttl` as a stand-in for the bank's deployment description. Running the pipeline produces:

```
ARCO CONDITION ASSESSMENT CERTIFICATE
========================================================================
  SYSTEM:                  CreditScorer_001
  REGIME:                  ARCO ontology encoding of EU AI Act (Article 6 / Annex III)
  INPUT INSTANCE:          ARCO_instances_creditscoring.ttl
  PRIMARY ARCO CLASSIFICATION:  AnnexIII5bApplicableSystem (ENTAILED, all three ARCO gates)
  LATENT-RISK FLAG:             HighRiskSystem (INFERRED, Gate 1 capability precondition only)
  TRIGGERING CAPABILITY:   CreditScorer_Eval_Disposition
  EVIDENCE PATH:
  CreditScorer_001 -> CreditScorer_Processing_Module -> CreditScorer_Eval_Disposition
  SHACL:                   PASS
  TRACEABILITY:            PASS
  LATENT RISK:             DETECTED
  INTENDED USE:            PASS
  ANNEX III 1(a):          NOT APPLICABLE
  ANNEX III 5(b):          VERIFIED (ENTAILED, Article 6(3) derogation not evaluated)
  OBLIGATION:              PASS
  ENTAILED TRIPLES ADDED:  +19758
```

This is the architectural output. It says: given the typed RDF describing CreditScorer_001, all three gates for Annex III 5(b) are satisfied under OWL-RL entailment, the latent-risk flag is on, and Article 6(3) was not evaluated.

For Bank Y's compliance team to act on this, they need more.

---

## What a defensible determination would actually say

Compare ARCO's certificate to what Bank Y's compliance lead would need to put in front of internal counsel and (eventually) the EU AI Office:

> **Annex III 5(b) Applicability Determination — Bank Y's Deployment of Vendor X Credit Score API for Personal Loans up to €25,000**
>
> **Determination: Annex III 5(b) APPLIES.**
>
> Conditions met:
>
> 1. The system performs creditworthiness evaluation. Source: Vendor X Product Documentation v3.1, Section 2.1 ("The API returns a creditworthiness score in the range 300-850 based on applicant features"); Vendor X Model Card published at [URL], stating "Intended use: support of consumer credit decisions."
> 2. The system is intended for use in evaluating natural persons' creditworthiness. Source: Bank Y Deployment Policy 2026-04, Section 1.2 ("Deployed for personal loan decisions for individual EU resident applicants"); Bank Y Customer Segment Definition 2026-Q1 (loans up to €25k to natural persons).
> 3. The system is placed on the market in the EU and used by an EU deployer. Source: Vendor X's EU Distribution Agreement [URL]; Bank Y's German banking license.
>
> **Annex III 5(b) fraud-detection carve-out: DOES NOT APPLY.**
>
> Source: Vendor X Product Documentation v3.1, Section 1 ("Primary purpose: creditworthiness scoring") and Section 4 ("Fraud detection is a separate Vendor X product"). Bank Y's Deployment Policy does not invoke fraud detection as a primary purpose.
>
> **Article 6(3) derogation: DOES NOT APPLY.**
>
> Bank Y considered each of the four conditions in Article 6(3):
> - (a) Narrow procedural task: NO. Bank Y Deployment Policy Section 3.4 indicates the score materially influences loan officer decisions, not a narrow procedural step.
> - (b) Improving result of previously completed human activity: NO. The score is used at the time of the credit decision, not afterward.
> - (c) Detecting decision-making patterns: NO. The score IS the decision input, not a pattern-detection layer.
> - (d) Preparatory task: NO. The score is the operative input.
> - Profiling proviso: The system performs profiling per GDPR Article 4(4); per AI Act Article 6(3), the derogation does not apply when profiling is performed.
>
> **Provider obligations attach to Vendor X (Article 16):** quality management system, technical documentation, registration, conformity assessment, post-market monitoring, serious-incident reporting.
>
> **Deployer obligations attach to Bank Y (Article 26):** use according to instructions, monitor operation, log generation/retention, ensure human oversight per Article 14, transparency to applicants per Article 13, data input governance, suspension if risk emerges.
>
> **Conformity evidence required:** Vendor X must produce Annex IV technical documentation; Bank Y must maintain Article 9 risk management, Article 10 data governance, Article 13 transparency notice to applicants, Article 14 human oversight specification, Article 15 accuracy/robustness/cybersecurity evidence.
>
> **External validation:** This determination has been reviewed by [counsel], dated [date]. It is not a conformity assessment under Article 43; it is a determination of Annex III applicability and obligation attribution.

That is the document a compliance team signs. ARCO's current certificate is closer to a worked example of one ingredient (the gate-fires-or-doesn't entailment) than to this final document.

---

## The gap: what's missing in ARCO

Mapping ARCO's current capability against what the determination above requires:

### 1. Documentary source anchoring (Article 3(12))

**What's needed:** The determination cites "Vendor X Product Documentation v3.1, Section 2.1" as the evidence for capability. The intended-use specification must trace to specific clauses in specific documents per Article 3(12) (instructions for use, technical documentation, promotional or sales material).

**ARCO today:** `:CreditScorer_IntendedUse_001 a :IntendedUseSpecification ; cco:prescribes :CreditScorer_EvalProcess_Token`. The IntendedUseSpecification is an abstract Directive ICE; it has no relation to a source document.

**To close the gap:** introduce ICE subclasses for `:InstructionsForUse`, `:TechnicalDocumentation`, `:PromotionalMaterial` (per Article 3(12)) and a provenance property linking the IntendedUseSpecification to source-document IRIs. The ARCO_governance_extension already has the IAO bridging machinery; this would extend the pattern.

### 2. Article 6(3) derogation evaluation

**What's needed:** The determination evaluates each of the four Article 6(3) conditions and the no-profiling proviso, with named evidence for each.

**ARCO today:** ARCO flags the existence of a `:DerogationClaim` artifact (an audit-layer SPARQL ASK) and emits "Article 6(3) derogation not evaluated" in the certificate. It does not model the four conditions or evaluate them.

**To close the gap:** extend the ontology with conditions (a)-(d) as `:DerogationCondition` subclasses, model the profiling test, and add OWL or SHACL rules that evaluate the conditions against provider-supplied evidence. This is non-trivial: each condition is interpretive and requires evidence-based judgment.

### 3. Provider vs deployer obligation chain

**What's needed:** A positive Annex III 5(b) classification entails Vendor X's Article 16 obligation set and Bank Y's Article 26 obligation set, with each obligation traceable to its triggering condition.

**ARCO today:** ARCO has `:ProviderRole`, `:DeployerRole`, `:ProviderOrganization`, and `:ComplianceObligationSpecification` classes. It has SHACL shapes verifying that obligations are linked to a system and a role. It does NOT have axioms entailing "if X is AnnexIII5bApplicableSystem and Y is its provider and Z is its deployer, then Y has Article 16 obligations and Z has Article 26 obligations."

**To close the gap:** add obligation classes (`:Article16Obligation`, `:Article26Obligation`, with subclasses for each specific obligation in Articles 16 and 26) and OWL axioms that entail obligation membership from the applicability classification + role assignment.

### 4. Coverage beyond Annex III 5(b)

**What's needed:** Annex III has eight high-risk areas. A real deployment may touch more than one. The determination must address all relevant areas, not just one.

**ARCO today:** Annex III 1(a) and 5(b) only.

**To close the gap:** add per-category capability classes, regulated process classes, and gate axioms for items 1(b) (high-risk biometric categorization), 2 (critical infrastructure), 3 (education), 4 (employment), 5(a) (essential services), 5(c)-(d) (law enforcement, migration), 6 (justice), 7 (democratic processes), 8 (immigration). Each is its own modeling exercise.

### 5. Per-deployment instance authoring from real provider documentation

**What's needed:** Vendor X and Bank Y do not produce typed RDF. They produce Word documents, PDFs, model cards, internal policy memos. ARCO needs to ingest those and produce the typed instance graph.

**ARCO today:** the instance file is hand-authored. LLMs may assist the authoring upstream, but the artifact ARCO classifies is the typed RDF.

**To close the gap:** an extraction pipeline that parses the provider's actual documentation and produces the typed instance graph, with provenance back to the source documents. This is itself a substantial project. The MCP plugin's `arco_run_pipeline` tool could be the downstream of such an extractor; the extractor is not built.

### 6. External legal counsel review

**What's needed:** The encoded interpretation of Annex III 5(b) and Article 6(3) must be reviewed by qualified counsel for the specific deployment's jurisdiction (Germany, in this scenario).

**ARCO today:** the encoded interpretation has not been externally reviewed (LIMITATIONS.md §8).

**To close the gap:** counsel review for the encoded interpretation, plus per-deployment review for the determination output. Counsel's involvement is structural, not optional.

---

## What this means for ARCO's positioning

ARCO is a reference implementation that demonstrates how a BFO 2020-aligned ontology can encode EU AI Act Annex III applicability with deterministic OWL-RL classification, two-layer audit, HermiT cross-check, and traceable competency questions. It is NOT a deployable enterprise compliance tool.

The credit-scoring use case above shows why. ARCO's certificate is an architectural artifact: it answers "given the typed inputs, do the gates fire?" A defensible determination is a different artifact: it answers "given the actual provider and deployer documentation, in this specific deployment, what are the applicable Annex III items, what obligations attach to whom, and what is the evidence chain?"

The first is a reasoner output. The second is a worked legal-and-engineering determination.

ARCO's architecture supports the path from one to the other. Closing each numbered gap above is a discrete, scoped piece of work. Done in the right order (1 first; then 3; then 2 and 5 in parallel; 4 incrementally; 6 throughout), the pattern extends to the determination quality real clients need.

---

## What this document is not

- It is not a substitute for counsel review.
- It is not a published worked use case from a real Vendor X or Bank Y. The names are placeholders.
- It is not a roadmap commitment. It is a gap analysis.
- It is not exhaustive. There are smaller gaps (real-time vs post biometric for Annex III 1(a), coverage of GPAI integration cases, multi-jurisdictional considerations) that are not enumerated here.

It is one specific use case rendered concretely enough that the gap between ARCO's current state and a defensible client-facing determination is visible. Reviewers reading this should be able to verify each gap claim against the cited regulatory text and against ARCO's actual code (`03_TECHNICAL_CORE/ontology/ARCO_instances_creditscoring.ttl`, `03_TECHNICAL_CORE/ontology/ARCO_governance_extension.ttl`, `03_TECHNICAL_CORE/scripts/run_pipeline.py`, the SPARQL queries in `03_TECHNICAL_CORE/reasoning/`, and the SHACL shapes in `03_TECHNICAL_CORE/validation/`).

---

## Reviewer questions

A useful review of this document answers, for each numbered gap:

1. Is the gap real, or is the existing ARCO machinery sufficient for the determination quality the gap claims?
2. Is the proposed close-the-gap path concrete enough to estimate effort?
3. Is there ordering or prioritization the document missed?
4. Is there an additional gap not enumerated here that a real determination would surface?

The intent of soliciting these questions is to ground ARCO's next phase of work in real-deployment-quality requirements rather than internal aesthetics.
