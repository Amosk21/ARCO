# ADR-002: Merge Decision — audit-arco-imports branch → main

_Date: 2026-03-19 · Status: ACCEPTED_

## Decision

Merge branch `claude/audit-arco-imports-RjcFZ` into `main`. Use it as the new truth-aligned baseline. Stop expanding it.

## What this branch changes vs. main

### Correctness fixes (non-discretionary)

| Defect on main | Fix on branch |
|---|---|
| `HighRiskSystem` bridge axiom accepts any `has_part` bearer — no `SystemComponent` requirement | Tightened to `System ∩ has_part some (SystemComponent ∩ has_disposition some AnnexIIITriggeringCapability)` |
| Gate 3 status derived from `reg_alignment_ok` (wrong SPARQL source) | Derived from actual gate evidence (`gate_evidence["gate3"]["uss_uri"]`) |
| Pipeline exits 0 on failure — CI silently passes broken runs | `sys.exit(1)` on `all_pass == False` |
| Dependencies unpinned (`rdflib`, `pyshacl`, `owlrl`) | Pinned to `rdflib==7.6.0`, `pyshacl==0.31.0`, `owlrl==7.1.4` |
| README links 3 files that are broken or missing | Fixed: canonical/archived doc structure with correct paths |
| No capability disjointness — a component could be typed as both biometric ID and creditworthiness | Pairwise `owl:disjointWith` on all three capability classes |
| BFO was labels only (local stubs) — no active semantics, no disjointness enforcement | Real BFO 2020 import; supertype chains and category disjointness are now machine-enforced |

### Structural improvements

- **Two-layer pass/fail separation.** Classification layer (OWL-RL + SHACL) and audit layer (SPARQL ASK) computed and reported independently. Matches the architectural invariant in CLAUDE.md.
- **Annex III 5(b) implemented.** Creditworthiness evaluation — second category with full three-gate entailment and cross-category isolation.
- **Multi-scenario regression tests.** 5 systems including adversarial cases (equivalency decoy, blank node ghost) that prove the reasoner does real OWL entailment.
- **Gate-removal and scenario tests wired into CI.** Both GitHub Actions workflows run them.
- **Certificate and HTML output say "ARCO ontology encoding of EU AI Act"** instead of implying ARCO *is* the Act.
- **Docs corrected:** "BFO-aligned ontology (CCO terms as local stubs)" replaces "BFO/CCO-grounded."

### Discretionary changes

- 5 non-canonical narrative docs moved to `90_ARCHIVE/NARRATIVE_DRAFTS/`. Content preserved, git history intact. README now distinguishes canonical from archived.
- `bfo_cco_alignment_audit.md` (321 lines) — records what the BFO import actually added and what the CCO gap is.
- `adr_001_alignment_end_state.md` — records the strategic import decision.

## Why merge

The strongest reason is not "it fixes bugs." It is:

**This branch reduces the number of ways ARCO can appear to work while being wrong** — about what the ontology enforces, what the output says, what the tests prove, and what the docs claim.

- `main` is easier to demo but harder to defend.
- This branch is heavier but more credible.

Given that ARCO's value proposition is deterministic, auditable, defensible classification, credibility is the more important metric.

## Why not main

`main` is simpler and smaller. Choose it only if the priority is the narrowest possible Sentinel-only proof of concept with the least moving parts. That choice comes with: weaker ontology semantics, weaker test coverage, no adversarial proof against pattern-matching criticism, more misleading docs, and broken README links.

## Non-blocking caveats

1. The diff is large (~2.6k insertions). Most of it is BFO 2020 OWL (1670 lines), alignment audit (321), test suite (169), adversarial TTL (169). Edits to existing files are surgical.
2. Untracked debug artifacts (`_main_snapshot/`, `_tmp_governance_patched.ttl`) remain. Harmless; add to `.gitignore` at convenience.
3. `ARCO_Pilot_Engagement_Scope.md` contains both a pilot scope and a second determination case. Archived whole. If revived later, split it.

## Stop-here boundary

After merge, the following are **in scope** for near-term work:
- Bug fixes to anything landed in this branch
- Keeping docs accurate if the pipeline changes
- Staged RO → IAO → CCO import per ADR-001 (when ready, not speculatively)

The following are **out of scope** until explicitly decided:
- New Annex III categories beyond 1(a) and 5(b)
- New outward-facing narrative documents
- Ontology refactoring beyond what is required by import steps
- Expanding the doc/agent instruction surface

The branch is the new baseline. It is not permission for more ontology sprawl.

## Related

- `docs/agent/adr_001_alignment_end_state.md` — BFO/CCO import strategy
- `docs/agent/bfo_cco_alignment_audit.md` — technical alignment audit
- `docs/agent/extension_protocol.md` — protocol for new Annex III categories
