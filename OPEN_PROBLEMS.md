# OPEN_PROBLEMS — ARCO active fix register

**Read this first.** This is the active fix register. Every PR ships against one or more rows here. If a proposed fix is not on this list, add a row before doing the work.

**Goal:** move ARCO from "reasoner-green demo" to a small, defensible design-time classifier:

`reviewed evidence -> RDF commitments -> reasoned graph -> honest output status -> inspectable answer`

Each change should make that chain clearer, shorter, or more trustworthy. If it only adds doctrine, diagrams, or code without closing a broken chain step, it is bloat.

**Status legend:**
- `OPEN` — known, not yet started
- `IN-FLIGHT` — work begun, not landed
- `BLOCKED` — waiting on a dependency
- `DISCLOSED` — documented as deliberate scope, not a defect (still listed here so future sessions do not re-litigate)
- `LANDED` — fix merged; row stays for one cycle for traceability

**Last reviewed:** 2026-05-10  
**Layer model:** L1 evidence adjudication / L2 ontology pattern / L3 reasoning / L4 output.  
**North-star chain:** source evidence -> reviewed RDF commitments -> BFO/CCO graph -> reasoned graph -> honest output -> inspectable answer. The current synthesis is `docs/MODELING_ADEQUACY_BRIEF.md`; the session-level CQ spine is `docs/COMPETENCY_QUESTIONS.md`. The old `runs/loop/2026-05-09_beverley-research/sentinel_chain_v0_with_gaps.md` file is historical detail until an auto-generated traceability diagram replaces it.

**Modeling orientation:** read `docs/MODELING_ADEQUACY_BRIEF.md` for the current adequacy verdict, `docs/COMPETENCY_QUESTIONS.md` for the CDO-question interview flow, then `docs/MODELING_QUESTION_MAP.md` before proposing individual ontology commitments.

---

## L1 — Evidence adjudication (the missing first mile)

| # | Problem | Where | Status | Fix | Acceptance |
|---|---|---|---|---|---|
| L1.1 | No evidence ledger exists for any fixture. Sentinel is hand-authored canonical TTL with no source-doc provenance per row. | `03_TECHNICAL_CORE/ontology/ARCO_instances_sentinel.ttl` (entire file) | OPEN | B5 — kiosk ledger v1 per `docs/EVIDENCE_TO_COMMITMENT_POLICY.md` | First ledger row authored for kiosk case; chain steps 1-3 cease being red blocks for at least one fixture |

---

## L2 — Ontology pattern (modeling debt)

| # | Problem | Where | Status | Fix | Acceptance |
|---|---|---|---|---|---|
| L2.1 | Bare process tokens lack participants, temporal region, realizer. `:Sentinel_RBIP_Process` typed only as `:RemoteBiometricIdentificationProcess` with no occurrent context. Violates BFO Process semantics. | `ARCO_instances_sentinel.ttl:61-63` | DISCLOSED + BLOCKED | B4 — Path Gamma: replace tokens with named IUS subkinds + extrinsic criteria. Disclosure: LIMITATIONS §3.7.a | HermiT regression test passes on all 6 fixtures; Gate 2 satisfies via IUS subkind, not bare token |
| L2.2 | `cco:is_tokenized_by` missing on ARCO-generated ICEs. Per Aboutness §1 / CCO §2.4, generated ICEs need a bearer particular pointing back to the file/run that emitted them. | `:HighRiskDetermination`, `:IntendedUseSpecification`, `:AssessmentDocumentation` (no annotation in any TTL) | OPEN | PR5 — in-graph annotation, NOT sidecar (the reverted commit `6349fd9` had wrong shape). Dual-PhD QA review required. | Every ARCO-generated ICE in a run carries a `cco:is_tokenized_by` triple to the run's certificate file as bearer |
| L2.3 | Citation strings live in `rdfs:comment` instead of `dc:source` on the ontology header. ~14 instances. Violates Beverley's own convention (verified from abi repo). | TTL files, scattered (see prior `PROGRESS.md` punch list at `runs/loop/2026-05-08_a_bplus/PROGRESS.md`) | OPEN | Citation scrub PR (mechanical) — bundles into PR1 or stands alone | Zero citation strings in `rdfs:comment` across `03_TECHNICAL_CORE/ontology/`; ontology header carries `dc:source` per file |
| L2.4 | No `:NaturalPersonRole` bearer instances minted; Gate 3 designates the universal via `cco:designates owl:hasValue`. | `ARCO_governance_extension.ttl:454-466` | DISCLOSED | Deliberate. Aboutness-only design (LIMITATIONS §3.1). Q9 held-closed in `modeling_decisions_queue.md`. | Stays disclosed. Do not re-litigate. |
| L2.5 | Component-level capability bearer (`:HardwareComponent` bears disposition) chosen over system-level (PNG showed system as bearer). | `ARCO_core.ttl:62-70` | DISCLOSED | LIMITATIONS §3.5 names this as deliberate traceability choice. PR1 tightens disclosure if needed. | Stays disclosed. |

---

## L3 — Reasoning / audit (partial gaps in the deductive layer)

| # | Problem | Where | Status | Fix | Acceptance |
|---|---|---|---|---|---|
| L3.1 | Gate 2 SPARQL underdeterministic. No `ORDER BY`, no category filter. Same fixture can produce different evidence rows across runs. | `run_pipeline.py:323-342` | DONE (A+ 2026-05-10) | PR4 — add `ORDER BY` (determinism) + category filter (correctness). Half-fix that does only one leaves bias live. | Same fixture produces same Gate 2 evidence across N runs; filter restricts rows to the fixture's category. CLOSED: inline SPARQL moved to `reasoning/select_gate_2_prescribed_process.sparql` with `ORDER BY ?ius ?process` and `FILTER(?process_class IN (:RemoteBiometricIdentificationProcess, :CreditworthinessEvaluationProcess))`. |
| L3.2 | `:NaturalPersonRole` hardcoded at FIVE loci across Python + SPARQL + SHACL. Gate 3 not parameterized by category. | `run_pipeline.py:354` (FILTER), `:371` (init), `:407` (else); `reasoning/check_intended_use.sparql:31`; `validation/assessment_documentation_shape.ttl:96-100` | OPEN | PR3 — parameterize all 5 sites by category | All 5 loci accept role per category; 5(b) and 1(a) both pass without role-IRI hardcoding |
| L3.3 | 5(b) gate-evidence has NO SPARQL. HTML emission carries hardcoded Python literals for capability/process/role. | `run_pipeline.py:549-551` (HTML emission) | DONE (PR #34, 2026-05-10) | PR4 — write `select_5b_gate_evidence.sparql`. Without it, PR3's parameterization does not help 5(b). | CLOSED: PR #34 (commit `6465675f`) replaced the three Python literals in `write_html_view` 5(b) branch with reads from `gate_evidence["gate2"]["process_type_label"]` etc. The existing parameterized helpers (Gate 1/2/3 SELECT files post-A+) are category-agnostic and system-scoped, so they return creditworthiness-shaped values for 5(b) systems. HTML view fields are now bound to graph-derived labels via the `gate_evidence` intermediate, not Python literals. |
| L3.4 | `gate3_ok = bool(uss_uri)` is a Python truth-predicate weaker than the OWL Gate 3 axiom (`cco:designates :NaturalPersonRole`). Fixing IRI loci without fixing this leaves Gate 3 weakened. | `run_pipeline.py:735` | OPEN | PR3 — replace `bool(...)` with SPARQL ASK that mirrors the OWL Gate 3 axiom | Python predicate matches axiom semantics; fixture without `cco:designates` triple fails Gate 3 even if `uss_uri` truthy |
| L3.5 | `test_gate_removal.py` covers Annex III 1(a) Sentinel only. No parallel coverage for Annex III 5(b) CreditScorer. Each 5(b) gate is independently load-bearing per the equivalentClass intersection but no regression test verifies it. Surfaced 2026-05-10 by Modeling Adequacy Brief. | `03_TECHNICAL_CORE/scripts/test_gate_removal.py:26-67` | OPEN | Mechanical: parameterize `INSTANCES`, `system_iri`, gate-removal triples, and expected-entailment classes; add 5(b) cases (capability disposition, IUS prescribes `:CreditworthinessEvaluationProcess` token, USS designates `:NaturalPersonRole`). | Removing each 5(b) gate triple in turn flips `:AnnexIII5bApplicableSystem` to False; test reports OK across both Sentinel and CreditScorer fixtures. |

---

## L4 PR Harness — operational discipline for output-emission PRs

Every PR closing an L4 row (or any field-emission cleanup) runs through this checklist BEFORE merge. This is the Critique + Conform stages of the AI-assisted ontology-engineering methodology made operational. Each rule exists because we have already had a real bug it would have caught.

0. **Consult canon first.** Before authoring a new SPARQL query, axiom edit, or modeling change, name which canon source(s) the decision is grounded in. Canon = `KB/00_INBOX_RAW/papers/` (Beverley CCO/Capabilities/Middle-Architecture, Smith papers, BFO2-Reference, Allemang Working Ontologist, Dougal Watt slides), `docs/agent/`, `runs/loop/2026-05-09_beverley-research/` and `2026-05-10_beverley-procedure/`. **If no canon clearly answers, STOP and ask the user, even in auto mode.** Modeling decisions are not routine. (Memory rule: `feedback_consult-canon-or-ask.md`)
1. **Names the OPEN_PROBLEMS row(s) it closes** in the PR body. Each PR closes at least one row.
2. **For each new or changed SPARQL query, lists the BFO/CCO/IAO/RO axiom path the query mirrors** in the PR body. The realist Critique-stage check made visible.
3. **Each new query has a per-fixture expected-answer test** added in `test_scenarios.py` (Sentinel for 1(a), CreditScorer for 5(b), VerificationKiosk for negative case).
4. **`test_output_provenance.py` violation count goes down or stays the same.** Up = regression, blocked.
5. **No new custom predicates.** Every property in the query namespace is from {BFO, RO, IAO, CCO} or `https://arco.ai/ontology/core#`.
6. **PR body short** per `feedback_pr-descriptions-short.md`. Bullet list of fixes; no test-plan tables; no rationale essays.
7. **Dual-PhD QA agent review** for any non-trivial ontology/SHACL/SPARQL/pipeline change per `feedback_dual-phd-qa-agent.md`.

If a step does not apply, the PR body says so explicitly with `N/A: <reason>`. Skipping a step silently is forbidden.

---

## L4 — Output / trust surface (synthesis without graph backing)

| # | Problem | Where | Status | Fix | Acceptance |
|---|---|---|---|---|---|
| L4.1 | `non_applicable_run` short-circuit force-sets `audit_pass = True`. Renaming `all_checks_passed` to v2 without removing this reproduces the lie under fresh field names. | `run_pipeline.py:1654-1655` | DONE (A+ 2026-05-10) | PR2 — remove force-set OR expose `applicability_status` as separate enum field so consumers disambiguate. Bundle with B1 schema. | Non-applicable run does not set `audit_pass=True`; consumers see distinct applicability vs. audit fields. CLOSED: force-True removed; `audit_pass = None` and `all_pass = None` on non-applicable runs; new `applicability_status` field (`applicable` / `not_applicable`) in summary.json and determination_packet.json. Schema bumped 1.2 → 1.3. |
| L4.2 | Hardcoded determination IRI `:HighRiskDetermination_001` exists as a graph node ONLY in Sentinel fixture. Runs against credit/verification/adversarial fixtures emit an IRI not asserted in their loaded graph. | `run_pipeline.py:1906` | DONE (A+ 2026-05-10) | PR5 — replace with SPARQL lookup against the run's reasoned graph; ties to L2.2 (`cco:is_tokenized_by`) | Determination IRI in output traces to a triple in the run's reasoned graph. CLOSED: new `reasoning/select_determination_node.sparql` SELECTs `?det rdf:type :HighRiskDetermination ; iao:0000136 ?system`; emitter binds result or null. Sentinel returns `:HighRisk_Determination_001`, CreditScorer returns `:CreditScorer_Determination_001`, Verification/Decoy return null, FlagTest returns its asserted IRI. Asserted-vs-entailment alignment is a separate concern tracked at X.9. |
| L4.3 | Headline strings composed as Python literals, not graph-derived. `PRIMARY ARCO CLASSIFICATION` and `LATENT-RISK FLAG` are templated format strings. | `run_pipeline.py:1703-1704` | DONE (A+ 2026-05-10) | PR2 — bind to graph-derived field per the G block discipline; bundle with B1 schema | Headline fields trace to a SPARQL query on the reasoned graph; manifest names which query. CLOSED: new `reasoning/select_primary_classification.sparql` binds class IRI list; `format_primary_arco_classification` and `format_latent_risk_flag` no longer compose Python qualifiers (`(ENTAILED, all three ARCO gates)` and `(Annex III Capability-Precondition Flag; ...; not the EU AI Act legal high-risk classification)` dropped). Headline value is now the pure class IRI; mode/scope text lives in separate fields. |
| L4.4 | `summary.json` v1.2 has 5 name/source mismatches: `latent_risk_class`, `primary_arco_classes`, `classification_mode`, `latent_risk_mode`, `entailment`. External consumers also key off old status strings. | `run_pipeline.py:1817-1840`; `mcp/arco_mcp.py`; MCP docs/tests; CI grep of `ALL CHECKS PASSED`; public demo/talk examples | OPEN | PR2 — schema v2 + deprecation window per B1 | Field names match their semantic source; legacy fields stay for one cycle with deprecation metadata; MCP docs/tests and CI grep are updated in same PR |
| L4.5 | No G/M/D field labels in any output. Cannot distinguish graph-derived from run-metadata from documentary-from-ledger. | All output files (certificate, summary, packet, HTML) | OPEN | PR2 schema v2 introduces labels; PR6 enforces them | Every output field labeled G or M or D; CI gate fails if unlabeled |
| L4.6 | No per-field source-query manifest. Text-pattern CI test would accept v2 G fields that are still Python composition. | `test_output_provenance.py` (does not exist yet) | OPEN | PR6 — manifest table embedded in B1 schema doc; runtime check that emitted G value matches a binding from the named SPARQL on the run's reasoned graph | CI gate written FIRST against current output (must FAIL); passes after PR2-PR5 land |
| L4.7 | Kiosk HTML gate-card section emitted a sentence that falsely concretized `:RemoteBiometricIdentificationProcess` for the verification kiosk. Root: `gate2_ok = intended_use_ok` at `run_pipeline.py:806` (variable name suggested Gate 2 typed-content satisfaction; the bound ASK is documentary-traceability per `reasoning/check_intended_use.sparql:5-12`); plus `or "RemoteBiometricIdentificationProcess"` Python literal fallback at `run_pipeline.py:816`. When `gate2_ok` was TRUE on the kiosk and the typed-evidence label was empty, the literal fired, producing "An Intended Use Specification prescribes the system for RemoteBiometricIdentificationProcess" — false against the loaded TTL. Determination_packet.json gate_2 status had the same scope-mismatch at `run_pipeline.py:2053`. Output-discipline defect; reasoner output was correct throughout. | `run_pipeline.py:806` (HTML variable binding), `run_pipeline.py:815-817` (three Python literal fallbacks), `run_pipeline.py:849` (HTML sentence template), `run_pipeline.py:2053` (packet writer) | DONE (2026-05-11) | (1) Rebind HTML-side `gate2_ok` to `bool(gate_evidence["gate2"]["process_type_uri"])` so the affirmative branch only fires when typed evidence exists. (2) Replace the three `or "<class IRI>"` Python literal fallbacks with non-concretizing placeholders. (3) Mirror the rebind for packet-side `gate_2.status` at the determination_packet writer. (4) Add regression test `test_kiosk_html_no_false_concretization.py` asserting kiosk HTML does not emit the Gate 2 affirmative phrase. (5) Wire the new test into `arco-smoke-test.yml` and `arco-demo.yml` so future regressions are caught in CI. | CLOSED: Kiosk HTML produces no Gate 2 affirmative sentence (negative branch fires under typed-evidence absence); packet gate_2.status is `NOT_SATISFIED` with empty evidence on the kiosk (parallel to gate_3 which already had this semantics); `test_kiosk_html_no_false_concretization.py` PASS and wired into both `arco-smoke-test.yml` and `arco-demo.yml`; the code shapes the `output_manifest_v2.yaml` forbidden-pattern entries were authored to catch (Python `or "<Sentinel-shaped-class-IRI>"` fallbacks at lines 815-817) no longer appear in `run_pipeline.py` (code-grep fact); 5/5 fixture pipeline runs continue passing per prior baseline. (Note: the manifest's forbidden-pattern regexes themselves have a trailing-`\b` issue that prevents them from matching the literals even pre-fix; tightening those regexes is out of scope for L4.7.) |

---

## Cross-cutting discipline

| # | Problem | Where | Status | Fix | Acceptance |
|---|---|---|---|---|---|
| X.1 | Reasoning-chain visualization is hand-drawn and drifts from code. North-star artifact is currently a markdown file (`sentinel_chain_v0_with_gaps.md`), not auto-generated. | `runs/loop/2026-05-09_beverley-research/sentinel_chain_v0_with_gaps.md` | OPEN | PR7 — `scripts/draw_chain.py` reads reasoned graph + emission code; CI compares output to canonical | Per-fixture chain artifact regenerable from a run; CI fails on drift |
| X.2 | CQ doc old contradictions were resolved by the 2026-05-10 v2 rewrite (`CQ0`-`CQ17`), but the new spine has not yet been cross-checked line-by-line against TTL/SPARQL/SHACL/pipeline surfaces, and the older `docs/ARCO_DSQs_and_Scope.md` draft may now drift from it. | `docs/COMPETENCY_QUESTIONS.md`; `docs/ARCO_DSQs_and_Scope.md` | PARTIAL | PR8 — doc-only cross-check: verify CQ0-CQ17 against current technical files, update or archive the older DSQ draft, and adjust LIMITATIONS cross-refs if needed. | CQ spine internally consistent; each CQ points to current technical artifacts; older DSQ doc either matches or is explicitly superseded; `05_cq_vs_technical_reality.md`-style check re-run if available. |
| X.3 | LIMITATIONS missing PNG-pattern disclosures. §3.7 PNG two-process conjunction; §6 Safety Component Role inference deferral; §7 Verification as BFO Process scope choice. | `LIMITATIONS.md` | OPEN | PR1 — three one-paragraph entries; documentation only | LIMITATIONS §3.7, §6, §7 carry the disclosures; cross-references to `runs/loop/2026-05-09_beverley-research/png_vs_arco_pattern_check.md` |
| X.4 | Low-confidence Haiku Tradecraft report can reintroduce fabricated authority (`50 rules`, `86% compliance`) if future agents read it as a real Beverley audit. | `runs/loop/2026-05-09_beverley-research/tradecraft_rules_extracted.md`; `tradecraft_compliance_check.md` | OPEN | PR1 — add low-confidence header or move to `low_confidence/`; cite `haiku_findings_audit_and_arco_design_pattern.md` Part A | Future sessions cannot treat Week5 as an independent rubric; decisions cite primary sources or repo facts |
| X.5 | Fixture-wide HermiT agreement claim is not locally reproducible on this Windows environment due temp cleanup `WinError 5`. | `03_TECHNICAL_CORE/scripts/hermit_cross_check.py`; `runs/loop/2026-05-09_beverley-research/adversarial_audit_2026-05-09.md` M9 | OPEN | PR6 or standalone tooling fix — robust temp handling + local/CI note | HermiT cross-check runs locally or the limitation is explicitly marked CI-only; no doc claims unsupported local reproducibility |
| X.7 | `docs/ARCO_explained.md:97` carries OWA-loose framing that implies documentation can override physical capability ("a device that physically can identify faces but is documented as a verification-only kiosk... is not an Annex III 1(a) system"). The OWA-honest version: "where identification capability is not asserted in reviewed commitments and verification capability is asserted, ARCO does not entail :AnnexIII1aApplicableSystem; whether underlying hardware could in principle identify is a separate question ARCO does not adjudicate." | `docs/ARCO_explained.md:97` | OPEN | Doc-only edit; bundle with other ARCO_explained.md cleanup if any; no behavior change | Sentence rephrased to OWA-bounded form; no implication that documentation overrides physical capability. |
| X.6 | Sentinel-1(a) bucket + property commitment audit missing. Before `docs/MODELING_VALUE_DEMO.md` can make outward-facing claims about BFO/RO/IAO/CCO interoperability, the Sentinel toy chain must be checked against both (a) the seven-bucket category framework and (b) property-level domain/range/intended-use commitments. Scope is Sentinel → Annex III 1(a) only: Sentinel TTL, governance TTL, SHACL, SPARQL, `run_pipeline.py`, and CQs served by that path. | `docs/MODELING_VALUE_DEMO.md`; `runs/loop/2026-05-09_beverley-research/sentinel_chain_v0_with_gaps.md`; Sentinel/gov/SHACL/SPARQL/Python files | OPEN | Four-phase no-sprawl audit: (1) inventory actual modeled entities/properties/CQs; (2) Smith/BFO bucket review; (3) Beverley/CCO property review; (4) adversarial synthesis into one consolidated table. Verdict vocabulary: `fix`, `disclose`, `out-of-scope`, `keep`, `queue`. Phase 1-3 files are scratch under `runs/loop/.../sentinel_1a_bucket_audit/` and are deleted or archived after synthesis. No standalone `PROPERTY_USAGE_AUDIT.md`. | One consolidated "Property + Bucket Discipline" table exists, preferably as a section inside `docs/MODELING_VALUE_DEMO.md`, covering each load-bearing entity/property in the Sentinel 1(a) CQ path with source commitment, ARCO usage site, verdict, and action. `MODELING_VALUE_DEMO.md` is not committed until this table grounds its interoperability/value claims. |
| X.8 | ARCO own TTLs (`ARCO_core.ttl`, `ARCO_governance_extension.ttl`, instance files) declare `owl:Ontology` but not `owl:versionIRI`. Manifest run_metadata field `ontology_version_iri` (per `output_manifest_v2.yaml:69-75`) cannot emit usefully today; a generic `SELECT ?versionIRI WHERE { ?o a owl:Ontology ; owl:versionIRI ?versionIRI }` returns BFO's imported version, not ARCO's. Deferred from A+ on 2026-05-10 to keep that PR scoped to leak fixes; flagged here so the manifest field is not silently abandoned. | `ARCO_core.ttl:10`, `ARCO_governance_extension.ttl:12`; `output_manifest_v2.yaml:69-75`; new `reasoning/select_ontology_version.sparql` (does not yet exist) | OPEN | Standalone PR after A+: (1) pick version scheme (date-based, semver, or release-tag) and document the choice; (2) add `owl:versionIRI` to `ARCO_core.ttl` and `ARCO_governance_extension.ttl`; (3) create `reasoning/select_ontology_version.sparql` constrained to the ARCO namespace; (4) wire `ontology_version_iri` field into the emitter. | ARCO's own ontology files carry `owl:versionIRI`; the new SPARQL returns ARCO's version (not BFO's imported one); `summary.json` emits the `ontology_version_iri` field for every fixture; scheme choice noted in `LIMITATIONS.md` or release notes. |
| X.9 | `:HighRiskDetermination` ICE alignment with entailment not checked, bidirectional. A fixture TTL could assert `?det a :HighRiskDetermination ; iao:0000136 ?system` for a system that is NOT entailed as `:AnnexIII1aApplicableSystem` or `:AnnexIII5bApplicableSystem` (asserted-without-entailment); conversely, a system could be entailed as Annex III applicable with NO determination ICE asserted (entailed-without-determination). `select_determination_node.sparql` correctly surfaces asserted ICEs per Smith/Ceusters Reality/Representation cut (ICE existence is documentary, independent of entailment truth) and per Beverley sibling-query pattern (Gate 2 and Gate 3 SELECTs report asserted IUS/USS contents without entailment-gating — `:HighRiskDetermination` is the same kind of ICE and follows the same emission discipline). The pipeline does not enforce alignment. Surfaced during A+ review on 2026-05-10; no fixture currently exhibits either mismatch direction. Complementary to L2.2 (`cco:is_tokenized_by` for determiner provenance — alignment-check + provenance-bearer together make the ICE layer real instead of just labeled). | new SHACL shape or new SPARQL ASKs in `03_TECHNICAL_CORE/reasoning/`; consumed at audit layer; `output_manifest_v2.yaml` negative_statuses (line 320+) | OPEN | Standalone PR after A+: (1) write `flag_determination_ice_without_entailment.sparql` for the asserted-without-entailment case AND `flag_applicable_system_without_determination_ice.sparql` for the entailed-without-determination case. (2) Add new manifest negative-status `asserted_but_not_entailed` (manifest currently distinguishes `absent_in_loaded_graph` from `not_entailed` but lacks the diagnostic mismatch status). (3) Surface as new audit constituent field `determination_consistency_check` enum: `aligned` / `asserted_without_entailment` / `entailed_without_determination` / `not_run`. (4) Do not modify the existing `select_determination_node.sparql` — that query correctly answers its own question (ARCO Invariant 2: SPARQL is audit, not classifier; folding entailment-gating into the emission SELECT would invert the invariant). (5) Consider bundling with L2.2 (same epistemic neighborhood) or landing X.9 first as the smaller cut. | Two new SHACL shapes (or named SPARQL ASKs) flag each mismatch direction; new fixtures exercise both cases; audit layer reports `determination_consistency_check`; manifest negative-status vocabulary expanded to include `asserted_but_not_entailed`; the CDO question "If a vendor submits a HighRiskDetermination for a system ARCO does not classify as Annex III applicable, what does ARCO report?" returns: ICE surfaced AND `determination_consistency_check = asserted_without_entailment`. |
| X.10 | A primary reference cited in `LIMITATIONS.md` points to a file that is not included in the public repo, so external readers (CDOs, auditors, regulators) following the citation hit a dead link. `LIMITATIONS.md:11` lists `docs/ARCO_DSQs_and_Scope.md` as Primary Reference #5 ("decision-support questions and scope"), but that file is excluded by `.gitignore:87`. Reasoning behavior unaffected; this is a presentation defect that surfaces only when someone outside the project tries to follow the citation. Surfaced 2026-05-11 during PR #42 adversarial review. | `LIMITATIONS.md:11`; `docs/ARCO_DSQs_and_Scope.md` (target file); `.gitignore:87` (where the file is excluded) | OPEN | Doc-only fix, two options to choose from: (a) include `docs/ARCO_DSQs_and_Scope.md` in the public repo by removing the `.gitignore` entry, after a content review confirms the file is appropriate for external readers; or (b) replace the citation with a reference to a document already published in the repo (for example `docs/COMPETENCY_QUESTIONS.md` if that file covers the same ground). Choice depends on whether the gitignored content is intended to be public-facing. | Every Primary Reference in `LIMITATIONS.md` resolves to a file present in the published repo. No external reader following a Primary Reference encounters a dead link. |

---

## Disclosed (not defects, listed to prevent re-litigation)

| # | Item | Where disclosed |
|---|---|---|
| D.1 | Component-level bearer (vs system-level) | LIMITATIONS §3.5 |
| D.2 | Reality/representation split | LIMITATIONS §3.6 |
| D.3 | Bare process tokens (Path Gamma is the fix, but design-time scope acknowledges debt) | LIMITATIONS §3.7.a |
| D.4 | Universal-designation via `cco:designates owl:hasValue` (avoids minting role-bearer fakes) | LIMITATIONS §3.1, modeling_decisions_queue Q9 |
| D.5 | Cross-reasoner gate + GhostSystem profile-divergence exclusion | LIMITATIONS §7.4 |
| D.6 | Gate 2 underdetermined output (sharpened wording) | LIMITATIONS §7.5 |
| D.7 | No Article 5 prohibition routing; no Article 6(3) derogation evaluation | LIMITATIONS §3, §7 |
| D.8 | No runtime monitoring, no substantial-modification tracking | LIMITATIONS §6 |
| D.9 | HighRiskDetermination ≠ legal high-risk determination by Articles 16-29 regulator | `ARCO_core.ttl:130-140` rdfs:comment, README, public claims doc |

---

## Held closed (do NOT solo-implement)

From `runs/loop/2026-05-09_beverley-research/modeling_decisions_queue.md`:

| Q | Why held |
|---|---|
| Q6 | Full aboutness chain on every static fixture ICE — museum risk |
| Q7 | Article 6(3) derogation as OWL consequence — legal interpretation not firm |
| Q8 | Annex III 5(b) fraud exclusion as OWL consequence — same reasoning |
| Q9 | Mint `:NaturalPersonRole` bearers — would manufacture witnesses |

---

## Sequenced PR plan (drives this register)

| PR | Closes rows | Move |
|---|---|---|
| PR1 | X.3, X.4, L2.3 (partial) | LIMITATIONS coherence + low-confidence report quarantine + citation scrub |
| PR2 | L4.1, L4.3, L4.4, L4.5 (intro) | Schema v2 + short-circuit removal + headline field provenance + external-consumer deprecation |
| PR3 | L3.2, L3.4 | NaturalPersonRole parameterization (5 loci) + `gate3_ok` strengthen |
| PR4 | L3.1, L3.3 | 5(b) gate-evidence SPARQL + Gate 2 `ORDER BY` + category filter |
| PR5 | L2.2, L4.2 | Determination ICE bearer pattern + `cco:is_tokenized_by` (dual-PhD QA review) |
| PR6 | L4.5 (full), L4.6, X.5 | Per-field source-query manifest CI gate + HermiT reproducibility hardening |
| PR7 | X.1 | Auto-generated reasoning-chain artifact |
| PR8 | X.2 | CQ doc + ARCO_DSQs_and_Scope coherence |

PR1-PR4 make the output honest. PR5 closes the generated-determination commitment. PR6-PR7 enforce the discipline. PR8 aligns the docs with the graph.

---

## Update protocol

- Every PR that lands updates the `Status` column for the rows it closes.
- New problems get a row before any fix work begins. Do not fix something not on this list — add the row first.
- Disclosed items stay listed (do not delete) so future sessions do not re-discover them as new defects.
- The header `Last reviewed` date bumps on each substantive review pass.
- Cross-reference entry-points: `docs/MODELING_ADEQUACY_BRIEF.md` (current adequacy verdict), `docs/COMPETENCY_QUESTIONS.md` (CQ0-CQ17 modeling spine), `docs/MODELING_QUESTION_MAP.md` (new-commitment checklist), `LIMITATIONS.md` (scope), and `CONSOLIDATED_DECISIONS_2026-05-09.md` / `sentinel_chain_v0_with_gaps.md` only as historical context when a current row points back to them.

---

## What this register does NOT replace

- **`LIMITATIONS.md`** — scope and deliberate non-modeling. Disclosure-side, not workstream-side.
- **`CONSOLIDATED_DECISIONS_2026-05-09.md`** — durable record of B-items + reasoning + reviewer convergences.
- **Audit files in `runs/loop/2026-05-09_beverley-research/`** — point-in-time findings.

This file is the **active fix register**. The other files are the durable context. Both are needed.
