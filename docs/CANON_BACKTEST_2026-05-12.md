# Canon Backtest — 2026-05-12

**Purpose.** Durable record of what canon (Beverley / Smith / Ceusters papers, CCO v1.7, abi production ontology) actually says on three modeling questions that block ARCO foundation decisions. Replaces ephemeral in-conversation agent reports with citation-verified findings.

**Method.** Each load-bearing claim is verified against the actual canon file by direct read (not paraphrase, not memory). Where the canon agent ([summary tool result] of 2026-05-12 03:xx) made errors or omitted findings, the errors are surfaced explicitly. Where canon is silent or self-contradictory, that fact is recorded rather than papered over.

**Scope.** Three questions:
- Q1 — Canonical seven BFO buckets.
- Q2 — How is Interest modeled?
- Q3 — Aboutness targets (universal-level vs configuration-level).

Plus emergent finding on class-minting discipline (Smith-Against-Idiosyncrasy Principles 5 and 8).

**Status.** Immutable record. Do not edit historical content. New findings extend; corrections to existing claims add a dated note rather than overwriting.

---

## A. Bucket framework — Beverley canonical seven (Q1)

### A.1 Direct citation

`KB/00_INBOX_RAW/papers/Design_Pattern_Lecture_5_Disambiguation.md` lines 50-58:

> When identifying classes, describe:
> 1. Material entities within scope, i.e. **Material Entity**
> 2. Qualities these material entities have, i.e. **Quality**
> 3. What these material entities could do, i.e. **Realizable Entity**
> 4. What these material entities actually do, i.e. **Process**
> 5. Where these material entities and boundaries are located, i.e. **Immaterial Entity**
> 6. When these entities exist, i.e. **Temporal Region**
> 7. Information we use to talk about 1-6, i.e. **Generically Dependent Continuant**

Restated at lines 65-72 (same seven, briefer labels: Material Entities / Qualities / Processes / Realizables / Sites & Boundaries / Temporal Region / Information).

### A.2 Canonical RELATIONS connecting buckets

Same lecture, lines 196-204:

> When identifying relations, describe:
> 1. Qualities to material entities, i.e. **inheres in**
> 2. Realizables to material entities, i.e. **inheres in, has material basis**
> 3. Processes to material entities, i.e. **participates in**
> 4. Realizables to processes, i.e. **has realization**
> 5. Immaterial location of material entity, i.e. **located in**
> 6. When any such entities exist, i.e. **exists at, datatype property**
> 7. When any such entities carry information, e.g. **generically depends on**

Critical: "has material basis" appears at line 199 as a RELATION (bucket 3 ↔ bucket 1). It is NOT a separate bucket.

### A.3 Verdict on ARCO's prior framework

ARCO's prior CLAUDE.md §29-47 (now corrected) had:
- Bucket 5 = "Temporal regions and sites" (Beverley separates these into 5 and 6).
- Bucket 7 = "Material basis and realization" (Beverley has this as RELATIONS between buckets, not a separate bucket; canonical Bucket 7 = GDC/Information).

**Verdict: ARCO's prior framework was non-canonical.** The corrected CLAUDE.md (committed 2026-05-12) matches Beverley canonical seven, with the realization/material-basis relations relocated to a "cross-bucket structural check" section that is NOT a bucket.

### A.4 Regulatory fiat placement

Smith-Against-Idiosyncrasy line 153 (Principle 9):

> An ontology should clearly mark whether given expressions are referring to types (universals, kinds, generals) or to instances (particulars, tokens, individuals).

For ARCO:
- Regulatory ICE artifacts (`:AnnexIII_Condition_1a`, `:AnnexIII_Condition_5b`, `:RegulatoryContent`) are particulars typed as Information Content Entities → Bucket 7 (GDC).
- Regulatory universals defined by axiomatic restrictions over Material Entity (`:HighRiskSystem`, `:AnnexIII1aApplicableSystem`, `:AnnexIII5bApplicableSystem`) are restriction-defined kinds of Material Entity → Bucket 1.
- These are bridged by `iao:is_about`.

ARCO's prior CLAUDE.md §66 conflated both into Bucket 6 (now Bucket 7). The corrected note distinguishes them per Principle 9.

---

## B. Interest modeling (Q2)

### B.1 Beverley Capabilities paper — primitive relation

`KB/00_INBOX_RAW/papers/Capabilities-arxiv-2405.00183.md` line 156:

> Having an interest in the realization of a capability is a relation which holds between organisms or groups of organisms and processes that are realizations of dispositions in some material entity.

Line 167:

> We take 'has an interest in' as a primitive relational expression, which means that we cannot provide a non-circular definition.

Lines 169-175 give necessary conditions:

> o has an interest in p only if
> 1. o is an organism or group of organisms.
> 2. For some material entity m with dispositions bi and realizations pi: p is among these realizations and p may causally influence or be influenced by o.
> 3. p contributes to the survival and reproduction of o or to the realization of o's goals.

**Findings:**
- Paper's Interest is a PRIMITIVE RELATION, not a typed entity.
- Domain: organism or group of organisms.
- Range: PROCESS (the realization, not the disposition).
- Paper does NOT type Interest as Quality.

### B.2 CCO v1.7 — `cco:has_interest_in` predicate

`C:\Users\subdu\AppData\Local\Temp\cco-v17\CCO_merged.ttl` lines 1349-1361:

```turtle
cco:has_interest_in rdf:type owl:ObjectProperty ;
    owl:inverseOf cco:is_interest_of ;
    rdfs:domain cco:Agent ;
    rdfs:range obo:BFO_0000015 ;
    rdfs:label "has interest in"@en ;
    skos:definition "A relation between an entity and some process where the entity has an interest in that process."@en ;
    skos:editorialNote "This term is meant to be weakly normative...";
    skos:scopeNote "There are four conditions in which an entity has an interest in some process. 1) Biological Condition... 2) Artifactual Condition... 3) Prescription Condition: If an agent or group of agents has a plan, then it has an interest in the realization of all the processes and process-combinations prescribed by that plan. 4) Facilitation Condition..."
```

**Findings:**
- CCO v1.7 has a canonical `cco:has_interest_in` predicate.
- Domain: `cco:Agent`. Range: `bfo:0000015` (Process).
- Aligns with Beverley Capabilities paper (Agent → Process).
- CCO does NOT have a typed `cco:Interest` class.
- Prescription Condition (item 3 in scopeNote) is directly relevant to ARCO regulatory ICEs: if an agent has a plan, it has interest in realizations of processes prescribed by that plan. Regulatory plans / intended-use specifications fit here.

### B.3 abi production ontology — Interest as Quality (extension)

`C:\Github Repos\abi\src\core\abi\ontologies\domain-level\CapabilityOntology.ttl` lines 60-64:

```turtle
capability:Interest rdf:type owl:Class ;
    rdfs:subClassOf bfo:BFO_0000019 ;           # Quality
    rdfs:label "Interest"@en ;
    skos:definition "A quality of an organism or group of organisms 
                     indicating stake in the realization of certain capabilities."@en .
```

Lines 154-159 (axiomatic restriction):

```turtle
capability:Interest rdfs:subClassOf [
    rdf:type owl:Restriction ;
    owl:onProperty bfo:BFO_0000052 ;             # inheres_in
    owl:someValuesFrom bfo:BFO_0000040 ] .       # Material Entity
```

Lines 77-82 (relation):

```turtle
capability:hasInterestIn rdf:type owl:ObjectProperty ;
    rdfs:domain capability:Interest ;
    rdfs:range capability:Capability .          # NB: range is Capability, not Process
```

Lines 84-89 (bearer):

```turtle
capability:bearerOfInterest rdf:type owl:ObjectProperty ;
    rdfs:domain capability:Interest ;
    rdfs:range bfo:BFO_0000040 .                 # Material Entity (redundant w/ BFO bearer_of)
```

Header line 21 cites the Beverley Capabilities paper as `dc:source`. Lines 18 list Barry Smith and John Beverley as contributors.

**Findings:**
- abi types Interest as a Quality subclass.
- abi's `hasInterestIn` has range CAPABILITY (disposition), not PROCESS. This DIVERGES from the paper and from CCO.
- abi's `bearerOfInterest` is REDUNDANT with BFO `bearer_of` (`bfo:0000196`). Over-mint.
- abi is a CONSISTENT EXTENSION of the paper (you can imagine Interest as a Quality borne by an organism with the paper's relation lifted into a property), but it is NOT what the paper or CCO does.
- abi's contributors include Smith and Beverley themselves, lending production-canon weight to the Quality typing.

### B.4 Three options inventory

| Option | Source | Interest typing | Direction | Class minted? | Notes |
|---|---|---|---|---|---|
| **A** | CCO v1.7 + Beverley paper | Primitive relation | Agent → Process | No | Canonical default; aligns paper + CCO; matches Beverley's "primitive relational expression" |
| **B** | abi production extension | Quality (BFO_0000019) | Organism → Interest → Capability | Yes (`:Interest`) | Production canon per abi; simplifies paper (Interest → Capability not Interest → Process); requires also rejecting abi's redundant `bearerOfInterest` and using BFO `bearer_of` |
| **C** | Hybrid (paper-aligned typed) | Quality (BFO_0000019) | Organism → Interest → Process | Yes (`:Interest`) | NEW option not in original agent inventory: type Interest as Quality but keep paper's Agent→Process semantic. Mints class, but matches paper's relation direction. |

**Adversarial note (correction to prior conversation):** I previously said "canon-by-paper is open; canon-by-production is B." This is partially right but understates two facts:
1. CCO v1.7 (which ARCO is pinned to per CLAUDE.md Invariant 13) has `cco:has_interest_in` as canonical predicate matching the paper. So CCO is NOT silent — CCO supports Option A.
2. abi's Option B simplifies the paper's Interest → Process semantic to Interest → Capability. This is a non-trivial divergence from the paper, not just a typing extension.

The user's statement "interest as quality follows literally all smith beverley papers/work and our textbooks" was over-stated. abi (production) supports Quality typing; the paper itself does not; CCO does not; textbooks are silent.

### B.5 Smith-Against-Idiosyncrasy applied (Principle 5)

`KB/00_INBOX_RAW/papers/Smith-Against-Idiosyncrasy.md` line 67:

> **5. The principle of terminological moderation:** Stay as close as possible to the terms already used by your intended audience and to their already established meanings. Use only terms for which either (1) there is a reasonable expectation that intended users of the ontology will have a need for them, or (2) such terms are required to fill gaps in the ontology in order to create a complete hierarchy.

Applied to ARCO's M-Capability-1 decision: do not mint `:Interest` as a Quality class unless we genuinely NEED it. We need it only if:
- We want to refer to specific interests as particulars (e.g., "Sentinel's natural-person-rights-protection interest" as an IRI).
- We want to carry properties on the interest (strength, source, etc.).
- The class is required to fill an Annex III hierarchy gap (e.g., to define `:NaturalPersonRightsInterest ⊑ :Interest` as a typed subclass).

If `cco:has_interest_in` (Agent → Process) suffices for the regulatory chain, then Principle 5 says: do NOT mint.

---

## C. Aboutness (Q3)

### C.1 ICE definition (broadened)

`KB/00_INBOX_RAW/papers/Ceusters-Smith-Aboutness.md` line 21 gives the original IAO definition; lines 55-65 propose the broadening:

> In (Ceusters, 2012) we proposed broadening the definition of ICE to require 'aboutness to some portion of reality' rather than just 'to some entity,' in order to allow the domain of the aboutness relation to include inter alia
> - **universals**, for instance in the ICE concretized by the string *there are no instances of dinosaur which survive*,
> - **relations**, for instance in the ICE concretized by the string *the part-whole relation is transitive*,
> - **other ICEs**, for instance when someone asserts that what someone else just stated is true, and
> - **configurations**, for instance in the ICE concretized by *Barack Obama is the current President of the USA*
> 
> – **none of which is an entity in BFO terms**.

**Critical adversarial finding (correction to prior conversation):** The bolded final clause "none of which is an entity in BFO terms" was MISSED by the canon agent. This is load-bearing.

Configurations (along with universals, relations, and other ICEs) are PORTIONS OF REALITY but NOT BFO ENTITIES. So:
- Minting a `:SystemConfiguration` class as a BFO Class to be an aboutness target would CONTRADICT Ceusters-Smith. The whole point of the broadening is to allow aboutness to targets that aren't BFO entities.
- My prior framing of "C-full" as "mint a typed configuration class" was WRONG.

### C.2 Configuration as POR target

Same paper line 67 (the Obama example):

> The last example on this list is not only about Barack Obama but also about his role of being President of the USA and about the USA itself. But it is not only about these entities taken singly; in addition, it is about how the three entities are related to each other in a certain interval of time, and about the entire portion of reality – the configuration – made up by all of these together. This configuration is asserted to exist by a human subject using the corresponding sentence in a specific sort of context and with a specific sort of associated cognitive quality. But it can also be referred to, for instance when someone makes a second-order assertion using a nominalized expression, as in: *That Barack Obama is President of the USA is of epoch-making significance*.

**Findings:**
- A configuration is "the entire portion of reality – the configuration – made up by all of these together" (entities + their relations + temporal interval).
- A configuration is NOT a BFO entity (per line 65).
- A configuration CAN be referred to via nominalized expressions.
- An ICE can be about a configuration without that configuration being a typed class.

### C.3 The `is_about` primitive

Same paper lines 133-135:

> x is_about y means:
> x refers to or is cognitively directed towards y. Domain: representations; Range: portions of reality. Axiom: if x is_about y then y exists (veridicality).

**Findings:**
- Domain is REPRESENTATIONS (Qualities, SDC). Not ICEs directly.
- Range is PORTIONS OF REALITY.
- ICEs inherit aboutness from cognitive representations via concretization (line 33, 77).
- Veridicality: if x is_about y, then y exists.

### C.4 Veridicality and design-time

Same paper line 173:

> Although it is a requirement that the target of aboutness be a portion of reality (POR), there is no requirement that the relevant POR exists at the time when the associated cognitive representation exists. Thus a patient can contemplate a past disorder.

**Finding:** ARCO design-time aboutness is canonically supported. The regulatory ICE can be about a future deployment configuration; the POR doesn't need to exist NOW.

### C.5 ICE concretization

Same paper lines 139-143:

> x concretizes y at t means: x is a QUALITY & y is a GENERICALLY DEPENDENT CONTINUANT & for some material entity z, x specifically_depends_on z at t & y generically_depends_on z at t & if y migrates from bearer z to another bearer w then a copy of x will be created in w.

**Findings:**
- Concretization is the inverse of is_carrier_of (BFO `bfo:0000084`) per the chain Quality → ICE → bearer.
- An IQE (Information Quality Entity) is the Quality that concretizes an ICE.
- ARCO's L2.2 row (`cco:is_tokenized_by` missing on ARCO-generated ICEs) sits exactly here in the canon.

### C.6 Three options revised

| Option | Target of aboutness | Canon position | Class minted? |
|---|---|---|---|
| **B** (universal-only) | The defined class universal (`:AnnexIII1aApplicableSystem`) | Canonical per §5 line 135; satisfies §2 line 59 (universal as POR target) | No (universal already exists) |
| **C-lite** (particular continuant) | The particular system instance (`:Sentinel_ID_System`) | Canonical per §5 line 135; the system instance is a Material Entity, hence a POR | No |
| **C-multi** (multiple constituents) | The system instance PLUS its constituent typed parts (disposition, IUS, USS) | Canonical per §2 line 59 + line 67; multiple aboutness targets, configuration implicit in the union | No |
| **C-full** (REJECTED) | A typed `:SystemConfiguration` class | CONTRADICTS §2 line 65 ("none of which is an entity in BFO terms") | Would require minting — DON'T |

**Verdict reversal from prior conversation:** I previously framed "C-full" as a canonically-maximal option. That was wrong. Per §2 line 65, configurations are NOT BFO entities, so minting a typed configuration class CONTRADICTS the very passage that licenses configuration-level aboutness. The actual canonically-maximal option is **C-multi**: assert is_about to multiple constituent entities, letting the configuration emerge implicitly from the typed relations in the graph.

### C.7 Does C-multi require modeling temporal regions?

Per §2 line 67: "in addition, it is about how the three entities are related to each other in a certain interval of time, and about the entire portion of reality – the configuration."

The temporal interval is part of the canonical configuration description. But aboutness can target:
- The entities (no temporal modeling required — they're continuants)
- Their relations (visible in graph through typed predicates)
- The temporal interval (would require Bucket 6 modeling)

So C-multi without temporal modeling captures parts (a) and (b) but not (c). This is HONESTLY PARTIAL.

**Disclosure required if ARCO adopts C-multi:** "ARCO's configuration-level aboutness asserts is_about to the constituent system instance and its typed parts. The temporal interval of the configuration (per Ceusters-Smith §2 line 67) is not modeled (Bucket 6 scope cut). Reconstruction of the configuration's temporal extent is left to the consumer."

---

## D. Class-minting discipline (Smith-Against-Idiosyncrasy)

### D.1 Principle 5 — terminological moderation

Cited in B.5 above. Applies to whether to mint `:Interest`, whether to mint configuration classes, whether to mint role-bearer particulars.

### D.2 Principle 8 — compositional term construction

`KB/00_INBOX_RAW/papers/Smith-Against-Idiosyncrasy.md` line 116:

> **8. The principle of compositional term construction:** if an ontology uses in a systematic way terms of the form 'a † b' (where '†' stands in for some term-binding operator like 'of' or 'with') then it should include also the corresponding a and b terms (or it should link to treatments of the latter in some other standard ontology).

**New finding on ARCO:** `:CapabilityDisposition` is a compositional name (Capability + Disposition). Per Principle 8, ARCO should EITHER:
- Have `:Capability` as its own class (e.g., subclass of `bfo:0000016` Disposition, mirroring abi's `capability:Capability`)
- OR rename `:CapabilityDisposition` to just `:Capability` and let `:Capability ⊑ bfo:0000016` carry the disposition typing via BFO subsumption

The current ARCO state — `:CapabilityDisposition` with no `:Capability` class — violates Principle 8. This was NOT flagged by the prior canon agent or by my prior analysis.

### D.3 Principle 9 — types and instances

Cited in A.4 above. Applies to regulatory fiat placement (Bucket 1 universals vs Bucket 7 ICE particulars).

---

## E. Adversarial findings — where prior analysis was wrong

### E.1 Canon agent (2026-05-12 03:xx) errors

1. **Q1 verdict (buckets):** Agent endorsed ARCO's prior Bucket 7 ("Material basis and realization") as canonical because the relations (`ro:0000091`, `bfo:0000055`) are canonical. This conflated canonical RELATIONS with canonical BUCKETS. Beverley Lecture 5 line 199 lists "has material basis" as a RELATION, not a bucket. Caught by my first-pass critique.

2. **Q2 verdict (interest):** Agent claimed canon is "silent" on Interest typing. Missed abi production canon entirely. Caught by my grep of abi `CapabilityOntology.ttl`.

3. **Q3 verdict (aboutness):** Agent missed the critical clause "none of which is an entity in BFO terms" at Aboutness §2 line 65. This clause INVALIDATES the C-full option (mint `:SystemConfiguration` as typed class). Caught by my direct re-read of Aboutness paper.

### E.2 My own prior errors (in conversation before this artifact)

1. **C-lite vs C-full framing:** I framed C-full as a canonically-maximal option requiring temporal modeling. Per Aboutness §2 line 65, C-full (minting a typed configuration class) CONTRADICTS canon. The correct maximal option is C-multi (assert is_about to multiple constituents).

2. **"Canon-by-production B" framing for Interest:** I said canon-by-paper is open, canon-by-production is B. Misleading because CCO v1.7 (which ARCO is pinned to) has the canonical predicate matching the paper, not B. So CCO is NOT silent — it supports A. The user's claim that Interest-as-Quality is universal across canon is over-stated.

3. **CapabilityDisposition compositional naming:** Missed Smith-Against-Idiosyncrasy Principle 8 application to ARCO's existing class name. Now flagged.

### E.3 Open questions where canon is silent or self-contradictory

1. **Whether abi's Interest-as-Quality is endorsed by Beverley himself.** abi credits Smith and Beverley as contributors, which suggests endorsement, but the published Capabilities paper deliberately leaves typing primitive. abi's extension may be a production simplification rather than a canon commitment.

2. **Whether ICE-direct iao:is_about is canonical.** Aboutness paper line 135 sets is_about domain = REPRESENTATIONS (Qualities). But IAO operationally uses iao:0000136 on ICEs directly. The paper proposes that ICEs inherit aboutness via concretization. ARCO's practice (asserting iao:is_about directly on ICE instances) is operational-IAO-canonical but not strict-Aboutness-paper-canonical.

3. **What "configuration as POR but not BFO entity" means for RDF representation.** Aboutness paper says configurations are PORs but not entities. In RDF, every aboutness target needs an IRI (or a literal). How do you assert is_about to "the configuration" without giving it an IRI that types it as something? Canon does not formalize this. ARCO's pragmatic answer (C-multi) is to distribute aboutness across constituent IRIs, treating the configuration as emergent.

---

## F. ARCO implications

### F.1 M-Capability-1 (Interest modeling) — three options revisited

| Option | Choice | Canon backing | Discipline cost |
|---|---|---|---|
| **A — `cco:has_interest_in` relation only** | Use CCO v1.7 predicate; no new class | Canonical per CCO v1.7 + Beverley paper | Lightest; satisfies Principle 5; matches Hub-and-spoke |
| **B — Interest as Quality (abi-style)** | Mint `:Interest ⊑ cco:Quality`; use abi pattern minus the over-mints | Production canon per abi (Smith & Beverley contributors); extension beyond paper | Heavier; expands Bucket 2 from empty to populated; must reject abi's `bearerOfInterest` (redundant) and avoid `hasInterestIn` simplification (use CCO direction Agent→Process) |
| **C — Hybrid: Quality + paper direction** | Mint `:Interest ⊑ cco:Quality`; relation Interest → Process (not Capability) | Combines abi typing + paper semantics; not directly in any single canon source | Mid-weight; new combinatorial choice; harder to defend with single citation |

**Discipline check (Principle 5):** Do we need `:Interest` as a class? The question is what ARCO needs to express for Annex III applicability:
- "Natural persons have a rights-protection interest in the realization of biometric identification processes" — can be expressed at relation level as `cco:Person cco:has_interest_in :RBI_Process` (Option A).
- "Each particular interest has a strength, a source, a regulatory basis" — would require typed Interest (Option B or C). Does ARCO need this for Annex III? Probably no for design-time classification; possibly yes for evidence-ledger demo at higher fidelity.

Recommendation pending user decision. The user's prior preference for B is reasonable but is the heaviest option; A is canonically defensible and lighter. Decision must be made consciously with awareness that abi diverges from paper/CCO.

### F.2 M-Aboutness-Config-1 (configuration-level aboutness)

C-full is REJECTED per §2 line 65 (configurations are not BFO entities; minting a typed configuration class contradicts the very basis of configuration-level aboutness).

The actual options are:
- **B — universal-only:** `:AnnexIII_Condition_1a iao:is_about :AnnexIII1aApplicableSystem`. One triple per ICE. Canonical (§5 + line 59 covers universals as POR).
- **C-lite — particular continuant:** Add per-assessment triple `:AnnexIII_Condition_1a iao:is_about :Sentinel_ID_System`. Particular as POR per §5.
- **C-multi — multiple constituents:** Add per-assessment triples is_about to system + its capability + its IUS + its USS. Configuration implicit. Closest to canon §2 line 67 (configuration = entities + relations together) without minting a configuration class.

Recommendation pending user decision. C-multi is canonically richest; C-lite is canonically minimal-but-adequate; B is canonically baseline.

**No temporal/spatial unlock required for any of these options** (Buckets 5 and 6 stay cut). The temporal interval that §2 describes as part of a configuration is part of the canonical description but not required as an aboutness target.

### F.3 New foundation finding — `:CapabilityDisposition` naming

Per Principle 8 (Smith-Against-Idiosyncrasy line 116), ARCO's `:CapabilityDisposition` is a compositional name without a corresponding `:Capability` class.

Two resolutions:
- **R1 — Add `:Capability` as a separate class.** Mirror abi pattern: `:Capability ⊑ bfo:0000016` (Disposition). Then `:CapabilityDisposition` either becomes `:Capability` directly OR a subclass of `:Capability`.
- **R2 — Rename to `:Capability` only.** Remove the compositional name; use BFO subsumption (`:Capability ⊑ bfo:0000016`) to carry the Disposition typing.

Recommendation: R2 (rename to `:Capability`). The "Disposition" suffix is redundant with the BFO hierarchy. R2 is the lighter discipline-satisfying option and matches abi.

This is a separate foundation issue requiring its own OPEN_PROBLEMS row.

---

## G. Source register (every load-bearing citation in this doc verified by direct file read)

| Claim | Source file | Line(s) verified |
|---|---|---|
| Canonical seven buckets | `KB/00_INBOX_RAW/papers/Design_Pattern_Lecture_5_Disambiguation.md` | 50-58, 65-72 |
| Canonical inter-bucket relations | same file | 196-204 |
| Interest as primitive relation | `KB/00_INBOX_RAW/papers/Capabilities-arxiv-2405.00183.md` | 154-156, 167 |
| Interest necessary conditions | same file | 169-175 |
| Capability hierarchy (Function ⊑ Capability ⊑ Disposition) | same file | 138, 140, 247 |
| Material-entity-bearer requirement | same file | 148-150 |
| CCO `cco:has_interest_in` Agent → Process | `C:\Users\subdu\AppData\Local\Temp\cco-v17\CCO_merged.ttl` | 1349-1361 |
| abi `:Interest` ⊑ Quality | `C:\Github Repos\abi\src\core\abi\ontologies\domain-level\CapabilityOntology.ttl` | 60-64, 154-159 |
| abi attribution Smith+Beverley | same file | 18, 21 |
| Aboutness broadening (POR targets) | `KB/00_INBOX_RAW/papers/Ceusters-Smith-Aboutness.md` | 55-65 |
| "None of which is an entity in BFO terms" | same file | 65 |
| Configuration paragraph (Obama) | same file | 67 |
| is_about primitive | same file | 133-135 |
| Veridicality + past/future POR | same file | 173 |
| Concretization definition | same file | 139-143 |
| Principle 5 (terminological moderation) | `KB/00_INBOX_RAW/papers/Smith-Against-Idiosyncrasy.md` | 67 |
| Principle 8 (compositional term construction) | same file | 116 |
| Principle 9 (types and instances) | same file | 153 |

---

**Last verified:** 2026-05-12.  
**Author:** Alex Moskowitz (synthesis); canon citations verified by direct file read.  
**Status:** Immutable record of canon backtest. New findings extend; corrections add dated notes.  
**Related:** `CLAUDE.md` § Seven Buckets (updated 2026-05-12 to match Section A); `OPEN_PROBLEMS.md` M-rows pending for M-Capability-1, M-Aboutness-Config-1, and the new `:CapabilityDisposition` naming finding.
