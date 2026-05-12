# Modeling Decisions — Diagram Set

This folder holds the canonical visual artifacts for ARCO's modeling decisions and value chain. The diagrams are tested against the actual technical core (TTL, SPARQL, SHACL, Python), against the active register at `OPEN_PROBLEMS.md`, and against the project's stated goals at `CLAUDE.md`. Every load-bearing claim in a diagram cites the file or line it rests on.

## What's in the folder

| File | What it answers | When to update |
|---|---|---|
| `value_chain.md` | What is the end-to-end path from a source document to an honest certificate, and which BFO/CCO/RO/IAO relation connects each pair of nodes? | A new layer lands in code, an existing layer changes shape, or a new fixture exercises a path that wasn't visible before. |
| `seven_buckets_status.md` | What does ARCO populate in each of the seven BFO modeling buckets, and what is in progress or deliberately scope-cut? | A bucket gains a populated instance type, an in-progress row lands, or a scope cut is revised. |
| `three_gate_classifier.md` | What is the OWL axiom shape for Annex III applicability, and how does it relate to the latent-risk flag? | A new Annex III category is added, a gate's axiom shape changes, or the PRIMARY / LATENT-RISK FLAG bifurcation is refactored. |
| `decisions_justification_map.md` | For every load-bearing modeling decision in ARCO, what is the plain-English rationale and where does its justification live in the canonical files (CLAUDE.md, LIMITATIONS.md, OPEN_PROBLEMS.md, TTL rdfs:comment, BFO/CCO canon)? | A new modeling decision lands, an existing decision is refactored, a LIMITATIONS section is renumbered, or a Global Invariant in CLAUDE.md is added or modified. |

## Status framing used in the diagrams

The diagrams describe ARCO as it actually is, not as it might be. Three statuses are used:

- **POPULATED** — the artifact is present and load-bearing in the current graph; the pipeline exercises it on at least one fixture; the entailment or audit it supports fires.
- **IN PROGRESS** — the artifact is spec'd in `OPEN_PROBLEMS.md`, the canon-grounding is verified, the modeling decision is locked, but the code or graph commitment has not yet landed. The diagram shows the artifact with the in-progress visual treatment so a reader can tell what is real today from what is pending.
- **SCOPE CUT** — the artifact is deliberately not modeled, disclosed at `LIMITATIONS.md` with rationale. Drawing it would overcommit. The diagram shows it as a refusal, not as a gap to be closed silently.

The diagrams avoid the binary "active / gap" framing because reality has gradations and the discipline rules in `CLAUDE.md` (collapse, minimal cut, evidence-to-commitment policy) reward honest staging over aspirational pictures.

## How a diagram in this folder is built

Each diagram file follows the same shape:

1. **Purpose** — one sentence on what the diagram answers.
2. **Mermaid diagram** — the visual artifact, with explicit class IRIs and relation IRIs on the edges (not generic prose labels).
3. **Verification table** — every node and every load-bearing edge cites the file path (and line where useful) it was verified against.
4. **Status notes** — which nodes are POPULATED, which are IN PROGRESS (with OPEN_PROBLEMS row number), which are SCOPE CUT (with LIMITATIONS section).
5. **What this diagram does NOT show** — explicit list of intentional omissions and where they live.
6. **When to update** — the trigger conditions for revising this diagram.

The pattern is the same as `output_manifest_v2.yaml` for output fields: every commitment has a citation back to the canon or the code that grounds it. A diagram in this folder is not allowed to introduce a class, relation, or status claim that doesn't trace to a verifiable source.

## Cross-references

These diagrams supersede the inline mermaid diagrams in `docs/_archive/MODELING_ADEQUACY_BRIEF.md` and `docs/_archive/MODELING_QUESTION_MAP.md` for the topics they cover. The two parent files now point readers here for the canonical pictures, and keep their own inline content focused on prose adequacy verdict and modeling-question worksheet respectively.

## Backtest discipline

Per `CLAUDE.md` Global Invariant 13 (canon version pinning) and the trust-test discipline established by the X.11 / Agent-C review patterns, every IRI cited in these diagrams has been checked against the pinned import file in `03_TECHNICAL_CORE/ontology/imports/`. CCO IRIs use the readable v1.7-2024-11-03 form. BFO predicate labels are verified against `bfo-2020.owl`. RO predicate hierarchies are verified against `ro_bot.owl`. If a future regeneration of the slim modules changes any cited IRI or hierarchy, the diagrams must be re-verified before continued use.

## Authority

These diagrams are TIER 1 visualization artifacts (matching the repo's documentary tier rules in `CLAUDE.md`). They are tested, citation-grounded, and update with code changes. Marketing diagrams, slide decks, and presentation material may simplify these but should not contradict them. If a presentation diagram says something these diagrams don't, the presentation is wrong.
