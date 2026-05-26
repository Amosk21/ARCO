# ARCO Modeling Roadmap

**Status as of 2026-05-13.**

I'm using this document to give a public-facing picture of ARCO: what's actually working, what I'm in the middle of, and what I've deliberately cut from scope. The day-to-day fix register lives in `OPEN_PROBLEMS.md` (local-only); this file is the slower-moving summary, and I update it only when something has stabilized enough that it isn't going to flip again next week.

---

## What ARCO does today

ARCO is the EU AI Act Annex III classifier I've been building. You hand it a structured description of an AI system (its intended use, its hardware capability, the role of the people it affects), and it entails whether the system falls under Annex III 1(a) (remote biometric identification) or Annex III 5(b) (creditworthiness assessment).

Mechanically: the classification axioms are written as `owl:equivalentClass` `owl:intersectionOf` definitions with three gates (capability disposition, intended use, affected role) at `03_TECHNICAL_CORE/ontology/ARCO_governance_extension.ttl`. The reasoning runs against BFO 2020, RO 2025-12-17, IAO 2026-03-30, and CCO v1.7-2024-11-03 commitments under OWL-RL. SHACL runs after reasoning to catch documentation inconsistencies. HermiT (under OWL 2 DL) runs in CI as an independent second reasoner so I'm not trusting a single inference profile. Outputs are gated through a failing-by-design provenance contract (`output_manifest_v2.yaml`, `test_output_provenance.py`) that refuses to ship a value unless its source is either graph-backed (named SPARQL query), run-metadata (declared sources), or a labeled documentary block.

Seven fixtures drive this today: two production positives (Sentinel ID for 1(a), Credit Scoring for 5(b)), one negative control (Verification Kiosk, a 1:1 biometric verification system that should not classify under 1(a), since verification is not identification per Recital 15, Recital 17, and the Annex III 1(a) operative carve-out (Article 3(36) defines biometric verification as 1:1; Article 3(41) defines the RBI system)), two adversarial fixtures (one decoy that injects an `owl:equivalentClass` to test whether the gates collapse on hostile input, one with an anonymous blank-node disposition to test whether the reasoner needs named individuals), and two flag-test fixtures (where all three Annex III gates are satisfied alongside an audit-layer flag like a provider-asserted derogation claim or a fraud-detection process token, to verify classification and audit don't bleed into each other).

The EU AI Act lists 8 high-risk Annex III categories. I've modeled 2. The other 6 are deferred and I'm honest about that in `LIMITATIONS.md` §1.

---

## What I'm working on next

### Small PRs I'm shipping first

These are mechanical and the canon checks are done. Each has one precondition I want satisfied before it lands.

| PR | What it does | Precondition |
|---|---|---|
| **L2.8** | Renames `:CapabilityDisposition` to `:Capability` across 22 occurrences in 7 files. The parent stays at `bfo:0000016` Disposition (per X.11 and the formal capability definition in the Capabilities paper §4.2). I'm not adopting abi's `bfo:0000017` Realizable parent; abi is internally inconsistent on that point. | Sentinel-ID Invariant 7 forbids class deletes. The rename has to bridge via `owl:equivalentClass` for one cycle, not delete-and-rename. I want to verify the bridge step before shipping. |
| **X.12** | Documents the `cco:designates owl:hasValue` punning chain in `docs/agent/modeling_rules.md` and adds cross-reference comments at `ARCO_governance_extension.ttl:446-453, 532-535`. | None. The canon chain is verified. |
| **L3.4** | Replaces the Python `gate3_ok = bool(uss_uri)` predicate (`run_pipeline.py:819` and `:2069`) with a SPARQL ASK that mirrors the OWL axiom (caller-bound `?expected_role`). Adds a false-positive fixture (USS designates a non-`:NaturalPersonRole`) for regression. | Pair with L3.2 parameterization so the same predicate works across categories. |

### Modeling questions I checked and confirmed don't block

I had five modeling decisions queued under a "Foundation Map" precondition that I expected to slow down the next phase of work. I ran adversarial verification (sequential agents per decision, independent canon-grep backtest on the findings) and was honestly surprised by the result: none of them block the 7-fixture classification chain as it stands. They become status updates, scope disclosures, or future-work flags rather than open modeling holes. The senior-level catch in here is L2.2, which I think is worth flagging directly.

| Row | Where it actually stands |
|---|---|
| **L2.6** Capability Interest hookup | Non-blocking; the chain test passes without the interest hookup. The canonical relation is `cco:has_interest_in` (Agent -> Process, `runs/scratch/cco-v1.7/CommonCoreOntologiesMerged.ttl:1349-1361`), which matches the Capabilities paper: the interest holds toward the realization (a process), not toward the disposition, so range `Process` is the intended shape, not a defect. The open question is the modeling choice (relation-only vs minting an Interest Quality), not whether the property works. |
| **L2.7** Aboutness target shape | Does not change classification outcomes, but it is a real realist choice (what the regulatory ICE is about), not mere presentation. Partial C-multi already ships at the universal layer: each condition ICE is `iao:is_about` the capability, process, and role universals (`ARCO_governance_extension.ttl:175-189`; the triples moved here from the instance files on 2026-05-14). The open piece is the particular-system layer (B vs C-multi); until I pick, the row sits at `DISCLOSED-PENDING-CHOICE`. |
| **L2.9** Gate 3 role specification | Wish-list. No fixture currently misclassifies on the existing axiom. |
| **L2.10** Gate 2 use-purpose proxy | I had this framed wrong. `cco:prescribes` (`cco_bot.owl:435-444`, domain `DirectiveInformationContentEntity`) is the canonical CCO directive-intentionality property, and `:IntendedUseSpecification` already carries it (`ARCO_governance_extension.ttl:282-287`). It's not a "loose proxy" for something better; it is the thing. The row collapses to a documentation update. |
| **L2.2** ICE bearer property choice | Defers to L1.1 (the kiosk evidence ledger). The lesson from the reverted commit was source-warrant discipline, not the property choice. The candidate I was leaning on, `cco:is_tokenized_by`, is also wrong on its own terms: it's declared `owl:AnnotationProperty` (`runs/scratch/cco-v1.7/CommonCoreOntologiesMerged.ttl:193-196`), so it doesn't participate in OWL reasoning. It's also not present in the pinned slim module. |

### Modeling evidence work

| Row | What ships |
|---|---|
| **X.6** | I want to promote the Sentinel-1(a) bucket and property audit (currently at `runs/loop/2026-05-09_beverley-research/sentinel_1a_bucket_audit/10_phase4_consolidated_table.md`) into `docs/MODELING_VALUE_DEMO.md`. It's per-entity verification of every load-bearing axiom commitment against BFO, RO, IAO, and CCO; right now it's sitting in scratch. |
| **X.9** | Two new adversarial fixtures (entailed-without-determination, asserted-without-entailment) and the SPARQL queries that catch the misalignment cases. New manifest status `asserted_but_not_entailed`. |

### The actual load-bearing modeling work

| Row | What ships |
|---|---|
| **L1.1** | A programmatic per-triple evidence ledger for the kiosk fixture. The kiosk demo today carries a narrative ledger at `docs/kiosk_demo_v1/kiosk_demo.md:73-80`, but the path from source documents to reviewed RDF commitments isn't yet machine-readable per row. The triple shape is paired with L2.2 (the property choice for the bearer relationship). This is the one piece I think actually moves the project forward, and it's where my modeling energy is going next. |

---

## What I've cut from scope

These are deliberate choices I've made. Each one is also disclosed in `LIMITATIONS.md` so a reviewer can see the cut and the reason in the same place:

- 6 of 8 Annex III categories not modeled (LIMITATIONS §1).
- BFO Bucket 5 (Site) and Bucket 6 (TemporalRegion) not modeled. ARCO is a design-time classifier, so runtime spatial/temporal regions don't carry weight at the entailment layer. If I extend ARCO to monitor jurisdiction-specific deployment or substantial modification, these activate (LIMITATIONS §3.7).
- Provider-organization-to-ICE structural link not modeled (per PR #62).
- Source documents do not auto-promote to reality-side commitments. Promotion is rare, conditional, and human-adjudicated per `docs/EVIDENCE_TO_COMMITMENT_POLICY.md`. I've been deliberate about not letting extraction wire directly to instance TTL.
- Closed-world hardware-incapability claims for software-configurable systems are forbidden. EU AI Act Annex III 1(a) keys on the "intended to be used for biometric verification" language present in Recital 15, Recital 17, and the Annex III 1(a) operative carve-out, not on what the hardware in isolation can do. Article 3(36) supplies the technical 1:1 verification definition (LIMITATIONS §3.5).

---

## Where to start reading

If you want to verify the picture above against the repo:

1. `README.md` for current state and the active-changes table.
2. `LIMITATIONS.md` for the disclosed scope cuts and known debt.
3. `docs/MODELING_ADEQUACY_BRIEF.md` for whether I think the source-to-RDF-to-reasoned-graph chain hangs together.
4. `docs/COMPETENCY_QUESTIONS.md` for the CQ0 through CQ17 modeling spine.
5. `03_TECHNICAL_CORE/ontology/ARCO_governance_extension.ttl` for the three-gate axioms.

---

*This roadmap was drafted with AI assistance and reviewed against the pinned upstream canon files (BFO 2020, RO 2025-12-17, IAO 2026-03-30, CCO v1.7-2024-11-03). The claims here are mine; the verification methodology is documented at the row level in `OPEN_PROBLEMS.md`.*
