# ARCO

**Assurance & Regulatory Classification Ontology**

Companies are building AI systems without knowing whether those systems will be classified as high-risk under the EU AI Act and other regulatory frameworks. When that determination happens after deployment, the costs are severe: redesign, retraining, fines (up to 6% of global revenue), forced withdrawal, reputational damage.

ARCO moves that risk decision upstream. It is a pre-deployment regulatory classification engine that tells organizations — before deployment, before sunk costs, before regulatory exposure — whether a system triggers high-risk conditions and exactly why.

The output is not a score, a confidence level, or an advisory opinion. It is a deterministic, audit-traceable regulatory determination backed by formal logic.

**TL;DR**
- ARCO is a deterministic regulatory classification framework grounded in BFO/CCO realist ontology. The current implementation demonstrates it against the EU AI Act: formal OWL-RL reasoning tells you — before you build — whether your system is high-risk and exactly why. The architecture generalizes to any regulatory domain where obligations attach to capability, structure, and role.
- Classifications are deterministic and audit-traceable: formal OWL-RL reasoning + SHACL validation + SPARQL queries over a BFO/CCO-grounded ontology, with no probabilistic scoring and no LLMs in the decision loop.
- Run `python 03_TECHNICAL_CORE/scripts/run_pipeline.py` to produce a regulatory determination certificate with a full evidence path from system components through capabilities to regulatory criteria.

**What's modeled (current scope)**

| Annex III category | Capability (Gate 1) | Prescribed process (Gate 2) | Affected role (Gate 3) |
|--------------------|---------------------|-----------------------------|------------------------|
| 1(a) — Remote biometric identification | `BiometricIdentificationCapability` | `RemoteBiometricIdentificationProcess` | `NaturalPersonRole` |
| 5(b) — Creditworthiness evaluation | `CreditworthinessEvaluationCapability` | `CreditworthinessEvaluationProcess` | `NaturalPersonRole` |

All three gates must be satisfied for entailment. A system bearing only a biometric capability is **not** entailed as a creditworthiness system, and vice versa — cross-category isolation is formally enforced by the ontology, not asserted by hand.

---

[![ARCO Demo Run](https://github.com/Amosk21/ARCO/actions/workflows/arco-demo.yml/badge.svg?branch=main)](https://github.com/Amosk21/ARCO/actions/workflows/arco-demo.yml)

## What organizations get

- **Regulatory clarity at design time** — know whether your system is high-risk before you build it, not after you deploy it
- **Audit-ready evidence** — every classification traces back through components, capabilities, and regulatory criteria with no gaps
- **Reduced regulatory exposure** — identify classification triggers while architecture changes are still cheap
- **Repeatable, defensible determinations** — same system description in, same classification out, every time
- **No AI in the loop for decisions** — AI extracts candidates; formal logic drives the determination

> **The core value:** Replace probabilistic "confidence" with audit-traceable logical determination.

---

## Proof: a real determination

```text
========================================================================
REGULATORY DETERMINATION CERTIFICATE
========================================================================
  SYSTEM:                  Sentinel_ID_System
  REGIME:                  EU AI Act (Article 6 / Annex III)
  CLASSIFICATION:          HighRiskSystem (INFERRED)
  TRIGGERING CAPABILITY:   Sentinel_FaceID_Disposition
  EVIDENCE PATH:
  Sentinel_ID_System -> Sentinel_FaceID_Module -> Sentinel_FaceID_Disposition
  SHACL:                   PASS
  TRACEABILITY:            PASS
  LATENT RISK:             DETECTED
  INTENDED USE:            PASS
  ANNEX III 1(a):          VERIFIED (ENTAILED)
  OBLIGATION:              PASS
  ENTAILED TRIPLES ADDED:  +891
========================================================================
```

This determination is **derived**, not asserted. If the structural prerequisites for the regulated capability were not present, the classification would not be inferred. Full case study: [`ARCO_Regulatory_Determination_Case.md`](01_COMMERCIAL/ARCO_Regulatory_Determination_Case.md)

---

## The problem ARCO solves

The root cause: systems are built without an explicit model of **what exists**, **what those things are capable of**, and **which regulatory conditions those capabilities trigger**. Early modeling choices quietly lock in regulatory exposure, but because those choices are treated as technical configuration rather than structural commitments, they escape governance entirely.

ARCO moves that risk decision upstream — to design time, where it costs a fraction of post-deployment remediation.

---

## How it works

**Input:** A system description modeled as instances — components, roles, capabilities, intended use context.

**Process:**
1. The system's structure is encoded in a formal ontology grounded in [BFO](https://basic-formal-ontology.org/) (the same foundational ontology used across biomedical, defense, and industrial standards)
2. OWL-RL reasoning derives what the system is capable of and whether it meets the three-gate classification condition: capability (reality-side), prescribed process type (representation-side), and affected role category (representation-side). All three gates check specific content — not the existence of documentation alone.
3. SHACL validation enforces documentary completeness
4. SPARQL audit queries run on the reasoned graph as a downstream documentation layer — confirming that the right content is explicitly declared and that the law's process prescription aligns with the provider's documentation. These queries inspect what the reasoning produced; they do not produce the classification themselves.

**Output:** A regulatory determination certificate with full evidence path — which component bears which capability, which regulatory condition it triggers, and why.

The system is **agnostic by design**. New AI systems are evaluated by authoring new instance data against the same framework. The core ontology, validation rules, and classification logic do not change.

---

## Why the approach is structural, not behavioral

Liability attaches to what a system **is able to do**, not only to what it happens to be doing. Modern regulation classifies by capability, not configuration.

ARCO treats capability as something that **resolves from structure** — traced from system components through dispositions to regulatory conditions. If the structural prerequisites for a regulated capability are not present, the capability does not exist for regulatory purposes. If they are present, the classification follows as a logical consequence.

This makes ARCO fundamentally different from post-hoc tools that observe behavior or score risk probabilistically. The classification is deterministic, traceable, and stable — it changes only when the system's structure changes.

---

## Foundational ontology versions

| Ontology | Version / release | IRI namespace used |
|----------|------------------|--------------------|
| **BFO** | BFO 2020 (ISO/IEC 21838-2:2021) | `http://purl.obolibrary.org/obo/BFO_` |
| **RO** | OBO Relation Ontology (current OBO release) | `http://purl.obolibrary.org/obo/RO_` |
| **IAO** | Information Artifact Ontology (current OBO release) | `http://purl.obolibrary.org/obo/IAO_` |
| **CCO** | CCO 1.3-era terms (pre-integrated release, local stubs) | `http://www.ontologyrepository.com/CommonCoreOntologies/` |

**BFO 2020** is the second edition of Basic Formal Ontology, standardized as ISO/IEC 21838-2:2021. ARCO uses the OBO Foundry numeric-ID namespace (`BFO_0000015`, `BFO_0000016`, etc.) that is definitive of this release. The earlier BFO 1.1 used a different IRI scheme (`http://www.ifomis.org/bfo/1.1/snap#`, `span#`) and is not used here.

**CCO** terms are declared as local stubs rather than via a full `owl:imports` of the CCO modules. This means only the specific CCO classes and properties ARCO requires are declared in-file (`cco:Organization`, `cco:DirectiveInformationContentEntity`, `cco:prescribes`, `cco:has_output`, etc.), using the pre-integrated-release IRI namespace. The pipeline does not depend on fetching external CCO files at runtime.

---

## Beyond a single regulation

While this repository demonstrates ARCO against the EU AI Act, the underlying approach generalizes to any domain where obligations attach to capability, structure, and role rather than observed behavior alone.

Once a system's structure exists, certain regulatory futures are locked in unless the structure changes. ARCO surfaces those commitments early — before they appear as audit findings, regulatory enforcement, forced redesigns, or reputational loss.

---

## Orientation (5-minute entry point)

**0. Executive overview (non-technical)**
A concise, business-facing overview of ARCO's purpose, economic value, and positioning for decision-makers.
→ [`EXEC_PITCH.md`](01_COMMERCIAL/EXEC_PITCH.md)

**1. ARCO as a deployment gate**
A one-page diagram showing how ARCO functions as a formal regulatory decision point before model deployment.
→ [`arco_deployment_gate.png`](04_DIAGRAMS_AND_MODELS/arco_deployment_gate.png)

**2. Where ARCO sits in the governance ecosystem**
A short narrative explaining how ARCO relates to existing compliance, monitoring, and AI tooling.
→ [`arco_positioning.md`](02_SYSTEM_OVERVIEW/arco_positioning.md)

**3. EU AI Act classification models (reference diagrams)**
Visual models showing how Article 6 and Annex III classification criteria are represented and evaluated within ARCO.
→ [`EUAI_mmd_1.png`](04_DIAGRAMS_AND_MODELS/EUAI_mmd_1.png)
→ [`EUAI_mmd_2.png`](04_DIAGRAMS_AND_MODELS/EUAI_mmd_2.png)

---

## Where to start

This repository supports both high-level review and hands-on technical validation. Three entry paths depending on your role.

### Phase 1: Methodology (Strategic View)

- [`ARCO_Assurance_Engine.md`](01_COMMERCIAL/ARCO_Assurance_Engine.md)
- [`Command_Center.md`](01_COMMERCIAL/Command_Center.md)
- [`Glass_Box_Compliance_White_Paper.md`](01_COMMERCIAL/Glass_Box_Compliance_White_Paper.md)

### Phase 2: Technical Deep-Dive

- [`TechnicalDeck.md`](02_SYSTEM_OVERVIEW/TechnicalDeck.md)
- [`ARCO_Technical_Implementation.md`](02_SYSTEM_OVERVIEW/ARCO_Technical_Implementation.md)

### Phase 3: Execution (Operational View)

- [`ARCO_Regulatory_Determination_Case.md`](01_COMMERCIAL/ARCO_Regulatory_Determination_Case.md)
- [`ARCO_Pilot_Engagement_Scope.md`](01_COMMERCIAL/ARCO_Pilot_Engagement_Scope.md)
- [`run_pipeline.py`](03_TECHNICAL_CORE/scripts/run_pipeline.py)

---

## Getting started (run the reference pipeline)

### Requirements

- Python 3.10 or newer

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the pipeline

```bash
python 03_TECHNICAL_CORE/scripts/run_pipeline.py
```

The pipeline will:

1. Load ontology (core + governance extension) and instance data
2. Run OWL-RL reasoning to materialize entailments (400 asserted → 1291 post-reasoning)
3. Validate documentary completeness with SHACL
4. Run two layers of checks:
   - **Classification layer (OWL-RL):** SHACL conformance, HighRiskSystem entailment, Annex III 1(a) three-gate entailment — these are the formal classification outputs
   - **Audit documentation layer (SPARQL ASK on reasoned graph):** traceability, latent risk, intended use, obligation linkage, regulatory alignment — these inspect declared documentary content and confirm it matches what the classification requires
5. Emit a regulatory determination certificate with evidence path
6. Write artifact files to `runs/demo/` (certificate, summary JSON, evidence bindings, SHACL report)

### Run in GitHub Actions

This pipeline also runs automatically in CI. Go to **Actions > ARCO Demo Run > Run workflow** to trigger it manually. The workflow uploads `runs/demo/` as a downloadable artifact.
