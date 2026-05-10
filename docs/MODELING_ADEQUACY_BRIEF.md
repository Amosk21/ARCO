# ARCO Modeling Adequacy Brief

**Date:** 2026-05-10  
**Scope:** ARCO at current reference scope: EU AI Act Annex III 1(a) and 5(b).  
**Status:** This is the durable synthesis of the 2026-05-10 Beverley-style review pass. The phase files under `runs/loop/2026-05-10_beverley-procedure/` are method residue, not canon.

## Question

Is ARCO's current `document -> reviewed commitment -> BFO/CCO model -> entailment -> answer` chain coherent, load-bearing, and reviewable?

## Short Verdict

| Layer | Verdict | Meaning |
|---|---|---|
| Modeling core | Sound at toy scope | The load-bearing terms fit the BFO/CCO buckets without obvious category mistakes. |
| Reasoning | Load-bearing | Classification changes when dispositions, intended-use specs, process types, or role designations change. |
| Input provenance | Not yet demonstrated | Fixture TTL exists, but the source-packet -> evidence-ledger -> RDF commitment loop still needs the kiosk demo. |
| Output provenance | Known-broken, tracked | The v1 emitter still mixes graph-backed values with Python-composed values; `output_manifest_v2.yaml` and `test_output_provenance.py` are the repair contract. |

## Method Boundary

This brief draws from a local-canon Beverley-style pass:

- Design Pattern lectures for domain/CQ/class/relation/disambiguation/design-pattern procedure.
- The `amosk21/Ontology-Tradecraft` fork at commit `89df996` for engineering-rubric checks.
- ARCO TTL, SHACL, SPARQL, tests, `README.md`, `LIMITATIONS.md`, and `OPEN_PROBLEMS.md`.

It does **not** claim full fidelity to every Beverley course, video, or repository. Missing canon remains a research gap, not a hidden authority claim.

## Story Diagram

```mermaid
flowchart TB
  classDef source fill:#fff7ed,stroke:#c2410c,color:#431407
  classDef graph fill:#e0f2fe,stroke:#075985,color:#082f49
  classDef bfo fill:#ecfdf5,stroke:#047857,color:#022c22
  classDef reason fill:#fef9c3,stroke:#a16207,color:#3f2a00
  classDef output fill:#f5f3ff,stroke:#6d28d9,color:#2e1065
  classDef human fill:#fee2e2,stroke:#b91c1c,color:#450a0a,stroke-dasharray:5 4

  CDO["CDO question<br/>Does this system satisfy ARCO's encoded Annex III conditions?"]:::human
  DOC["Source packet / documentation<br/>not itself a graph commitment"]:::source
  LEDGER["Evidence ledger<br/>human adjudicates what the source licenses"]:::source
  RDF["Reviewed RDF commitments<br/>fixture triples"]:::graph
  BUCKET["BFO/CCO bucket assignment<br/>bearer, disposition, ICE, process, role, fiat"]:::bfo
  AXIOM["OWL defined classes<br/>Gate 1 capability + Gate 2 prescribed process + Gate 3 designated role"]:::reason
  CLOSURE["Reasoned graph<br/>OWL-RL closure + HermiT cross-check"]:::reason
  WITNESS["SPARQL / SHACL witnesses<br/>query the reasoned graph and validate structure"]:::graph
  CERT["Answer / certificate<br/>graph-backed values + run metadata + labeled documentary text"]:::output
  LIMITS["Refusals and limits<br/>Article 6(3), Article 5 routing, runtime/site/temporal scope"]:::human

  CDO --> DOC
  DOC -->|"licenses, does not assert reality by itself"| LEDGER
  LEDGER -->|"human-reviewed promotion"| RDF
  RDF --> BUCKET
  BUCKET --> AXIOM
  AXIOM --> CLOSURE
  CLOSURE --> WITNESS
  WITNESS --> CERT
  CERT --> LIMITS
  LIMITS -.->|"hard questions return to human review"| CDO
```

The core discipline is: documents license reviewed commitments; commitments are modeled in BFO/CCO-shaped RDF; the reasoner answers over the graph; the certificate must say which values are graph-backed, which are run metadata, and which are documentary disclosure.

## What ARCO Knows

ARCO knows only what follows from the reviewed graph and its axioms.

- `:AnnexIII1aApplicableSystem` is entailed when all three 1(a) gates hold.
- `:AnnexIII5bApplicableSystem` is entailed when all three 5(b) gates hold.
- `:HighRiskSystem` is a Gate-1 latent-risk flag, not the legal high-risk classification.
- Verification-only biometric capability does not satisfy the biometric-identification gate under current commitments.
- HermiT and OWL-RL agreement is the cross-reasoner check for certificate-grade fixtures.

## What ARCO Merely Reports Today

The v1 output layer still reports some values that are not graph-backed:

- `ALL CHECKS PASSED` style aggregation hides constituents on non-applicable runs.
- Determination IRIs can be hardcoded rather than selected from the run graph.
- Some evidence rows use `LIMIT 1` without deterministic selection.
- Article 6(3) derogation wording is documentary scope text, not an entailment.

These are not modeling-core failures. They are output-provenance failures tracked in `OPEN_PROBLEMS.md` L4 and governed by `03_TECHNICAL_CORE/scripts/output_manifest_v2.yaml`.

## What ARCO Refuses To Claim

ARCO does not currently claim:

- Article 6(3) derogation evaluation.
- Article 5 prohibited-practice routing for real-time RBI in public law-enforcement contexts.
- Provider/deployer obligation entailment.
- Runtime monitoring, deployment-site facts, temporal-region modeling, or substantial-modification tracking.
- Annex III categories beyond 1(a) and 5(b).
- That source documents directly "become reality."

## Human-Loop Modeling Questions

These questions need explicit human judgment before the model is trusted at a broader scope:

1. **Process token vs prescribed process kind:** should Gate 2 continue to reference bare process tokens, or should it move fully to prescribed process kinds to avoid fake occurrent witnesses?
2. **Concretization boundary:** which ICEs need explicit bearers or `cco:is_tokenized_by` triples, and which can remain modeled as information artifacts without bearer particulars in v1?
3. **Verification vs identification:** is an explicit `owl:disjointWith` between `:RemoteBiometricIdentificationProcess` and `:BiometricVerificationProcess` required now, or only once a test or fixture makes it load-bearing?
4. **Provider vs deployer roles:** should `:ProviderRole` and `:DeployerRole` be disjoint at the role-instance level, given that one organization can bear different roles for different systems?
5. **Cloud/SaaS bearer model:** how should ARCO model a system whose capability is realized across shared cloud infrastructure without inventing fictional hardware parts?
6. **Article 5 boundary:** when does the Annex III 1(a) path need to branch into prohibited-practice routing for real-time RBI?
7. **Source authority:** what evidence tier is sufficient to promote a source sentence into a reality-side disposition commitment?

For the operational interview script, use `docs/COMPETENCY_QUESTIONS.md`. That
file turns these hard questions into CQ0-CQ17, from scoping and source evidence
through BFO/CCO commitments, entailment, validation, output receipts, and
explicit refusals.
8. **Certificate authority:** for each output field, is it graph-backed, run metadata, or documentary text?

These are the questions that keep the graph honest. If a proposed change does not answer one of them or close a row in `OPEN_PROBLEMS.md`, it should wait.

## Promotion Rule

Raw audit artifacts promote only if they do at least one of the following:

1. name a concrete code, TTL, SPARQL, SHACL, or test defect;
2. clarify one real modeling decision;
3. become a test or query;
4. directly help the source -> commitment -> entailment -> answer demo.

Everything else remains method residue.

## Next Concrete Move

The next proof move is still `OPEN_PROBLEMS.md` L1.1: the kiosk evidence-ledger demo.

That demo shows the missing first mile:

`source packet -> evidence ledger -> reviewed RDF -> reasoner non-entailment -> honest answer`

The output-provenance work then makes the final certificate honest enough to carry that story.

## Raw Review Sources

The raw phase files live under `runs/loop/2026-05-10_beverley-procedure/`:

- `phase0_canon_inventory.md`
- `phase0_addendum_tradecraft.md`
- `phase1a_modeling_spine.md`
- `phase1b_engineering_rubric.md`
- `phase2a_qa_audit.md`
- `phase2b_cdo_synthesis.md`
- `phase3_traceability_pack.md`
- `phase4_decision_register.md`

Read this brief first. Read the phase files only when auditing the derivation.
