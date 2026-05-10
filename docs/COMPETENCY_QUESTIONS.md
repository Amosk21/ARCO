# ARCO Competency Questions

Purpose: this file is the working question spine for ARCO modeling sessions. It is
not only a list of tests. It is the set of questions that must stay answerable if
ARCO is going to be a real BFO/CCO-aligned design-time classifier rather than a
pipeline that happens to print plausible results.

This file is session-level: use it when a CDO question, source packet, fixture,
or new case needs to become an answerable ARCO workflow. For one proposed term,
triple, relation, or certificate field, drop into `docs/MODELING_QUESTION_MAP.md`
as the per-commitment workbench.

Use this with:

- `docs/MODELING_ADEQUACY_BRIEF.md` for the current one-page story.
- `docs/MODELING_QUESTION_MAP.md` for the seven-bucket modeling checklist.
- `docs/EVIDENCE_TO_COMMITMENT_POLICY.md` for source-to-commitment rules.
- `LIMITATIONS.md` for scope cuts and disclosed non-claims.
- `OPEN_PROBLEMS.md` for queued fixes and human-session decisions.

The central chain is:

```text
CDO question
  -> source packet or reviewed documentation
  -> human adjudicated ontological commitment
  -> BFO/CCO graph commitment
  -> OWL entailment or non-entailment
  -> SHACL/SPARQL witness
  -> certificate field with receipt
  -> explicit refusal for what ARCO does not know
```

Every CQ below should make one part of that chain easier to draw, query, validate,
or explain.

## CQ Types

The local-canon Beverley-style procedure separates questions by job:

| Type | Job in ARCO |
| --- | --- |
| Scoping | Decide whether ARCO is allowed to answer the question at all. |
| Foundational | Decide what kind of entity is being modeled: material object, process, role, disposition, ICE, quality, temporal or spatial region. |
| Relation | Decide which BFO/RO/IAO/CCO relation is allowed to connect the entities. |
| Validation | Decide what query, shape, regression, or witness proves the commitment is doing work. |
| Output | Decide what the certificate may say, where the receipt comes from, and what must be refused. |

## DSQ Spine

These are the human-facing decision-support questions ARCO is trying to answer.
The detailed CQs below decompose them into modelable commitments.

| DSQ | Question | Current status |
| --- | --- | --- |
| DSQ-1 | Given reviewed design-time commitments about a system, does ARCO entail an EU AI Act Annex III applicability class in current scope? | Implemented for Annex III `1(a)` and `5(b)` fixtures. |
| DSQ-2 | Which modeled gate commitments caused the answer: capability, prescribed process, designated affected role, or category-specific equivalent class? | Partly implemented; v2 output provenance work is required for full certificate receipts. |
| DSQ-3 | What does ARCO know, what does it merely report from documentation, and what does it refuse to claim under OWA? | Conceptually defined; output layer and demo notes still need hardening. |
| DSQ-4 | What additional human modeling decision is required before a new source statement can become a graph commitment? | Defined by evidence policy and modeling question map; needs a compact interview flow. |

## Current CQ Spine

### CQ0 - Is the requested answer in ARCO scope?

Type: Scoping

Question: Is the user's question about design-time Annex III applicability for a
system described by reviewed commitments, rather than legal approval,
deployment permission, runtime behavior, or raw document extraction?

Expected answer pattern:

- Yes, if the question can be answered from structured RDF commitments within the
  current modeled categories: Annex III `1(a)` remote biometric identification
  and Annex III `5(b)` creditworthiness evaluation.
- No, or disclose, if the question asks for Article 5 prohibition routing, full
  provider/deployer obligation compliance, jurisdiction, runtime operation, or
  legal advice.

Current artifacts: `LIMITATIONS.md`, `README.md`, `docs/MODELING_ADEQUACY_BRIEF.md`.

Human question: What exact CDO question are we trying to answer in one sentence?

### CQ1 - What source licenses each reviewed commitment?

Type: Scoping + validation

Question: For every instance triple used in classification, what source packet,
document, or reviewed evidence row licenses the commitment?

Expected answer pattern:

- Each reality-side instance triple **must trace to** an evidence-ledger row.
  Today no fixture has a ledger; Sentinel, CreditScorer, and VerificationKiosk
  are hand-authored canonical TTL (`OPEN_PROBLEMS.md` L1.1). The kiosk demo is
  the next demonstration artifact and the proof-of-existence for this CQ.
- The ledger distinguishes explicit source claims, adjudicator commitments, and
  statements ARCO refuses to mint.
- Raw vendor text, LLM extraction, or marketing claims do not directly write
  reality-side RDF.

Current artifacts: `docs/EVIDENCE_TO_COMMITMENT_POLICY.md`; kiosk ledger is the
next demonstration artifact.

Human question: Which source statements are strong enough to license a
disposition, a process, a role, or only an information-side claim?

### CQ2 - What is the system, and what material bearer carries the relevant capability?

Type: Foundational

Question: What material entity is the system, what component is part of it, and
what component bears the disposition that matters for classification?

Expected answer pattern:

```text
System
  bfo:has_part some SystemComponent
SystemComponent
  ro:0000091 some CapabilityDisposition
```

Current artifacts: `ARCO_core.ttl`, `ARCO_instances_sentinel.ttl`,
`ARCO_instances_creditscoring.ttl`, `ARCO_instances_verification.ttl`.

Former CQ mapping: old CQ1 and CQ12.

Human question: Is this a physical device, hardware-software amalgam, cloud
service, document-only claim, or something ARCO currently refuses to model?

### CQ3 - Which capability disposition is licensed?

Type: Foundational + relation

Question: Does the source license a biometric identification capability, a
biometric verification capability, a creditworthiness evaluation capability, or
something else?

Expected answer pattern:

- Capabilities are modeled as dispositions, not functions, unless future evidence
  licenses design-intent etiology strongly enough to promote them.
- `BiometricIdentificationCapability` and `BiometricVerificationCapability` stay
  distinct and disjoint.
- A source saying "biometric", "face matching", or "AI" is not enough by itself.

Current artifacts: `ARCO_core.ttl`, `docs/MODELING_QUESTION_MAP.md`,
`docs/EVIDENCE_TO_COMMITMENT_POLICY.md`.

Former CQ mapping: old CQ1, CQ2, CQ3, CQ12.

Human question: What capability would still exist as a realizable disposition
before any runtime process occurs?

### CQ4 - What intended-use specification exists?

Type: Foundational + relation

Question: What information content entity records the intended use, and what
process does it prescribe?

Expected answer pattern:

```text
IntendedUseSpecification
  cco:prescribes some Process
```

For Annex III `1(a)`, the current modeled route uses the
`RemoteBiometricIdentificationIntendedUseSpec` subkind. For `5(b)`, the analogous
creditworthiness intended-use pattern must stay category-specific.

Current artifacts: `ARCO_governance_extension.ttl`,
`docs/MODELING_QUESTION_MAP.md`, `OPEN_PROBLEMS.md`.

Former CQ mapping: old CQ4 and CQ6.

Human question: Should Gate 2 continue to use a typed process token as a closure
witness, or should ARCO move to a cleaner "prescribed process kind" pattern?

### CQ5 - What process is prescribed, and is it runtime or design-time?

Type: Foundational + validation

Question: Is the graph talking about an intended or prescribed process, or about
an actual runtime process that occurred in the world?

Expected answer pattern:

- Current ARCO scope is design-time.
- Runtime events, deployments, dates, participants, and temporal regions are not
  minted unless a source licenses them and the model has an explicit scope path.
- The current process-token pattern is a known modeling decision, not a hidden
  claim that ARCO observed runtime behavior.

Current artifacts: `LIMITATIONS.md`, `OPEN_PROBLEMS.md`,
`docs/MODELING_ADEQUACY_BRIEF.md`.

Former CQ mapping: old CQ4 and CQ6, corrected.

Human question: For this source, are we allowed to assert an actual process
particular, or only an intended/prescribed process description?

### CQ6 - What use scenario designates the affected role?

Type: Foundational + relation

Question: What use-scenario specification exists, and what role universal does it
designate?

Expected answer pattern:

```text
UseScenarioSpecification
  cco:designates NaturalPersonRole
```

The role universal may be referenced directly. ARCO should not mint fake
role-bearer particulars just to satisfy a gate.

Current artifacts: `ARCO_governance_extension.ttl`, `LIMITATIONS.md`,
`docs/MODELING_QUESTION_MAP.md`.

Former CQ mapping: old CQ5.

Human question: Is the source describing a role kind, such as natural person,
provider, deployer, or employee, or a real individual bearer of that role?

### CQ7 - Does the system have a latent Annex III triggering capability?

Type: Validation

Question: Does OWL reasoning entail that the system is a `HighRiskSystem` because
some part bears an Annex III triggering capability?

Expected answer pattern:

- This is a latent-risk or Gate-1 style result, not the full Annex III category
  answer.
- It should be true for Sentinel and Decoy-style identification cases.
- It should be false for the verification kiosk under current commitments.

Current artifacts: `check_high_risk_inference.sparql`,
`ARCO_governance_extension.ttl`, `docs/MODELING_VALUE_DEMO.md`.

Former CQ mapping: old CQ1 and CQ12, corrected. Old CQ1 mixed Gate 1 with the
full three-gate category answer.

Human question: Is the source licensing a capability that belongs in the
triggering-capability union, or only a nearby non-triggering capability?

### CQ8 - Does Annex III 1(a) apply under current commitments?

Type: Validation

Question: Does the reasoned graph entail `AnnexIII1aApplicableSystem`?

Expected answer pattern:

Annex III `1(a)` applies only when all current modeled gates are satisfied:

1. The system bears a biometric identification triggering capability.
2. A documented intended use prescribes remote biometric identification process.
3. A use scenario designates the affected natural-person role.

Current artifacts: `check_annex_iii_1a_entailment.sparql`,
`test_gate_removal.py`, HermiT/OWL-RL cross-check tooling.

Former CQ mapping: old CQ2.

Human question: Which of the three gates is actually supported by evidence, and
which gate is merely being inferred because we chose a loose class?

### CQ9 - Does Annex III 5(b) apply under current commitments?

Type: Validation

Question: Does the reasoned graph entail `AnnexIII5bApplicableSystem`?

Expected answer pattern:

The creditworthiness category should be entailed for the CreditScorer fixture and
should stay isolated from biometric identification fixtures.

Current artifacts: `check_annex_iii_5b_entailment.sparql`,
`ARCO_instances_creditscoring.ttl`, HermiT/OWL-RL cross-check tooling.

Former CQ mapping: old CQ3.

Human question: What is the category-specific capability, process, and affected
role for a creditworthiness case, and does each have evidence?

### CQ10 - Why does the verification kiosk not trigger Annex III 1(a)?

Type: Validation + output

Question: Under reviewed commitments, why is Annex III `1(a)` not entailed for a
1:1 biometric verification kiosk?

Expected answer pattern:

- `BiometricVerificationCapability` is asserted.
- `BiometricIdentificationCapability` is not asserted.
- The two capability classes are disjoint.
- Gate 1 for `1(a)` requires identification, not verification.
- The result is OWA-bounded non-entailment, not proof that the device lacks every
  possible identification capability.

Current artifacts: `ARCO_instances_verification.ttl`,
`ARCO_core.ttl`, `docs/EVIDENCE_TO_COMMITMENT_POLICY.md`.

Human question: What exact source language licenses "verification only", and what
does ARCO refuse to conclude from silence?

### CQ11 - Is the entailment real, or just string matching?

Type: Validation

Question: Does classification still work when the instance data avoids obvious
class-name strings and relies on OWL semantics?

Expected answer pattern:

- Decoy-style fixtures classify through `owl:equivalentClass` or subclass
  propagation, not direct assertion of the final category type.
- Gate-removal and content-mutation tests break the entailment when a necessary
  condition is removed or changed.

Current artifacts: `ARCO_instances_adversarial_decoy.ttl`,
`docs/MODELING_VALUE_DEMO.md`, `test_gate_removal.py`.

Human question: What adversarial fixture would convince a skeptical reviewer that
the next modeled category is also doing semantic work?

### CQ12 - Is the submitted documentation structurally complete enough to assess?

Type: Validation

Question: Does SHACL validate that the required local documentation structures
exist before ARCO presents an assessment answer?

Expected answer pattern:

- SHACL checks structural completeness and local graph constraints.
- SHACL does not close the world and does not prove legal truth.
- Missing documentation should be reported as missing, not silently patched by
  Python defaults.

Current artifacts: `assessment_documentation_shape.ttl`, pipeline SHACL step.

Former CQ mapping: old CQ4, CQ7, CQ8.

Human question: Which missing fields should block assessment, which should warn,
and which are outside current scope?

### CQ13 - Can every answer be traced to a SPARQL witness?

Type: Output + validation

Question: For each certificate claim, is there a named SPARQL query or explicit
run-metadata source that produces the value?

Status: TARGET, NOT YET ENFORCED. `output_manifest_v2.yaml` is a draft contract;
`test_output_provenance.py` fails by design until the v1 emitter is brought into
compliance. The pipeline currently emits v1.2 output that violates the contract
in named ways.

Expected answer pattern (target, post-PRs B-E):

- Category answers, gate evidence, and determination nodes should be selected by
  deterministic queries.
- No certificate headline should be composed from hardcoded Python claim values.
- Queries that select one row must define ordering where multiple rows are
  possible.

Current violations (live):

- Python-literal headlines for `PRIMARY ARCO CLASSIFICATION` and
  `LATENT-RISK FLAG`: `run_pipeline.py:1703-1704`. `OPEN_PROBLEMS.md` L4.3.
- Hardcoded determination IRI `:HighRisk_Determination_001`:
  `run_pipeline.py:1906`. `OPEN_PROBLEMS.md` L4.2.
- `non_applicable_run` short-circuit force-sets `audit_pass = True`:
  `run_pipeline.py:1654-1655`. `OPEN_PROBLEMS.md` L4.1.
- Article 6(3) qualifier inlined into `annex_iii_1a` field value:
  `run_pipeline.py:1832`. `OPEN_PROBLEMS.md` L4.4.
- Gate 2 SPARQL lacks `ORDER BY` and category filter:
  `run_pipeline.py:323-342`. `OPEN_PROBLEMS.md` L3.1.
- No `select_5b_gate_evidence.sparql`; 5(b) HTML emission uses Python literals:
  `run_pipeline.py:549-551`. `OPEN_PROBLEMS.md` L3.3.

Closure: `OPEN_PROBLEMS.md` PRs B-E.

Current artifacts: `03_TECHNICAL_CORE/scripts/output_manifest_v2.yaml` (draft
contract), `03_TECHNICAL_CORE/scripts/test_output_provenance.py` (failing-by-
design enforcement harness).

Former CQ mapping: old CQ6, CQ7, CQ12 plus new v2 output contract.

Human question: For each certificate field a CDO will read, what is its
provenance today: graph-bound query, run metadata, or labeled documentary text?
For several fields the honest answer right now is "neither yet."

### CQ14 - What derogations, exclusions, or human-review flags are present?

Type: Scoping + output

Question: Does the graph contain a documented derogation or exclusion claim that
must be reported without being silently evaluated as pass/fail?

Expected answer pattern:

- Article 6(3) derogation claims and fraud-detection exclusion candidates are
  reported as claims requiring human/legal review unless ARCO explicitly models
  their decision criteria.
- ARCO must not collapse "claim exists" into "claim accepted".

Current artifacts: Article 6(3) and exclusion SPARQL queries, `LIMITATIONS.md`.

Former CQ mapping: old CQ9 and CQ10.

Human question: Is this a rule ARCO can evaluate, or only a claim ARCO can surface
for a human?

### CQ15 - What does ARCO refuse to claim?

Type: Output

Question: For this run, what is outside ARCO's evidence, model, or legal scope?

Expected answer pattern:

The certificate or demo note should explicitly refuse claims such as:

- legal approval to deploy;
- runtime behavior;
- exhaustive absence under OWA;
- Article 5 routing when not modeled;
- real source-document ingestion when using a hypothetical packet;
- complete provider/deployer obligation compliance.

Current artifacts: `LIMITATIONS.md`, `docs/MODELING_ADEQUACY_BRIEF.md`,
output-provenance manifest.

Human question: What would a reader be tempted to believe from the output that
ARCO has not actually proven?

### CQ16 - What modeling decision is required before adding a new class or fixture?

Type: Foundational + relation

Question: Does the proposed change answer the seven-bucket checklist and the
source-to-commitment policy before new ontology classes or instance triples ship?

Expected answer pattern:

For a new class, fixture, or category, record:

- entity bucket;
- parent BFO/CCO type;
- allowed relations;
- evidence requirement;
- entailment target;
- validation query or SHACL shape;
- explicit non-claims.

Current artifacts: `docs/MODELING_QUESTION_MAP.md`, `OPEN_PROBLEMS.md`,
`CLAUDE.md` local discipline rules.

Human question: What would make this modeled entity wrong, and what test would
catch that error?

### CQ17 - Does each gate remain necessary after refactor?

Type: Validation

Question: If any category gate or category-specific content value is removed or
mutated, does the entailment fail?

Expected answer pattern:

- Gate-removal tests pass for Annex III `1(a)`.
- CreditScorer needs symmetric gate-removal coverage before broader claims about
  fixture-wide gate necessity.

Current artifacts: `test_gate_removal.py`, `OPEN_PROBLEMS.md` L3.5.

Human question: Which gate is the weakest or least well-evidenced in the new case?

## Human Modeling Interview Flow

Use this as the live session script before new modeling work.

1. What exact CDO question should ARCO answer in one sentence?
2. Which current scope bucket is it in: `1(a)`, `5(b)`, evidence ledger, output, or out of scope?
3. What source statement licenses the first commitment?
4. Is the commitment reality-side, information-side, regulatory text, or output text?
5. If reality-side: what BFO bucket is it in?
6. If information-side: what ICE is it, and what is it about, prescribing, or designating?
7. What material bearer, if any, carries the capability?
8. Is the capability a disposition, role, function, quality, or something ARCO should refuse to type?
9. Is the process an intended/prescribed process or an actual runtime event?
10. What role universal or role bearer is involved?
11. What OWL entailment should follow if the commitment is correct?
12. What SHACL shape or SPARQL query should catch missing or malformed support?
13. What adversarial or negative fixture would prove this is not string matching?
14. What must the certificate say, and what must it refuse to say?

## Legacy CQ Corrections

This section records why the previous CQ framing changed.

| Former CQ | Current treatment |
| --- | --- |
| CQ1 component bearing triggering capability | Split into CQ2, CQ3, and CQ7 because `HighRiskSystem` is a latent Gate-1-style result, not the full three-gate category answer. |
| CQ2 Annex III 1(a) | Retained as CQ8. |
| CQ3 Annex III 5(b) | Retained as CQ9. |
| CQ4 intended use documented | Split into CQ4, CQ5, and CQ12 because intended-use ICEs, prescribed processes, and SHACL completeness are different questions. |
| CQ5 use scenario designates role | Retained as CQ6. |
| CQ6 prescribed process alignment | Folded into CQ4, CQ5, CQ8, and CQ13. |
| CQ7 assessment doc traceability | Folded into CQ1, CQ12, and CQ13. |
| CQ8 compliance obligation spec | Treated as structural documentation in CQ12 and scope-limited by CQ15. Full obligation compliance remains out of current scope. |
| CQ9 Article 6(3) derogation | Retained as human-review flag CQ14, not automated legal evaluation. |
| CQ10 fraud detection exclusion | Retained as human-review flag CQ14, not automated legal evaluation. |
| CQ11 ProviderRole inherence | Covered by CQ6 and CQ16; provider/deployer role details remain a modeling-decision area. |
| CQ12 latent-risk entailment | Retained as CQ7, with explicit distinction from Annex III category applicability. |

## Minimum Acceptance for a New Case

A new ARCO case is not modeling-complete until these are true:

1. CQ0 says the question is in scope, or CQ15 records the refusal.
2. CQ1 has an evidence-ledger row for every classification-relevant instance triple.
3. CQ2 through CQ6 place the system, capability, process, ICE, and role in the seven-bucket map.
4. CQ7 through CQ11 demonstrate that the reasoner changes answers for the right structural reasons.
5. CQ12 and CQ13 provide SHACL/SPARQL receipts.
6. CQ14 and CQ15 surface human-review flags and non-claims.
7. CQ16 records any new modeling decision before ontology expansion.
8. CQ17 has a regression or negative fixture showing the gates are necessary.

If a proposed change does not help answer one of these questions, it waits.
