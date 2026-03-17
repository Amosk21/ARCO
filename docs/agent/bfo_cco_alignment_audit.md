# BFO/CCO Alignment Audit
_Version: 2 · Date: 2026-03-17 · Audited by: full subagent codebase scan (all TTL, SHACL, SPARQL, pipeline)_

<!-- Update version + date each time a full audit is run. Do not edit content without re-running the scan. -->
<!-- v1: 2026-03-17 — initial audit after BFO 2020 import -->
<!-- v2: 2026-03-17 — confirmed by deep subagent scan of all files; corrected Surveillance_Run_001 false-positive; confirmed RO and IAO also stubs -->

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
