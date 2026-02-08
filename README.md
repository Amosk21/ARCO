# ARCO

**Assurance & Regulatory Classification Ontology**

ARCO produces regulatory classifications as logical consequences of explicitly modeled system capabilities, rather than probabilistic assessments.

---

## Instant understanding

- **Input:** A system description modeled as instances (components, roles, capabilities, intended context)
- **Output:** A deterministic regulatory determination plus traceability artifacts (validation report + query evidence)
- **Mechanism:** BFO-aligned OWL ontology (axioms) + SHACL completeness validation + SPARQL ASK audit queries

**Why:** Replace probabilistic "confidence" with audit-traceable logical determination.

A concrete example of a produced determination is available below and in detail here:
→ [`ARCO_Regulatory_Determination_Case.md`](01_COMMERCIAL/ARCO_Regulatory_Determination_Case.md)

---

## Example output (regulatory determination)

```text
========================================================================
REGULATORY DETERMINATION CERTIFICATE
========================================================================
SYSTEM:                Sentinel_ID_System
REGIME:                EU AI Act (Article 6 / Annex III)
CLASSIFICATION:        HighRiskSystem (INFERRED)
TRIGGERING CAPABILITY: Sentinel_FaceID_Disposition
EVIDENCE PATH:
  Sentinel_ID_System -> Sentinel_FaceID_Module -> Sentinel_FaceID_Disposition
SHACL:                PASS
TRACEABILITY:          PASS
LATENT RISK:           DETECTED
========================================================================
```

This determination is **derived**, not asserted.
If the structural prerequisites for the regulated capability were not present, the classification would not be inferred.

---

## Why this exists (design-time governance)

The core problem in AI governance is not a lack of rules, transparency, or oversight. It is that systems are built without an explicit, shared model of **what exists**, **what those things are capable of**, and **which processes can occur as a result**.

Early modeling choices quietly define reality for a system, fixing what can be perceived, optimized, or ignored. Because those choices are treated as technical configuration rather than structural commitments, they escape ownership and governance.

Liability attaches to what a system **is able to do**, not only to what it happens to be doing. The real leverage point is **design time**, where continuants, capabilities, roles, and processes can still be made explicit, inspectable, and contestable.

---

## Regulatory classification as a design-time problem

Modern AI regulation increasingly classifies systems by **capability**, not by configuration or stated intent. Under the EU Artificial Intelligence Act, this shift is explicit: Article 6 and Annex III define high-risk status in terms of what a system is structurally capable of doing, regardless of whether those capabilities are currently enabled.

ARCO operates on top of this regulatory reality.

Rather than treating regulatory classification as an interpretive or post-hoc exercise, ARCO formalizes Article 6 and Annex III criteria as explicit, capability-based conditions that can be evaluated at design time using a general assurance architecture designed for capability-based regulation.

---

## Ontological grounding (why structure matters)

For regulatory classification to be derived from system structure, the underlying model must distinguish clearly between:

- what exists
- what it is capable of
- what processes may occur as a result

ARCO is grounded in a realist ontological framework aligned with the [Basic Formal Ontology (BFO)](https://basic-formal-ontology.org/). This grounding enforces explicit separation between material entities, dispositions (capabilities), roles, and processes, preventing regulatory classifications from being inferred from implementation detail alone.

This is what allows ARCO to treat capability as something that **resolves from structure** rather than something asserted by documentation or intent. If the structural prerequisites for a regulated capability are not present, the capability does not exist for regulatory purposes.

---

## Overview

ARCO is a framework for producing clear, defensible regulatory classifications for high-stakes AI systems.

ARCO is **system-agnostic by design**. New AI systems are evaluated by authoring new instance data against the same ontological and reasoning framework; the core ontology, validation rules, and classification logic do not change.

Instead of generating scores, confidence levels, or probabilistic assessments, ARCO produces regulatory determinations that can be traced directly back to the structure and capabilities of the system being evaluated.

> **The goal is simple:**
> Replace probabilistic "confidence" with audit-traceable logical determination.

This repository contains the complete reference implementation and supporting materials for that approach.

ARCO is under active development. Ontological commitments and determination mechanics are stable; documentation and additional regulatory regimes, extensions, and integrations are evolving.

---

## Orientation (5-minute entry point)

For readers who want a fast, system-level understanding before diving into the full materials:

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

This repository is structured to support both high-level review and hands-on technical validation. Depending on what you are trying to understand, there are three recommended entry paths.

### 🏛️ Phase 1: Methodology (Strategic View)

- [`ARCO_Assurance_Engine.md`](01_COMMERCIAL/ARCO_Assurance_Engine.md)
- [`Command_Center.md`](01_COMMERCIAL/Command_Center.md)
- [`Glass_Box_Compliance_White_Paper.md`](01_COMMERCIAL/Glass_Box_Compliance_White_Paper.md)

### 📄 Phase 2: Technical Deep-Dive

- [`TechnicalDeck.md`](02_SYSTEM_OVERVIEW/TechnicalDeck.md)
- [`ARCO_Technical_Implementation.md`](02_SYSTEM_OVERVIEW/ARCO_Technical_Implementation.md)

### ⚙️ Phase 3: Execution (Operational View)

- [`ARCO_Regulatory_Determination_Case.md`](01_COMMERCIAL/ARCO_Regulatory_Determination_Case.md)
- [`ARCO_Pilot_Engagement_Scope.md`](01_COMMERCIAL/ARCO_Pilot_Engagement_Scope.md)
- [`run_pipeline.py`](03_TECHNICAL_CORE/scripts/run_pipeline.py)

---

## Getting started (run the reference pipeline)

This repository includes a reference implementation that demonstrates the full ARCO assurance pipeline in execution.

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

1. Load ontology and instance data
2. Materialize inferences
3. Validate completeness with SHACL
4. Run audit queries
5. Emit a regulatory determination certificate
