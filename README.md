# ARCO [Research Project]

**Assurance & Regulatory Classification Ontology Engine**

Companies are building AI systems without knowing whether those systems will satisfy the high-risk conditions of the EU AI Act and other regulatory frameworks. When that exposure surfaces after deployment, the costs are severe: redesign, retraining, fines (up to 6% of global revenue), forced withdrawal, reputational damage.

ARCO moves that risk decision upstream. It is a pre-deployment classification engine that tells organizations (before deployment, before sunk costs, before regulatory exposure) whether a system satisfies ARCO's formal encoding of Annex III conditions, and exactly why.

The output is not a score, a confidence level, or an advisory opinion. It is a deterministic, audit-traceable assessment grounded in formal logic and BFO/RO/IAO-aligned, CCO-informed structure: same structured inputs, same classification, every time.

**TL;DR**
- ARCO is a deterministic regulatory classification framework grounded in BFO 2020, with ROBOT-BOT-extracted slim modules of OBO Relations Ontology, Information Artifact Ontology, and Common Core Ontologies — the OBO Foundry / ODK standard pattern, version-pinned and reproducible from seed files in the repo. The current implementation demonstrates it against the EU AI Act: formal OWL-RL reasoning tells you, before you build, whether your system triggers high-risk conditions per ARCO's encoding of Article 6 and Annex III, and exactly why. The architecture generalizes to any regulatory domain where obligations attach to capability, structure, and role.
- Classifications are deterministic and audit-traceable: formal OWL-RL reasoning + SHACL validation + SPARQL queries over a BFO-aligned ontology, with no probabilistic scoring and no LLMs in the decision loop.
- From a fresh clone, install the Python dependencies and run `python 03_TECHNICAL_CORE/scripts/run_pipeline.py` from the repository root to produce a formal condition assessment certificate with a full evidence path from system components through capabilities to Annex III criteria.

Bounded working example. Currently models two EU AI Act Annex III categories (1(a) remote biometric identification, 5(b) creditworthiness evaluation). Architecture generalizes; implementation is intentionally small.

**What's modeled (current scope)**

| Annex III category | Capability (Gate 1) | Prescribed process (Gate 2) | Affected role (Gate 3) |
|--------------------|---------------------|-----------------------------|------------------------|
| 1(a): Remote biometric identification | `BiometricIdentificationCapability` | `RemoteBiometricIdentificationProcess` | `NaturalPersonRole` |
| 5(b): Creditworthiness evaluation | `CreditworthinessEvaluationCapability` | `CreditworthinessEvaluationProcess` | `NaturalPersonRole` |

All three gates must be satisfied for category-specific Annex III applicability entailment. A system bearing only a biometric capability is **not** entailed as a creditworthiness system, and vice versa. Cross-category isolation is formally enforced by the ontology, not asserted by hand. `HighRiskSystem` remains a Gate 1 latent-risk flag, not the full category-specific output.

---

[![ARCO Demo Run](https://github.com/Amosk21/ARCO/actions/workflows/arco-demo.yml/badge.svg?branch=main)](https://github.com/Amosk21/ARCO/actions/workflows/arco-demo.yml) [![ROBOT Validation](https://github.com/Amosk21/ARCO/actions/workflows/robot-validate.yml/badge.svg?branch=main)](https://github.com/Amosk21/ARCO/actions/workflows/robot-validate.yml)

## What organizations get

- **Regulatory clarity at design time:** know whether your system satisfies Annex III conditions before you build it, not after you deploy it
- **Audit-ready evidence:** every classification traces back through components, capabilities, and regulatory criteria with no gaps
- **Reduced regulatory exposure:** identify classification triggers while architecture changes are still cheap
- **Repeatable, defensible determinations:** same system description in, same classification out, every time
- **No probabilistic model in the determination path:** current assessments run on hand-authored structured instances; formal logic drives the classification

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

---

## How it works

**Input:** A system description modeled as instances: components, roles, capabilities, intended use context.

**Process:**
1. The system's structure is encoded in a formal ontology grounded in [BFO](https://basic-formal-ontology.org/) (the same foundational ontology used across biomedical, defense, and industrial standards)
2. OWL-RL reasoning derives what the system is capable of and whether it meets the category-specific three-gate classification condition: capability (reality-side), prescribed process type (representation-side), and affected role category (representation-side). All three gates check specific content, not the existence of documentation alone.
3. SHACL validation enforces documentary completeness
4. SPARQL audit queries run on the reasoned graph to confirm that the right content is explicitly declared and that the law's process prescription aligns with the provider's documentation. These queries inspect what the reasoning produced; they do not produce the classification themselves.

**Output:** A formal condition assessment certificate with full evidence path: which component bears which capability, which Annex III condition it satisfies, and why.

**Independent verification:** A separate CI workflow runs a second validation pass using [ROBOT](https://robot.obolibrary.org/) (v1.9.10) and HermiT, a full OWL 2 DL reasoner, on every push to main and every pull request. This workflow is independent of the production pipeline and confirms three things. First, the ontology is OWL 2 DL conformant: the gate axioms, including the anonymous inverse property expressions used in Gates 2 and 3, are valid under the OWL 2 Description Logic profile. Second, the ontology is consistent under a DL reasoner with no contradictions found. Third, the production OWL-RL reasoner and HermiT agree on all seven classification queries for the Sentinel-ID system: same input, same output, both reasoners. OWL-RL is a restricted fragment of OWL-DL, so the agreement check confirms RL is not producing classifications the full DL specification would reject or missing ones it would require.

The system is **agnostic by design**. New AI systems are evaluated by authoring new instance data against the same framework. The core ontology, validation rules, and classification logic do not change.

---

## Why the approach is structural, not behavioral

Liability attaches to what a system **is able to do**, not only to what it happens to be doing. Modern regulation classifies by capability, not configuration.

ARCO treats capability as something that **resolves from structure**, traced from system components through dispositions to regulatory conditions. If the structural prerequisites for a regulated capability are not present, the capability does not exist for regulatory purposes. If they are present, the classification follows as a logical consequence.

This makes ARCO fundamentally different from post-hoc tools that observe behavior or score risk probabilistically. The classification is deterministic, traceable, and stable. It changes only when the system's structure changes.

---

## Foundational ontology versions

| Ontology | Version / release | IRI namespace used | How it's loaded |
|----------|------------------|--------------------|------------------|
| **BFO** | BFO 2020 (ISO/IEC 21838-2:2021) | `http://purl.obolibrary.org/obo/BFO_` | Full ontology loaded from `03_TECHNICAL_CORE/ontology/imports/bfo-2020.owl` |
| **RO** | OBO Relations Ontology release `2025-12-17` | `http://purl.obolibrary.org/obo/RO_` | ROBOT BOT-extracted slim module loaded from `03_TECHNICAL_CORE/ontology/imports/ro_bot.owl` |
| **IAO** | Information Artifact Ontology release `2026-03-30` | `http://purl.obolibrary.org/obo/IAO_` | ROBOT BOT-extracted slim module loaded from `03_TECHNICAL_CORE/ontology/imports/iao_bot.owl` |
| **CCO** | Common Core Ontologies release `v1.7-2024-11-03` (last release before the v2.0 IRI-namespace migration) | `http://www.ontologyrepository.com/CommonCoreOntologies/` | ROBOT BOT-extracted slim module loaded from `03_TECHNICAL_CORE/ontology/imports/cco_bot.owl`, plus a small set of local bridging assertions in `ARCO_governance_extension.ttl` |

**BFO 2020** is the second edition of Basic Formal Ontology, standardized as ISO/IEC 21838-2:2021. ARCO uses the OBO Foundry numeric-ID namespace (`BFO_0000015`, `BFO_0000016`, etc.) that is definitive of this release. BFO is loaded as a full local file because it is small (~100 KB), ISO-standardized, and the authoritative grounding for everything else; this matches IAO's own pattern of full-importing BFO while extracting slim modules of any other dependency.

**RO**, **IAO**, and **CCO** are loaded as ROBOT-extracted slim modules using `--method BOT`, a syntactic locality variant. The seed term lists ARCO depends on are version-controlled in `03_TECHNICAL_CORE/ontology/imports/seeds/{ro,iao,cco}_seed.txt`, and the slim modules can be regenerated reproducibly from the pinned upstream releases. This is the OBO Foundry / Ontology Development Kit (ODK) standard pattern, used by Gene Ontology, the OBO Relations Ontology itself, and the hundreds of ODK-managed projects.

**Local CCO bridging assertions.** Upstream CCO has its own `cco:InformationContentEntity` class that is not formally linked to IAO's `iao:0000030`. ARCO's `ARCO_governance_extension.ttl` contains two small bridging assertions (`cco:DirectiveICE rdfs:subClassOf iao:0000030`, `cco:DescriptiveICE rdfs:subClassOf iao:0000030`) that connect the CCO and IAO information-content-entity hierarchies. These are the only stubs that do non-trivial work; the remaining CCO declarations in that file are now redundant with the BOT module and are kept for in-file readability rather than logical effect.

### Why ROBOT BOT slim modules

Using `robot extract --method BOT` to pull slim, version-pinned modules is the OBO Foundry's standard pattern for depending on external ontologies. The choice rests on five practical points:

1. **Formal entailment-preservation guarantee.** BOT is a syntactic locality module variant (Cuenca Grau, Horrocks, Kazakov, Sattler 2007/2008): for any axiom α whose signature is contained in the seed signature Σ, the extracted module entails α iff the full upstream ontology does. This includes property characteristics (`FunctionalProperty`, `Transitive`, `Symmetric`), property chain axioms, inverse-of axioms, and `rdfs:domain` / `rdfs:range`. ARCO's gate axioms depend on these — particularly anonymous inverse property expressions on `iao:0000136` — so this is the strict property the project needs.
2. **OBO Foundry / ODK convention.** The Ontology Development Kit, which scaffolds ~hundreds of OBO Foundry projects, hardcodes `module_type_slme: "BOT"` as default. Gene Ontology, OBI, ChEBI, and the OBO Relations Ontology itself all ship BOT-extracted slim modules for their dependencies. ARCO matching this convention shortens the trust chain for any reviewer fluent in OBO practice.
3. **MIREOT is legacy and unsafe for reasoning-critical projects.** ROBOT's own documentation states MIREOT "preserves the hierarchy of the input ontology (subclass and subproperty relationships), but does not try to preserve the full set of logical entailments." The documented MIREOT failure mode is silently dropping property typing and characteristic axioms. For a project whose headline product is OWL-DL reasoning correctness over inverse-property gate axioms, MIREOT is the wrong choice on principle and BOT is the right one.
4. **Reproducibility.** Each slim module is regenerable from a pinned upstream release using a single ROBOT command with a version-controlled seed file. The seed lists are in `03_TECHNICAL_CORE/ontology/imports/seeds/`. A reviewer auditing ARCO can re-run the extraction and verify byte-equivalent output.
5. **Operational scaling.** A pipeline run on Sentinel-ID with the BOT modules loads roughly 7744 asserted triples and produces 27454 post-reasoning (about 19710 derived). The HermiT reasoning step in the ROBOT validation workflow runs in approximately seven minutes on the merged ontology. An earlier intermediate state of ARCO loaded the full upstream releases of RO and IAO, which took the HermiT step to thirty to forty minutes and was projected to grow to one to three hours when CCO was added; this is operationally noisy without adding any reasoning-correctness signal that BOT does not already provide. The full-import experiments are preserved in git history at PRs #24 and #25 and confirmed that the slim modules produce byte-identical classification outputs.

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
2. Run OWL-RL reasoning to materialize entailments (7744 asserted -> 27454 post-reasoning, on the BFO + BOT-extracted RO/IAO/CCO + ARCO union)
3. Validate documentary completeness with SHACL
4. Run two layers of checks:
   - **Classification layer (OWL-RL):** SHACL conformance, `HighRiskSystem` latent-risk entailment, Annex III 1(a) three-gate entailment (the formal classification outputs)
   - **Audit documentation layer (SPARQL ASK on reasoned graph):** traceability, latent risk, intended use, obligation linkage, regulatory alignment (inspects declared documentary content and confirms it matches what the classification requires)
5. Emit a formal condition assessment certificate with evidence path
6. Write artifact files to `runs/demo/` (certificate, summary JSON, determination packet, evidence bindings, SHACL report, HTML view)

### Run in GitHub Actions

This pipeline also runs automatically in CI. Go to **Actions > ARCO Demo Run > Run workflow** to trigger it manually. The workflow uploads `runs/demo/` as a downloadable artifact.
