# ARCO

**Assurance & Regulatory Classification Ontology**

> **Note.** ARCO is a research-grade applied ontology and reference pipeline. It currently encodes EU Regulation 2024/1689 (AI Act) Annex III categories 1(a) (remote biometric identification) and 5(b) (creditworthiness evaluation). The architecture is designed to generalize to other regulatory regimes; the implementation is intentionally bounded. ARCO produces structured evidence for human review and does not replace legal review. The encoded interpretation of the regulatory text has not been externally reviewed by qualified counsel or by the EU AI Office.

Companies are building AI systems without knowing whether those systems will satisfy the high-risk conditions of the EU AI Act. When that exposure surfaces after deployment, the costs are real: redesign, retraining, administrative fines under Regulation (EU) 2024/1689 Article 99 (up to 3% of worldwide annual turnover or €15M for high-risk operator obligations, up to 7% or €35M for Article 5 prohibited practices), forced withdrawal, and reputational damage.

ARCO moves the classification decision upstream. Before deployment, the pipeline tells organizations whether a structured description of a system satisfies ARCO's formal encoding of Annex III conditions, and exactly why.

The output is not a score, a confidence level, or an advisory opinion. Most AI governance asks what a system does. ARCO asks what a system formally is — its dispositions, the processes it is prescribed to participate in, and the role categories it affects — and entails the classification by formal logic from that structure. The result is a deterministic, audit-traceable assessment grounded in BFO/RO/IAO/CCO-aligned structure: same structured inputs, same classification, every run.

**TL;DR**
- ARCO tells you, before deployment, whether a structured description of your system triggers EU AI Act high-risk conditions per ARCO's formal encoding of Article 6 and Annex III, and exactly why. The architecture is designed to generalize to regulatory domains where obligations attach to capability, prescribed process, and affected role; the current encoding is EU AI Act-specific.
- Classifications are deterministic and audit-traceable: formal OWL-RL reasoning + SHACL validation + SPARQL queries over a BFO 2020-grounded ontology, with RO, IAO, and CCO loaded as ROBOT BOT-extracted slim modules per the OBO Foundry / ODK standard pattern (version-pinned, reproducible from seed files in the repo). No probabilistic scoring, no LLMs in the decision loop.
- From a fresh clone, install the Python dependencies and run `python 03_TECHNICAL_CORE/scripts/run_pipeline.py` from the repository root to produce a formal condition assessment certificate with a full evidence path from system components through capabilities to Annex III criteria.

**What's modeled (current scope)**

| Annex III category | Capability (Gate 1) | Prescribed process (Gate 2) | Affected role (Gate 3) |
|--------------------|---------------------|-----------------------------|------------------------|
| 1(a): Remote biometric identification | `BiometricIdentificationCapability` | `RemoteBiometricIdentificationProcess` | `NaturalPersonRole` |
| 5(b): Creditworthiness evaluation | `CreditworthinessEvaluationCapability` | `CreditworthinessEvaluationProcess` | `NaturalPersonRole` |

All three gates must be satisfied for category-specific Annex III applicability entailment. A system bearing only a biometric capability is **not** entailed as a creditworthiness system, and vice versa. Cross-category isolation is formally enforced by the ontology, not asserted by hand. `HighRiskSystem` remains a Gate 1 latent-risk flag, not the full category-specific output.

---

[![ARCO Demo Run](https://github.com/Amosk21/ARCO/actions/workflows/arco-demo.yml/badge.svg?branch=main)](https://github.com/Amosk21/ARCO/actions/workflows/arco-demo.yml) [![ROBOT Validation](https://github.com/Amosk21/ARCO/actions/workflows/robot-validate.yml/badge.svg?branch=main)](https://github.com/Amosk21/ARCO/actions/workflows/robot-validate.yml)

---

## Active modeling considerations

A small set of modeling choices in the current axioms are under active review. These are not announced changes; they are open questions documented as part of the artifact at the time of writing.

1. **`HardwareComponent` requires a `CapabilityDisposition` filler.** The current restriction (`HardwareComponent ⊑ has_disposition some CapabilityDisposition`) is correct for capability-bearing hardware but over-specified for non-capability hardware such as power supplies, mounting, or cabling. A possible refinement would split the class so the disposition restriction lives on a more specific subclass (for example, `CapabilityBearingComponent ⊑ HardwareComponent`); whether that refinement is worth the modeling cost is being considered.

2. **`OperationalProcess` requires realizing a `CapabilityDisposition`.** Same shape as (1). Maintenance, calibration, and startup processes involve the system but do not realize an AI capability. Whether to weaken the restriction or introduce a more specific subclass for capability-realizing processes is being considered.

3. **Cloud-hosted and pure-software AI systems are out of current scope.** The mereology requires every `:System` to have at least one material `:SystemComponent` part. This accommodates on-device and on-prem AI; cloud-hosted systems whose physical infrastructure is shared do not satisfy the restriction without fictional component instances. Whether to revise the mereology, or to scope cloud-native AI to a sibling class with its own modeling, is being considered.

4. **`bfo:0000051 has_part` between Information Content Entities.** The regulatory scaffold uses the generic mereological relation between ICEs (e.g., `:AnnexIII_List bfo:0000051 :AnnexIII_Condition_Q1`). CCO and IAO offer more specific properties for parts of information. Whether the generic property is the right choice for ICE-to-ICE parthood, or whether to migrate to a more specific information-parthood relation, is being considered.

---

## What organizations get

- **Regulatory clarity at design time:** know whether your system satisfies Annex III conditions before you build it, not after you deploy it
- **Inspectable evidence chain:** every classification traces from system components through capabilities and prescribed processes to the regulatory criteria encoded in the axioms. The structural correctness of the chain is verified end-to-end; the legal interpretation embedded in the axioms is the author's, and has not been externally reviewed by counsel.
- **Earlier visibility into classification triggers:** structural prerequisites for high-risk classification are identifiable while architectural changes are still cheap.
- **Repeatable, reproducible determinations:** same structured input, same classification, every run, with the entailment chain exposed and re-derivable from public axioms.
- **No probabilistic model in the determination path:** classification is OWL-RL entailment over hand-authored structured instances, not a confidence score. Regulators audit reasoning chains, not probability distributions.
- **Bounded scope: description-to-classification.** ARCO classifies systems described as structured RDF instances against the formal encoding. Authoring those descriptions (whether by hand, by form, or via upstream LLM-assisted extraction) is a separate problem and is not part of this pipeline.

---

## Proof: a real determination

```text
========================================================================
ARCO CONDITION ASSESSMENT CERTIFICATE
========================================================================
  SYSTEM:                  Sentinel_ID_System
  REGIME:                  ARCO ontology encoding of EU AI Act (Article 6 / Annex III)
  PRIMARY ARCO CLASSIFICATION:  AnnexIII1aApplicableSystem (ENTAILED, all three ARCO gates)
  LATENT-RISK FLAG:             HighRiskSystem (INFERRED, Gate 1 capability precondition only)
  TRIGGERING CAPABILITY:   Sentinel_FaceID_Disposition
  EVIDENCE PATH:
  Sentinel_ID_System -> Sentinel_FaceID_Module -> Sentinel_FaceID_Disposition

  [classification layer — OWL-RL entailment]
  SHACL:                   PASS
  ENTAILMENT:              PASS
  ANNEX III 1(a):          VERIFIED (ENTAILED)
  ANNEX III 5(b):          NOT APPLICABLE

  [audit documentation layer — SPARQL ASK on reasoned graph]
  TRACEABILITY:            PASS
  LATENT RISK:             DETECTED
  INTENDED USE:            PASS
  OBLIGATION:              PASS
  REG. ALIGNED:            PASS

  ENTAILED TRIPLES ADDED:  +19710

  Classification layer: PASS
  Audit layer:          PASS
========================================================================
```

This determination is **derived**, not asserted. If any category-specific gate were not present, the Annex III applicability class would not be inferred. The reference pipeline writes the supporting certificate, JSON summary, evidence bindings, and SHACL report to `runs/demo/`.

**Why so many entailed triples?** The `+19710` figure reflects the depth of the upper-ontology hierarchy ARCO grounds in. Most of those derived triples are housekeeping under OWL 2 RL semantics: subclass closure across BFO, RO, IAO, and CCO; inverse-property materialization (every `is_about` assertion produces its inverse triple); property-characteristic propagation; and domain/range inferences. The actually load-bearing classification triples are a small subset, including:

- `:Sentinel_ID_System rdf:type :HighRiskSystem` (entailed via the Gate-1 bridge axiom)
- `:Sentinel_ID_System rdf:type :AnnexIII1aApplicableSystem` (entailed via the three-gate `equivalentClass` axiom)
- `:Sentinel_FaceID_Disposition rdf:type :AnnexIIITriggeringCapability` (entailed via `rdfs:subClassOf`)
- A handful of inverse-aboutness triples supporting Gates 2 and 3

A regulatory determination is fundamentally a small number of bits of information ("does this system meet the conditions, yes or no, and which class does it instantiate"). The volume of derived triples is what allows downstream BFO-aligned consumers to reason over the same materialized graph without re-deriving the substrate.

---

## How it works

**Input:** A system description modeled as instances: components, roles, capabilities, intended use context.

**Process:**
1. The system's structure is encoded in a formal ontology grounded in [BFO](https://basic-formal-ontology.org/) (the same foundational ontology used across biomedical, defense, and industrial standards)
2. OWL-RL reasoning derives what the system is capable of and whether it meets the category-specific three-gate classification condition: capability (reality-side), prescribed process type (representation-side), and affected role category (representation-side). All three gates check specific content, not the existence of documentation alone.
3. SHACL validation enforces documentary completeness
4. SPARQL audit queries run on the reasoned graph to confirm that the right content is explicitly declared and that the law's process prescription aligns with the provider's documentation. These queries inspect what the reasoning produced; they do not produce the classification themselves.

**Output:** A formal condition assessment certificate with full evidence path: which component bears which capability, which Annex III condition it satisfies, and why.

**Independent verification:** A separate CI workflow runs a second validation pass using [ROBOT](https://robot.obolibrary.org/) (v1.9.10) and HermiT, a full OWL 2 DL reasoner, on every push to `main` and every pull request. This workflow is independent of the production pipeline and confirms three things. First, the ontology is OWL 2 DL conformant: the gate axioms — including the OWL inverse-property restrictions used in Gates 2 and 3, which let an axiom say "the system has, about it, an `IntendedUseSpecification` that prescribes a regulated process" rather than introducing a named inverse for `iao:0000136` — are valid under the OWL 2 Description Logic profile. Second, the ontology is consistent under a DL reasoner with no contradictions found. Third, the production OWL-RL reasoner and HermiT agree on all seven classification queries for the Sentinel-ID system: same input, same output, both reasoners. OWL 2 RL is a restricted fragment of OWL 2 DL, so the agreement check confirms RL is not producing classifications the full DL specification would reject or missing ones it would require.

The system is **agnostic by design**. New AI systems are evaluated by authoring new instance data against the same framework. The core ontology, validation rules, and classification logic do not change.

---

## Why three layers, not one

OWL, SHACL, and SPARQL look like alternative tools for the same job. They aren't. They answer different questions, and the regulatory determination case requires all three.

**OWL operates under the Open World Assumption.** What isn't asserted is unknown, not false. Reasoning over OWL adds new entailments because the world might contain facts that haven't been recorded. This makes OWL the right tool for **classification**: "is this system high-risk?" becomes a logical question with a derivable answer that the reasoner produces from axioms and asserted facts.

**SHACL operates under the Closed World Assumption.** A dataset either matches the shape or it doesn't. Reasoning is irrelevant; what matters is whether the record is structurally complete against the constraint. This makes SHACL the right tool for **documentary completeness**: given a determination must rest on specific evidence (an IntendedUseSpecification, a UseScenarioSpecification), SHACL checks the record for that evidence's structural presence.

**SPARQL queries the reasoned graph after both layers have run.** It doesn't entail; it inspects. This is the right tool for **audit**: pattern-match the post-reasoning graph for conditions worth human attention (derogation claims, fraud-exclusion candidates, regulatory alignment).

For regulatory determination, all three are required because three different audiences need three different artifacts:

- *"Is this system high-risk?"* — needs an entailed answer re-derivable from public axioms. **OWL's job.**
- *"Is the supporting evidence structurally complete?"* — needs a closed-world check that the record contains the required content. **SHACL's job.**
- *"Are there conditions warranting additional human review?"* — needs a pattern-match on the reasoned graph. **SPARQL's job.**

Remove any layer and a different audience loses the artifact they need: a complete record with no determinative power, a determination with no defensible supporting record, or answers without inspectable transparency.

The OWL-vs-SHACL choice some practitioners frame as a tooling decision is really an artifact-of-different-audiences distinction. Recent formal work — particularly Sirin et al., *"SHACL: A Description Logic in Disguise"* — shows the two formalisms are bridgeable, supporting the case for treating them as different layers of a single architecture rather than competing solutions.

---

## Why the approach is structural, not behavioral

Liability attaches to what a system **is able to do**, not only to what it happens to be doing. Modern regulation classifies by capability, not configuration.

ARCO treats capability as something that **resolves from structure**, traced from system components through dispositions to regulatory conditions. If the structural prerequisites for a regulated capability are not present, the capability does not exist for regulatory purposes. If they are present, the classification follows as a logical consequence.

This makes ARCO different from two adjacent categories of tool. **Post-hoc behavioral monitors** — red-teaming, content moderation, runtime policy enforcement — observe what a deployed system does. They cannot tell you whether a system *is* high-risk before it ships; they assume that classification has already happened. **Probabilistic scorers** — risk-rating LLMs, fine-tuned classifiers — produce confidence levels, not entailments. Regulators audit chains of reasoning, not probability distributions. ARCO produces the chain.

The classification is deterministic, traceable, and stable. It changes only when the system's structure changes.

---

## Foundational ontology versions

| Ontology | Version / release | IRI namespace used | How it's loaded |
|----------|------------------|--------------------|------------------|
| **BFO** | BFO 2020 (ISO/IEC 21838-2:2021) | `http://purl.obolibrary.org/obo/BFO_` | Full ontology loaded from `03_TECHNICAL_CORE/ontology/imports/bfo-2020.owl` |
| **RO** | OBO Relations Ontology release `2025-12-17` | `http://purl.obolibrary.org/obo/RO_` | ROBOT BOT-extracted slim module loaded from `03_TECHNICAL_CORE/ontology/imports/ro_bot.owl` |
| **IAO** | Information Artifact Ontology release `2026-03-30` | `http://purl.obolibrary.org/obo/IAO_` | ROBOT BOT-extracted slim module loaded from `03_TECHNICAL_CORE/ontology/imports/iao_bot.owl` |
| **CCO** | Common Core Ontologies release `v1.7-2024-11-03` (last release before the v2.0 IRI-namespace migration) | `http://www.ontologyrepository.com/CommonCoreOntologies/` | ROBOT BOT-extracted slim module loaded from `03_TECHNICAL_CORE/ontology/imports/cco_bot.owl`, plus a small set of local subsumption assertions in `ARCO_governance_extension.ttl` |

**BFO 2020** is the second edition of Basic Formal Ontology, standardized as ISO/IEC 21838-2:2021. ARCO uses the OBO Foundry numeric-ID namespace (`BFO_0000015`, `BFO_0000016`, etc.) that is definitive of this release. BFO is loaded as a full local file because it is small (~100 KB), ISO-standardized, and the authoritative grounding for everything else; this matches IAO's own pattern of full-importing BFO while extracting slim modules of any other dependency.

**RO**, **IAO**, and **CCO** are loaded as ROBOT-extracted slim modules using `--method BOT`, a syntactic locality variant. The seed term lists ARCO depends on are version-controlled in `03_TECHNICAL_CORE/ontology/imports/seeds/{ro,iao,cco}_seed.txt`, and the slim modules can be regenerated reproducibly from the pinned upstream releases. This is the OBO Foundry / Ontology Development Kit (ODK) standard pattern, used by Gene Ontology, the OBO Relations Ontology itself, and the hundreds of ODK-managed projects.

**ARCO subsumption assertions for CCO information-content classes.** CCO maintains its own information-content hierarchy in parallel to IAO's: in current CCO, both `cco:InformationContentEntity` and IAO's `iao:0000030` sit as siblings under `bfo:0000031` (Generically Dependent Continuant) rather than one being subordinate to the other. ARCO's `ARCO_governance_extension.ttl` contains two `rdfs:subClassOf` axioms (`cco:DirectiveICE rdfs:subClassOf iao:0000030`, `cco:DescriptiveICE rdfs:subClassOf iao:0000030`) that assert subsumption from CCO's directive and descriptive ICE classes into IAO's hierarchy. This is a deliberate parallel-subsumption choice ARCO makes to integrate the two information-content models for the directive/descriptive distinction the gate axioms depend on; it is not a fix for an upstream omission. The pinned CCO release (v1.7-2024-11-03) uses semantic IRIs and the class name `DirectiveICE`; current CCO v2.0 has migrated to opaque numeric IRIs and renamed the class to `PrescriptiveICE`. ARCO's encoding is correct against its pinned version; migration to v2.0 is tracked as a documented gap. The remaining CCO declarations in the file are redundant with the BOT-extracted module and are kept for in-file readability rather than logical effect.

### Why ROBOT BOT slim modules

Using `robot extract --method BOT` to pull slim, version-pinned modules is the OBO Foundry's standard pattern for depending on external ontologies. The choice rests on five practical points:

1. **Formal entailment-preservation guarantee.** BOT is a syntactic locality module variant (Cuenca Grau, Horrocks, Kazakov, Sattler 2007/2008): for any axiom α whose signature is contained in the seed signature Σ, the extracted module entails α iff the full upstream ontology does. This includes property characteristics (`FunctionalProperty`, `Transitive`, `Symmetric`), property chain axioms, inverse-of axioms, and `rdfs:domain` / `rdfs:range`. ARCO's gate axioms depend on these — particularly OWL inverse-property restrictions on `iao:0000136` — so this is the strict property the project needs.
2. **OBO Foundry / ODK convention.** The Ontology Development Kit, which scaffolds ~hundreds of OBO Foundry projects, hardcodes `module_type_slme: "BOT"` as default. Gene Ontology, OBI, ChEBI, and the OBO Relations Ontology itself all ship BOT-extracted slim modules for their dependencies. ARCO matching this convention shortens the trust chain for any reviewer fluent in OBO practice.
3. **MIREOT is legacy and unsafe for reasoning-critical projects.** ROBOT's own documentation states MIREOT "preserves the hierarchy of the input ontology (subclass and subproperty relationships), but does not try to preserve the full set of logical entailments." The documented MIREOT failure mode is silently dropping property typing and characteristic axioms. For a project whose headline product is OWL-DL reasoning correctness over inverse-property gate axioms, MIREOT is the wrong choice on principle and BOT is the right one.
4. **Reproducibility.** Each slim module is regenerable from a pinned upstream release using a single ROBOT command with a version-controlled seed file. The seed lists are in `03_TECHNICAL_CORE/ontology/imports/seeds/`. A reviewer auditing ARCO can re-run the extraction and verify byte-equivalent output.
5. **Operational scaling.** A pipeline run on Sentinel-ID with the BOT modules loads roughly 7,744 asserted triples and produces 27,454 post-reasoning (about 19,710 derived). The HermiT reasoning step in the ROBOT validation workflow runs in approximately seven minutes on the merged ontology. An earlier intermediate state of ARCO loaded the full upstream releases of RO and IAO, which took the HermiT step to thirty to forty minutes and was projected to grow to one to three hours when CCO was added; this is operationally noisy without adding any reasoning-correctness signal that BOT does not already provide. The full-import experiments are preserved in git history at PRs #24 and #25 and confirmed that the slim modules produce byte-identical classification outputs.

The conventional argument for full imports — single-hash audit traceability against published upstream releases — is recovered here by the seed-file plus version-pin pattern: the seed lists are version-controlled, the upstream releases are pinned, and the extraction tool (ROBOT v1.9.10) is pinned in CI. The audit story becomes "ARCO uses BOT-extracted modules of these specific upstream releases, regenerable from these seed files using this specific ROBOT command," which is a tighter and more reproducible claim than "ARCO uses these full upstream releases" because every step is mechanically verifiable.

---

## Orientation (5-minute entry point)

**1. Run the reference pipeline**
The quickest way to evaluate the project is to run the deterministic reference assessment.
→ [`run_pipeline.py`](03_TECHNICAL_CORE/scripts/run_pipeline.py)

**2. Inspect the core artifacts**
The implementation is intentionally small: ontology files, SHACL validation, SPARQL audit queries, and Python orchestration.
→ [`03_TECHNICAL_CORE/`](03_TECHNICAL_CORE/)

---

## Public repository scope

This repository is kept intentionally narrow: the public surface is the working ontology, validation/audit artifacts, executable pipeline, and CI configuration. Internal strategy notes, agent guardrails, sales drafts, generated run outputs, local virtual environments, and unreviewed concept diagrams are not part of the versioned source.

---

## Current scope and planned hardening

The current public implementation demonstrates ARCO on two EU AI Act Annex III categories: `1(a)` remote biometric identification and `5(b)` creditworthiness evaluation. The pipeline classifies structured RDF instance data; it does not ingest raw vendor documentation, inspect deployed systems, or issue legal approval to deploy.

Near-term hardening work is intentionally scoped:

- replace legacy concept diagrams with pipeline-accurate explanatory visuals
- add gate-removal regression tests for the `5(b)` creditworthiness path
- replace SPARQL placeholder substitution with bound system variables
- document the Gate 3 regulatory-aboutness encoding convention
- expand modeled Annex III categories only with corresponding ontology, SHACL, SPARQL, and regression coverage

---

## Getting started (run the reference pipeline)

### Requirements

- Python 3.10 or newer

### Fresh clone

```bash
git clone https://github.com/Amosk21/ARCO.git
cd ARCO
```

### Create a local environment and install dependencies

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

The virtual environment is local-only and intentionally not committed to the repository.

### Run the pipeline from the repository root

```bash
python 03_TECHNICAL_CORE/scripts/run_pipeline.py
```

The pipeline will:

1. Load ontology (core + governance extension) and instance data
2. Run OWL-RL reasoning to materialize entailments (7,744 asserted -> 27,454 post-reasoning, on the BFO + BOT-extracted RO/IAO/CCO + ARCO union)
3. Validate documentary completeness with SHACL
4. Run two layers of checks:
   - **Classification layer (OWL-RL):** SHACL conformance, `HighRiskSystem` latent-risk entailment, Annex III 1(a) three-gate entailment (the formal classification outputs)
   - **Audit documentation layer (SPARQL ASK on reasoned graph):** traceability, latent risk, intended use, obligation linkage, regulatory alignment (inspects declared documentary content and confirms it matches what the classification requires)
5. Emit a formal condition assessment certificate with evidence path
6. Write artifact files to `runs/demo/` (certificate, summary JSON, determination packet, evidence bindings, SHACL report, HTML view)

### Run in GitHub Actions

This pipeline also runs automatically in CI. Go to **Actions > ARCO Demo Run > Run workflow** to trigger it manually. The workflow uploads `runs/demo/` as a downloadable artifact.
