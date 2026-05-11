# ARCO Explained

A top-to-bottom walkthrough of what ARCO is, how it works, why each modeling decision was made, and how it compares to other approaches to AI governance. This document is the long-form companion to the README. The README answers "what does ARCO do." This document answers "why does ARCO work the way it does, and what is it doing under the hood at every step."

If you want to evaluate ARCO seriously, this is the source. If you want the demo, this is also the source the demo narrates from.

---

## Contents

1. [The problem ARCO solves](#1-the-problem-arco-solves)
2. [Why current approaches fall short](#2-why-current-approaches-fall-short)
3. [The core architectural commitment: reality vs representation](#3-the-core-architectural-commitment-reality-vs-representation)
4. [Why this ontological stack (BFO, RO, IAO, CCO)](#4-why-this-ontological-stack-bfo-ro-iao-cco)
5. [The three-gate model](#5-the-three-gate-model)
6. [The two-layer pipeline](#6-the-two-layer-pipeline)
7. [Worked example: Sentinel-ID end to end](#7-worked-example-sentinel-id-end-to-end)
8. [Independent verification: the HermiT cross-check](#8-independent-verification-the-hermit-cross-check)
9. [PRIMARY classification vs LATENT-RISK FLAG](#9-primary-classification-vs-latent-risk-flag)
10. [How ARCO compares to other approaches](#10-how-arco-compares-to-other-approaches)
11. [Modeling decisions in plain terms](#11-modeling-decisions-in-plain-terms)
12. [What ARCO is not, and known limitations](#12-what-arco-is-not-and-known-limitations)
13. [What the architecture generalizes to](#13-what-the-architecture-generalizes-to)

---

## 1. The problem ARCO solves

The EU AI Act creates obligations that attach to AI systems based on what those systems are capable of doing, who they are intended to be used on, and in what context. Article 6 and Annex III define the high-risk classification: if a system meets the conditions of any Annex III category, the provider takes on a heavy package of obligations (conformity assessment, risk management system, technical documentation, post-market monitoring, and more). If the system also engages in prohibited practices under Article 5, the consequences are sharper still.

The fines reflect that. EU AI Act Article 99(4) sets administrative fines for non-compliance with operator obligations at up to 3% of total worldwide annual turnover or €15,000,000, whichever is higher. Article 99(3) sets the ceiling for prohibited practices under Article 5 at up to 7% or €35,000,000.

There are three real costs of getting this wrong:

1. **The provider's design-time cost.** A team builds an AI system. Mid-development or post-deployment, someone realizes the system probably triggers Annex III. Now the team has to retrofit conformity assessment, risk management, post-market monitoring, technical documentation. Sometimes the architecture itself has to change. Sometimes the deployment has to be withdrawn. Every one of those costs is dramatically larger than the cost of knowing earlier.
2. **The regulator's audit cost.** A regulator looking at a high-risk system needs to see a defensible chain of reasoning showing why the system was classified the way it was. A score does not give them that. A confidence level does not give them that. A spreadsheet of yes/no answers does not give them that. They need a chain.
3. **The institutional buyer's procurement cost.** A bank, hospital, or government department buying an AI system from a vendor cannot rely on the vendor's word that the system is or is not high-risk. They need an artifact they can audit themselves and that holds up if challenged.

ARCO is a pre-deployment classification engine that produces that artifact. It tells you, before you build or buy, whether a system satisfies ARCO's formal encoding of an Annex III category, and exactly why. The output is a certificate with a full evidence path: which component bears which capability, which intended-use specification carries the prescribed process type, which role universal the use scenario references, and which Annex III applicability class is therefore entailed.

The classification is deterministic. The same structured input produces the same classification every time. A regulator can re-run it. A buyer can re-run it. A second auditor can re-run it. The reasoning chain is the artifact, not a confidence score.

---

## 2. Why current approaches fall short

ARCO is not the only thing in this space. It is competing implicitly with at least four other approaches. None of them produce what ARCO produces, and the gap is not cosmetic.

### LLM-based compliance scoring

A common product shape today: feed a system description to a large language model, get back "this system appears to fall under Annex III 1(a) with 87% confidence." The output looks authoritative and is fast to produce.

It fails the audit test. Confidence levels are not entailments. The same input run twice can produce different outputs. There is no chain of reasoning to inspect. A regulator asking "why does this system classify as 1(a)" gets a generated paragraph that may or may not correspond to anything the model actually computed. The model itself can be updated and silently change its outputs. None of that is governable.

There is also a circularity. If you are using an LLM to decide whether your AI system is high-risk under the AI Act, you are deciding the regulatory status of one AI system using another AI system, with neither having an auditable reasoning chain. That posture is fine for ideation. It is not fine for the determination that drives a conformity assessment.

### Spreadsheet and checklist tooling

Many compliance tools today are essentially structured questionnaires. Does the system process biometric data? Does it make decisions about natural persons? Does it operate in a high-risk sector? Tick the boxes. The output is a verdict and a paper trail.

These tools have a documentary-completeness problem and a content-sensitivity problem. The documentary problem: a checklist asks "do you have an intended use document?" and accepts a yes. It does not check what is in the document. The content problem: the regulated condition is not "the provider has an intended use document," it is "the provider's intended use document prescribes a regulated process type for a regulated affected role." Existence of an artifact is not equivalent to the right content being inside the artifact.

ARCO's gates are content-sensitive. Gate 2 does not check that an `IntendedUseSpecification` exists. It checks whether that specification prescribes some instance of `RemoteBiometricIdentificationProcess` (or `CreditworthinessEvaluationProcess`, for 5(b)). Gate 3 does not check that a `UseScenarioSpecification` exists. It checks whether that scenario references the affected role universal, `NaturalPersonRole`. The check fires on what the document says, not on whether a document is present.

### Generic enterprise ontologies and "compliance graphs"

Several enterprise-data vendors offer "compliance ontologies" or "regulatory knowledge graphs." Most are RDFS or lightweight OWL schemas with custom properties. They model relationships, but the relationships do not carry formal semantics that a reasoner can use to derive classifications.

The trap with these systems is that they look ontological without being ontological. They have classes. They have properties. But the properties are project-local, the classes are not aligned to a foundational ontology, and the reasoner has no axioms to work from. Classification, when it happens at all, is asserted by hand or computed by ad-hoc code that traverses the graph. There is no entailment. The graph is a database, and the database is shaped like RDF.

ARCO commits to the opposite posture. Every class is grounded, ultimately, in BFO 2020 (ISO/IEC 21838-2:2021). Every property is either a BFO/RO/IAO/CCO property loaded from upstream or a small number of explicitly justified bridging assertions. The reasoner has full axioms to work from. Classification is OWL entailment, not a hand-coded traversal. The chain is logical, not procedural.

### Post-hoc behavioral monitors

Red-teaming, content moderation, runtime policy enforcement, fairness monitors. These tools observe what a deployed system does. They are necessary for some obligations. They are not pre-deployment classifiers.

The structural problem: behavioral monitors assume the classification has already happened. You red-team a system because you have already decided it is the kind of system that warrants red-teaming. That decision is upstream of any monitor. ARCO produces that upstream decision.

### Generic AI governance frameworks (NIST AI RMF, ISO/IEC 42001)

These describe what good AI governance looks like in terms of controls and processes. They are organizational frameworks, not classification engines. They do not produce a determination for any specific system. A NIST AI RMF profile and an ISO 42001 management system are operating-context artifacts. ARCO is a per-system formal classification.

The two are complementary. ARCO produces the determination that drives which sections of an AI RMF profile apply to a given system. The framework does not produce the determination itself.

---

## 3. The core architectural commitment: reality vs representation

The single most important modeling decision in ARCO is the split between what the system is and what the provider claims about it. Most compliance work conflates these. ARCO refuses to.

**Reality side.** What the system is, in physical terms, regardless of what the provider says. A system has hardware components. Those hardware components bear dispositions. Some of those dispositions are capabilities to participate in particular kinds of process. A camera-equipped device with the right software can bear `BiometricIdentificationCapability`, whether or not anyone wrote a document saying it does.

**Representation side.** What the provider has committed to, formally, about the system. Intended use specifications. Use scenario specifications. Compliance obligation specifications. These are information content entities (in IAO terms): documentary artifacts that *say* something about the system.

Why split them? Because they answer different questions. The reality-side question is: can this system do the regulated thing? The representation-side question is: has the provider committed, in their own documentation, that this system will be used for the regulated thing on the regulated kind of subject?

The EU AI Act, like most modern regulation, does not classify by reality alone or by representation alone. It classifies by both. Where identification capability is not asserted in the reviewed commitments and verification capability is asserted, ARCO does not entail `:AnnexIII1aApplicableSystem`. Whether underlying hardware could in principle be configured to identify is a separate question that ARCO does not adjudicate; the disposition tracking is on the configured-system commitments under OWA, not on raw hardware capability (see [LIMITATIONS.md §3.5](../LIMITATIONS.md)). Conversely, a documented remote biometric identification system with no asserted hardware to support that capability fails Gate 1 in the reviewed graph and is not entailed as Annex III 1(a) applicable either.

ARCO requires both layers to align before classification fires. That is the load-bearing commitment.

A subtler consequence: misrepresentation is detectable. If the provider's documentation prescribes a process type that the underlying hardware cannot support, the documentation and the reality disagree. The disagreement does not block ARCO from running, but it does show up in the entailment graph: SHACL flags structural gaps, SPARQL audit queries flag content-vs-claim misalignments, and the certificate makes the disagreement visible.

This is fundamentally different from any tool that takes a self-reported description and trusts it. ARCO can take a self-reported description, but the structural commitments forces the description into a form where misrepresentation has a place to surface.

---

## 4. Why this ontological stack (BFO, RO, IAO, CCO)

ARCO is built on a specific stack: BFO 2020 as the foundational ontology, RO for relations (mereology, parthood, has_disposition), IAO for information content entities and the `is_about` relation, CCO for the directive ICE classes and the `prescribes` property. None of this is decorative. Each layer does load-bearing work.

### BFO 2020 (ISO/IEC 21838-2:2021)

BFO is a top-level, domain-agnostic ontology. Everything in BFO is either a continuant (something that persists through time, like a system or a hardware component) or an occurrent (something that happens, like a process). Continuants are further split into independent (objects, like a camera module) and dependent (qualities, dispositions, roles, which inhere in independent continuants).

This top-level distinction is what makes the reality/representation split work. A system is an independent continuant. Its capabilities are dispositions, which are dependent continuants that inhere in components. A process is an occurrent. An information content entity is a dependent continuant whose generic identity is information content (a specific kind of dependent continuant defined by IAO on top of BFO).

Why ISO standardization matters: BFO 2020 is the second edition of Basic Formal Ontology, standardized as ISO/IEC 21838-2:2021. That gives ARCO a portable grounding. A claim like "the system bears a disposition" is not a project-local claim. It is a claim in a standardized, ISO-published ontology that biomedical, defense, and industrial systems also build on. Anyone who has worked with OBO Foundry projects, BFO-aligned biomedical ontologies, or US Army CCO-grounded systems already knows the substrate.

### RO (OBO Relations Ontology)

RO defines the relations ARCO uses to connect entities: `bfo:0000051` (has_part), `ro:0000091` (has_disposition), `ro:0000052` (RO label "characteristic of"; ARCO locally commits this as `rdfs:subPropertyOf bfo:0000197` inheres_in, see `LIMITATIONS.md` §3.8), `ro:0000057` (has_participant), `ro:0000087` (has_role). These are the load-bearing relations of the gate axioms. A system has-part a hardware component that has-disposition a capability. A role inheres-in a bearer.

Using RO instead of project-local properties means the property characteristics (functional, transitive, inverse-of relationships) are defined upstream. A reasoner sees `ro:0000052` and knows what it means without ARCO having to redeclare it. ARCO additionally commits `ro:0000052 rdfs:subPropertyOf bfo:0000197` in `ARCO_core.ttl` section 5 so the reasoner inherits BFO 2020's IndependentContinuant range on the inferred inherence triple. See `LIMITATIONS.md` §3.8 for the bounded-enforcement disclosure and forward-looking constraints.

### IAO (Information Artifact Ontology)

IAO is where the representation side lives. The class `iao:0000030` (Information Content Entity) is the parent for documents, specifications, and claims. The property `iao:0000136` (is_about) is the relation between an information content entity and what it is about.

ARCO's three gates use `iao:0000136` heavily. Gate 2 says: an `IntendedUseSpecification` is_about the system AND prescribes some typed process token. Gate 3 says: a `UseScenarioSpecification` is_about the system AND is_about the role universal. The gates exploit `iao:0000136` from both directions, using anonymous inverse property expressions in the OWL axioms.

Why this matters: anyone using IAO knows what `is_about` means. Anyone using a project-local "describes" or "covers" relation does not. ARCO chose to do the work of expressing the gates in IAO terms rather than inventing project-local relations.

### CCO (Common Core Ontologies)

CCO is the BFO-aligned middle-level ontology developed originally by CUBRC and now used widely in US defense and intelligence community work. ARCO uses CCO for two specific things: the directive ICE class hierarchy (`cco:DirectiveICE`, which sits under `iao:0000030` via local bridging assertions) and the `cco:prescribes` property.

`cco:prescribes` is what carries the statutory prescriptive force in Gate 2. An intended use specification *prescribes* a regulated process type. This is not the same as "is about" or "covers." Prescription is a directive relation: the specification, qua directive, prescribes that some process of a regulated type will be carried out. CCO defines this relation in BFO-aligned terms.

The two CCO bridging assertions in `ARCO_governance_extension.ttl` (`cco:DirectiveICE rdfs:subClassOf iao:0000030` and `cco:DescriptiveICE rdfs:subClassOf iao:0000030`) connect the CCO and IAO information-content hierarchies, which upstream are not formally linked. This is a documented, intentional bridge. It is not silent project-local axiom invention.

### Why ROBOT BOT-extracted slim modules instead of full imports

This is a question that matters to anyone fluent in OBO Foundry practice. The short answer: ROBOT's BOT extraction is a syntactic locality module variant (Cuenca Grau, Horrocks, Kazakov, Sattler, 2007/2008). For any axiom whose signature is contained in the seed signature, the extracted module entails that axiom if and only if the full upstream ontology does. This includes property characteristics, property chains, inverses, and domain/range constraints — all of which ARCO's gate axioms depend on.

In practice that means the slim modules are not lossy. A BOT module of IAO containing the seed terms ARCO uses is logically equivalent to the full IAO for ARCO's purposes. The trade is a much faster reasoner pass (about 7 minutes for the HermiT cross-check on the merged ontology, vs 30 to 40 minutes when ARCO experimented with full RO and IAO imports, projected to 1 to 3 hours when CCO was added).

The OBO Foundry / Ontology Development Kit standard pattern is to do exactly this. Gene Ontology, OBI, ChEBI, and the OBO Relations Ontology itself ship BOT-extracted slim modules of their upstream dependencies. ARCO matching that pattern shortens the trust chain for any reviewer fluent in OBO practice.

The alternative pattern, MIREOT, is documented by ROBOT itself as not preserving the full set of logical entailments. For a project whose headline product is OWL-DL reasoning correctness over inverse-property gate axioms, MIREOT is the wrong tool. BOT is the right one.

---

## 5. The three-gate model

Annex III of the EU AI Act has a recurring grammatical structure. Almost every category reads: "AI systems intended to be used for [capability or process] of [affected entities] in [domain context]." That structure decomposes into three independent conditions. ARCO calls them gates.

| Gate | Layer | What it checks | OWL mechanism |
|------|-------|----------------|---------------|
| Gate 1 | Reality | The system has a hardware component that bears the regulated capability disposition | `bfo:0000051` (has_part) chained to `ro:0000091` (has_disposition), with `owl:someValuesFrom` on the capability class |
| Gate 2 | Representation (intended use) | An `IntendedUseSpecification` is_about the system and prescribes a typed instance of the regulated process class | Anonymous inverse property expression on `iao:0000136`, intersected with `cco:prescribes` and `owl:someValuesFrom` on the process class |
| Gate 3 | Representation (affected role) | A `UseScenarioSpecification` is_about the system and is_about the regulated role universal | Anonymous inverse property expression on `iao:0000136`, intersected with another `iao:0000136` and `owl:hasValue` on the role universal |

For category-specific Annex III applicability (`AnnexIII1aApplicableSystem`, `AnnexIII5bApplicableSystem`), all three gates must fire. Gate independence is verified by a regression test (`test_gate_removal.py`): with any single gate removed, the entailment must not fire. With all three present, it must.

Here is the actual OWL axiom for `AnnexIII1aApplicableSystem`, drawn directly from `ARCO_governance_extension.ttl`:

```turtle
:AnnexIII1aApplicableSystem rdf:type owl:Class ;
  rdfs:subClassOf :System ;
  owl:equivalentClass [
    rdf:type owl:Class ;
    owl:intersectionOf (
      :System

      # Gate 1: capability via component
      [ rdf:type owl:Restriction ;
        owl:onProperty bfo:0000051 ;                 # has_part
        owl:someValuesFrom [
          rdf:type owl:Class ;
          owl:intersectionOf (
            :SystemComponent
            [ rdf:type owl:Restriction ;
              owl:onProperty ro:0000091 ;            # has_disposition
              owl:someValuesFrom :BiometricIdentificationCapability
            ]
          )
        ]
      ]

      # Gate 2: intended use spec is_about the system AND prescribes a typed
      # instance of RemoteBiometricIdentificationProcess
      [ rdf:type owl:Restriction ;
        owl:onProperty [ rdf:type owl:ObjectProperty ; owl:inverseOf iao:0000136 ] ;
        owl:someValuesFrom [
          rdf:type owl:Class ;
          owl:intersectionOf (
            :IntendedUseSpecification
            [ rdf:type owl:Restriction ;
              owl:onProperty cco:prescribes ;
              owl:someValuesFrom :RemoteBiometricIdentificationProcess
            ]
          )
        ]
      ]

      # Gate 3: scenario spec is_about the system AND is_about the
      # NaturalPersonRole universal
      [ rdf:type owl:Restriction ;
        owl:onProperty [ rdf:type owl:ObjectProperty ; owl:inverseOf iao:0000136 ] ;
        owl:someValuesFrom [
          rdf:type owl:Class ;
          owl:intersectionOf (
            :UseScenarioSpecification
            [ rdf:type owl:Restriction ;
              owl:onProperty iao:0000136 ;
              owl:hasValue :NaturalPersonRole
            ]
          )
        ]
      ]
    )
  ] .
```

A few specific things this axiom is doing that are worth reading carefully.

**`owl:someValuesFrom :BiometricIdentificationCapability` (Gate 1).** The hardware component must bear a disposition that is *typed* as `BiometricIdentificationCapability`. Subclass reasoning matters here: `BiometricIdentificationCapability` is itself a subclass of `AnnexIIITriggeringCapability`, so a component bearing the capability is auto-typed as bearing a triggering capability under OWL-RL subsumption. That is what makes Gate 1 generalize cleanly: any new triggering capability subclass added to the ontology is recognized by the same audit query without changing the audit query.

**`owl:inverseOf iao:0000136` as an anonymous expression (Gates 2 and 3).** The gate restriction is on the *inverse* of `is_about`: that is, "this system is the subject of some `IntendedUseSpecification` that is_about it." This is OWL 2 DL expressible and OWL-RL materializes it correctly via inverse-of materialization, but it is the kind of axiom MIREOT would silently break if the inverse-of axiom on `iao:0000136` were lost. This is one of the reasons ARCO uses BOT extraction, not MIREOT.

**`owl:someValuesFrom :RemoteBiometricIdentificationProcess` (Gate 2).** The `cco:prescribes` filler must be a *typed instance*, not the class IRI itself. This is the content-sensitivity check. An earlier ARCO version used `owl:hasValue` here, which would have been satisfied by the class IRI as a punned individual. That pattern is content-blind: it would fire whenever any document mentions the regulated process class, regardless of whether the document actually prescribes a specific process token. The `owl:someValuesFrom` pattern requires that some specific named individual, typed as the regulated process class, exists as the filler. A classification-relevant assertion has to actually be made.

**`owl:hasValue :NaturalPersonRole` (Gate 3).** Here `owl:hasValue` is intentional, in contrast with Gate 2. The use scenario specification is about the role *category*, not a specific role-bearer instance. ARCO operates at the specification level. Bearer-token modeling (a particular natural person at a particular time) is a deployment-time concern outside ARCO's scope. Referencing the class IRI as a concept-individual is ARCO's encoding convention for "this scenario addresses the regulated role type" within the specification-level scope. The convention is documented in the rdfs:comment on the axiom and in the public claims doc.

Three ways this axiom could fail to fire, each diagnostic of something different:

- A system with a software-only or non-hardware component that "does" biometric identification (no `:HardwareComponent` in the chain): Gate 1 fails. The classification correctly does not fire, because dispositions inhere in independent continuants, and ARCO models software artifacts as ICEs, not as dispositional bearers.
- A system whose intended use specification mentions `:RemoteBiometricIdentificationProcess` but does not have a typed process token as the prescribes filler: Gate 2 fails. Documentation that refers to the regulated process category without committing to a process instance does not satisfy the gate.
- A system whose use scenario specification is about the system but does not reference `:NaturalPersonRole`: Gate 3 fails. A use scenario describing biometric identification of objects, animals, or non-natural-persons does not trigger 1(a).

Each failure mode is a real legal distinction. The axiom encodes those distinctions in a form a reasoner can verify.

---

## 6. The two-layer pipeline

ARCO's pipeline has two layers that do formally distinct work, plus a SHACL completeness check that sits between them. Confusing the layers, or describing one as the other, is the most common error in writing about systems like ARCO. The distinction is load-bearing.

```
Load TTL (BFO + BOT slim modules of RO/IAO/CCO + ARCO core + governance + instances)
      │
      ▼
OWL-RL reasoning  ─────────  CLASSIFICATION (the engine)
  Materializes entailed triples. AnnexIII1aApplicableSystem,
  AnnexIII5bApplicableSystem, HighRiskSystem are inferred here.
      │
      ▼
SHACL validation  ─────────  DOCUMENTARY COMPLETENESS (gates the audit, not the classification)
  Checks structural shape of inputs. Does the system have ≥1 has_part?
  Does the IntendedUseSpec have ≥1 prescribes? Does the assessment doc
  anchor to the system? SHACL FAIL means the input is structurally
  incomplete. It does NOT mean the system is or is not high-risk.
      │
      ▼
SPARQL ASK queries  ──────  AUDIT (queries the entailed graph; documents what fired)
  check_high_risk_inference, check_annex_iii_1a_entailment,
  check_intended_use, check_regulatory_alignment, detect_latent_risk,
  etc. These ASK queries verify, on the reasoned graph, that the
  evidence supports the classification the reasoner produced.
      │
      ▼
Certificate + summary.json + evidence.json + determination_packet.json
+ HTML view + SHACL report → runs/demo/
```

### Layer 1: OWL-RL classification

This is the engine. The OWL-RL reasoner (`owlrl==7.1.4`, pinned in CI) takes the merged graph and materializes all entailed triples. By "entailed" I mean: triples that follow logically from the asserted triples and the OWL axioms, under OWL-RL semantics.

Concretely: when the reasoner sees an instance bound to `:Sentinel_FaceID_Disposition` typed as `:BiometricIdentificationCapability`, and sees that `:BiometricIdentificationCapability rdfs:subClassOf :AnnexIIITriggeringCapability`, it materializes the triple `:Sentinel_FaceID_Disposition rdf:type :AnnexIIITriggeringCapability`. When it sees that `:Sentinel_ID_System` has the structure required by all three gates of `AnnexIII1aApplicableSystem`, it materializes `:Sentinel_ID_System rdf:type :AnnexIII1aApplicableSystem`.

That second triple is the classification. It is not asserted in the input. It is derived. The reasoner is the classifier. Anything else in the pipeline is downstream of that derivation.

The pipeline reports this as "entailment PASS" when the expected entailments materialize (about 19,710 derived triples on top of the 7,744 asserted, on the BFO + BOT-extracted RO/IAO/CCO + ARCO union, current as of the last pipeline run).

### SHACL: documentary completeness

SHACL is the W3C standard for validating RDF graph shape. It checks whether the input graph has the structural completeness an artifact requires, not whether the system is high-risk. Examples of what the ARCO SHACL shapes check:

- Systems have at least one `bfo:0000051` (has_part) child.
- HardwareComponents have at least one `ro:0000091` (has_disposition) edge.
- IntendedUseSpecifications have at least one `cco:prescribes` filler typed as a process, plus at least one `iao:0000136` is_about target.
- UseScenarioSpecifications have at least one `iao:0000136` to a system and at least one `iao:0000136` to a role.
- Assessment documentation processes have a participant and an output.
- ComplianceDeterminations have at least one `iao:0000136` is_about target.

A SHACL failure tells you the *artifact* is structurally incomplete. It does not tell you the system is or is not high-risk. A SHACL pass does not mean the system is high-risk either. SHACL is documentary, classification is OWL-RL.

This separation matters because regulators and auditors use the artifacts independently. A SHACL-conformant intended-use specification with no triggering capability in the underlying system is a complete document about a non-high-risk system. A SHACL-failing input with a triggering capability is an incomplete documentary artifact about a system that may still classify (if SHACL is not blocking) or that needs cleanup before we can claim anything about it.

### Layer 2: SPARQL ASK audit on the reasoned graph

The audit layer runs SPARQL ASK queries on the materialized graph (after OWL-RL has run). These are not classification queries. They are evidence-confirmation queries. Each one asks: did the entailment materialize, and is the supporting documentary content present?

A representative audit query, `check_annex_iii_1a_entailment.sparql`:

```sparql
PREFIX : <https://arco.ai/ontology/core#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

ASK WHERE {
  :Sentinel_ID_System rdf:type :AnnexIII1aApplicableSystem .
}
```

This is an audit query. Pre-reasoning, it returns FALSE: nobody asserted that triple. Post-reasoning, on a Sentinel-ID input with all three gates satisfied, it returns TRUE: OWL-RL materialized the triple, and the audit query confirms the materialization.

A subtler audit query, `detect_latent_risk.sparql`:

```sparql
ASK WHERE {
  :Sentinel_ID_System bfo:0000051 ?component .
  ?component ro:0000091 ?disposition .
  ?disposition a :AnnexIIITriggeringCapability .
}
```

This is the latent-risk traversal. It does not test whether classification fired. It tests whether the structural prerequisite (a hardware component bearing any triggering capability) is present at all. It can fire even when category-specific applicability does not, which is the entire point of the PRIMARY vs LATENT-RISK FLAG distinction.

The full audit suite includes queries for high-risk inference, Annex III 1(a) entailment, Annex III 5(b) entailment, intended-use evidence, regulatory alignment between law and use spec, assessment-document traceability, latent-risk detection, and obligation linkage. These cover the documentary content the classification depends on, plus structural traversal queries that document the evidence path.

The audit layer never produces or modifies the classification. Anyone describing SPARQL as "the classifier" or as part of the entailment is wrong. SPARQL inspects the entailed graph. OWL-RL produces it.

### Why the layers are formally distinct

Three reasons, in order of importance:

1. **Defensibility.** A regulator reviewing the certificate can ask: what produced this classification? The answer is: OWL-RL entailment over these axioms. They can re-run the reasoner. They can check the axioms against the regulation. The audit layer documents what fired but did not produce the firing. This separation is the audit story.
2. **Reproducibility under different reasoners.** OWL-RL is a restricted fragment of OWL 2 DL. ARCO's classifications have to hold under the full DL profile too. The HermiT cross-check (next section) verifies that. If classification were entangled with SPARQL audit queries, this cross-check would not be meaningful: you cannot run SPARQL queries through HermiT in a way that produces a comparable verdict.
3. **Honest scope.** Some classification questions are not OWL-decidable. Article 6(3) derogation, for instance, requires negation-as-failure or context-specific judgment that OWL cannot express. ARCO chooses to keep classification within OWL-RL and explicitly defer derogation modeling. The two-layer separation makes that scope honest: classification is what OWL-RL can derive, audit is what we can show on the derived graph.

---

## 7. Worked example: Sentinel-ID end to end

The reference example in the repository is a synthetic system called Sentinel-ID. It is a positive example for Annex III 1(a) (remote biometric identification). Here is what it looks like as input, what the reasoner does to it, and what the output certificate says.

### The input (slice of `ARCO_instances_sentinel.ttl`)

Reality side:

```turtle
:Sentinel_ID_System rdf:type :System ;
  bfo:0000051 :Sentinel_FaceID_Module .   # has part

:Sentinel_FaceID_Module rdf:type :HardwareComponent ;
  ro:0000091 :Sentinel_FaceID_Disposition .   # has disposition

:Sentinel_FaceID_Disposition rdf:type :BiometricIdentificationCapability .
```

Three triples, three commitments: there is a system, it has a hardware component, that component bears a biometric identification capability disposition. This satisfies Gate 1.

Representation side (intended use):

```turtle
:Sentinel_RBIP_Process rdf:type :RemoteBiometricIdentificationProcess .

:Sentinel_IntendedUse_001 rdf:type :IntendedUseSpecification ;
  cco:prescribes :Sentinel_RBIP_Process ;
  iao:0000136 :Sentinel_ID_System ;
  iao:0000136 :RemoteBiometricIdentificationProcess .
```

Note specifically what `:Sentinel_RBIP_Process` is. It is a *typed instance* of `:RemoteBiometricIdentificationProcess`. It is the specific process token that the intended use specification prescribes. This is what makes Gate 2 fire on `owl:someValuesFrom :RemoteBiometricIdentificationProcess`. The intended-use spec is also is_about the system (so the reasoner can find it via the inverse-aboutness chain) and is_about the process class (which is a documentary alignment marker the audit layer uses).

Representation side (use scenario):

```turtle
:Sentinel_UseScenario_001 rdf:type :UseScenarioSpecification ;
  iao:0000136 :Sentinel_ID_System ;
  iao:0000136 :NaturalPersonRole .
```

The use scenario is about the system and about the `NaturalPersonRole` universal. This satisfies Gate 3.

Three gates, each satisfied independently. The reasoner has everything it needs.

### What the reasoner does

OWL-RL runs over the merged graph and materializes:

- `:Sentinel_FaceID_Disposition rdf:type :AnnexIIITriggeringCapability` (via subclass reasoning: `BiometricIdentificationCapability ⊑ AnnexIIITriggeringCapability`)
- `:Sentinel_ID_System rdf:type :HighRiskSystem` (via the Gate 1-only bridge axiom: a system has-part a component bearing any triggering capability)
- `:Sentinel_ID_System rdf:type :AnnexIII1aApplicableSystem` (via the three-gate equivalentClass axiom on `AnnexIII1aApplicableSystem`)
- Inverse aboutness materialization: triples expressing that the system is the subject of the intended-use spec and the use scenario, derived via the inverse-of axiom on `iao:0000136`

The 19,710-ish derived triples include the above plus all the subsumption closure, property characteristic propagation, and inverse materialization that OWL-RL produces. The classification triples are the load-bearing ones for the certificate. The rest is supporting structure.

### What the certificate says

```text
========================================================================
ARCO CONDITION ASSESSMENT CERTIFICATE
========================================================================
  SYSTEM:                  Sentinel_ID_System
  REGIME:                  ARCO ontology encoding of EU AI Act
                           (Article 6 / Annex III)
  PRIMARY ARCO CLASSIFICATION:  AnnexIII1aApplicableSystem
                                (ENTAILED, all three ARCO gates)
  LATENT-RISK FLAG:             HighRiskSystem
                                (INFERRED, Gate 1 capability precondition only)
  TRIGGERING CAPABILITY:   Sentinel_FaceID_Disposition
  EVIDENCE PATH:
    Sentinel_ID_System -> Sentinel_FaceID_Module -> Sentinel_FaceID_Disposition

  [classification layer — OWL-RL entailment]
  SHACL:                   PASS
  ENTAILMENT:              PASS
  ANNEX III 1(a):          VERIFIED (ENTAILED)
  ANNEX III 5(b):          NOT APPLICABLE

  [audit documentation layer — SPARQL ASK on reasoned graph]
  TRACEABILITY:            PASS
  LATENT RISK:             DETECTED
  INTENDED USE:            PASS
  OBLIGATION:              PASS
  REG. ALIGNED:            PASS

  ENTAILED TRIPLES ADDED:  +19710

  Classification layer: PASS
  Audit layer:          PASS
========================================================================
```

The certificate distinguishes two things explicitly.

The **PRIMARY ARCO CLASSIFICATION** is `AnnexIII1aApplicableSystem`, labeled ENTAILED with the note "all three ARCO gates." This is the category-specific high-risk classification under Annex III 1(a). It is what an auditor or regulator should treat as the operative determination.

The **LATENT-RISK FLAG** is `HighRiskSystem`, labeled INFERRED with the note "Gate 1 capability precondition only." This is the looser, capability-only classification: any system with a triggering capability is flagged. On its own, the latent flag is not enough to apply category-specific Annex III obligations, but it is what should make a reviewer look harder.

The **EVIDENCE PATH** traces from system, through component, to disposition. An auditor verifying this certificate can follow the chain step by step and confirm each link in the source TTL.

The **classification layer** lists three things: SHACL conformance (the input was structurally complete), ENTAILMENT (OWL-RL produced the expected triples), and the per-category verification status. ANNEX III 1(a) is VERIFIED and ENTAILED. ANNEX III 5(b) is NOT APPLICABLE: the cross-category isolation check confirms the same Sentinel-ID input does not trigger the creditworthiness category. This is enforced by the ontology, not asserted by hand.

The **audit documentation layer** is the SPARQL pass on the reasoned graph. Each of TRACEABILITY, LATENT RISK, INTENDED USE, OBLIGATION, REG. ALIGNED is a separate ASK query that confirms supporting documentary content was present.

The two layers are reported separately. An auditor sees both. If they disagree (classification PASS but audit FAIL on, say, INTENDED USE), the certificate makes the disagreement visible rather than collapsing it into a single status.

### Negative example: VerificationKiosk

The repository also includes `ARCO_instances_verification.ttl`, a negative example. VerificationKiosk_001 has a `BiometricVerificationCapability`, not a `BiometricIdentificationCapability`. `BiometricVerificationCapability` is *not* a subclass of `AnnexIIITriggeringCapability` (intentionally — 1:1 verification does not trigger Annex III 1(a)). The same pipeline run produces:

- No `AnnexIII1aApplicableSystem` entailment (correct: not high-risk)
- No `HighRiskSystem` entailment (correct: no triggering capability)
- No `AnnexIII5bApplicableSystem` entailment (correct: not a credit system)

The negative example proves that the classification is content-sensitive. A system that *looks* similar (also a hardware-bound biometric capability) does not classify, because the ontology distinguishes verification (1:1) from identification (1:N).

### Cross-category example: CreditScorer

`ARCO_instances_creditscoring.ttl` is the second positive example, this time for Annex III 5(b) creditworthiness evaluation. It has a `CreditworthinessEvaluationCapability` and an intended-use spec prescribing `CreditworthinessEvaluationProcess`. Running the pipeline on this input produces:

- `AnnexIII5bApplicableSystem` entailment (correct: the 5(b) three gates fire)
- `HighRiskSystem` entailment (correct: capability is in `AnnexIIITriggeringCapability`)
- *No* `AnnexIII1aApplicableSystem` entailment (correct: cross-category isolation)

This generalization is what makes ARCO more than a one-trick demo. Adding a new Annex III category is a structured operation: define a new capability subclass, add it to `AnnexIIITriggeringCapability`, define the regulated process class, write the three-gate equivalentClass axiom following the 1(a)/5(b) pattern, write instance data, write an audit query. The framework does not change.

---

## 8. Independent verification: the HermiT cross-check

OWL-RL is fast and deterministic but it is a restricted fragment of OWL 2 DL. The full DL profile supports more inference patterns (some of them computationally expensive). For ARCO's classifications to be defensible under the full DL specification, two things have to be true:

1. The ontology has to be OWL 2 DL conformant. Every axiom, including the anonymous inverse property expressions in Gates 2 and 3, has to be expressible in DL.
2. A full DL reasoner has to produce the same classifications as OWL-RL on the inputs ARCO classifies. If the DL reasoner produces *more* classifications than OWL-RL, OWL-RL is missing inferences a regulator could legitimately make. If the DL reasoner produces *fewer*, OWL-RL is producing inferences DL would reject.

ARCO addresses this with an independent CI workflow that runs HermiT (a full OWL 2 DL reasoner) via ROBOT (v1.9.10) on every push to `main` and every pull request. The workflow does three things:

1. **Conformance check.** ROBOT validates that the merged ontology (BFO + BOT-extracted RO/IAO/CCO + ARCO core + governance + instances) is OWL 2 DL conformant. Any axiom that violates DL is reported.
2. **Consistency check.** HermiT verifies the merged ontology is logically consistent. A successful consistency check confirms there are no contradictions in the axioms.
3. **Reasoner agreement.** For every classification query (the same ones the audit layer runs through SPARQL), HermiT and OWL-RL must produce the same answer. This is the load-bearing claim. If HermiT classifies Sentinel-ID as `AnnexIII1aApplicableSystem` and OWL-RL does too, both reasoners agree. The current state: agreement on all classification queries for the Sentinel-ID positive case.

This cross-check is run by a separate workflow from the production pipeline. The production pipeline uses OWL-RL because it is fast and sufficient for production output. The CI cross-check uses HermiT because it is the higher-bar verification that the production output is also DL-correct.

The cross-check is what allows ARCO to claim its classifications hold under the full OWL 2 DL profile, not just the RL fragment. That claim is unusual for compliance tooling and is one of the three or four things that distinguishes ARCO from anything else in the space.

---

## 9. PRIMARY classification vs LATENT-RISK FLAG

The certificate distinguishes two outputs because the ontology produces two different inferences. The distinction matters legally and operationally, and the architecture respects it explicitly.

### `HighRiskSystem` (latent-risk flag)

`HighRiskSystem` is inferred as soon as a system has-part a component bearing *any* `AnnexIIITriggeringCapability`. It is Gate 1 alone. Specifically:

```turtle
:HighRiskSystem owl:equivalentClass [
  rdf:type owl:Class ;
  owl:intersectionOf (
    :System
    [ rdf:type owl:Restriction ;
      owl:onProperty bfo:0000051 ;
      owl:someValuesFrom [
        rdf:type owl:Class ;
        owl:intersectionOf (
          :SystemComponent
          [ rdf:type owl:Restriction ;
            owl:onProperty ro:0000091 ;
            owl:someValuesFrom :AnnexIIITriggeringCapability
          ]
        )
      ]
    ]
  )
] .
```

Under OWL-RL subsumption, every category-specific triggering capability subclass (currently `BiometricIdentificationCapability` and `CreditworthinessEvaluationCapability`) propagates instances up to `AnnexIIITriggeringCapability`, and the bridge fires.

The latent flag answers: does this system structurally contain capability that *could* trigger some Annex III category?

### `AnnexIII1aApplicableSystem` / `AnnexIII5bApplicableSystem` (PRIMARY classification)

The category-specific applicability classes require all three gates (capability + intended use + role). They answer: does this system formally meet the conditions of a *specific* Annex III category, including the intended-use commitments and the affected role?

### Why the distinction matters

A smartphone has a camera. A camera is a hardware component bearing a `BiometricIdentificationCapability` in many configurations. If ARCO collapsed the two outputs, every smartphone in the world would classify as a high-risk Annex III 1(a) system. That is wrong. It would over-classify dramatically, and any downstream regulator would lose trust in the tool immediately.

The three gates rescue this. A smartphone is *not* an `AnnexIII1aApplicableSystem` because there is no IntendedUseSpecification prescribing `RemoteBiometricIdentificationProcess` on it, and no UseScenarioSpecification about `NaturalPersonRole` for biometric identification. It is, however, a system that has the structural prerequisite for biometric identification capability. That is information worth surfacing as a latent flag, but it is not a PRIMARY classification.

ARCO's certificate makes both visible. PRIMARY ARCO CLASSIFICATION is the category-specific output. LATENT-RISK FLAG is the Gate 1 only outcome. A reviewer can act on each appropriately. Without the distinction, the tool would either over-classify (collapse to HighRiskSystem) or under-document (drop the latent flag).

---

## 10. How ARCO compares to other approaches

A side-by-side, organized by what each approach can and cannot produce.

### vs LLM-based compliance scoring

| Property | LLM scoring | ARCO |
|----------|-------------|------|
| Output | Confidence level / probability | Determination (entailed class membership) |
| Reproducibility | Same input may produce different output | Same input always produces same output |
| Audit chain | Generated explanation, may not match computation | Logical entailment chain from axioms |
| Defensibility under regulator review | Weak (probabilistic, opaque) | Strong (deterministic, axiomatic) |
| Failure mode | Silent miscalibration | Structural failure surfaces as missing entailment |
| Scope honesty | Implicit (model trained on something) | Explicit (axioms encode what is and is not modeled) |

LLM scoring is faster to ship and works on unstructured input. ARCO is slower to author for and requires structured input, but produces the artifact a regulator can actually audit. The two solve different problems. ARCO solves the determination problem. LLMs solve the upstream extraction and authoring problem (and may legitimately help author ARCO inputs from unstructured documentation, as long as the authored input is then classified deterministically).

### vs spreadsheet and checklist tooling

| Property | Checklist | ARCO |
|----------|-----------|------|
| Content sensitivity | Document existence ≠ document content | Gates check content, not artifact existence |
| Cross-category isolation | Manual / asserted | Enforced by ontology |
| Classification authority | Hand-coded rules | OWL-RL entailment |
| Adding a category | Edit the spreadsheet | Add ontology classes + axiom + instance test |

A checklist will tell you "the provider has an intended-use document." ARCO will tell you "the intended-use document prescribes the regulated process type for the regulated affected role, and therefore the system meets the formal condition of Annex III 1(a)." That is a different statement. The first is documentary. The second is substantive.

### vs custom enterprise compliance ontologies / "compliance graphs"

| Property | Custom compliance graph | ARCO |
|----------|------------------------|------|
| Foundational ontology | Project-local schema | BFO 2020 (ISO/IEC 21838-2) |
| Property semantics | Project-local "describes," "covers," "applies to" | RO, IAO, CCO with upstream axioms |
| Reasoner | Often ad-hoc graph traversal | OWL-RL with independent HermiT cross-check |
| Cross-system interoperability | Locked to vendor tooling | Aligns with all BFO/OBO ecosystem ontologies |

The "custom compliance graph" approach is RDF-shaped without being ontologically grounded. It looks formal but classification is asserted, not derived. ARCO's commitment is the opposite: classification is derived, the substrate is foundational.

### vs post-hoc behavioral monitors (red-teaming, runtime policy enforcement)

| Property | Behavioral monitor | ARCO |
|----------|-------------------|------|
| When in lifecycle | After deployment | Before deployment |
| What it observes | Outputs of running system | Structural and documentary properties |
| What it answers | "Is the system behaving acceptably?" | "Is the system formally subject to these obligations?" |

The two are complementary, not competing. ARCO determines whether a system is high-risk. Behavioral monitors enforce specific obligations once that determination has been made.

### vs generic AI governance frameworks (NIST AI RMF, ISO/IEC 42001)

| Property | Framework | ARCO |
|----------|-----------|------|
| Granularity | Organizational | Per-system |
| Output | Profile / management system | Per-system determination |
| Specificity | Broad applicability | Specific to formally encoded regulatory regime |
| Operational role | Defines controls and processes | Drives which controls apply |

Frameworks describe how an organization should govern AI generally. ARCO produces the per-system determinations that say which framework controls apply to a given system. They are at different layers of the governance stack.

---

## 11. Modeling decisions in plain terms

These are the load-bearing modeling decisions. Each has a reason. Each could have been done differently and would have produced a different (in most cases worse) tool.

### Capabilities are modeled as dispositions in hardware components, not as software properties

BFO distinguishes independent continuants (objects) from dependent continuants (qualities, dispositions, roles, which inhere in independent continuants). Software, in BFO + IAO terms, is a generically dependent continuant — an information content entity. ICEs do not bear dispositions in the BFO sense. Independent continuants do.

ARCO models hardware components as `:HardwareComponent ⊑ :SystemComponent ⊑ Object` (an independent continuant). It models software artifacts as `:SoftwareArtifact ⊑ ICE`. Dispositions, including capability dispositions, inhere in hardware. This is the BFO-correct posture and it has a legal consequence: a system's capability profile is anchored in physical structure, not in software running on it. A face recognition algorithm running on a server in another data center does not give the consuming system the capability disposition. The disposition lives in whatever hardware bears the bearer-side responsibility for the capability being realized.

This is a strong modeling commitment and is one of the things that distinguishes ARCO from compliance tools that treat "the system runs algorithm X" as if it were a structural property of the system.

### Gate 2 uses `owl:someValuesFrom` on a typed process token, not class punning

An earlier ARCO version had Gate 2 expressed as `owl:hasValue :RemoteBiometricIdentificationProcess`. Under OWL 2 punning, the class IRI also serves as a named individual, so `owl:hasValue` could fire on the class IRI itself. That made the gate content-blind: any document that mentioned `:RemoteBiometricIdentificationProcess` in the right structural position would satisfy the gate, regardless of whether it actually prescribed a process token.

Switching to `owl:someValuesFrom :RemoteBiometricIdentificationProcess` requires the prescribes filler to be a *typed individual* that is an instance of the regulated process class. A document that mentions the regulated process category but does not commit to a specific process token does not satisfy the gate. This is the correct legal posture: prescribing a regulated process means declaring a specific process will be carried out, not gesturing at the category.

The cost is that instance authoring has to include a typed process token (`:Sentinel_RBIP_Process rdf:type :RemoteBiometricIdentificationProcess`). The benefit is content-sensitivity and the elimination of an entire class of false positives.

### Gate 3 uses `owl:hasValue` on the role universal, intentionally

This one runs the opposite direction from Gate 2 and the asymmetry is intentional. Gate 3 says: the use scenario specification is_about `:NaturalPersonRole`. `:NaturalPersonRole` is the class IRI used as a concept-individual. ARCO is asserting that the specification is about the role *category*, not a specific role-bearer.

Why not require a typed bearer instance? Because role-bearers are deployment-time particulars. A specific natural person at a specific time is a token outside ARCO's specification-level scope. Modeling bearer tokens at classification time would force ARCO to be a runtime tool, not a pre-deployment classifier.

The trade is that Gate 3 is content-sensitive at the role-class level but not at the bearer-token level. That is a deliberate scope choice. The rdfs:comment on the axiom documents the convention. The public claims doc treats this as ARCO's specification-level encoding convention rather than a verdict on BFO doctrine about role universals.

### Annex III is modeled as a mereological list

`:AnnexIII_List` is a `RegulatoryContent` instance with `bfo:0000051` (has_part) edges to each modeled `AnnexIII_Condition_*` instance. The list is the mereological scaffold. New Annex III categories add via `bfo:0000051` as parts. Peer regulation lists (e.g. a hypothetical `:GDPR_Article22_List`) would follow the same pattern.

The mereological scaffold matters for two reasons. First, regulatory content has parts in the BFO sense: an article has subarticles, an annex has items, an item has gates. The structure is genuine, not metaphorical. Second, the scaffold lets ARCO express containment in formal terms: a determination is_about a condition, the condition is_part_of the annex, the annex is_part_of the regulation. The reasoning chain reaches the regulatory frame through actual ontology, not via a string match on a regulation reference.

A consequence: removing `:AnnexIII_List` is not allowed even if no system ever queries it directly. It is the regulatory scaffold and removing it would orphan the conditions. The CLAUDE.md project constitution treats this as an invariant.

### CCO bridging assertions are kept minimal and documented

ARCO uses CCO's directive ICE class hierarchy (`cco:DirectiveICE`, `cco:DescriptiveICE`) and the `cco:prescribes` property. Upstream CCO has its own `cco:InformationContentEntity` class that is not formally linked to IAO's `iao:0000030`. ARCO's `ARCO_governance_extension.ttl` contains two small bridging assertions:

```turtle
cco:DirectiveICE rdfs:subClassOf iao:0000030 .
cco:DescriptiveICE rdfs:subClassOf iao:0000030 .
```

These bridge the CCO and IAO information-content hierarchies so that CCO directive classes inherit IAO's `is_about` relation cleanly. The README and the public claims doc both surface these bridges explicitly. They are not silent. They are documented as the only non-trivial axiomatic additions ARCO makes on top of the upstream ontologies.

The discipline matters because the trust story for ARCO is "what we use is upstream; what we add is small, explicit, and documented." Inventing project-local bridging axioms invisibly is the failure mode that makes other compliance graphs untrustworthy. ARCO refuses to do that.

### `BiometricVerificationCapability` exists but is not a triggering capability

This is a small modeling decision with large legal consequences. EU AI Act Annex III 1(a) regulates *remote biometric identification* (1:N). It does not regulate biometric verification (1:1). A verification kiosk that compares a face to a single stored template for access control is not Annex III 1(a).

ARCO models this directly. `BiometricVerificationCapability` is defined as a `CapabilityDisposition` but is *not* a subclass of `AnnexIIITriggeringCapability`. A system bearing only a verification capability does not classify under any Annex III category in the current model. The negative example (`ARCO_instances_verification.ttl`) demonstrates this explicitly.

The modeling decision is what makes ARCO precise about a real legal distinction. A tool that conflated identification and verification would over-classify systematically.

---

## 12. What ARCO is not, and known limitations

Honest scope is part of the trust story. This section is the explicit list of things ARCO does not do or does not yet model. None of these are hidden. All of them appear in the public claims doc, the EU AI Act rules doc, or the README.

### Scope limitations (intentional)

- **Two Annex III categories are modeled.** 1(a) remote biometric identification, 5(b) creditworthiness evaluation. Other Annex III categories are not yet modeled. Adding them is a structured operation following the extension protocol. It is not a research project.
- **Article 5 (prohibited practices) is not modeled.** ARCO is currently scoped to Article 6 / Annex III. Article 5 prohibitions would require negation patterns ARCO has not yet committed to.
- **EU AI Act only.** The three-gate architecture is jurisdiction-agnostic, but the current encoding is specifically EU AI Act. Re-encoding to GDPR Article 22, NYC Local Law 144, or another regulatory regime is a separate authoring effort.
- **Pre-deployment, not runtime.** ARCO classifies a system based on its documented capability profile, intended use, and use scenario. It does not observe deployed behavior.

### Modeling gaps (acknowledged)

- **Article 6(3) derogation is not modeled.** A system that meets all three gates but qualifies for a derogation under 6(3)(a) through 6(3)(d) (narrow procedural task, improvement of prior human activity, pattern detection without replacement, preparatory task) will be classified as Annex III applicable regardless. ARCO over-classifies in those cases. Planned approach: descriptive ICE artifact for the derogation claim, queryable via SPARQL as a post-classification audit flag. Not v1 priority.
- **Annex III 5(b) fraud detection exclusion is not modeled.** The legal text reads "with the exception of AI systems used for the purpose of detecting financial fraud." A fraud-detection system that also evaluates creditworthiness would currently classify as `AnnexIII5bApplicableSystem` (false positive). Modeling exclusions requires either a negation gate (not expressible in OWL-RL) or a post-classification SPARQL/SHACL check. Deferred for v1.
- **Hand-authored structured input.** Instances are written by hand today. There is no LLM-to-ontology extraction pipeline yet. LLMs may legitimately help author candidate instances upstream of ARCO; they are not in the classification path.
- **Multi-system / shared-component scenarios are not modeled.** The current scope assumes one system at a time. A shared sensor module across multiple systems is expressible in BFO but the gate axioms would need extension to handle shared-bearer cases cleanly.

### Structural caveats

- **Garbage in, deterministic wrong answer out.** SHACL catches structural incompleteness. It does not catch factual misrepresentation. If the input asserts that `:Sentinel_FaceID_Module rdf:type :HardwareComponent` and that turns out to be false in the real world, the classification will fire correctly given the input but will be wrong about reality. ARCO is honest about this: the determination is as correct as the input description.
- **ARCO is not a legal opinion.** It encodes a formal interpretation of selected Annex III conditions. It does not replace legal counsel, and the public claims discipline forbids saying it does.
- **ARCO is not an AI system.** ARCO classifies AI systems. It is not itself one.

---

## 13. What the architecture generalizes to

The three-gate pattern (capability + prescribed process + affected role) is not specific to the EU AI Act. It maps onto any regulatory regime where obligations attach to:

1. A capability the system has,
2. Carried out as a process,
3. On a particular kind of subject.

A few examples where the same architecture re-encodes cleanly:

- **GDPR Article 22 (automated decision-making).** Capability: automated decision-making. Process: a decision process producing legal or significant effects. Affected role: data subject. The three gates rewrite directly: a system has-part a component bearing automated-decision capability; an intended-use spec prescribes a typed decision-process token; a use scenario references the data-subject role universal.
- **NYC Local Law 144 (automated employment decision tools).** Capability: automated employment decision capability. Process: hiring or promotion decision. Affected role: candidate or employee.
- **HIPAA covered electronic transactions.** Capability: electronic protected health information processing. Process: covered transaction type. Affected role: covered individual.
- **Defense / dual-use export control.** Capability: regulated technology category. Process: prescribed end-use. Affected role: regulated end-user category.

In each case the substrate (BFO 2020 + RO + IAO + CCO) does not change. The capability classes, the process classes, and the equivalentClass axioms are new. The gate pattern is the same. The two-layer pipeline is the same. The independent DL cross-check is the same.

This is the "structural pre-classification engine" framing that the public claims doc recommends for non-EU contexts. The current encoding is EU AI Act specific. The architecture is not.

---

## A reading order for evaluators

If you have an hour:

1. Run the pipeline (`python 03_TECHNICAL_CORE/scripts/run_pipeline.py`) and read the certificate.
2. Read sections 3, 5, 6, and 9 of this document (reality vs representation, three gates, two-layer pipeline, PRIMARY vs LATENT-RISK).
3. Open `ARCO_instances_sentinel.ttl` and `ARCO_governance_extension.ttl` side by side. The instance file is the input; the governance file is the axioms that classify it.
4. Skim the SPARQL audit queries in `03_TECHNICAL_CORE/reasoning/`.

If you have a day:

1. The hour version, above.
2. Read sections 4, 7, 8, 10, 11 (ontology stack rationale, full worked example, HermiT cross-check, comparison, modeling decisions).
3. Re-run the pipeline with `--instances 03_TECHNICAL_CORE/ontology/ARCO_instances_creditscoring.ttl` and confirm cross-category isolation by reading the resulting certificate.
4. Read the alignment audits in `docs/agent/alignment_audit_{RO,IAO,CCO}_2026-04-29.md`.

If you are evaluating ARCO as a procurement candidate or a research artifact:

1. The day version, above.
2. Read `docs/agent/ARCO_public_claims.md` (the authority document for outward-facing wording).
3. Read `docs/agent/eu_ai_act_rules.md` (scope, derogation handling, fraud exclusion handling).
4. Look at the CI workflows in `.github/workflows/` and confirm the HermiT cross-check is gated on every push.

The thing to verify, repeatedly, is the chain. Follow the system in the certificate to its component, to its disposition, to the capability class, to the triggering grouping, to the equivalentClass axiom that uses that grouping, to the OWL-RL entailment that materializes the classification. Every link is in the repo. The chain is the artifact. That is the entire claim.
