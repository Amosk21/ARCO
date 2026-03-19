# ADR-001: BFO/CCO Alignment End State

_Date: 2026-03-17 · Status: ACCEPTED_

## Context

ARCO imported BFO 2020 (2026-03-17). RO, IAO, and CCO remain as local stubs — IRI declarations with no domain, range, or chain axioms. The question: should the stubs become permanent local declarations (end state B) or temporary scaffolding for staged full imports (end state A)?

## Decision

**End state A: full import.** ARCO will progressively import RO → IAO → CCO after resolving known blockers for each. Local declarations are temporary scaffolding, not permanent architecture.

## Rationale

- Local declarations without source ontology axioms provide no machine enforcement — usage errors pass silently
- "BFO-aligned" with stub properties is not interoperable with other BFO-aligned systems
- The risks of full import (documented in `bfo_cco_alignment_audit.md` v2) are real but tractable in staged order

## Import Order and Blockers

| Step | Ontology | Blocker |
|------|----------|---------|
| Done | BFO 2020 | None — imported and verified |
| Next | RO | Lowest risk. Pin version, import, run pipeline |
| Then | IAO | `Surveillance_Run_001` is subject of `iao:0000136` but typed as Occurrent. Fix before import or IAO domain constraint creates Continuant/Occurrent disjointness violation |
| Last | CCO | `AnnexIII_Condition_Q1 cco:prescribes :RemoteBiometricIdentificationProcess` uses class IRI as individual. CCO range constraint would infer the class is a Process instance. Patch CCO imports to local files. Performance impact (~300k triples) |

## Consequences

1. Every local property declaration gets a comment: `# scaffold — replace on [RO|IAO|CCO] import`
2. Extension protocol (`docs/agent/extension_protocol.md`) must document that new property usage requires reviewing import-readiness
3. All outward-facing text distinguishes between "BFO class enforcement (real)" and "property layer (scaffolded)"

## Related

- `docs/agent/bfo_cco_alignment_audit.md` — full technical audit
- `docs/agent/extension_protocol.md` — Annex III category addition protocol
