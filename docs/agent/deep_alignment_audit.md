# ARCO Deep Alignment Audit

_Date: 2026-03-19 · Branch: claude/audit-arco-imports-RjcFZ · Status: COMPLETE_

## Primary Question

**Is ARCO, as currently designed, actually doing the valuable thing it claims to do: providing deterministic, traceable, design-time regulatory classification results from explicit ontological commitments?**

**Answer: Yes.** The architecture delivers its core value. The findings below identify three doc overclaims to fix, two real gaps to document, and confirm that the rest is either deliberate design or deferred scope.

---

## Output 1: Alignment Memo

### What the architecture is actually doing

ARCO takes system descriptions modeled as OWL instances (components, capabilities, intended use directives, use scenario directives), runs OWL-RL reasoning over them against bridge axioms, and produces inferred `rdf:type` memberships (`HighRiskSystem`, `AnnexIII1aApplicableSystem`, `AnnexIII5bApplicableSystem`). SHACL validates documentary completeness. SPARQL ASK queries provide an audit layer. A certificate is emitted.

The core entailment mechanism is genuine OWL Description Logic: three `owl:equivalentClass` definitions that fire only when instance data satisfies specific structural conditions. Verified by gate-removal tests, content-mutation tests, cross-category isolation tests, and adversarial tests (equivalence decoys, blank-node dispositions). Two Annex III categories are implemented (1(a) biometric identification, 5(b) creditworthiness evaluation), plus a negative case (1:1 verification kiosk).

### What is deliberate and defensible

1. **Three-gate decomposition.** Annex III items follow a consistent pattern: "AI systems intended to be used for [process] of [affected entities]" plus the implied structural prerequisite that the system bears the relevant capability. Decomposing into Gate 1 (capability disposition — reality-side), Gate 2 (intended use prescribing a typed process — representation-side), and Gate 3 (use scenario referencing the affected role category — representation-side) is a principled interpretive move. Not verbatim legal transcription, but a defensible formalization.

2. **HighRiskSystem as latent-risk signal.** Fires on capability alone (Gate 1). An ARCO design choice, not a direct legal encoding. Deliberately separates "this system has a component with a regulated capability" from "this system meets all three statutory conditions." Defensible as engineering early-warning.

3. **Reality/representation separation.** Capabilities as BFO Dispositions in material components (reality-side), intended use and scenario specifications as CCO Directive ICEs (representation-side). Textbook BFO applied ontology practice.

4. **NaturalPersonRole as Role.** "Natural person" in EU law is a legal status, not a biological classification. `bfo:0000023 (Role)` is defensible.

5. **Gate 3 `owl:hasValue` on class IRI.** The use scenario is about the role *category* (the universal "natural person"), not about a specific person. OWL 2 punning is permitted and correctly captures this semantics.

6. **AnnexIIITriggeringCapability as regulatory grouping class.** Explicitly documented as "not a BFO natural kind." Correct — placed in governance extension, not core.

7. **Two-layer certificate output.** Classification (OWL-RL) and audit (SPARQL) are cleanly separated in code, certificate, and documentation.

8. **Disjointness enforcement.** Pairwise capability disjointness + BFO category disjointness from real import.

### What is a real gap

1. **No Article 6(3) derogation mechanism.** A system meeting all three gates but qualifying for derogation cannot be exempted. Over-classifies in those cases. Genuine scope gap.

2. **No fraud exclusion for 5(b).** A fraud-detection system with creditworthiness capability would be incorrectly classified.

3. **`AnnexIII_Condition_Q1` vestigial `cco:prescribes` triple** (instances_sentinel.ttl line 25). Does not affect classification but is semantically misleading and blocks CCO import.

### What is merely deferred scope

- Annex III categories beyond 1(a) and 5(b) — extension protocol exists, pattern generalizes
- Full RO/IAO/CCO import — deferred per ADR-001 with documented blockers
- "At a distance" / "without active involvement" qualifiers — boundary conditions on process type, acceptable for v1
- Annex III 1 chapeau legality condition — verification exclusion partially handled
- Negative test infrastructure for isolated graph reasoning — documented, adversarial tests work around it

### What is overstated in docs

1. **`ARCO_Regulatory_Determination_Case.md` section 2.2:** "Regulatory classification under the EU AI Act depends on capability, not intent or configuration." Contradicts ARCO's own three-gate architecture where Gates 2-3 encode intent/scenario. Should say: "HighRiskSystem depends on capability alone; full Annex III applicability additionally requires documented intended use and affected role."

2. **`TechnicalDeck.md` ~line 237:** Shows stale `HighRiskSystem` axiom without `SystemComponent` in the intersection. No longer matches the actual axiom.

3. **`README.md` TL;DR:** "tells you whether your system is high-risk" without qualifier. Should say "per ARCO's encoding of."

---

## Output 2: Findings Table

| # | Issue | Type | Source | Severity | Why it matters | Action |
|---|-------|------|--------|----------|---------------|--------|
| 1 | Three-gate decomposition is interpretive formalization | Deliberate design choice | Annex III vs governance extension axioms | N/A | Defensible, already documented | No action |
| 2 | `HighRiskSystem` fires on capability alone | Deliberate design choice | Governance extension lines 156-177 | N/A | Latent risk detection, separated from full applicability | No action |
| 3 | Gate 3 `owl:hasValue` punning | Deliberate design choice | Governance extension Gate 3 axiom | N/A | Correct encoding of "about the category" | No action |
| 4 | `AnnexIII_Condition_Q1` vestigial `prescribes` triple | Documented deferral | instances_sentinel.ttl line 25 | Low-Med | CCO-import blocker, semantically misleading | Later |
| 5 | No Article 6(3) derogation | Real gap | EU AI Act Art. 6(3) | Medium | Over-classifies when derogation applies | Later (design doc first) |
| 6 | No 5(b) fraud exclusion | Real gap | Annex III 5(b) | Medium | False positive for fraud-detection credit systems | Later (document as known limitation now) |
| 7 | "At a distance" / "without active involvement" not modeled | Deferred scope | Art. 3(36) | Low | Acceptable for v1 | No action |
| 8 | Case study section 2.2 "capability, not intent" | Overclaim | Regulatory Determination Case | Low | Contradicts own three-gate design | **Now** |
| 9 | TechnicalDeck stale `HighRiskSystem` axiom | Overclaim (stale) | TechnicalDeck.md | Low | Misleading to technical reader | **Now** |
| 10 | README TL;DR unqualified "high-risk" | Overclaim | README.md | Low | Elides ARCO-encoding qualifier | **Now** |
| 11 | RO/IAO/CCO stubs, no domain/range | Documented deferral | ADR-001 | Medium (interop) | Property misuse passes silently | Later |
| 12 | `cco:prescribes` no domain/range | Documented deferral | Governance extension | Low | Part of CCO import | Later |
| 13 | Two-layer architecture | Deliberate design choice | Pipeline, certificate, CLAUDE.md | N/A | Cleanly separated, no cross-layer issue | No action |
| 14 | Gate 1 as explicit capability requirement | Deliberate design choice | Governance extension | N/A | Legally implied, BFO decomposition is ARCO-specific | No action |
| 15 | BFO active, property layer scaffolded | Deliberate design choice | ADR-001, alignment audit | N/A | Correctly documented | No action |
| 16 | Verification exclusion | Deliberate design choice (partially handles chapeau) | Core + governance | Low | Current encoding correct for modeled cases | No action |

---

## Output 3: Safe Claim Set

### Safe to claim now

- ARCO produces deterministic, reproducible regulatory classification results from explicit system descriptions, using OWL-RL formal reasoning with no LLMs in the classification loop
- Classifications are *derived* (entailed by the reasoner from bridge axioms), not asserted
- The three-gate architecture encodes a defensible interpretation of Annex III's structure: capability (reality-side), intended use (representation-side), affected role (representation-side). Each gate is independently necessary — gate-removal and content-mutation tests prove this
- The architecture generalizes across Annex III categories (demonstrated by 1(a) and 5(b), with cross-category isolation formally enforced)
- BFO 2020 is imported and active: real supertype chains, real disjointness enforcement
- The pipeline distinguishes classification (OWL-RL entailment) from audit (SPARQL ASK). These layers are independently computed and reported
- Verification-only negative case demonstrates non-triggering capabilities are correctly excluded
- Adversarial tests prove the pipeline does genuine OWL reasoning, not IRI pattern-matching

### Safe only with qualifier

- "ARCO classifies systems as high-risk" — **qualifier**: "per ARCO's ontology encoding of Article 6 and Annex III"
- "BFO/CCO-aligned" — **qualifier**: BFO class hierarchy is imported and enforced; CCO/RO/IAO terms used at correct IRIs via local stubs without domain/range enforcement
- "Capability-based classification" — **qualifier**: `HighRiskSystem` fires on capability alone (latent risk); full Annex III applicability requires capability + intended use + scenario
- "ARCO moves the risk decision upstream" — **qualifier**: surfaces whether a system satisfies its formal encoding of regulatory conditions; reduces uncertainty but does not replace legal review
- "Classification is invariant under runtime configuration" — **qualifier**: true for `HighRiskSystem` (capability-based); full classification depends on directive ICEs that could change

### Not safe yet

- "ARCO determines whether a system is legally high-risk under the EU AI Act" — conflates formal classification with legal determination
- "Full BFO/CCO/IAO/RO alignment" — property layer is not grounded
- "Complete Annex III coverage" — only 2 of 8+ categories
- "Production-ready compliance tool" — reference implementation, not deployed platform
- "Handles derogations and exclusions" — Article 6(3) and 5(b) fraud exclusion not modeled

---

## Output 4: Next-Step Recommendations

### 1. Fix the three doc overclaims

**Strengthens:** Credibility with any reviewer — legal, ontological, or commercial.

**Why highest priority:** Cheapest fixes (three sentence edits) with highest credibility return. A reviewer finding section 2.2 says "depends on capability, not intent" while the ontology has three gates would question the project's self-awareness.

**Why not a rabbit hole:** Three specific sentences. No architecture work. 30 minutes.

Fixes:
- `ARCO_Regulatory_Determination_Case.md` section 2.2: "depends on capability, not intent or configuration" → "HighRiskSystem classification depends on capability alone (latent risk detection); full Annex III applicability additionally requires documented intended use and affected role"
- `TechnicalDeck.md` ~line 237: update stale `HighRiskSystem` axiom to include `SystemComponent`
- `README.md` TL;DR: add "per ARCO's encoding of" qualifier

### 2. Document the 5(b) fraud exclusion as known limitation

**Strengthens:** Claim that scope boundaries are explicitly documented, not silently omitted.

**Why priority:** Anyone reading Annex III 5(b) will immediately notice the fraud exclusion clause. Undocumented omission looks like ignorance or concealment.

**Why not a rabbit hole:** One `rdfs:comment` update plus one line in `eu_ai_act_rules.md`.

### 3. Design the Article 6(3) derogation pattern (design document only)

**Strengthens:** Claim that architecture can accommodate regulatory complexity beyond positive-path classification.

**Why priority:** Most frequently cited gap in Annex III frameworks. Having a design doc showing how derogation claims would be modeled as ICE artifacts demonstrates extensibility without committing implementation effort.

**Why not a rabbit hole:** Design document only (extension protocol Steps 1-2). No TTL changes. No pipeline changes.

### 4. Run the pipeline to confirm green state

**Strengthens:** Empirical ground truth that audit findings do not indicate runtime failures.

**Why priority:** An audit that does not verify the system runs is incomplete.

**Why not a rabbit hole:** Three commands: `run_pipeline.py`, `test_gate_removal.py`, `test_scenarios.py`.

### 5. Consolidate legal-trace document

**Strengthens:** Claim that ontological commitments are traceable to specific legal text.

**Why priority:** Most common request from ontology and legal reviewers. Information exists but is scattered across comments, CLAUDE.md, and agent docs. One consolidated table (legal clause → axiom → interpretive choice → known gap) makes ARCO dramatically more defensible.

**Why not a rabbit hole:** Documentation exercise using existing information. Extension protocol Step 1 already defines the format.

---

## Answers to Specific Questions

### 1. Gate 1: direct legal encoding, legally implied, or ARCO-added?

**Legally implied requirement made explicit by ARCO as an engineering constraint.** The law does not separately state "the system must have the capability." It says "intended to be used for [regulated process]." The capability is *implied* — you cannot be intended for biometric identification without having biometric identification capability. ARCO makes this implicit prerequisite explicit and separately testable. The *specific BFO decomposition* (component → disposition) is ARCO's engineering choice. The *general requirement* (system must be capable) is legally implied.

### 2. HighRiskSystem: legal category, ARCO signal, or both?

**Primarily an ARCO latent-risk signal.** Article 6(2) classifies systems as high-risk when they fall under Annex III conditions, which include "intended to be used for" — an intent condition. `HighRiskSystem` fires on capability alone without requiring intent or scenario. It is *related to* the legal category (a system that is `HighRiskSystem` has the structural prerequisites for Annex III applicability) but not *identical to* it. The `AnnexIIIXxApplicableSystem` classes are the closer legal encoding.

### 3. Two-tier architecture: sound or misleading?

**Sound and intentional.** Classification (OWL-RL) and audit (SPARQL) are cleanly separated in code, certificate, and documentation. The pipeline computes them independently. Test infrastructure operates at the OWL entailment level. No material misleadingness.

### 4. Gate 3: defensible, under-explained, or misaligned?

**Defensible as-is.** `owl:hasValue :NaturalPersonRole` where `:NaturalPersonRole` is a class IRI used as concept-individual correctly encodes "about the role category (universal), not about a specific person." The punning dependency is documented. No misalignment.

### 5. Missing legal elements: priority gaps vs deferred scope?

| Element | Classification | Rationale |
|---------|---------------|-----------|
| Article 6(3) derogation | **Genuine priority gap** (medium) | Primary escape valve. Over-classifies when applicable. Design doc priority, not immediate implementation. |
| 5(b) fraud exclusion | **Genuine priority gap** (medium) | Explicit legal carve-out. Document as known limitation now. |
| "Without active involvement" / "at a distance" | **Deferred scope** (low) | Process type boundary conditions. Acceptable for v1. |
| Annex III 1 chapeau legality condition | **Deferred scope** (already partially handled) | Verification exclusion encoded. |

### 6. BFO/CCO/IAO/RO story: does it match?

**Yes, precisely.** BFO: imported and active. RO/IAO: IRIs used, no source axioms loaded. CCO: local stubs with subclass declarations, no domain/range. Product claims saying "BFO-aligned" are accurate. "CCO-aligned" should say "uses CCO vocabulary via local stubs."

### 7. Coherent value proposition without replacing legal review?

**Yes, concretely.** ARCO's value:
1. **Eliminates ambiguity in the positive path.** If a system has biometric ID capability, is intended for remote biometric ID, and acts on natural persons, there is no reasonable legal argument it escapes Annex III 1(a). ARCO makes this formal, reproducible, auditable.
2. **Provides design-time feedback.** Discovering classification triggers during design (cheap) rather than post-deployment compliance review (catastrophically expensive).
3. **Provides shared formal vocabulary.** Components, capabilities, intended use, scenario — gives engineering, legal, and compliance a common language.
4. **Detects latent risk.** Capability-only classification surfaces exposure that intent-based analysis would miss.

Legal review remains needed for edge cases, derogations, exclusions, and validating the encoding itself. ARCO eliminates the need for legal review to answer obvious classification questions.
