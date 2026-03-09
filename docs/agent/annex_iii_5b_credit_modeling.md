# ARCO — Annex III 5(b) Credit Scoring Modeling Context

## Purpose of This File

This file is the authoritative context document for extending ARCO to cover
**EU AI Act Annex III, point 5(b)** (creditworthiness assessment / credit
scoring). It contains:

1. Verbatim legal text (Article 6 + Annex III 5)
2. Every modeling decision required, with BFO/CCO ontological justification
3. Open questions that MUST be resolved with the human before writing TTL
4. Hard constraints that MUST NOT be violated

<instructions>
Before writing any TTL, SPARQL, or SHACL:
- Read this entire file
- Read `docs/agent/ontology_rules.md` (hard constraints)
- Read `docs/agent/eu_ai_act_rules.md` (Annex III structure)
- Do NOT write any triple until all OPEN QUESTIONs below are marked RESOLVED
- Bring OPEN QUESTIONs to the human with your recommended answer and reasoning
- The Sentinel-ID demo MUST still pass after every change
</instructions>

---

## Part 1 — Verbatim Legal Text

### Article 6 — Classification Rules for High-Risk AI Systems (excerpt)

> **Article 6(1)**: Irrespective of whether an AI system is placed on the market
> or put into service independently from the products referred to in this
> paragraph, that AI system shall be considered to be high-risk where both of
> the following conditions are fulfilled: [Annex I product safety regime — not
> applicable here]

> **Article 6(2)**: In addition to the high-risk AI systems referred to in
> paragraph 1, AI systems referred to in Annex III shall be considered to be
> high-risk.

> **Article 6(3)**: By derogation from paragraph 2, an AI system referred to
> in Annex III shall not be considered to be high-risk where it does not pose a
> significant risk of harm to the health, safety or fundamental rights of
> natural persons, including by not materially influencing the outcome of
> decision making. An AI system shall not be considered to be high-risk where
> it meets one or more of the following conditions:
> - (a) the AI system is intended to perform a narrow procedural task;
> - (b) the AI system is intended to improve the result of a previously
>   completed human activity;
> - (c) the AI system is intended to detect decision-making patterns or
>   deviations from prior decision-making patterns and is not meant to replace
>   or influence the previously completed human assessment, without proper human
>   review;
> - (d) the AI system is intended to perform a preparatory task to an
>   assessment relevant for the purposes of the use cases listed in Annex III.
>
> **Profiling exception**: Notwithstanding the foregoing, an AI system referred
> to in Annex III shall always be considered to be high-risk if the AI system
> performs profiling of natural persons.

---

### Annex III — Category 5 (Access to Essential Services) — Full Text

> **5. Access to and enjoyment of essential private services and essential
> public services and benefits:**
>
> **(a)** AI systems intended to be used by public authorities or on behalf of
> public authorities to evaluate the eligibility of natural persons for
> essential public benefits and services, including healthcare services, as well
> as to grant, reduce, revoke, or reclaim such benefits and services;
>
> **(b)** AI systems intended to be used to evaluate the creditworthiness of
> natural persons or establish their credit score, with the exception of AI
> systems used for the purpose of detecting financial fraud;
>
> **(c)** AI systems intended to be used for risk assessment and pricing in
> relation to natural persons in the case of life and health insurance;
>
> **(d)** AI systems intended to evaluate and classify emergency calls by
> natural persons or to be used to dispatch, or to establish priority in the
> dispatching of, emergency first response services, including by police,
> firefighters and medical aid, as well as of emergency healthcare patient
> triage systems.

**Source**: Regulation (EU) 2024/1689, Official Journal L 2024/1689, 12 July
2024. Full text at EUR-Lex:
https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng

---

### Key Legal Qualifiers for 5(b) — Parsed

| Element | Legal Text | Modeling Target |
|---|---|---|
| Trigger act A | "evaluate the creditworthiness of natural persons" | Process type |
| Trigger act B | "establish their credit score" | Process type (same or separate?) |
| Affected entity | "natural persons" | NaturalPersonRole |
| Exception | "detecting financial fraud" | Exclusion pattern |
| Gate | "intended to be used" | IntendedUseSpecification |

---

## Part 2 — Modeling Decisions

Each decision is marked **RESOLVED** or **OPEN QUESTION**.
OPEN QUESTIONs must be brought to the human before TTL is written.

---

### Decision 1 — Capability Class Name and Placement

**Legal basis**: The system must be capable of evaluating creditworthiness or
establishing a credit score.

**BFO/CCO analysis**:
A `CapabilityDisposition` (subclass of `bfo:Disposition`) inheres in a material
continuant — specifically a `SystemComponent`. Per existing ARCO architecture,
`SoftwareArtifact ⊑ ICE` and is NOT a SystemComponent. Credit scoring systems
are predominantly software-defined, but the disposition must inhere in the
hardware component that executes the process (servers, processing units). This
follows the same pattern as `BiometricIdentificationCapability` inhering in
`Sentinel_FaceID_Module` (hardware).

**Proposed class**:
```
:CreditworthinessAssessmentCapability ⊑ :CapabilityDisposition
```

**Justification**: The legal text lists two trigger acts (evaluate OR establish
score) but they describe one unified systemic power — the power to assess the
financial position of a natural person and produce a creditworthiness output.
One capability class correctly models one disposition; process phases are
particulars, not capability distinctions.

**Barry Smith alignment**: Dispositions are single-track powers. The OR in
the legal text is a legislative drafting choice covering two outputs of the same
underlying capability, not two distinct dispositions. Modeling two capability
classes would multiply ontological commitments without basis in the structure of
the power itself.

> **STATUS: OPEN QUESTION 1**
> Recommended answer: One class — `CreditworthinessAssessmentCapability`.
> Agree, or should we distinguish EvaluationCapability vs ScoreEstablishmentCapability?
> Human must confirm before proceeding.

---

### Decision 2 — Process Type

**Legal basis**: "evaluate the creditworthiness" / "establish their credit
score"

**Proposed class**:
```
:CreditworthinessAssessmentProcess ⊑ cco:Process
```

**Justification**: The three-gate pattern requires a regulated process TYPE
(a universal) to be prescribed by the IntendedUseSpecification. The process
type must cover both trigger acts (evaluate AND establish score). A single
process type is correct because both acts are constitutive of the same
regulatory concern: AI-generated financial judgment about a person.

**Barry Smith alignment**: Process types are universals instantiated by
particular processes. The legal text's OR covers two possible output types from
one process type, not two process types.

> **STATUS: OPEN QUESTION 2**
> Recommended answer: One process type — `CreditworthinessAssessmentProcess`.
> Agree?

---

### Decision 3 — Fraud Detection Exception

**Legal basis**: "with the exception of AI systems used for the purpose of
detecting financial fraud"

**The ontological problem**: The exception is not about capability — a system
could have both creditworthiness assessment capability AND fraud detection
capability. The exception is about **intended use**. A system whose
IntendedUseSpecification prescribes only fraud detection is out of scope for
5(b), even if it uses similar scoring mechanisms.

**Option A — Ignore in v1, document as known gap**:
Model only the positive classification path. The exception is a derogation
claim a provider would assert; ARCO verifies the positive case. Cost: incomplete
per legal text.

**Option B — Model FraudDetectionExclusionSpecification as ICE**:
A provider can assert a `FraudDetectionExclusionSpecification` that
`iao:0000136` the system. A SPARQL query checks for its presence and subtracts
it from the classification. Cost: adds significant complexity; creates a
precedent for soft overrides.

**Option C — Disjoint intended use**:
Assert `FraudDetectionIntendedUseSpecification` as disjoint from
`CreditworthinessAssessmentIntendedUseSpecification`. If system has a fraud
detection intended use, no creditworthiness intended use can exist
simultaneously. Cost: ontologically strict, may fail for dual-use systems.

**Barry Smith alignment**: The exception lives in the representation/regulatory
layer (about intended use ICEs), not the reality layer (capability). Option A
is conservative and honest. Option B risks creating a bypass pattern.

> **STATUS: OPEN QUESTION 3**
> Recommended answer: Option A for v1 — model the positive path, document the
> exception as a known gap with a comment in the TTL and a note in this file.
> Agree?

---

### Decision 4 — Bridge Axiom Extension

**Current state** (`ARCO_core.ttl`):
```
:AnnexIIITriggeringCapability ≡ owl:unionOf(
  :BiometricIdentificationCapability
)
```

**Required change**:
```
:AnnexIIITriggeringCapability ≡ owl:unionOf(
  :BiometricIdentificationCapability,
  :CreditworthinessAssessmentCapability
)
```

**Justification**: The bridge axiom drives HighRiskSystem entailment. Extending
the union is the correct and minimal change. No other axioms need modification.
The Sentinel-ID inference chain is unchanged.

**Barry Smith alignment**: Union extensions to defined classes are additive and
non-destructive. This is the canonical pattern for expanding regulatory scope.

> **STATUS: RESOLVED — extend the union.**
> Requires updating one equivalentClass axiom in ARCO_core.ttl.

---

### Decision 5 — AnnexIII5bApplicableSystem Equivalence Class

**Proposed** (analogous to AnnexIII1aApplicableSystem):
```
:AnnexIII5bApplicableSystem ≡
  :System
  ∩ (bfo:0000051 some (ro:0000091 some :CreditworthinessAssessmentCapability))
  ∩ (iao:0000136 some (:IntendedUseSpecification
       ∩ (cco:prescribes some :CreditworthinessAssessmentProcess)))
  ∩ (iao:0000136 some (:UseScenarioSpecification
       ∩ (iao:0000136 some :NaturalPersonRole)))
```

**Justification**: Three-gate logic, same structure as 1(a). Gate 1 = hardware
capability. Gate 2 = intended use prescribing the process. Gate 3 = scenario
involving natural persons. The legal text explicitly requires all three.

**Barry Smith alignment**: Equivalence classes for regulatory applicability
correctly capture necessary AND sufficient conditions. All three gates are
legally necessary; together they are sufficient for 5(b) classification.

> **STATUS: OPEN QUESTION 4**
> Recommended answer: Yes, model AnnexIII5bApplicableSystem with three-gate
> equivalence. Agree?

---

### Decision 6 — Instance File Location

**Proposed**: New file `03_TECHNICAL_CORE/ontology/ARCO_instances_creditscore.ttl`

**Justification**: `ontology_rules.md` prohibits creating separate files per
Annex III *item* but does not prohibit separate files per *system demo*. The
Sentinel-ID instance file is already one system per file. A separate file keeps
the demos modular and avoids touching working instances.

**Pipeline impact**: `run_pipeline.py` hardcodes the three TTL files. It will
need a new constant for the credit scoring instance file. This is a one-line
change with no architectural impact.

> **STATUS: OPEN QUESTION 5**
> Recommended answer: New file `ARCO_instances_creditscore.ttl`, and update
> pipeline to accept a config or a list of instance files.
> Alternative: add credit scoring instances to the existing Sentinel file.
> Human must decide: separate file or combined?

---

### Decision 7 — Article 6(3) Derogation Modeling

**Legal basis**: Any Annex III system that "does not pose a significant risk of
harm" may be non-high-risk under four conditions (see Part 1 above).

**Current state**: ARCO does not model the derogation path. The Sentinel-ID
demo only models the positive classification case.

**Position**: For v1 of credit scoring, do not model the derogation path.
Document it as a known gap. `eu_ai_act_rules.md` already notes the derogation
pattern ("Model derogation claims as ICE artifacts") — this establishes the
future pattern without requiring immediate implementation.

> **STATUS: RESOLVED — defer derogation modeling to a future extension.**
> Document in TTL comments.

---

## Part 3 — Pre-Implementation Checklist

Before writing any TTL, confirm all of the following:

- [ ] OPEN QUESTION 1 resolved (capability class count)
- [ ] OPEN QUESTION 2 resolved (process type count)
- [ ] OPEN QUESTION 3 resolved (fraud exception handling)
- [ ] OPEN QUESTION 4 resolved (AnnexIII5bApplicableSystem equivalence)
- [ ] OPEN QUESTION 5 resolved (instance file location)
- [ ] Confirmed: Sentinel-ID pipeline passes on current branch before changes
- [ ] Confirmed: New capability class will subclass CapabilityDisposition, not Disposition directly

---

## Part 4 — Implementation Sequence (post-approval)

Execute strictly in this order. Run pipeline after each step.

1. **ARCO_core.ttl** — Add `CreditworthinessAssessmentCapability` class +
   extend `AnnexIIITriggeringCapability` union + add
   `CreditworthinessAssessmentProcess` class + add
   `AnnexIII5bApplicableSystem` equivalence class.

2. **Run pipeline** — Sentinel-ID must still pass. No new instances yet.

3. **ARCO_instances_creditscore.ttl** — Author instance file with:
   - Credit scoring system (System + HardwareComponent)
   - CreditworthinessAssessmentCapability disposition instance
   - IntendedUseSpecification prescribing CreditworthinessAssessmentProcess
   - UseScenarioSpecification referencing NaturalPersonRole
   - HighRiskDetermination artifact
   - ProviderOrganization + ProviderRole + AssessmentDocumentation

4. **Run pipeline** — Both systems must pass.

5. **SPARQL** — Add `check_annex_iii_5b_entailment.sparql` (analogous to
   existing `check_annex_iii_1a_entailment.sparql`).

6. **Run pipeline** — Full pass required.

7. **SHACL** — Review whether `assessment_documentation_shape.ttl` needs
   extension for the new system type. Minimal changes only.

8. **Run pipeline** — Final full pass. Then commit.

---

## Part 5 — What This Does NOT Cover (Explicit Scope Boundary)

- Annex III 5(a): public benefit eligibility — NOT in scope for this extension
- Annex III 5(c): life/health insurance pricing — NOT in scope
- Annex III 5(d): emergency call classification — NOT in scope
- Article 6(3) derogation modeling — deferred
- Fraud detection exception (positive modeling) — deferred pending OPEN QUESTION 3
- Multi-system pipeline configuration — minimal only (one new constant)
- Any UI, API, or intake layer — explicitly out of scope

---

*Legal sources: [EUR-Lex OJ:L_202401689](https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng) · [artificialintelligenceact.eu Annex III](https://artificialintelligenceact.eu/annex/3/) · [ai-act-service-desk.ec.europa.eu](https://ai-act-service-desk.ec.europa.eu/en/ai-act/annex-3)*
