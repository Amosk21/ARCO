# ARCO — Assurance & Regulatory Classification Ontology

**Status:** Pilot-Ready (v1 Core)  
**Owner:** Alex Moskowitz  

---

## Context

This repository contains the complete IP stack for **ARCO**, a deterministic assurance framework for regulatory classification of high-stakes AI systems.

ARCO moves beyond governance commentary and probabilistic compliance tooling into a deployable, auditable capability.

**Core objective:**

> Replace probabilistic “confidence” with regulator-defensible logical determination.

ARCO does not provide advice, scores, or likelihoods.  
It produces **binding regulatory classifications** as a matter of logical necessity.

---

## What ARCO Does

ARCO produces a formal regulatory determination for an AI system by:

- Interpreting system documentation
- Encoding system capabilities into a formal ontology
- Enforcing structural admissibility with SHACL
- Evaluating regulatory criteria via deterministic logic
- Producing a traceable audit log of the reasoning path

The output is **not opinion**.  
It is a logically forced conclusion derived from system structure.

---

## Recommended Reading Order (High-Level → Concrete)

For first-time reviewers, read in the following order:

1. **ARCO_Assurance_Engine.pdf**  
   Conceptual overview of Glass-Box Assurance and why probabilistic tools fail in regulated domains.

2. **StakeholderDeck.pdf**  
   Executive-level explanation of latent capability risk (disposition vs realization).

3. **ARCO_Regulatory_Determination_Case.pdf**  
   Concrete example of ARCO’s output using the Sentinel reference system.

4. **ARCO_Pilot_Engagement_Scope.pdf**  
   Fixed-scope Statement of Work defining how ARCO is deployed commercially.

---

## Document Layers and Purpose

### Commercial Layer (Buyer-Facing)

Located in: `01_COMMERCIAL/`

- **ARCO_Pilot_Engagement_Scope.pdf**  
  *Statement of Work*  
  Defines price ($25k), scope (1 system), timeline (4 weeks), and deliverables.

- **ARCO_Regulatory_Determination_Case.pdf**  
  *Sample Deliverable*  
  Demonstrates the determination certificate, audit trace, and gap analysis.

- **ARCO_Assurance_Engine.pdf**  
  *Positioning Paper*  
  Explains deterministic assurance vs probabilistic governance tools.

- **StakeholderDeck.pdf**  
  *Executive Pitch*  
  Visual explanation of latent capability risk.

---

### Technical Core (The IP)

Located in: `03_TECHNICAL_CORE/`

#### Core Ontologies (TTL)
- `ARCO_core.ttl`
- `ARCO_governance_extension.ttl`

BFO-aligned structures defining systems, capabilities, dispositions, and regulatory triggers.

#### Instance Data (TTL)
- `ARCO_instances_sentinel.ttl`

Sentinel reference system used to demonstrate deterministic reasoning.

#### Validation Shapes (SHACL)
- `assessment_documentation_shape.ttl`

Constraints enforcing structural admissibility and documentation completeness.

#### Audit Queries (SPARQL)
- `check_assessment_traceability.sparql`
- `ask_assessment_doc_process_wiring.sparql`
- `ask_provider_role_inheres_in_org.sparql`

Queries that generate traceable determination logic.

#### Execution Scripts (Python)
- `run_pipeline.py`

Executes validation and reasoning in sequence.

**Pipeline:**  
Interpretation → Representation → Validation → Inference → Trace

---

### Diagrams and Models

Located in: `04_DIAGRAMS_AND_MODELS/`

Graph and architecture visualizations used across decks and documentation.

---

### Reference Material

Located in: `90_REFERENCE/`

- **Glass_Box_Compliance_White_Paper.pdf**  
  Academic framing of deterministic assurance.

- **NCOR_Defense_Dossier.pdf**  
  Contextual reference material.

---

### Personal / Non-Front-Facing

Located in: `personal/`

Internal documents not part of the ARCO product surface.

---

## Current Status

**Technical:**  
Complete enough to demonstrate non-trivial, deterministic regulatory reasoning.

**Commercial:**  
Ready for pilot deployment as a fixed-scope assessment.

**Primary Focus Going Forward:**  
Sequencing, packaging, and execution — not expanding the ontology surface area.
