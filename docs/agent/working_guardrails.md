# ARCO Working Guardrails

Use this file to stay aligned before making ontology, pipeline, or claim changes.
It is intentionally short. It is not a design memo, not a legal opinion, and not a rewrite plan.

## Why This Exists

ARCO work can drift in two bad directions:

1. **Collapse panic** — treating every interpretive move or audit finding as proof that the architecture is wrong
2. **Ontology sprawl** — treating every possible refinement, import, or alternative encoding as necessary progress

This file prevents both.

## Stable Working Truths

- ARCO is **not hollow**. The current architecture stands.
- ARCO's core value is **deterministic, traceable, design-time regulatory classification under ARCO's formal encoding**, not "replace law."
- The current two-tier structure is intentional and should be preserved unless a real contradiction is shown:
  - `HighRiskSystem` = latent structural / capability-based risk signal
  - `AnnexIII1aApplicableSystem` and `AnnexIII5bApplicableSystem` = fuller three-gate applicability classes
- Recent project improvements have mostly been **articulation and trust fixes**, not ontology redesign.
- Passing pipeline/tests are a hard baseline. Do not trade away a green baseline for speculative elegance.

## Primary User Concerns To Respect

- Hidden bad assumptions in ontology commitments
- Making changes that quietly weaken or distort the original model
- Getting pushed into ontology rabbit holes by over-analysis
- Losing the value proposition by tightening claims
- Having to defend modeling choices that cannot be explained simply
- Drifting away from the original EU AI Act modeling without noticing

Treat these as legitimate engineering constraints, not emotional noise.

## End Goal

Support a system that:

- engineers can trust
- engineers can explain
- auditors can inspect
- legal/compliance review can narrow and structure
- ontology/legal reviewers can challenge locally rather than dismiss globally

If a proposed change does not help one of those outcomes, it is probably not the right next move.

## Anti-Drift Rules

- Preserve the current architecture by default.
- Prefer documentation, traceability, and test-backed clarification over ontology surgery.
- Do not treat a possible alternative model as evidence that the current one is wrong.
- Do not let audits become commands. An audit is an input, not an instruction to rework.
- Distinguish carefully:
  - deliberate design choice
  - real gap
  - documented deferral
  - overclaim
  - contradiction

## Before Any Ontology Change

Do not change a load-bearing class, axiom, or modeling pattern unless all five are stated explicitly:

1. **Current behavior** — what the ontology currently entails and why
2. **Problem** — the exact legal, ontological, or runtime issue being fixed
3. **Proposed behavior** — what will change and what will stay stable
4. **Defense** — why the new choice is easier to justify than the old one
5. **Backtest plan** — which pipeline/tests/scenario checks prove no regression

If these cannot be stated clearly, do not change the ontology.

## What Counts As "Correctness" Here

Correctness does **not** mean:

- complete legal automation
- full dependency import
- no interpretation

Correctness **does** mean:

- current claims match current implementation
- ontology commitments are explicit and defensible
- outputs are reproducible
- tests catch regressions
- known gaps are documented instead of hidden

## Quick Triage For New Ideas

When a new idea appears, classify it first:

- **Keep as-is** — current design is deliberate and adequate
- **Document** — wording/traceability problem, not an ontology problem
- **Defer** — real issue, but not the highest-leverage next move
- **Change** — only if a real contradiction, trust failure, or repeated regression is shown

Default to `Document` or `Defer` unless strong evidence justifies `Change`.

## Scope Reminder

Near-term high-value work is usually:

- tighter claims
- better traceability
- clearer known limitations
- stronger test coverage
- cleaner auditor-facing explanation

Near-term low-value rabbit holes are usually:

- large ontology refactors without a demonstrated contradiction
- full dependency import "because serious ontology"
- renaming core classes to chase elegance
- broadening legal scope before stabilizing current trust boundaries

## One-Sentence Operating Principle

Make small, justified, test-backed moves that improve trust, explainability, and defendability without destabilizing ARCO's current architecture.
