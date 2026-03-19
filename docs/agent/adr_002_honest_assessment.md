# ADR-002: Honest Assessment — What ARCO Is, What It Isn't, What's Next

_Date: 2026-03-19 · Status: ACCEPTED_

## Context

This document records an honest, research-grounded assessment of ARCO's current state, value proposition, competitive position, and weaknesses. It incorporates the design conversation about Gate 3 (NaturalPersonRole), the earlier alignment audit (v3), and external market research conducted 2026-03-19.

Its purpose is to prevent the project from inflating claims beyond what the evidence supports, and to provide a clear foundation for deciding what to do next.

---

## 1. What ARCO Actually Is (Current State)

### Technical Inventory

| Component | Status | Detail |
|-----------|--------|--------|
| OWL-RL classification pipeline | Working | Loads TTL → BFO 2020 reasoning → SHACL → SPARQL audit → certificate + HTML view |
| Three-gate classification axioms | Working | 2 Annex III categories: 1(a) biometric identification, 5(b) creditworthiness evaluation |
| Gate independence tests | Working | 5 removal + 2 mutation tests prove each gate is independently necessary |
| Multi-scenario regression | Working | 5 scenarios (2 positive, 1 negative, 2 adversarial). Cross-category isolation verified. |
| BFO 2020 import | Done | Real disjointness enforcement. 2,528 BFO-driven entailments. |
| RO/IAO/CCO | Stubs only | IRI declarations with no domain/range/chain axioms. Scaffolding for staged import. |
| CI | Working | 2 GitHub Actions workflows (demo run, smoke test) |
| Documentation | Thorough | Alignment audit (v3), ADR-001, extension protocol, ontology/coding/writing rules |
| UI / API / intake | Does not exist | System descriptions are hand-modeled TTL |
| Real-world system evaluation | Does not exist | All demos use synthetic systems (Sentinel-ID, CreditScorer) |
| Legal validation of gate decomposition | Does not exist | The three-gate interpretation of Annex III has not been reviewed by a lawyer |
| Annex III coverage | 2 of ~35 categories | 1(a) and 5(b) only |

### One-Sentence Summary

ARCO is a working formal classification prototype that does something genuinely novel — deterministic, ontology-based regulatory classification with full entailment traceability — but it has no intake mechanism, no UI, no real-world validation, and covers a small fraction of the regulation.

---

## 2. What ARCO's Value Proposition Actually Is

### The strong version (defensible)

> ARCO forces explicit design-time commitments about system capability, intended use, and affected-party scope, and uses formal logic to test whether those commitments trigger encoded regulatory categories. The output is deterministic, reproducible, and audit-traceable.

### The weak version (inflated — do not use)

> ARCO provides interoperable, philosophically grounded regulatory determination across real enterprise systems.

The strong version is true today. The weak version requires: more categories, real intake, legal validation, demonstrated interoperability, and full upper-ontology grounding. None of these exist yet.

### Why the strong version matters

Most organizations fail regulation not because they lack legal text but because:
- System descriptions are vague
- Capability claims are sloppy
- Intended use is not formalized
- Design commitments are not explicit
- Nobody can show why a classification was reached

ARCO addresses all five of these by requiring explicit, formal assertions and producing traceable logical consequences.

---

## 3. Competitive Landscape (Researched 2026-03-19)

### Market timing

The EU AI Act's high-risk system obligations take effect **August 2, 2026** — 4.5 months from this writing. Companies deploying high-risk AI in the EU must comply by then. The market is real and urgent.

### Who's in the market

| Competitor type | Examples | What they sell | ARCO's differentiation |
|----------------|----------|---------------|----------------------|
| Big 4 consulting | Deloitte, PwC, EY, KPMG | Consulting engagements, audit services | ARCO is deterministic; consulting is opinion-based |
| GRC platforms | OneTrust, TrustArc | AI Act modules on existing risk platforms | ARCO has formal entailment; they have checklists |
| AI governance startups | Holistic AI, Credo AI | Purpose-built governance platforms | ARCO has structural traceability; they have risk scores |
| Certification bodies | ForHumanity | Audit standards, certified auditor training | ForHumanity defines criteria; ARCO automates classification |
| Academic / formal methods | AIRO (Trinity College Dublin), W3C DPV AI Act extension, FinRegOnt | Research / vocabularies | AIRO represents risks; ARCO classifies. W3C DPV is vocabulary, not reasoning. See below. |

### Market size (Gartner, February 2026)

- AI governance platform spending: **~$492 million in 2026**, projected to surpass **$1 billion by 2030**
- This is tooling/platforms only; consulting spend is larger but harder to measure
- Broader context: worldwide AI spending forecast at $2.52 trillion in 2026; governance is a tiny fraction

### The BFO/NCOR ecosystem

- BFO is ISO/IEC 21838-2, used by 700+ ontology groups
- DoD and IC adopted BFO + CCO as baseline standards (January 2024)
- CUBRC (~170 engineers) does commercial ontology work for defense/intelligence
- **Nobody in this ecosystem is doing EU AI Act regulatory classification with BFO**
- The commercial activity is data integration and interoperability, not regulatory determination
- Semantic Arts created gistBFO for enterprise data integration, not regulatory compliance

### What competitors have that ARCO doesn't

- UIs, APIs, customer bases, revenue
- Full compliance lifecycle coverage
- Real-system evaluations
- Sales teams and go-to-market

### The closest academic precedent: AIRO

AIRO (AI Risk Ontology), developed at Trinity College Dublin's ADAPT Centre by Golpayegani, Pandit, and Lewis (2022), is an OWL 2 ontology for representing AI risks based on the EU AI Act and ISO risk management standards. It models AI use cases and their risks, and the authors demonstrated that SHACL validation and logical reasoning can determine whether a use case is high-risk. AIRO is integrated into the W3C Data Privacy Vocabulary (DPV) AI Act extension.

**How ARCO differs from AIRO:** AIRO is a risk *representation* ontology — it models risks and their relationships. ARCO is a deterministic *classification* ontology — it uses OWL-RL entailment via gate-structured equivalentClass axioms grounded in BFO/CCO to produce actual regulatory classifications (e.g., "this system IS an Annex III 1(a) system"). AIRO describes risk; ARCO classifies. These are fundamentally different approaches.

AIRO does not use BFO. The W3C DPV AI Act extension uses RDFS/SKOS as default semantics — it is a vocabulary/taxonomy, not a classification engine.

### What ARCO has that competitors don't

1. **Deterministic classification** — same input, same output, every time. No human judgment in the pipeline.
2. **Structural traceability** — full entailment chain from component → capability → regulatory condition → classification.
3. **BFO alignment** — positions for interoperability with other BFO-aligned systems (defense, biomedical, industrial).
4. **Three-gate decomposition** — novel encoding of Annex III conditions as OWL equivalentClass axioms. No published precedent found. AIRO (closest academic work) represents risk but does not do gate-structured entailment classification.

---

## 4. Weaknesses (Ranked by Severity)

### 1. Unvalidated legal decomposition (CRITICAL)

The three-gate decomposition (capability + prescribed process type + affected party category) is ARCO's engineering interpretation of Annex III. It has never been validated against the actual legal text by someone with legal authority. If the decomposition is wrong, the entire model is wrong regardless of how clean the engineering is.

**This is the single biggest risk to the project.** It cannot be resolved by more ontology work.

### 2. No traceability artifact connecting legal text to axioms (HIGH)

Known Gap #2 from the alignment audit. There is no single document connecting specific Annex III text to specific OWL axioms with explicit justification for each mapping decision. The connection exists in scattered comments and CLAUDE.md, but it is not systematically documented.

### 3. No intake mechanism (HIGH for product, irrelevant for research)

System descriptions must be hand-modeled as TTL triples. This is fine for a prototype. It is a hard blocker for any product use.

### 4. Gate 3 NaturalPersonRole naming (LOW)

The `NaturalPersonRole ⊑ bfo:0000023 (Role)` modeling is defensible but the name invites unnecessary criticism. Best near-term move: rename to `NaturalPersonCategory` or `NaturalPersonAffectedPartyCategory`. This is a cosmetic fix, not a structural one.

### 5. Partial upper-ontology grounding (LOW for current claims, HIGH for interoperability claims)

RO/IAO/CCO are stubs. Property usage is consistent with those ontologies' intent but not machine-validated. This is fully documented in the alignment audit and ADR-001.

---

## 5. Design Conversation Record: Gate 3

### Current defense (strong)

- The `owl:hasValue` + punning pattern is defensible as a category-reference gate
- The regulatory text operates at the level of affected-party categories, not specific person tokens
- Forcing phantom bearer instances to satisfy `someValuesFrom` would be worse if all you mean is category reference
- The punning fires correctly under owlrl and is not fragile

### Current vulnerability (real but contained)

- The weakest part is not the punning itself but the decision to encode "natural persons" as a Role
- The `rdfs:comment` says "Legal designation under EU law. Not a biological kind" — but the class name suggests something else
- A rename to category-explicit terminology would remove the surface-level attack without changing the logic

### Options (ranked)

| Option | What it does | Effort | Risk |
|--------|-------------|--------|------|
| **C: Rename** | Change `NaturalPersonRole` to `NaturalPersonCategory` | Small | None to pipeline |
| **A: Redesign to someValuesFrom** | Move Gate 3 to typed-instance existential | Medium | Reconceptualizes Gate 3 from category-reference to participant-typing |
| **B: Representation-side category spec** | Introduce explicit affected-party category ICE | Medium | Architecturally clean but premature |

**Recommended:** Option C now. Options A/B only when something forces the question (e.g., adding a category where the affected party is not a natural person).

**Important caveat on Option A:** Moving to `someValuesFrom` with participation semantics is a reconceptualization, not just a structural parallel to Gate 2. It changes Gate 3 from "the document references this category" to "the scenario has participants of this type." That's a bigger semantic move than it first appears.

---

## 6. What Should Happen Next

### If ARCO is a portfolio / research project

1. Write the legal traceability artifact (connect specific Annex III text to specific axioms)
2. Get informal legal feedback on the three-gate decomposition from someone who knows the AI Act
3. Add 1-2 more Annex III categories to prove the pattern generalizes
4. Write it up as a paper (the three-gate OWL entailment approach has no published precedent)

### If ARCO is intended to become a product

All of the above, plus:
5. Build a minimal intake UI (web form → TTL generation → pipeline → HTML view)
6. Do the RO import (lowest-risk next step for real property enforcement)
7. Evaluate one real system (even a public/synthetic-realistic one)
8. Find one potential buyer and show them the determination view

### What not to do

- Do not add more ontology classes to prove sophistication
- Do not attempt CCO import (too many blockers, documented in alignment audit)
- Do not write more positioning documents until the legal traceability artifact exists
- Do not claim interoperability until it's demonstrated

---

## 7. The Product Claim Distinction (Restated)

This was already documented in the alignment audit v3 (Open Question 2) but it is important enough to restate:

- ARCO determines whether a system description satisfies **ARCO's formal encoding** of Annex III categories
- ARCO does **not** determine whether a system is legally high-risk under the EU AI Act
- The three-gate equivalentClass definition is ARCO's engineering interpretation — not a verified legal determination
- All outward-facing text must maintain this distinction

---

## Related

- `docs/agent/bfo_cco_alignment_audit.md` — full technical audit (v3, 2026-03-17)
- `docs/agent/adr_001_alignment_end_state.md` — staged import decision
- `docs/agent/extension_protocol.md` — Annex III category addition protocol
