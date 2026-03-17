# BFO/CCO Alignment Audit
_Version: 3 · Date: 2026-03-17 · Audited by: full subagent codebase scan + adversarial design review_

<!-- Update version + date each time a full audit is run. Do not edit content without re-running the scan. -->
<!-- v1: 2026-03-17 — initial audit after BFO 2020 import -->
<!-- v2: 2026-03-17 — confirmed by deep subagent scan of all files; corrected Surveillance_Run_001 false-positive; confirmed RO and IAO also stubs -->
<!-- v3: 2026-03-17 — adversarial review of proposed hardening plan; recorded strategic open questions, unresolved design decisions, work items with dependencies, and product claim distinction -->

## Context

This document records the findings of a deep audit into ARCO's actual BFO/CCO alignment status,
triggered by switching from local BFO stubs to a real BFO 2020 import. It records what the
2528 additional entailments actually are, what is genuinely grounded, what is not, and what
would be required to close the gap.

---

## Entailment Audit: What BFO Import Actually Added

### Measured Numbers (post-reasoning)

| Configuration | Asserted triples | After OWL-RL | New entailments |
|---|---|---|---|
| Without BFO | 403 | 1,297 | +894 |
| With BFO 2020 | 1,417 | 4,839 | +3,422 |
| **BFO-driven new entailments** | — | — | **+2,528** |

### Breakdown of the 4,116 new triples (BFO graph vs. no-BFO graph)

| Category | Count | Description |
|---|---|---|
| Blank-node triples | 2,456 | OWL-RL internal closure machinery — membership in BFO's anonymous restriction expressions |
| Named-entity triples | 1,660 | Real inferences about named ARCO classes and instances |

The blank-node triples are bookkeeping, not substantive reasoning. The 1,660 named-entity triples are real.

### What the Named-Entity Triples Actually Are

**ARCO instances now have real BFO supertype chains:**

| Instance | New BFO types entailed |
|---|---|
| `Sentinel_ID_System` | MaterialEntity, IndependentContinuant, Continuant, Entity |
| `Sentinel_FaceID_Module` | MaterialEntity, IndependentContinuant, Continuant, Entity |
| `Sentinel_FaceID_Disposition` | RealizableEntity, SpecificallyDependentContinuant, Continuant, Entity |
| `Sentinel_RBIP_Process` | Occurrent, Entity |
| `Surveillance_Run_001` | Occurrent, Entity |
| `ProviderOrg_001` | MaterialEntity, IndependentContinuant, Continuant, Entity |
| `ProviderRole_001` | RealizableEntity, SpecificallyDependentContinuant, Continuant, Entity |

**Every ARCO class now has its full BFO supertype chain entailed** — e.g. `System ⊑ MaterialEntity ⊑ IndependentContinuant ⊑ Continuant`. These are now real BFO entailments, not just annotations.

### Why Classification Result Didn't Change

The three gates check ARCO-defined class membership:
- Gate 1: `System`, `SystemComponent`, `BiometricIdentificationCapability` — all ARCO IRIs
- Gate 2: `IntendedUseSpecification`, `cco:prescribes`, `RemoteBiometricIdentificationProcess` — ARCO IRIs + a CCO property stub
- Gate 3: `UseScenarioSpecification`, `iao:0000136`, `:NaturalPersonRole` — ARCO IRIs + a stub property

BFO import adds the ancestry chain *above* those ARCO classes. The gates don't look upward into BFO.
The classification was already correct because all key triples are **directly asserted** —
`has_part`, `has_disposition`, type membership. OWL-RL's `cls-svf2` rule fires on direct triples.
The gate was never dependent on CCO/RO domain/range inference chains.

### What BFO Import *Did* Change (Meaningfully)

BFO 2020 declares `IndependentContinuant` and `SpecificallyDependentContinuant` as disjoint.
After import:
- `Sentinel_FaceID_Module` is now provably an IndependentContinuant
- `Sentinel_FaceID_Disposition` is now provably a SpecificallyDependentContinuant

If anything in ARCO were ever typed in both categories simultaneously, the reasoner would now detect
the inconsistency. Before, that error would have passed silently. **Disjointness enforcement is now real.**

---

## The CCO Gap

### What the Stubs Actually Declare

```turtle
cco:prescribes rdf:type owl:ObjectProperty ;
  rdfs:label "prescribes" ;
  rdfs:comment "Domain: DirectiveInformationContentEntity. Range: Process." .
  # ^^^ COMMENT ONLY. No rdfs:domain. No rdfs:range. Zero OWL axioms.

cco:Organization rdf:type owl:Class ;
  rdfs:subClassOf bfo:0000027 .  # Correctly declared in stub

cco:Person rdf:type owl:Class ;
  rdfs:subClassOf bfo:0000040 .  # Correctly declared in stub

cco:DirectiveInformationContentEntity rdf:type owl:Class ;
  rdfs:subClassOf iao:0000030 .  # Correctly declared in stub
```

After full BFO reasoning, `cco:prescribes` has only tautological triples:
`sameAs` itself, `subPropertyOf` itself. **No inference machine exists for this property.**

### What's Missing Across All Dependency Ontologies

| Ontology | Status | What's absent |
|---|---|---|
| BFO 2020 | ✅ Fully imported | Nothing |
| RO (OBO Relation Ontology) | ⚠️ Stubs only | `has_disposition`, `has_role`, `has_part` domain/range; property chain axioms; transitivity |
| IAO | ⚠️ Stubs only | `is_about` domain (InformationContentEntity); real ICE hierarchy |
| CCO | ⚠️ Stubs only | `prescribes` domain/range; `has_output` domain/range; full Organization/Person hierarchy |

---

## Risks of Importing CCO (Not a Simple Addition)

### Risk 1: Import Chain Version Conflict
CCO's OWL file contains `owl:imports` statements pointing to specific URLs for BFO and IAO.
If those URLs resolve to different versions than ARCO's local BFO 2020, two BFO versions
load simultaneously. At best: redundant assertions. At worst: conflicting disjointness axioms.

### Risk 2: `cco:prescribes` Domain/Range Cascade
Real CCO declares `cco:prescribes rdfs:range bfo:0000015` (Process).

ARCO instances file line 25:
```turtle
:AnnexIII_Condition_Q1 cco:prescribes :RemoteBiometricIdentificationProcess ;
```
Here `:RemoteBiometricIdentificationProcess` is the **class IRI used as an individual** (OWL punning).
With real CCO range `Process`, the reasoner infers:
```
:RemoteBiometricIdentificationProcess rdf:type bfo:0000015
```
The class itself becomes an individual typed as Process. BFO's property chain axioms for Process
then fire against it as an individual. This is a cascade of unintended inferences currently absent.

### Risk 3: IAO `is_about` Domain Constraint
If IAO declares `iao:0000136 rdfs:domain iao:0000030` (InformationContentEntity), then everything
that is the *subject* of `is_about` gets inferred as ICE.

`Surveillance_Run_001` (an OperationalProcess, i.e. Occurrent) is the subject of `iao:0000136`
in the instance data. Occurrent ∩ ICE (SpecificallyDependentContinuant → Continuant) would
trigger BFO's `Continuant disjointWith Occurrent` constraint — **genuine inconsistency**.
This would make the reasoner report the ontology as incoherent.

### Risk 4: `owl:sameAs` Propagation
BFO import added 676 `owl:sameAs` triples (reflexivity closure). CCO adds more equivalentClass
and equivalentProperty declarations. OWL-RL sameAs semantics are powerful: if two things are
ever connected by a sameAs chain, ALL their properties merge. CCO might create an equivalence
that unexpectedly collapses two ARCO things that should be distinct.

### Risk 5: Pipeline Performance
CCO merged is ~300,000+ triples. Reasoning time would increase significantly.

### Risk 6: Gate 3 Punning Under Load
Gate 3 uses `owl:hasValue :NaturalPersonRole` where `:NaturalPersonRole` is a class used as
an individual. After BFO, NaturalPersonRole has as a class:
```
rdfs:subClassOf BFO:0000023, BFO:0000017, BFO:0000020, BFO:0000002, BFO:0000001
```
Gate 3 fires because `Sentinel_UseScenario_001 iao:0000136 :NaturalPersonRole` exists as a
direct triple. `owl:hasValue` is a graph pattern match on object identity — not affected by
what type triples NaturalPersonRole accumulates as a class. Currently safe. But if CCO or IAO
adds property chain axioms that fire through is_about, this needs re-verification.

---

## Precise State of ARCO Alignment

### What ARCO IS
- **BFO-compatible** — the class hierarchy and category placements are correct and now enforced
- **Formally classified** — the three-gate equivalentClass definition is genuine OWL Description Logic
- **Deterministic** — same inputs always produce same outputs, auditable entailment chain
- **BFO-grounded** (after 2026-03-17 import) — real disjointness enforcement, real supertype chains

### What ARCO IS NOT (yet)
- **BFO-derived** — BFO's own axioms do not compute the classification; they don't contradict it
- **CCO/IAO/RO property-validated** — the properties are used consistently with those ontologies'
  intent, but their actual domain/range/chain axioms are not in the graph to verify this
- **Fully interoperable** — the class hierarchy is compatible with BFO-aligned ontologies;
  the property usage is not yet machine-validated against CCO/IAO/RO constraints

### Summary in One Sentence
ARCO is BFO-**compatible** and formally correct OWL. It is not yet BFO/CCO-**grounded** in the
sense that the property axiom layer of the dependency ontologies is loaded and validating usage.

---

## What Full Grounding Would Require

Ordered by risk (lowest first):

### Step 1: Import RO (Lowest Risk)
- Single well-maintained file, already BFO 2020-aligned
- Adds real `has_disposition`, `has_role`, `has_part`, `inheres_in` domain/range enforcement
- Run pipeline; verify no category violations fire

### Step 2: Validate and Import IAO
- First: audit every subject of `iao:0000136` in all instance files
  — verify each subject is typed as an InformationContentEntity
  — `Surveillance_Run_001` is a Process, not an ICE; this triple pattern must be fixed first
- Then import IAO; verify no Occurrent/Continuant disjointness violations fire

### Step 3: CCO (Highest Risk, Most Work)
1. Fix the punning at instances line 25: `AnnexIII_Condition_Q1 cco:prescribes :RemoteBiometricIdentificationProcess`
   — replace with a proper process token (as was done for Gate 2 with `Sentinel_RBIP_Process`)
2. Obtain CCO at a pinned version and store locally (same pattern as BFO 2020)
3. Patch CCO's `owl:imports` to point to local files, not remote URLs
4. Run pipeline; systematically address each new inference or inconsistency
5. Verify Gate 2 and Gate 3 still fire correctly under full CCO axioms

---

## Files Implicated

| File | Issue |
|---|---|
| `ARCO_governance_extension.ttl` | CCO stubs lack domain/range axioms; IAO `is_about` is a stub |
| `ARCO_instances_sentinel.ttl` | Line 25: class-as-individual punning with `cco:prescribes`; Line 82-86: `Surveillance_Run_001 iao:0000136` on a Process subject |
| `ARCO_instances_verification.ttl` | Same `is_about` pattern check needed |
| `ARCO_instances_creditscoring.ttl` | Same `is_about` pattern check needed |
| `03_TECHNICAL_CORE/ontology/imports/` | Needs RO and pinned IAO/CCO files added |

---

## v3: Strategic Open Questions and Unresolved Design Decisions

_Added 2026-03-17 after adversarial review of a proposed four-phase hardening plan. This section records what was identified but NOT implemented. Nothing below has been built. Read this entire section before proposing or implementing any alignment work._

### Open Question 1: End State — Full Import vs. Permanent Local Declarations

There are two coherent end states for ARCO's property layer. They have not been chosen between.

**End state A (full import):** ARCO imports BFO (done), then RO, then IAO, then CCO after punning fixes. Every layer — classes, properties, instances — is governed by source ontology axioms with real machine enforcement. This is the strongest alignment claim. The v2 "What Full Grounding Would Require" section describes the staged path to get there.

**End state B (permanent local declarations):** ARCO imports BFO (done) and stops there. RO, IAO, and CCO properties are declared locally with ARCO-scoped domain and range. This is simpler but is a permanent retreat from full alignment. The claim becomes: "ARCO uses BFO/RO/IAO/CCO vocabulary with BFO class axioms enforced and property usage approximated locally."

**Why this matters:** Every piece of work below — property audit, punning fix, test suite, ADR, extension protocol updates — is designed differently depending on which end state is the target. ARCO-local declarations that are permanent architecture require different documentation, different product claims, and different extension protocols than ARCO-local declarations that are temporary scaffolding for a staged import plan.

**MANDATORY:** This question must be answered before implementing any property-layer work. Do not default to either end state implicitly.

### Open Question 2: Product Claim Distinction

ARCO determines whether a system description satisfies ARCO's formal encoding of Annex III categories. It does NOT determine whether a system is legally high-risk under the EU AI Act. These are different claims.

The first is verifiable by inspecting the axioms. The second requires legal authority ARCO does not have.

The three-gate equivalentClass definition is ARCO's engineering interpretation of Article 6 and Annex III. That interpretation has never been validated against the actual legal text by a lawyer. Internal consistency (OWL entailment is correct) proves nothing about external correctness (the axioms correctly encode the law).

**Required actions before any product or commercial documentation is finalized:**
1. Certificate output must say "classified per ARCO ontology encoding of Annex III 1(a)" — not "classified as high-risk under the EU AI Act"
2. README and commercial documentation must distinguish between the two claims
3. The three-gate interpretation is flagged as an open assumption, not a verified legal determination

### Unresolved Design Decision: The cco:prescribes Punning Fix

The current triples use class IRIs as the object of `cco:prescribes`:
```turtle
:AnnexIII_Condition_Q1 cco:prescribes :RemoteBiometricIdentificationProcess
```
where `:RemoteBiometricIdentificationProcess` is a class.

The fix requires creating token individuals, but their typing is a design decision:

- **Option A:** Type them as instances of the process class (`arco:RemoteBiometricIdentificationProcess_prescribed rdf:type :RemoteBiometricIdentificationProcess`). This means "there exists a process of this type that is being prescribed." Standard OWL practice but philosophically says a specific process exists rather than a process type being prescribed.
- **Option B:** Create a new class like `ProcessTypeSpecification` to hold regulatory references. This is a new design commitment and a new class that needs BFO placement.
- **Option C:** Leave them untyped as bare individuals. Valid OWL but philosophically unsatisfying.

**MANDATORY:** Choose an option before implementing the fix. The choice affects Gate 2's `owl:someValuesFrom` restriction behavior.

### Unresolved Engineering Problem: Negative Test Infrastructure

The current pipeline loads all TTL files into a single graph before reasoning. A deliberately miscategorized instance in a negative test file contaminates the reasoning graph for all positive cases.

Negative testing requires one of:
- Parameterized pipeline runs (accept a specific instance file as argument, run reasoning against only that file + core ontology)
- A test harness that invokes the pipeline multiple times with different input sets
- Named graph isolation (owlrl support uncertain)

**None of these mechanisms exist.** The negative test suite cannot be written until a test isolation mechanism is built.

### Identified Work Items (Ordered by Dependency)

These items were identified during adversarial review. They are listed in dependency order. None have been implemented.

**Step 0 — Property audit.** Enumerate every property triple across all TTL files. For each property, record current usage, correct ARCO-scoped domain and range, and whether the domain/range decision requires new judgment. This audit must be complete before property declarations or negative tests can be designed. _Depends on: Open Question 1 (end state) being resolved, because the audit produces different outputs for permanent vs. temporary declarations._

**Step 1 — Fix cco:prescribes punning.** Replace class-as-individual usage with proper typed individuals. _Depends on: Unresolved Design Decision above being resolved._

**Step 2 — Build negative test harness + write tests.** Build the parameterized pipeline mechanism first. Then write negative test cases for: Gate 1 fail, Gate 2 fail with Gate 1 pass, Gate 3 fail with Gates 1-2 pass, disjointness violation caught, domain/range violation caught. _Depends on: Step 0 (need to know what declarations will exist to test against them) and Step 1 (punning fix changes what valid/invalid triples look like)._

**Step 3 — Architectural Decision Record.** Document every load-bearing design choice with its justification. Must include three consequence commitments: (a) every new property usage requires an explicit declaration following a documented process, (b) the extension protocol gets a mandatory property declaration step and a mandatory disjointness analysis step, (c) all outward-facing text distinguishes between imported BFO class enforcement and the property layer's actual status. _Depends on: Open Question 1 (the ADR records a different decision depending on end state)._

**Step 4 — Implement property declarations and disjointness.** Phase 1 (ARCO-local property domain/range), Phase 2 (ARCO-specific disjointness: BiometricIdentificationCapability disjoint BiometricVerificationCapability; process type AllDisjointClasses), Phase 4 (pipeline hardening: cross-category type check SPARQL query, disjointness axiom presence guard). _Depends on: Steps 0-3 all being complete._

**Deferred — has_part transitivity.** Adding transitivity to has_part is a classification decision, not a neutral engineering choice. It expands Gate 1 scope: a system whose sub-component (not direct component) has a triggering capability would satisfy Gate 1 through the transitive chain. This may be correct behavior but it is a substantive regulatory decision that must be explicitly verified, not assumed safe. Deferred until someone confirms sub-component capability propagation is intended. Inverse declaration (has_part / part_of) is safe and can proceed independently.

### Known Gaps Not Addressed by Any Work Item Above

1. **Extension protocol lacks disjointness analysis.** `docs/agent/extension_protocol.md` governs adding new Annex III categories but does not require analyzing whether a new class needs disjointness declarations against existing classes. Must be updated when Step 3 is implemented.

2. **No single traceability artifact.** There is no document connecting regulatory text (specific Articles, Recitals, Annex paragraphs) to specific ontological commitments (which axiom encodes which legal requirement). CLAUDE.md and inline comments carry this information but it is scattered.

3. **Surveillance_Run_001 is_about pattern.** `Surveillance_Run_001` (an OperationalProcess / Occurrent) is the subject of `iao:0000136` (is_about). If IAO is ever imported with domain InformationContentEntity, this triple creates a Continuant/Occurrent disjointness violation. Identified in v2 but not yet fixed.
