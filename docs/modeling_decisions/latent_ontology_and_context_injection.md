# Latent Ontology and Context Injection: ARCO's Position

**Status: position note, 2026-09-10.** This is not a new modeling decision. The operative decision is F4 in [decisions_justification_map.md](decisions_justification_map.md) (no LLMs in classification). This note records *why* F4 survives a specific and increasingly common counter-argument, so the next person who raises it gets an answer with anchors instead of a preference.

## The claim being assessed

A public post attributed to Animesh Kumar (CTO, DataOS), curated by Modern Data 101, argues for a **"Minimal Ontology Principle."** Read on 2026-09-10 from screenshots of the post; the linked long-form article was not retrieved, so this note responds to the post text only and should not be treated as a reading of the full argument.

The post's load-bearing moves, quoted:

1. *"Every LLM already carries a latent ontology: a geometric map of how business concepts relate to each other, distilled from millions of documents."*
2. *"What it DOES need to explain is the delta"* — and, in the post's diagram, *"Your Structural Ontology only needs to be as large as the deviations between your enterprise's usage and the model's prior."*
3. *"Agent confusion is a design signal ... Instead of a committee deciding upfront what everything means, you let the AI's misinterpretations surface which concepts actually need formal definition. The confusion IS the methodology."*

Short answer: **agree with (1) as a metaphor and with the minimalism instinct behind (2); reject (2) as stated and reject (3) as a governance principle for anything ARCO-shaped.**

## Where ARCO already agrees

ARCO is not an ontology maximalist, and the repo shows it rather than asserts it:

- Two of eight Annex III categories are modeled; the other six are deferred and disclosed (`LIMITATIONS.md` §1, §2).
- Time and place of operation are cut on purpose — ARCO is a design-time classifier and does not model when or where a system runs (`README.md`, "Some pieces of the picture are kept partial on purpose").
- ARCO refuses to mint natural-person particulars, temporal regions, or role-bearer tokens without source warrant. Honest sparseness over dishonest completeness is a named discipline, F6 (no fake-witness creation).
- LLMs are already permitted upstream: *"LLMs may be used upstream to draft instance data, but the classification itself runs on the hand-reviewed RDF"* (`LIMITATIONS.md` §5, line 242).

So "don't formalize the universe, and let the model handle ordinary language" is not the disagreement. ARCO does that.

## Where the argument breaks for ARCO

### 1. A prior is not an ontology, and the difference is pinning

"Latent ontology" is a metaphor for a statistical prior over language. It has no stable identifiers, no declared axioms, no consistency conditions, no provenance, and no guaranteed entailments. It also is not a fixed object: it varies by model, version, prompt, decoding parameters, and surrounding context.

ARCO's own history is the argument here. Decision F7 pins CCO to v1.7-2024-11-03 for one concrete reason: the v2.x line renamed readable IRIs (`cco:Person`) to ont-numbered IRIs (`cco:ont00000016`), and *"Cross-references between ARCO and external work ... fail silently if the version isn't pinned and tracked explicitly."* If a **published, versioned, human-authored** ontology can break a downstream commitment silently on a version bump, an unversioned latent prior cannot be the semantic baseline underneath a regulatory determination. There is no `owl:versionInfo` to write for it.

### 2. The delta is not reliably detectable by disagreement

Proposal (2) presupposes you can find the places where the model's meaning diverges from yours. The dangerous divergences are precisely the ones that do not present as disagreement: the model returns something fluent and plausible while grounding the concept wrong.

ARCO carries a worked example of exactly this shape. Biometric **verification** (1:1) and biometric **identification** (1:N) are near-neighbours in ordinary usage and separate in law: Article 3(36) defines verification as *"the automated, one-to-one verification, including authentication, of the identity of natural persons,"* and Recitals 15 and 17 plus the Annex III 1(a) operative carve-out exclude verification-only systems (`docs/legal/eu_ai_act_kernel.md:22-24, 111, 131, 137`). ARCO models the distinction as a disjointness axiom and keeps a standing negative control — the Verification Kiosk fixture, a 1:1 system that must *not* classify under 1(a) — plus a named acceptance test (`03_TECHNICAL_CORE/scripts/test_bi_rbi_genus.py`) that pins the non-entailment.

To be precise about what is and is not claimed: ARCO has not measured any model's behaviour on this pair, and this note asserts no such measurement. The structural point stands without one. A disagreement-driven method finds this distinction only if someone already knows it exists and goes looking — and if they know it exists, the "let confusion surface it" methodology did no work. The same hardware, per `LIMITATIONS.md` §3.5, is vendor-advertised as configurable for both modes, so the distinction lives in documented intent, not in anything a prior over text can be asked to adjudicate.

### 3. Definitions do not fail closed; axioms do

The post's remedy is a definition injected into context: *"net_revenue: Total billed minus refunds, recognized on cash receipt date."* For read-only question answering that can be sufficient, and this note does not dispute that.

It is not what ARCO's ontology is doing. ARCO's classification is a single `owl:equivalentClass` axiom, not a procedural check, so *"anyone with a standard reasoner can re-derive the result from the public definitions"* (`README.md`, "Why the architecture matters"). Two consequences have no counterpart in context injection:

- **Entailment.** The three-gate conjunction *entails* category applicability; nothing has to be trusted to have followed the instruction. A second reasoner (HermiT, OWL 2 DL) independently agrees on every push.
- **Fail-closed category errors.** Put `cco:designates` and `cco:prescribes` on one ICE individual and the graph is inconsistent under pinned CCO v1.7 domains plus disjointness; the pipeline halts during reasoning, names the violated disjoint pair, and emits no certificate (`03_TECHNICAL_CORE/scripts/test_ice_subfamily_trap.py`). A context-injected definition has no analogue: a malformed commitment produces a fluent answer, not a refusal.

This is the real distinction the post collapses. **Context injection corrects an interpretation. An ontology fixes what the system is entitled to treat as true and what follows from it.** Related, not equivalent.

### 4. "Confusion is the methodology" inverts the burden for consequential systems

As a *discovery heuristic* — mine agent failures for concepts that deserve formalization — (3) is genuinely useful, and ARCO has no objection to it in that role.

As a *governance principle* it lets failures decide what gets rigor, which is the wrong order for a system whose entire purpose is answering a high-consequence question before the build is shaped around a guess (`README.md`, opening). ARCO's posture is the opposite and is written down in advance: F5 (source documents don't directly become reality — human adjudication *is* the warrant), F6, and `LIMITATIONS.md` §3.9, which discloses that Gate 1 is ARCO's own evidential addition and that the resulting error runs in the **under**-classification direction. That is a decision about which way to be wrong, made and published before an answer ships. "Wait for the agent to be visibly confused" cannot produce that disclosure, because the systems that matter are the ones where confusion is not visible.

## What ARCO does take from the post

Two points are worth acting on, and one is already load-bearing here:

- **Annotations are a correction surface, not decoration.** *"Every description field in your dbt model or metric store is now being read by an LLM. Write accordingly."* ARCO's equivalent is its `rdfs:comment` / `skos:definition` / `skos:scopeNote` layer — e.g. `AnnexIIITriggeringCapability` is annotated in-file as a regulatory grouping class rather than a discovered universal (`LIMITATIONS.md` §3.2). Those annotations should be written for a model reader as well as a human one.
- **ARCO's MCP server is a context-injection boundary.** `mcp/arco_mcp.py` is where a model meets ARCO's commitments, and the honest scoping is already disclosed: an LLM calling the HermiT tool *"gets a bounded single-fixture assurance signal unless it explicitly runs multiple calls"* (`LIMITATIONS.md` §7.5, line 334). That is the correct shape — the model consumes a determinate, re-derivable result and is told the bound; it does not supply the semantics.

## The reformulation

> Model to the level of semantic commitment required by the decisions, integrations, and inferences the system must support.

This keeps the minimalism and drops the overreach. It does not make the model's prior the default semantic authority, and it scales the work to consequence rather than to detected disagreement.

The corollary for ARCO specifically: **the delta that matters is between the regulation's commitments and ARCO's encoding of them — not between a model's prior and ARCO's labels.** The reasoner, the fixtures, the adversarial decoys, and the HermiT cross-check all measure that first delta. None of them are measuring the second, and nothing in ARCO should start.

## What would change this position

Stated so it can be challenged rather than restated:

- A method that detects silent divergence (the plausible-but-wrongly-grounded case, not the visibly-confused case) at a measured rate, on a pair like verification/identification, without the distinction being supplied in advance. That would rehabilitate (2).
- A version-pinnable, inspectable artifact extracted from a model's prior, with stable identifiers and declared entailments, that a second implementation can re-derive. That would make "latent ontology" more than a metaphor.
- An LLM-mediated path that fails closed on a category error the way `test_ice_subfamily_trap.py` pins — refusing to emit rather than answering fluently. That would narrow the gap in §3.

Absent those, F4 stands: LLMs upstream of adjudication, never inside classification.
