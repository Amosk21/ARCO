# ARCO — Known Limitations and Scope Boundaries

**Purpose.** This document is the single place where ARCO's scope boundary, ontological commitments, and engineering gaps are stated plainly. Read it before quoting ARCO's capabilities in any external context, before making a commercial claim, or before extending the ontology. If a statement elsewhere in the repo appears to overreach what this document allows, this document wins and the other should be corrected.

**Primary references** (authority order, per [docs/agent/ARCO_public_claims.md](docs/agent/ARCO_public_claims.md)):

1. Pipeline output (`runs/demo/`) — observed behavior
2. [CLAUDE.md](CLAUDE.md) — project invariants
3. [README.md](README.md) — outward-facing claim
4. [docs/agent/ARCO_public_claims.md](docs/agent/ARCO_public_claims.md) — claim discipline
5. [docs/agent/bfo_cco_alignment_audit.md](docs/agent/bfo_cco_alignment_audit.md) — BFO/CCO alignment state
6. [docs/agent/eu_ai_act_rules.md](docs/agent/eu_ai_act_rules.md) — regulatory scope rules
7. [KB/40_REVIEWS/2026-04-20_bfo-commitment-backtest.md](KB/40_REVIEWS/2026-04-20_bfo-commitment-backtest.md) — commitment backtest grading each load-bearing choice

**Last reviewed:** 2026-06-10 (coherent disclosure pass following the 2026-06-10 adversarial design audit; see `runs/audits/2026-06-10_adversarial_design_audit.md`)

**Refresh trigger:** any change to ontology class hierarchy, three-gate axioms, imported upstream ontology, Annex III category coverage, or instance-file design conventions.

---

## 1. What ARCO classifies — and what that means

ARCO is a **reference implementation**, not a deployable enterprise compliance tool. It demonstrates an architectural pattern (BFO 2020 / RO / IAO / CCO grounding; three-gate `owl:equivalentClass` classification; two-layer separation between OWL-RL entailment and SPARQL ASK audit; HermiT OWL 2 DL cross-check) on a bounded scope of EU AI Act Annex III. Producing a defensible client-facing determination for a real AI deployment requires additional work outlined in README.md "What ARCO is, and what it is not."

ARCO classifies **structured descriptions of AI systems**, not deployed systems. The input is a hand-authored RDF/Turtle instance file asserting components, dispositions, intended use, and affected role categories. The output is a formal entailment — whether the described system satisfies ARCO's OWL-RL encoding of a specific Annex III category.

This matters because three things ARCO's output is **not**:

- It is **not** a determination that a system is legally high-risk under EU AI Act Article 6. ARCO determines whether a description satisfies ARCO's formal encoding. Whether the encoding correctly captures the legal intent has not been validated by a qualified EU AI Act lawyer (see §9).
- It is **not** a statement about the deployed system's behavior. If the description does not match what the system actually does in production, ARCO's output does not catch that mismatch. ARCO classifies the description the provider authored, not the physical artifact the provider runs.
- It is **not** a conformity assessment. Article 43 conformity assessments are performed by notified bodies or via prescribed self-assessment procedures. ARCO produces classification evidence; it does not execute the assessment procedure or substitute for one.
- It is **not** a determination that the described artifact is an AI system under Article 3(1). ARCO does not evaluate the Article 3(1) threshold; AI-system status is a human-adjudicated input commitment held by whoever authors and reviews the instance data. A described non-AI artifact carrying the right gate triples would still be entailed by the encoding.

The `HighRiskSystem` OWL class in the ontology is a **latent-risk flag based on Gate 1 only** — i.e., a system has a component that bears an `AnnexIIITriggeringCapability`. It is useful as an early-warning classifier and as a precondition for the category-specific gates, but it is not the full legal category. Category-specific classes (`AnnexIII1aApplicableSystem`, `AnnexIII5bApplicableSystem`) are the stronger output; they require all three gates to hold. This distinction is explicit in the architecture defense memo §4 and is enforced by the class definitions in [ARCO_governance_extension.ttl](03_TECHNICAL_CORE/ontology/ARCO_governance_extension.ttl).

---

## 2. Current Annex III coverage

Two Annex III categories are modeled. The rest are out of scope in the current release.

| Annex III category | Status | Gate 1 capability | Gate 2 process | Gate 3 role |
|---|---|---|---|---|
| 1(a) — Remote biometric identification | **Modeled** | `BiometricIdentificationCapability` | `RemoteBiometricIdentificationProcess` | `NaturalPersonRole` |
| 1(b) — Biometric categorisation by sensitive attributes | Not modeled | — | — | — |
| 1(c) — Emotion recognition | Not modeled | — | — | — |
| 2 — Critical infrastructure | Not modeled | — | — | — |
| 3 — Education and vocational training | Not modeled | — | — | — |
| 4 — Employment, worker management, access to self-employment | Not modeled | — | — | — |
| 5(a) — Access to essential public services | Not modeled | — | — | — |
| 5(b) — Creditworthiness evaluation | **Modeled** | `CreditworthinessEvaluationCapability` | `CreditworthinessEvaluationProcess` | `NaturalPersonRole` |
| 5(c) — Emergency response dispatch | Not modeled | — | — | — |
| 6 — Law enforcement | Not modeled | — | — | — |
| 7 — Migration, asylum, and border control | Not modeled | — | — | — |
| 8 — Administration of justice and democratic processes | Not modeled | — | — | — |

**Known modelling limits within the two covered categories:**

- **Annex III 5(b) fraud-detection exclusion is not modeled as a classification gate.** The legal text excludes AI intended for financial fraud detection from 5(b) classification. ARCO includes `FraudDetectionProcess` as a declared class and `flag_fraud_exclusion_candidate.sparql` surfaces candidates as a post-classification audit flag for human review; the exclusion is not expressed as a negation in OWL-RL (no negation gate exists in v1), so a fraud-detection system evaluating creditworthiness produces a false positive at the entailment layer, with the audit flag as the correction surface. See [docs/agent/eu_ai_act_rules.md](docs/agent/eu_ai_act_rules.md) "Known limit — 5(b) fraud exclusion."
- **Article 6(3) derogation is detected, not evaluated.** If a provider declares a `DerogationClaim`, `flag_derogation_candidate.sparql` surfaces it for human legal review. ARCO does not evaluate whether the claim is legally valid. The OWL-RL classification is computed independently of any derogation claim — a flagged system with all three gates satisfied is still entailed as `HighRiskSystem` in the ontology. The profiling-of-natural-persons exception (derogation always unavailable for profiling) is not separately modeled.
- **Biometric verification is correctly excluded from 1(a).** `BiometricVerificationCapability` is declared `owl:disjointWith BiometricIdentificationCapability` and is not a subclass of `AnnexIIITriggeringCapability`. A verification-only system does not satisfy Gate 1 for 1(a). This is intentional, tested, and documented in [03_TECHNICAL_CORE/ontology/ARCO_core.ttl](03_TECHNICAL_CORE/ontology/ARCO_core.ttl) line 79.

**Explicitly out of scope:**

- Article 5 prohibited AI systems — different regulatory structure, different obligations, not modeled.
- Article 51 general-purpose AI model / foundation-model obligations — different legal category.
- Article 10 training-data governance — ARCO classifies systems by capability, not by training-data provenance.
- Article 4 AI literacy and staff training — organizational obligation, not a system-level classification question.
- Article 26 operator retention, logging, and monitoring obligations — runtime concerns, not pre-deployment classification.
- Article 6(1) / Annex I product-safety high-risk path — ARCO encodes only the Article 6(2) / Annex III limb. A system can be high-risk under 6(1) (safety component of an Annex I harmonised product) with no Annex III category; ARCO's output carries no assessment of that limb.
- Article 3(1) "AI system" threshold — not evaluated; a human-adjudicated input commitment (see §1).
- Annex III category-1 chapeau conditionality ("in so far as their use is permitted under relevant Union or national law") — not modeled or surfaced.
- Article 3(13) reasonably foreseeable misuse — ARCO classifies on documented intended use only; misuse analysis is a non-goal of the current release.
- Article 50 transparency-tier obligations — a different risk tier; not modeled and not named in outputs.

---

## 3. Ontological commitments that carry stretch or debt

The [BFO commitment backtest](KB/40_REVIEWS/2026-04-20_bfo-commitment-backtest.md) grades each load-bearing choice against primary BFO/IAO/CCO/RO definitions. The choices below are not wrong; they are documented here so a reader can see where a serious ontologist would focus critique first.

### 3.1 Gate 3 role-category encoding — `cco:designates` over the role universal

Gate 3 expresses "this use scenario designates the natural-person role category" as:

```
UseScenarioSpecification (a Designative ICE) is_about some System
  AND cco:designates :NaturalPersonRole
```

`:UseScenarioSpecification rdfs:subClassOf cco:DesignativeInformationContentEntity`. The `cco:designates` filler is the role universal class IRI, not a role-token individual. `cco:designates` is the typed CCO designation property whose specification supports inscription naming an entity, including a universal (CCO range is `bfo:0000001` Entity, which admits both particulars and universals). Class-level designation is the load-bearing pattern: the spec designates the regulated role category by name, without instantiating a role-bearer at design time.

**Known sub-issues:**
- ARCO uses `cco:designates` to designate a role universal. CCO's canonical examples (URL designating a Web Page, name designating a person, VIN designating a vehicle) all designate particulars. ARCO widens the local reading to include universal designation; whether that widening is fully licensed is an open modeling question, and a strict CCO consumer may flag it.
- Instance authors must know the encoding convention: the Gate 3 target is the `:NaturalPersonRole` class IRI as the value of `cco:designates`, not a role-token individual and not a role-bearer instance. The role universal is preserved untouched in the realizable-entity tree for future deployment-time bearer modeling.
- The `AnnexIII_Condition_1a cco:prescribes :RemoteBiometricIdentificationProcess` triple in [ARCO_instances_sentinel.ttl](03_TECHNICAL_CORE/ontology/ARCO_instances_sentinel.ttl) line 25 is a separate class-as-individual usage retained for regulatory traceability. It does not affect current classification but is a known blocker for importing full CCO (see §4).

**Backtest grade:** Defensible encoding using the canonical CCO designation pattern, with an honest disclosure of the universal-designation widening.

### 3.2 `AnnexIIITriggeringCapability` is a regulatory grouping class, not a realist natural kind

`AnnexIIITriggeringCapability` groups together the capability subclasses whose realizations trigger regulatory consequences under Annex III. It exists because the law groups these together, not because they share a BFO-level natural-kind property. The class is honestly labeled in-file and in the architecture defense memo §4 as a regulatory artifact.

This is fine as long as it is described as such. It is **not** a discovered universal. ARCO does not claim otherwise.

### 3.3 `HighRiskSystem` as latent-risk flag, not the legal high-risk category

`HighRiskSystem` is satisfied by Gate 1 alone — the system has a component bearing an `AnnexIIITriggeringCapability`. It is ARCO's formal precondition flag. It is **not** equivalent to the EU AI Act's legal category "high-risk AI system" — that legal status also requires documented intent (Gate 2), an affected population (Gate 3), and the absence of a valid Article 6(3) derogation (not evaluated by ARCO). Outward-facing copy must not equate the two. The category-specific classes (`AnnexIII1aApplicableSystem`, `AnnexIII5bApplicableSystem`) are the stronger outputs.

### 3.4 `System ⊑ bfo:ObjectAggregate` is arguable

Many AI systems decompose cleanly as aggregates of material hardware components. Some (cloud-native, service-like, or purely software-as-a-service) do not. BFO does not compel either choice. ARCO commits to the aggregate pattern because it enables component-level capability tracing and produces meaningful evidence paths. A different system pattern (e.g., system as `MaterialEntity` without aggregate decomposition) would also be defensible and might fit certain deployment profiles better. If ARCO is applied to a system that does not decompose cleanly, the pattern may need adjustment.

### 3.5 Component-level bearer for Gate 1 capability

Gate 1 locates the capability disposition on a `SystemComponent`, not on the `System` itself. This is a design choice for traceability: it produces evidence paths like "system → component → disposition → triggering capability." The EU AI Act talks about systems, not hardware subcomponents. A whole-system bearer pattern would also be ontologically defensible. The component-level choice is not legally compelled.

A second, narrower simplification sits inside this gate: for a model-driven biometric module, the in-repo Sentinel fixture types the bearer as `:HardwareComponent` only, but a strict realist reading would locate the disposition on the *amalgam* of hardware plus the concretized model artifact running on it. The 2024 Capabilities paper's hardware-software-amalgam discussion treats software qua pattern as a generically dependent continuant, not itself a capable continuant; capabilities require a material bearer that concretizes the pattern. ARCO's classification result does not depend on which of these two bearer choices is taken — Gate 1 is satisfied as long as some component bearer instantiates a triggering-capability disposition — so the simplification is documented here rather than rebuilt as a structural change.

A third, related point: for software-configurable AI systems where the same hardware can be configured for different modes (e.g., 1:1 verification vs 1:N identification on the same biometric kiosk hardware), the disposition assertion describes what THIS specific deployment is intended to do under its current commitments, not what the hardware-in-isolation could theoretically do. ARCO does not make closed-world hardware-incapability claims; per-fixture disposition assertions reflect the configured-system commitments under OWA. A different deployment of the same hardware (different configuration, software, or database) would be modeled as a separate `:System` instance with its own asserted disposition. This matches the EU AI Act's classification on intended use (Recital 15, Recital 17, and the Annex III 1(a) operative carve-out, which together carry the "intended to be used for biometric verification" framing), not on raw hardware capability. Article 3(36) supplies the underlying 1:1 verification definition. Validated 2026-05-10 against vendor documentation for Suprema, ZKTeco, Matrix, HID, and IDEMIA biometric kiosks, all of which advertise the same hardware as configurable for both 1:1 and 1:N modes.

A fourth boundary case (added 2026-06-10): Gate 1 presupposes the capability-bearing hardware is a mereological part (`bfo:0000051`) of the described system. Where inference runs on a third party's hardware behind an API — the common SaaS architecture — the disposition inheres in hardware outside the described system's boundary, and under the fake-witness prohibition the reviewer may not mint a vendor-datacenter component without source warrant. Gate 1 then cannot fire honestly, and a system whose documented intent is clearly within a modeled category is not entailed (under-classification; cross-reference §3.4 on aggregate decomposition and §3.9 on Gate 1's evidential status). The system-boundary modeling decision is queued as M-SystemBoundary-1 in the working register.

### 3.6 Reality/representation split

Capabilities are BFO dispositions inhering in independent continuants. Intended uses and use scenarios are IAO/CCO information content entities (directive ICEs). This split is load-bearing for ARCO's entire architecture — if it blurs, the distinction between "what the system can do" and "what documents say" collapses. This is a **strength** of the design, listed here because any future extension that violates the split (e.g., putting a disposition on an information artifact, or a specification on a material component) would quietly break the classification guarantees.

### 3.7 Gate 2 named IUS subkind family and process-token treatment

ARCO's Gate 2 is factored via named subkinds of `:IntendedUseSpecification` (currently `:RemoteBiometricIdentificationIntendedUseSpec` for Annex III 1(a) and `:CreditworthinessEvaluationIntendedUseSpec` for Annex III 5(b)). Each subkind is a defined class via `owl:equivalentClass owl:intersectionOf (IntendedUseSpec, [prescribes someValuesFrom :RegulatedProcessClass])`, factored by what the IUS prescribes. This factoring mirrors the CCO Specification family pattern (Artifact Function Specification, Quality Specification, Plan, Algorithm). New Annex III categories add via the same template.

#### 3.7.a Process token existence-witness pattern

`owl:someValuesFrom` requires existence of an instance of the regulated process class. ARCO's fixtures mint typed process individuals (e.g., `:Sentinel_RBIP_Process rdf:type :RemoteBiometricIdentificationProcess`) for this purpose. These tokens are *bare*: they carry only the type assertion, with no participants, no temporal region, no realizer, no output. This is a deliberate choice: the process has not unfolded at design time, so participants and temporal extent would be assertions of facts that are not true. ARCO declines to adorn tokens with placeholder context that would be known-not-true.

Two failure modes are disclosed honestly:

- The bare token denotes (under owlrl materialization) a process particular asserted to be of the regulated kind without evidence of participants/time/realization. A strict realist reading treats this as residual debt against BFO's occurrent semantics (a Process is an entity that unfolds in time).
- Under a strict open-world reasoner, the existential restriction can be satisfied without an asserted token at all (the existence claim is permitted, not asserted). The "existence-witness" framing weakens to "permitted-but-not-asserted-witness" in that case.

ARCO accepts this debt rather than adorning with placeholders. Future deployment-time fixtures with real participants, real temporal regions, and real realizer chains would close the debt for the deployed cases without changing the design-time scope of this loop.

#### 3.7.b IUS subkind classes are defined classes by extrinsic regulatory criterion

The IUS subkind family is membership-fixed by Annex III categorial criterion, not by a shared natural-kind property of intended-use specifications in general. A `:RemoteBiometricIdentificationIntendedUseSpec` is one whose prescribed process is `:RemoteBiometricIdentificationProcess`, the kind named by Annex III 1(a). The `skos:definition` and `rdfs:comment` of each subkind disclose this explicitly. Membership at the particular level is non-exclusive: a single IUS instance may fall in multiple regulated subkinds if it prescribes multiple regulated process kinds (a hybrid system that does both biometric ID and credit evaluation). Disjointness is NOT asserted between IUS subkinds; cross-category isolation is provided by the gates' distinct class targets (each category's axiom requires its own capability and process kinds). The capability-layer disjointness additionally prevents a single disposition token from being dual-typed; it is the distinct `someValuesFrom` targets, not disjointness, that do the isolation work.

#### 3.7.c Real-time vs. post RBI subclass declaration; Article 5 routing scoped future

ARCO declares `:PostRemoteBiometricIdentificationProcess` and `:RealTimeRemoteBiometricIdentificationProcess` as disjoint subclasses of `:RemoteBiometricIdentificationProcess`. The regulatory verbatim text uses "system" rather than "process": Article 3(43) defines a post-RBI system as "a remote biometric identification system other than a real-time remote biometric identification system," and Article 3(42) defines a real-time RBI system as one whereby "the capturing of biometric data, the comparison and the identification all occur without a significant delay, comprising not only instant identification, but also limited short delays in order to avoid circumvention." ARCO models these as Process subclasses (BFO Bucket 4 / Occurrent) since classification reasons over the deployment-and-operation occurrence rather than the system artifact alone; the class-name "Process" is ARCO's modeling translation of the regulation's "system" term. The disjointness is correct: the regulation defines the two as exhaustive subtypes within the parent term.

The Annex III 1(a) Gate 2 axiom continues to reference the parent class via `someValuesFrom`, so subclass propagation means an IUS prescribing either a real-time or a post RBI process particular satisfies Gate 2 and entails `:AnnexIII1aApplicableSystem`. No fixture is currently typed into either subclass; both are forward-declared.

This is a deliberate scope-narrowing: Article 5(1)(h) prohibits real-time RBI in publicly accessible spaces for law enforcement (with conditional permissible-use carve-outs in Article 5(1)(h)(i)-(iii) and deployment conditions and prior judicial authorisation in Article 5(2)-(3)). For systems deployed by law enforcement in publicly accessible spaces, the regulation routes real-time RBI to the Article 5 prohibition rather than to Annex III 1(a) high-risk. ARCO does not yet model the Article 5 prohibited-practice class, deployer-actor entailment, or spatial/site context. Under the current parent-class Gate 2 routing, a real-time RBI process particular will entail `:AnnexIII1aApplicableSystem` regardless of deployer or context. This is correct for cases where Article 5(1)(h) does not apply (real-time RBI by non-law-enforcement deployers, or in non-publicly-accessible spaces, or post-RBI in any context). For Article 5-prohibited cases, ARCO currently fires Annex III 1(a) without an Article 5 prohibition flag; downstream consumers must handle this as a coverage gap pending Article 5 modeling. A future loop will introduce the prohibited-practice class, deployer-context modeling, and the routing.

#### 3.7.d Biometric-identification process genus

ARCO introduces `:BiometricIdentificationProcess` as the genus (Regulation (EU) 2024/1689 Article 3(35), one-to-many identification), with `:RemoteBiometricIdentificationProcess` re-parented under it as the regulated subkind (Article 3(41); its definition re-authored onto the differentia that does the regulatory work, performed without the subject's active involvement). Gate 2 continues to key on `:RemoteBiometricIdentificationProcess` only, so the bare genus does NOT entail Annex III 1(a). `:BiometricVerificationProcess` is held `owl:disjointWith` the genus, mirroring the capability-layer disjointness, so the genus does not subsume verification.

No positive "non-remote identification" class is minted. A verbatim audit of Recitals 15 and 17 confirmed the Act defines only three kinds: biometric identification (1:N, the genus, Art 3(35)); biometric verification (1:1, excluded, the exclusion explicitly naming "security access to premises"); and remote biometric identification (1:N without active involvement, the regulated subkind, Art 3(41)). There is no "cooperative identification" category in the Act. So the non-regulated cases are handled without inventing one: the at-the-door / premises-access case is biometric verification (`:BiometricVerificationProcess`, carved out per Recitals 15 and 17), and 1:N identification not asserted to be remote is the bare genus (`:BiometricIdentificationProcess`, not the remote subkind), which does not trigger 1(a). The bare genus is the honest non-triggering type the iDFace scratch backtest needed. An earlier draft minted a positive non-remote subkind; it was removed as an invented regulatory category after the verbatim source audit.

Disclosed debt:

- Whether a given walk-up 1:N deployment is "remote" (without active involvement, Art 3(41)) is genuinely left open by the Act. ARCO does not bake an answer into a class; it is a deployer-elicitation question (the forced-fork elicitation, component D).
- The remoteness differentia is carried by `:RemoteBiometricIdentificationProcess` and its `skos:definition`, not by a formal participant-structure axiom (semantic-not-axiomatic differentia, the same residual debt the existing process kinds carry). The abi-faithful upgrade (a `bfo:0000055` realizes / `ro:0000091` restriction tying the genus to `:BiometricIdentificationCapability` at a single point) is deferred.
- The verification / identification-genus disjointness is enforced at two layers, stronger than first documented here: `owlrl` fires `cax-dw` violations into closure error messages and the pipeline aborts the run on them (empirically verified 2026-06-10), and the HermiT (OWL 2 DL) cross-check independently catches the contradiction in CI. `owlrl` does not materialize the disjointness as a classification effect (no `owl:Nothing` membership), but a contradictory typing is a hard run failure under the production pipeline, not a HermiT-only catch.

### 3.8 Local subPropertyOf binding: ro:0000052 → bfo:0000197

ARCO commits the canonical OBO RO inherence property `ro:0000052` (RO label: "characteristic of"; this was the previous "inheres in" label before RO renamed it to avoid collision with the stricter BFO 2020 sense) as `rdfs:subPropertyOf bfo:0000197` (BFO 2020 "inheres in"). The binding lives at `03_TECHNICAL_CORE/ontology/ARCO_core.ttl` in section 5 (External Property Commitment).

**Why the binding exists.** RO removed the BFO range constraint on `ro:0000052` deliberately, to support domains where qualities inhere in processes or in information entities. ARCO does not model those domains. For ARCO's use cases (roles inhering in organizations, dispositions inhering in hardware components), the stricter BFO 2020 sense is the realist-correct commitment. The binding inherits BFO's range (IndependentContinuant intersected with not-spatial-region) on the inferred `bfo:0000197` triple via owlrl `prp-spo1` + `prp-rng` rules.

**Bounded enforcement.** The binding catches a wrong-typed bearer ONLY when that bearer is already typed as a member of a class disjoint with IndependentContinuant (for example, an Information Content Entity typed as `iao:0000030` which is `bfo:0000031` GenericallyDependentContinuant, disjoint from IndependentContinuant under BFO 2020 upper-level disjointness). It does NOT catch an untyped bearer (under the Open World Assumption, the reasoner accepts that an untyped bearer could still be an IndependentContinuant). For comprehensive bearer-type validation, the SHACL shapes at `03_TECHNICAL_CORE/validation/assessment_documentation_shape.ttl` remain the primary mechanism.

**Forward-looking constraints.** If ARCO ever expands scope to model qualities of processes, qualities of information artifacts, role-of-Site, role-of-Process, or hardware-software amalgam patterns where the disposition is pinned to a software pattern qua generically-dependent continuant, the binding will need revisit because RO removed the range precisely to support those cases. The current state of those scope cuts is documented in §3.4 (cloud-native), §3.5 (hardware-software amalgam), §3.7 (process tokens), and §6 (temporal, spatial, lifecycle).

**Pattern precedent.** This is the same axiomatic shape as `cco:designates rdfs:subPropertyOf iao:0000136` already declared at `ARCO_governance_extension.ttl:140`, though the semantic direction differs: that binding widens `cco:designates` up into `iao:is_about` to reflect designation into the same aboutness layer used elsewhere in ARCO, whereas this binding narrows `ro:0000052` down through BFO's stricter range. CCO uses subPropertyOf binding extensively (for example, `cco:has_output rdfs:subPropertyOf BFO_0000057`). The pattern is canonical, not novel.

**What this binding does NOT do.** It does not replace RO. ARCO still uses `ro:0000052` in all fixture assertions, SPARQL queries, and SHACL shapes. RO's `owl:FunctionalProperty` declaration on `ro:0000052` (one-bearer-per-role-or-disposition) remains in effect. RO's sub-property family (function_of, quality_of, role_of, disposition_of) remains intact in the loaded slim. The binding adds one TBox axiom in ARCO's namespace; it does not modify upstream.

### 3.9 Gate 1 is an ARCO-added evidential condition (under-classification direction)

The Annex III conditions ARCO encodes trigger on documented intended purpose: 5(b) reads "intended to be used to evaluate the creditworthiness of natural persons…", and 1(a) regulates remote biometric identification systems, which Article 3(41) defines by their purpose ("an AI system for the purpose of identifying natural persons, without their active involvement…"). Neither provision conditions applicability on a demonstrated component-level capability. ARCO's three-gate `equivalentClass` axioms make the Gate 1 capability disposition conjunctively necessary anyway, because surfacing latent capability at design time is the project's thesis.

The consequence is a deliberate strictness in the **under-classification** direction — the mirror of the disclosed over-classification cases (fraud carve-out, derogation): a reviewed description carrying a fully documented regulated intended use (Gate 2) and designated natural persons (Gate 3) but no reviewed capability commitment (Gate 1) is **not** entailed, and the output reads as a negative. Gate 1 is ARCO's evidential addition, not an Annex III condition; "three gates satisfied → Annex III-shaped" is the legally grounded direction, not the converse. Outward copy must not present the three-gate conjunction as what the regulation itself requires.

A report-only audit flag for the "documented intent without asserted capability" case is queued in the working register (L3.10); whether category applicability should instead entail from Gates 2 and 3 alone, with Gate 1 reported as evidence strength, is an open modeling decision (M-Gate1Status-1), sequenced behind the foundation modeling map.

---

## 4. Property-layer grounding

ARCO loads BFO 2020 as a full upstream file and loads RO, IAO, and CCO as **ROBOT BOT-extracted slim modules** per the OBO Foundry / Ontology Development Kit (ODK) standard pattern. BOT is a syntactic-locality module variant (Cuenca Grau, Horrocks, Kazakov, Sattler 2008) that preserves all axioms whose signature is contained in the seed signature — including `rdfs:domain`, `rdfs:range`, property chains, inverse-of axioms, and property characteristics (`FunctionalProperty`, `Transitive`, `Symmetric`). The seed term lists are version-controlled at `03_TECHNICAL_CORE/ontology/imports/seeds/` and the slim modules are reproducible from the pinned upstream releases.

| Upstream ontology | Version | Status | How loaded |
|---|---|---|---|
| BFO 2020 | ISO/IEC 21838-2:2021 | Full upstream file | `imports/bfo-2020.owl` |
| RO | release `2025-12-17` | ROBOT BOT slim module | `imports/ro_bot.owl` (seed: `seeds/ro_seed.txt`) |
| IAO | release `2026-03-30` | ROBOT BOT slim module | `imports/iao_bot.owl` (seed: `seeds/iao_seed.txt`) |
| CCO | v1.7 pinned semantic-IRI release | ROBOT BOT slim module + bridge/readability declarations | `imports/cco_bot.owl` (seed: `seeds/cco_seed.txt`) plus local declarations in `ARCO_governance_extension.ttl` that map CCO Directive, Descriptive, and Designative Information Content Entity classes into `iao:0000030`, assert `cco:designates rdfs:subPropertyOf iao:0000136`, and keep BFO subsumptions for `cco:Person` and `cco:Organization` readable in-file |

Per-ontology audits (2026-04-29, see `docs/agent/alignment_audit_{RO,IAO,CCO}_2026-04-29.md`) verify term-level consistency: RO 5/5, IAO 2/2, CCO 6/6.

**What this means for claims:**

- ARCO is **BFO-grounded** — instances have real BFO supertype chains and disjointness enforcement is active under the reasoner.
- ARCO is **RO/IAO-aligned and CCO-informed** — property usage is consistent with upstream semantics and the BOT modules carry domain/range and characteristic axioms over the seed signature.
- The correct external claim is "BFO 2020-grounded, with RO, IAO, and CCO loaded as ROBOT BOT-extracted slim modules per the OBO Foundry / ODK standard pattern." Wording such as "full CCO validation" or "BFO/CCO certified" implies a certification ARCO does not claim — see `docs/agent/ARCO_public_claims.md` "Excluded Statements."

The staged-full-import question that earlier versions of this document discussed has been resolved: ADR-001 ("BFO/CCO Alignment End State") records the decision and the BOT-import experiment in branch `experiment/bot-extracted-imports` realized it. The full-upstream-import alternative was tested in PRs #24 and #25 and confirmed byte-identical classification outputs at substantially higher reasoning cost (see `README.md` "Why ROBOT BOT slim modules" §5 for the operational comparison).

Detail: [docs/agent/adr_001_alignment_end_state.md](docs/agent/adr_001_alignment_end_state.md), [docs/agent/bfo_cco_alignment_audit.md](docs/agent/bfo_cco_alignment_audit.md) (historical), and the three 2026-04-29 alignment audits.

---

## 5. Input and ingestion

ARCO accepts hand-authored RDF/Turtle instance files against the core ontology. No automatic intake exists.

**Specifically:**

- There is no parser for narrative system descriptions, regulatory filings, or policy documents.
- There is no adapter for JSON, CSV, JSON-LD, or other structured-but-non-RDF formats.
- There is no LLM-backed extraction path in the classification pipeline. LLMs may be used upstream to draft instance data, but the classification itself runs on the hand-reviewed RDF — not on LLM output directly.
- Instance authors must know ARCO encoding conventions that are not machine-enforced at authoring time:
  - Gate 2 prescribed process must be a typed process *individual* (e.g., `Sentinel_RBIP_Process rdf:type :RemoteBiometricIdentificationProcess`), not a class IRI used as an individual.
  - Gate 3 `cco:designates` target must be the `:NaturalPersonRole` class IRI (universal designation), and the use scenario specification must be typed as a `cco:DesignativeInformationContentEntity` for the gate restriction to fire.
  - Hardware components must declare dispositions via `ro:has_disposition` (RO:0000091), not via `bearer_of` or other generic relations.
  - Software artifacts must be typed as ICEs, not as `SystemComponent` — putting a disposition on a software artifact is a BFO category error.

**Consequence.** ARCO does not today accept arbitrary descriptions from providers and produce classifications. Providers or intermediaries must produce ARCO-shaped instance data. Reducing this burden is a known engineering direction but is not in v1.

---

## 6. Temporal, lifecycle, and actor-model limits

- **No BFO temporal-region modeling.** The condition assessment certificate records a determination timestamp as an ISO 8601 string. There is no `bfo:TemporalRegion` modeling, no compliance-interval representation, no reassessment trigger.
- **No Article 25 substantial-modification tracking.** If a deployed system is materially changed post-classification, ARCO has no built-in mechanism to detect that the earlier classification is stale. Re-running the pipeline against an updated instance file is the only path.
- **No provider / deployer / distributor / importer actor distinction.** The ontology contains `ProviderRole` and `DeployerRole` as BFO Role subclasses and a minimal `ProviderOrganization` class (subClassOf `cco:Organization`). There is no formalized delegation or obligation chain between these actors, no representation of jurisdictional transitions, and no modelling of the Article 25 "distributor becomes provider upon substantial modification" rule.
- **No structural authorship triple from `:ProviderOrganization` to `:IntendedUseSpecification`, `:UseScenarioSpecification`, or `:ComplianceDetermination` ICEs.** In the kiosk fixture (`ARCO_instances_verification.ttl`) the provider organization is linked to the system only via the `:AssessmentDocumentationProcess` participant chain (`ro:0000057`) plus `cco:has_output` to `:AssessmentDocumentation`. No triple asserts that the provider authored the IUS, USS, or determination ICEs directly. This is a deliberate scope cut: the three-gate classification depends on what the IUS prescribes and the USS designates, not on who authored them. The parent disclosure at the bullet above ("no formalized delegation or obligation chain between these actors") covers the actor-to-actor side; this bullet covers the actor-to-ICE structural side. A future scope extension into provider obligation entailment (Article 16, Article 47) would activate the authorship modeling.
- **No site, spatial, or deployment-location modeling.** The BFO Site category is not instantiated.
- **No quality or physical-property modeling.** The BFO Quality category is not instantiated.

These are intentional scope boundaries, not accidental omissions. Extending any of them requires a deliberate ontology decision, not an incremental addition.

---

## 7. What each pipeline layer does and does not do

Three layers. Not interchangeable. Each has a single authority.

### 7.1 OWL-RL (classification layer)

**Does:** Compute which systems satisfy the equivalentClass definitions for `HighRiskSystem`, `AnnexIII1aApplicableSystem`, `AnnexIII5bApplicableSystem` via materialized deductive closure.

**Does not:** Evaluate content accuracy, check whether the provider's description matches deployed behavior, apply legal reasoning, or resolve Article 6(3) derogation validity.

**Reasoner dependency.** Verified on `owlrl==7.1.4`. Gate 2 and Gate 3 use anonymous inverse property expressions in equivalentClass axioms (`[owl:inverseOf iao:0000136]`). These are valid OWL 2 DL, but reasoner portability across other OWL-RL implementations is not tested. Changing the reasoner requires re-verification.

### 7.2 SHACL (documentary completeness layer)

**Does:** Validate that documentary artifacts are structurally present and correctly linked — that an `IntendedUseSpecification` exists, prescribes a Process, and is `is_about` a System; that a `UseScenarioSpecification` exists and is `is_about` a Role; and so on. Shapes are in [03_TECHNICAL_CORE/validation/assessment_documentation_shape.ttl](03_TECHNICAL_CORE/validation/assessment_documentation_shape.ttl).

**Does not:** Classify systems. A SHACL pass means the documentary record is structurally complete. It does not mean the system is or is not high-risk. A SHACL fail does not overturn the OWL-RL classification — they are independent checks.

**Does not:** Evaluate content accuracy or legal sufficiency. SHACL checks that a `ComplianceObligationSpecification` *exists* and has the required links; it does not check that the specification covers all obligations the provider actually bears under the Act, nor that obligations have been discharged.

**Subtle design dependency.** The Gate 3 SHACL shape verifies that the use scenario specification carries `cco:designates :NaturalPersonRole`. The shape runs against the post-OWL-RL reasoned graph, so the universal-designation check holds without requiring a separately-typed role-token individual. This pairs with the OWL gate axiom (`cco:designates owl:hasValue :NaturalPersonRole`) so SHACL and OWL agree on what counts as Gate 3 satisfaction.

### 7.3 SPARQL ASK (audit and flag layer)

**Does:** Verify post-reasoning entailments are present on the reasoned graph, and detect declared artifacts requiring human review (`DerogationClaim`, `FraudDetectionProcess`).

**Does not:** Classify. A SPARQL query returning FALSE does not mean the OWL classification is wrong; it means a specific pattern was not found. OWL-RL classification is computed before and independently of any SPARQL query.

**Does not:** Evaluate the legal validity of declared artifacts. A `DerogationClaim` is surfaced for human legal review, not evaluated.

A SHACL fail and an OWL-RL classification result are independent. Diagnose each in its own layer. Do not patch one to satisfy the other.

### 7.4 Cross-reasoner agreement and known profile divergence

**Does:** Run a HermiT (full OWL 2 DL) cross-check via ROBOT in CI on every push and PR. The check merges ontology + imports + core + governance + each certificate-grade fixture, runs HermiT, and compares classification SPARQL results against the production OWL-RL pipeline for every modeled system across the certificate-grade fixture set (Sentinel, CreditScorer, verification kiosk, DecoySystem, WeirdCalcSystem, both flag tests). Disagreement on any (fixture, system, query) triple fails the build. Logic and exclusion rules: [03_TECHNICAL_CORE/scripts/hermit_cross_check.py](03_TECHNICAL_CORE/scripts/hermit_cross_check.py).

**Does not:** Cover the `ARCO_instances_adversarial_blanknode.ttl` fixture (`GhostSystem_001`). GhostSystem's disposition is an anonymous individual (blank node), and HermiT does not emit `ClassAssertion` axioms for anonymous individuals in its serialized output — this is correct DL profile behavior, since anonymous individuals are existential witnesses for satisfiability, not first-class ABox individuals. The `detect_latent_risk` audit traversal therefore returns `False` under HermiT and `True` under OWL-RL on GhostSystem. The classification entailment itself (`HighRiskSystem`, `AnnexIII1aApplicableSystem`) fires correctly under both reasoners; the divergence is confined to the audit-side traversal that walks `?system → ?component → ?disposition a :AnnexIIITriggeringCapability`.

GhostSystem is a reasoner-property probe (it tests OWL-RL's `owl:someValuesFrom` entailment on anonymous existentials), not production modeling guidance. The question of whether ARCO should require named IRIs for evidence-bearing dependent continuants in certificate-grade data is queued for a human modeling session, not resolved by this CI gate. See the local design memos and modeling-decisions queue (runs/loop, 2026-05-09; untracked working notes) (Q1).

**Operational implication.** Real ARCO classification scenarios use named dispositions, named ICEs, and named role categories — see Sentinel, CreditScorer, the verification kiosk, the flag fixtures. The HermiT cross-check holds on all of them. The blank-node case is a fixture-only edge that does not appear in production modeling.

### 7.5 Output composition layer (Boundary 4): known integrity gaps

**Added 2026-05-09. Updated 2026-05-11** — closure annotations added for items resolved on main; remaining live items retain their original framing.

The pipeline's output layer (`run_pipeline.py` from line 1699 onward, plus `write_html_view`) composes the certificate, `summary.json`, `determination_packet.json`, and the HTML view from SPARQL bindings, Python computations over those bindings, and hardcoded constants. This layer has no discipline analogous to the two-layer rule of §7.1 through §7.3. The 2026-05-09 code-only audit identified the following gaps.

**Cross-layer contradictions** (output emits commitment-shaped values inconsistent with the graph or with adjacent fields):

- `all_checks_passed: true` can coexist with per-check `FAIL` fields in the same `summary.json`. On non-applicable runs (e.g. `VerificationKiosk_001`), `audit_pass` is set to `True` by a Python short-circuit (`run_pipeline.py:1775-1787`) regardless of which audit checks failed. The certificate's "ALL CHECKS PASSED" banner is false on these runs. **CLOSED 2026-05-10 (PR #36, OPEN_PROBLEMS L4.1).** The force-True short-circuit is removed: `audit_pass` and `all_pass` both return `None` on non-applicable runs. A new `applicability_status` enum (`applicable` / `not_applicable`) is added to `summary.json` and `determination_packet.json`. Schema bumped 1.2 → 1.3. Consumers see distinct applicability vs. audit fields.
- `determination_node_uri` is a hardcoded constant (`run_pipeline.py:2041`). It emits `:HighRisk_Determination_001`, which exists as a graph node only in `ARCO_instances_sentinel.ttl`. Runs against `ARCO_instances_creditscoring.ttl` or `ARCO_instances_verification.ttl` emit an IRI not asserted in the loaded graph for that run. **CLOSED 2026-05-10 (PR #36, OPEN_PROBLEMS L4.2).** New `reasoning/select_determination_node.sparql` selects the determination node from the run's reasoned graph; `run_pipeline.py:2108` binds the result. Sentinel returns `:HighRisk_Determination_001`, CreditScorer returns `:CreditScorer_Determination_001`, verification kiosk and decoy return `null`, flag-tests return their asserted IRIs. Asserted-vs-entailment alignment is tracked separately at `OPEN_PROBLEMS.md` X.9.
- Gate 2 evidence selection uses `LIMIT 1` without `ORDER BY` and without category filtering (`run_pipeline.py:430-449`). The behaviour is **underdetermined**: on `FlagTest_CreditSystem_WithFraudProcess` the packet and HTML can name either `:FraudDetectionProcess` or `:CreditworthinessEvaluationProcess` as the process satisfying Gate 2, because SPARQL row order without `ORDER BY` is implementation-defined. Same fixture, same data, different certificate evidence across runs. The 5(b) classification entails correctly either way; the audit-trace claim is what is non-reproducible. Closing this requires both `ORDER BY` (for determinism) and a category filter (for correctness); a half-fix that does only one leaves the underdetermined behaviour live. **CLOSED 2026-05-10 (PR #36, OPEN_PROBLEMS L3.1).** Inline SPARQL moved to `reasoning/select_gate_2_prescribed_process.sparql` with `ORDER BY ?ius ?process` for determinism and a `FILTER(?process_class IN (:RemoteBiometricIdentificationProcess, :CreditworthinessEvaluationProcess))` category filter for correctness.

**Sentinel-shaped hardcoding** (the same affected-role pattern is hardcoded in three independent places, making the Gate 3 surface category-specific rather than parameterized):

- Python: Gate 3's display and determination-packet status now require the USS to designate `:NaturalPersonRole`; USS existence alone is not treated as Gate 3 satisfaction. **CLOSED 2026-05-20 (OPEN_PROBLEMS L3.4)** for the current modeled categories. **LIVE** (OPEN_PROBLEMS L3.2): the role target remains hardcoded to `:NaturalPersonRole` rather than parameterized by Annex III category.
- SPARQL: `check_intended_use.sparql:31` hardcodes `cco:designates :NaturalPersonRole`, bundling Gates 2 and 3 into one ASK with the affected role baked in. **LIVE** (OPEN_PROBLEMS L3.2).
- SHACL: `assessment_documentation_shape.ttl:96-100` hardcodes `sh:hasValue :NaturalPersonRole` at the shape level. **LIVE** (OPEN_PROBLEMS L3.2). The 5(b) HTML-emission counterpart was a separate locus and is **CLOSED 2026-05-10 (PR #34, OPEN_PROBLEMS L3.3)**: `write_html_view`'s 5(b) branch now reads `gate_evidence["gate2"]["process_type_label"]` and the parameterized gate-evidence helpers rather than Python literals.

**Synthesized narrative**:

- The certificate's Annex III line now emits pure graph-backed values such as `VERIFIED (ENTAILED)` or `NOT APPLICABLE`. Article 6(3) derogation scope is surfaced separately as run metadata (`ARTICLE 6(3) DEROGATION: NOT EVALUATED (run scope)` in the certificate and `derogation_evaluation_scope` in `summary.json`). **CLOSED 2026-05-20** for the mixed-provenance string caught by `test_output_provenance.py`. **REMAINING**: Article 6(3) validity is still not evaluated; `:DerogationClaim` is surfaced for human legal review only.

**Operational**:

- `runs/demo/` is not auto-cleaned. The OUTPUT FILES listing (`run_pipeline.py:2082-2083`) advertises every file present, so reverted artifacts can appear as current outputs until manually removed.
- Pipeline exit code reflects classification only (`run_pipeline.py:2085-2091`). Audit-layer failure produces exit 0. Wrappers consuming exit code must separately parse `summary.json` to detect audit failure.
- The MCP HermiT tool runs one named fixture per call; the standalone `hermit_cross_check.py` is the fixture-wide sweep used by CI. An LLM calling the MCP tool gets a bounded single-fixture assurance signal unless it explicitly runs multiple calls.
- The fixture-wide HermiT cross-check has failed with `WinError 5` on at least one Windows local environment. The 24/24 agreement claim holds in CI but is not currently reproducible across all developer machines.

**Path forward.** A "Three-Block Output Discipline" rule (graph-backed / run-metadata / documentary) is queued in the local modeling-decisions queue (Q12; untracked working notes). The schema bumps it implies (`summary.json` and `determination_packet.json` 1.3 to 2.0) are contract changes requiring a human modeling session. A planned CI gate (`test_output_provenance.py`) will fail on current output and pass after the schema rework. Until that work lands, the gaps above are present in the pipeline.

---

## 8. Legal authority and validation

- **The three-gate encoding has not been validated by a qualified EU AI Act lawyer.** It is an engineering interpretation of Article 6 and Annex III. Internal consistency (OWL entailment is correct under the encoding) does not prove the encoding correctly captures legal intent.
- **ARCO is a self-assessment tool.** It does not perform or substitute for a conformity assessment under Article 43.
- **NCOR affiliation is at the upstream-ontology level, not the ARCO level.** BFO is maintained by the National Center for Ontological Research, which is the credentialing authority for BFO-conformant ontologies. ARCO builds on BFO. ARCO has **not** been formally reviewed or credentialed by NCOR. Outward-facing copy must not imply NCOR has evaluated ARCO specifically.
- **Audit-artifact retention is the operator's responsibility.** The pipeline writes certificate, summary, evidence, and SHACL report artifacts to `runs/demo/`. Retention, access control, and integrity guarantees beyond file-system persistence are out of scope.

---

## 9. Engineering gaps

- **Negative test infrastructure is incomplete.** Gate-removal regression tests ([test_gate_removal.py](03_TECHNICAL_CORE/scripts/test_gate_removal.py)) verify each gate is independently necessary for both modeled Annex III categories (1(a) Sentinel and 5(b) CreditScorer) by mutating axioms and confirming entailment breaks. Symmetric coverage across the two categories was added 2026-05-14. Adversarial-mechanism tests ([test_adversarial_mechanism.py](03_TECHNICAL_CORE/scripts/test_adversarial_mechanism.py)) verify three cases: DecoySystem_001 classifies via `owl:equivalentClass` on the Annex III 1(a) branch (not direct IRI assertion); WeirdCalcSystem_001 classifies via `owl:equivalentClass` on the 5(b) branch with cross-category isolation preserved (added 2026-05-20); and GhostSystem_001 classifies via blank-node `owl:someValuesFrom` (not a named individual). What does **not** exist is a parameterized test harness that loads an isolated deliberately-miscategorized instance file and runs the full pipeline against it, because the pipeline currently loads all TTL files into a single graph before reasoning — a negative-case file in the graph would contaminate positive cases. Building this harness is Step 2 of the ADR-001 work plan. Noted in [docs/agent/bfo_cco_alignment_audit.md](docs/agent/bfo_cco_alignment_audit.md) §"Unresolved Engineering Problem."
- **Dependency pinning.** The pipeline is verified only on: `rdflib==7.6.0`, `pyshacl==0.31.0`, `owlrl==7.1.4`. Upgrading any of these requires re-running the full regression suite. The `owlrl` pin is especially load-bearing: Gate 2 and Gate 3 use anonymous inverse property restrictions whose entailment behavior could change across reasoner versions.
- **`AnnexIII_Condition_1a cco:prescribes :RemoteBiometricIdentificationProcess`** remains in [ARCO_governance_extension.ttl](03_TECHNICAL_CORE/ontology/ARCO_governance_extension.ttl) (moved 2026-05-14 from the Sentinel instance file to the governance extension as universal regulatory content) as a class-as-individual triple retained for regulatory traceability. The companion 5(b) triple `:AnnexIII_Condition_5b cco:prescribes :CreditworthinessEvaluationProcess` is in the same file. Neither affects current classification. Both are known blockers for a future CCO import (see §4).
- **Single-reasoner portability.** The anonymous inverse property expressions in Gate 2 and Gate 3 equivalentClass axioms have been empirically verified on `owlrl==7.1.4` only. Other OWL-RL reasoners may or may not materialize these the same way.
- **No automated tracking of regulatory amendments.** Annex III categories and Article 6(3) derogation criteria may change via EU delegated acts. Updates to the ontology are manual.

---

## 10. What ARCO is not

Plainly, to prevent adjacent-category confusion:

- **Not a runtime governance tool.** ARCO does not intercept tool calls, memory writes, inter-agent messages, or any runtime agent action. It does not perform Policy Enforcement Point (PEP) or Policy Decision Point (PDP) roles. Pre-deployment classification is the scope.
- **Not a content-moderation or prompt-safety tool.** ARCO does not inspect LLM inputs or outputs, does not detect prompt injection, and does not enforce content policies.
- **Not a training-data governance tool.** Article 10 obligations around training-data quality, representativeness, and provenance are out of scope.
- **Not a conformity-assessment substitute.** ARCO does not execute Article 43 conformity-assessment procedures or issue the related attestations.
- **Not a legal-advice tool.** ARCO encodes a formal interpretation; it does not replace counsel or notified-body review.
- **Not a certification.** The pipeline produces a classification certificate artifact; this is technical output, not a regulatory certification.
- **Not a probabilistic classifier.** No scores, no confidence levels, no thresholds. Entailment or non-entailment, deterministically reproducible under the pinned reasoner.
- **Not a deployable enterprise compliance tool.** ARCO is a reference implementation of an architectural pattern. Producing a defensible client-facing determination for a real AI deployment requires per-deployment instance authoring grounded in the provider's actual documentation, documentary anchoring per Article 3(12), Article 6(3) derogation evaluation, provider/deployer obligation differentiation, real-time vs post biometric distinction for Annex III 1(a), and external legal counsel review. README.md "What ARCO is, and what it is not" enumerates the gap.

---

## 11. Relationship to other governance tools

ARCO occupies the **pre-deployment classification** layer. Adjacent tools occupy different layers and are not substitutable:

- **Runtime governance platforms** (e.g., Microsoft Agent Governance Toolkit, ATOM) intercept agent actions and apply policy. They assume a classification has already happened — a "high-risk" deployment requires a different policy bundle than a "limited-risk" one. ARCO's output can condition that selection; there is no built-in integration today.
- **Content-safety tools** operate at the token level and are orthogonal to ARCO.
- **Model-evaluation and red-teaming tools** assess deployed model behavior and are orthogonal to ARCO.
- **Identity and credentialing frameworks** (DID, SPIFFE/SVID) assign identities to agents and are orthogonal to ARCO.

If a downstream tool requires ARCO output as input, the interface is the current pipeline artifacts in `runs/demo/` (certificate, summary JSON, evidence bindings, SHACL report). No adapter for any specific downstream tool is shipped.

---

## 12. Dual-use disclosure

The architectural pattern ARCO uses is general-purpose. Deterministic OWL-RL classification, three-gate `equivalentClass` entailment, BFO grounding via slim modules, SHACL completeness validation, SPARQL audit and flag, the full evidence chain. None of these are specific to compliance work or to the EU AI Act. The same pattern, with different class names and different gate definitions, can be reused for surveillance categorization, target classification, behavioral profiling, autonomous-weapons targeting decisions, or any other person-categorization workflow at scale.

A vendor implementing such a system does not need to copy any ARCO file. They re-implement the pattern in their own namespace with their own classes. There is no mechanism by which copyright, licensing, or technical means can prevent this. The pattern itself is mathematics, in published OBO Foundry literature for over a decade. It is not ownable.

The properties that make ARCO valuable for compliance are exactly the properties that would make a surveillance system more powerful and harder to challenge legally. Deterministic output is more legally defensible than a probabilistic classifier. Audit traceability looks the same whether the audit is for compliance or for operational targeting. The three-gate pattern maps cleanly onto person-categorization workflows: capability of the system, intended use of the deployer, role of the affected entity. A judge looking at the certificate output of a compliance system and a surveillance system grounded in the same architecture cannot tell the difference by looking at the reasoning chains alone. Both are equally rigorous.

ARCO has no architectural mechanism to prevent this adaptation. The bounded scope of this work (EU AI Act Annex III 1(a) and 5(b) compliance assessment of AI systems) is a public-claim discipline, not a technical or legal constraint. Disclosure is the only honest response available.

**Required disclosure language.** ARCO uses a formal-ontology approach that is general-purpose. The specific encoding ARCO contains is bounded to EU AI Act Annex III 1(a) and 5(b) compliance classification of AI systems. The architecture's generality means a different encoding could be used for purposes ARCO does not endorse, including surveillance-scale categorization. ARCO has no technical mechanism to prevent that adaptation; the bounded scope is a public-claim discipline, not an architectural constraint.

---

## 13. How this document is maintained

- Update this document **first** when scope changes, before README or commercial copy.
- A claim in README, EXEC_PITCH, or any outward-facing artifact that exceeds what this document permits is a bug. Correct the outward artifact, not this one.
- The scope boundary in §2 is coupled to [docs/agent/eu_ai_act_rules.md](docs/agent/eu_ai_act_rules.md). Both must be updated together when coverage changes.
- The ontological commitment status in §3 is coupled to [KB/40_REVIEWS/2026-04-20_bfo-commitment-backtest.md](KB/40_REVIEWS/2026-04-20_bfo-commitment-backtest.md). When a commitment's grade changes (a stretch is resolved, a new stretch is introduced), update the backtest first, then this document.
- The property-layer status in §4 is coupled to [docs/agent/bfo_cco_alignment_audit.md](docs/agent/bfo_cco_alignment_audit.md). Import progress updates there first.
