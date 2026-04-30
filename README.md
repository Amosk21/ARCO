# ARCO

**Assurance & Regulatory Classification Ontology**

Companies are building AI systems without knowing whether those systems will satisfy the high-risk conditions of the EU AI Act and other regulatory frameworks. When that exposure surfaces after deployment, the costs are severe: redesign, retraining, fines (up to 6% of global revenue), forced withdrawal, reputational damage.

ARCO moves that risk decision upstream. It is a pre-deployment classification engine that tells organizations (before deployment, before sunk costs, before regulatory exposure) whether a system satisfies ARCO's formal encoding of Annex III conditions, and exactly why.

The output is not a score, a confidence level, or an advisory opinion. It is a deterministic, audit-traceable assessment grounded in formal logic and BFO/RO/IAO-aligned, CCO-informed structure (the OBO Foundry upper- and mid-level ontologies are loaded as full upstream releases): same structured inputs, same classification, every time.

**TL;DR**
- ARCO is a deterministic regulatory classification framework aligned with BFO 2020 and the OBO Foundry: BFO, the OBO Relations Ontology (RO), and the Information Artifact Ontology (IAO) are loaded as full upstream releases; CCO terms are declared as local stubs for governance vocabulary not yet covered by an imported ontology. The current implementation demonstrates it against the EU AI Act: formal OWL-RL reasoning tells you, before you build, whether your system triggers high-risk conditions per ARCO's encoding of Article 6 and Annex III, and exactly why. The architecture generalizes to any regulatory domain where obligations attach to capability, structure, and role.
- Classifications are deterministic and audit-traceable: formal OWL-RL reasoning + SHACL validation + SPARQL queries over a BFO-aligned ontology (full BFO/RO/IAO upstream imports, CCO terms as local stubs), with no probabilistic scoring and no LLMs in the decision loop.
- From a fresh clone, install the Python dependencies and run `python 03_TECHNICAL_CORE/scripts/run_pipeline.py` from the repository root to produce a formal condition assessment certificate with a full evidence path from system components through capabilities to Annex III criteria.

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

> **The core value:** Replace probabilistic "confidence" with audit-traceable logical assessment grounded in ontologically disciplined structure.

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

  ENTAILED TRIPLES ADDED:  +47888

  Classification layer: PASS
  Audit layer:          PASS
========================================================================
```

This determination is **derived**, not asserted. If any category-specific gate were not present, the Annex III applicability class would not be inferred. The reference pipeline writes the supporting certificate, JSON summary, evidence bindings, and SHACL report to `runs/demo/`.

---

## The problem ARCO solves

The root cause: systems are built without an explicit model of **what exists**, **what those things are capable of**, and **which regulatory conditions those capabilities trigger**. Early modeling choices quietly lock in regulatory exposure, but because those choices are treated as technical configuration rather than structural commitments, they escape governance entirely.

ARCO moves that risk decision upstream, to design time, where it costs a fraction of post-deployment remediation.

---

## How it works

**Input:** A system description modeled as instances: components, roles, capabilities, intended use context.

**Process:**
1. The system's structure is encoded in a formal ontology grounded in [BFO](https://basic-formal-ontology.org/) (the same foundational ontology used across biomedical, defense, and industrial standards)
2. OWL-RL reasoning derives what the system is capable of and whether it meets the category-specific three-gate classification condition: capability (reality-side), prescribed process type (representation-side), and affected role category (representation-side). All three gates check specific content, not the existence of documentation alone.
3. SHACL validation enforces documentary completeness
4. SPARQL audit queries run on the reasoned graph as a downstream documentation layer, confirming that the right content is explicitly declared and that the law's process prescription aligns with the provider's documentation. These queries inspect what the reasoning produced; they do not produce the classification themselves.

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
| **RO** | OBO Relations Ontology release `2025-12-17` | `http://purl.obolibrary.org/obo/RO_` | Full ontology loaded from `03_TECHNICAL_CORE/ontology/imports/ro.owl` |
| **IAO** | Information Artifact Ontology release `2026-03-30` | `http://purl.obolibrary.org/obo/IAO_` | Full ontology loaded from `03_TECHNICAL_CORE/ontology/imports/iao.owl` |
| **CCO** | CCO pre-integrated release (exact version unverified; local stubs) | `http://www.ontologyrepository.com/CommonCoreOntologies/` | Local stubs only — specific terms declared in `ARCO_governance_extension.ttl` |

**BFO 2020** is the second edition of Basic Formal Ontology, standardized as ISO/IEC 21838-2:2021. ARCO uses the OBO Foundry numeric-ID namespace (`BFO_0000015`, `BFO_0000016`, etc.) that is definitive of this release. The earlier BFO 1.1 used a different IRI scheme (`http://www.ifomis.org/bfo/1.1/snap#`, `span#`) and is not used here.

**RO** and **IAO** are loaded as full upstream releases. The pipeline pulls the entire `ro.owl` and `iao.owl` files into the reasoning graph alongside BFO. This was not always the case: earlier ARCO revisions referenced RO and IAO terms by IRI with only minimal local label declarations and no full `owl:imports`. The promotion from stub-style references to full-file imports was performed under independent verification (alignment audit, OWL 2 DL profile validation under ROBOT, and HermiT consistency check) and confirmed not to change any classification outputs. See `docs/agent/alignment_audit_RO_2026-04-29.md` and `docs/agent/alignment_audit_IAO_2026-04-29.md`.

**CCO** terms remain declared as local stubs rather than via a full `owl:imports` of the CCO modules. Only the specific CCO classes and properties ARCO requires are declared in-file (`cco:Organization`, `cco:DirectiveInformationContentEntity`, `cco:prescribes`, `cco:has_output`, etc.), using the pre-integrated-release IRI namespace. The pipeline does not depend on fetching external CCO files at runtime.

### Why full upstream imports rather than slim MIREOT modules

The conventional OBO Foundry pattern for depending on an external ontology is to extract a slim "import module" using a tool such as ROBOT's `extract` command (e.g. MIREOT, BOT, or STAR), pulling in only the specific terms a project references plus their ancestors. ARCO instead loads the complete upstream releases. This is a deliberate choice grounded in ARCO's role as a regulatory classification framework rather than a biological ontology fragment.

Five reasons full imports are the right default for ARCO:

1. **Audit traceability.** A reviewer, auditor, or regulator can verify with a single hash that ARCO uses BFO 2020, OBO Relations Ontology release `2025-12-17`, and Information Artifact Ontology release `2026-03-30` exactly as published — with no curation step in between. A MIREOT module would itself be an audit surface ("which axioms made the cut, why, and is the slice still consistent with the full upstream?"). Removing that step shortens the chain of trust.
2. **No silent upstream drift.** When an upstream ontology adds a new property-chain axiom, strengthens a domain or range, or refines a class definition, the full import picks it up automatically on the next release pin. A slim module would freeze the previous slice and quietly miss the change. For a tool whose entire purpose is tracking formal definitions of regulated concepts, this matters.
3. **Extensibility to new Annex III categories and to peer regulations.** Adding Annex III 1(b), 5(a), or 6 — or modeling GDPR Article 22, FDA pre-cert, NIS2, or sectoral safety regimes — will reach for additional BFO, RO, and IAO terms ARCO does not currently reference. With full imports those terms are already in scope; the only ontology engineering work is the new gate axioms. With slim modules every new category or domain triggers a module-rebuild step.
4. **Cross-domain generalization is part of the architectural pitch.** The README and the underlying design claim that ARCO generalizes to any regulatory domain where obligations attach to capability, structure, and role. Full imports are consistent with that claim; per-domain slim modules quietly contradict it.
5. **Stronger independent-reasoner verification.** The HermiT cross-check in CI exists to confirm that the production OWL-RL reasoner agrees with a full DL reasoner over the actual upstream axiomatization. Running HermiT against a slim module would only verify agreement over the axioms ARCO chose to import; running HermiT against the full ontologies verifies agreement over what the upstream specifications actually say.

The cost ARCO accepts in exchange is operational, not logical: the HermiT step in the ROBOT validation workflow takes roughly thirty to forty minutes on the merged BFO + RO + IAO + ARCO ontology, and the production OWL-RL reasoner produces a larger entailed graph. Neither affects correctness, and both have been confirmed under CI on the consolidated branch. The conventional MIREOT counter-argument — sibling biological ontologies needing slim modules to avoid cyclic imports — does not apply here because ARCO has no such cycles to avoid.

**What the entailment counts actually represent.** A pipeline run on Sentinel-ID currently loads roughly 17266 asserted triples and produces roughly 65154 post-reasoning triples — about 47888 derived. The overwhelming majority of those derived triples come from OWL-RL closure over upstream axioms that ARCO does not directly invoke: BFO upper-level subclass propagation, the property-chain and inverse-property axioms in RO that fire across every relation in the merged graph, and IAO's information-content-entity hierarchy. Only a small fraction is ARCO-specific (the gate-axiom entailments that classify a system as `HighRiskSystem` or `AnnexIII1aApplicableSystem`, plus the supporting traceability triples those entailments lean on). With slim MIREOT modules the same Sentinel-ID classification would still emerge, but the post-reasoning graph would be perhaps an order of magnitude smaller because the bulk of the upstream axiomatization would not be loaded. ARCO carries the larger graph deliberately, in exchange for the five reasons above; the inflation is observability cost, not reasoning complexity that the gate axioms had to traverse to produce a verdict.

**Adding new Annex III categories or new regulatory domains.** When a future contributor adds Annex III 1(b), 5(a), 6, or a peer regulation such as GDPR Article 22 or NIS2, full imports mean the only ontology engineering work is the new gate axioms and any new ARCO-side classes (capability, prescribed-process, role). Whatever BFO, RO, or IAO terms the new category needs are already in the reasoning graph. With a MIREOT-style setup, the same addition would also require updating a `terms.txt` file and re-running the module extraction for each affected upstream ontology, then re-running independent verification against the new module. Both approaches reach the same end state; full imports remove a category of forgettable bookkeeping that tends to silently rot.

---

## Beyond a single regulation

While this repository demonstrates ARCO against the EU AI Act, the underlying approach generalizes to any domain where obligations attach to capability, structure, and role rather than observed behavior alone.

Once a system's structure exists, certain regulatory futures are locked in unless the structure changes. ARCO surfaces those commitments early, before they appear as audit findings, regulatory enforcement, forced redesigns, or reputational loss.

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
2. Run OWL-RL reasoning to materialize entailments (17266 asserted -> 65154 post-reasoning, on the full BFO + RO + IAO + ARCO union)
3. Validate documentary completeness with SHACL
4. Run two layers of checks:
   - **Classification layer (OWL-RL):** SHACL conformance, `HighRiskSystem` latent-risk entailment, Annex III 1(a) three-gate entailment (the formal classification outputs)
   - **Audit documentation layer (SPARQL ASK on reasoned graph):** traceability, latent risk, intended use, obligation linkage, regulatory alignment (inspects declared documentary content and confirms it matches what the classification requires)
5. Emit a formal condition assessment certificate with evidence path
6. Write artifact files to `runs/demo/` (certificate, summary JSON, determination packet, evidence bindings, SHACL report, HTML view)

### Run in GitHub Actions

This pipeline also runs automatically in CI. Go to **Actions > ARCO Demo Run > Run workflow** to trigger it manually. The workflow uploads `runs/demo/` as a downloadable artifact.
