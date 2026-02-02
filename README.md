# ARCO  
**Assurance & Regulatory Classification Ontology**

ARCO produces regulatory classifications as logical consequences of explicitly modeled system capabilities, rather than probabilistic assessments.

## Instant understanding

- **Input:** A system description modeled as instances (components, roles, capabilities, intended context)  
- **Output:** A deterministic regulatory determination plus traceability artifacts (validation report + query evidence)  
- **Mechanism:** BFO-aligned OWL ontology (axioms) + SHACL completeness validation + SPARQL ASK audit queries

**Why:** Replace probabilistic "confidence" with audit-traceable logical determination.

A concrete example of a produced determination is available here:  
→ [01_COMMERCIAL/ARCO_Regulatory_Determination_Case.md](01_COMMERCIAL/ARCO_Regulatory_Determination_Case.md)

---

## Why this exists (Design-time governance)

The core problem in AI governance is not a lack of rules, transparency, or oversight. It is that systems are built without an explicit, shared model of what exists, what those things are capable of, and which processes can occur as a result. Early modeling choices quietly define reality for the system, fixing what can be perceived, optimized, or ignored. Because those choices are treated as technical configuration rather than structural commitments, they escape ownership and governance.

Liability attaches to what a system is able to do, not only to what it happens to be doing. The real leverage point is design time, where continuants, capabilities, roles, and processes can still be made explicit, inspectable, and contestable.

### Regulatory classification as a design-time problem

Modern AI regulation increasingly classifies systems by *capability*, not by configuration or stated intent. Under the EU Artificial Intelligence Act, this shift is explicit: Article 6 and Annex III define high-risk status in terms of what a system is structurally capable of doing, regardless of whether those capabilities are currently enabled.

ARCO operates on top of this regulatory reality.

Rather than treating regulatory classification as an interpretive or post-hoc exercise, ARCO formalizes Article 6 and Annex III criteria as explicit, capability-based conditions that can be evaluated at design time, using a general assurance architecture designed for capability-based regulation.

### Ontological grounding (why structure matters)

For regulatory classification to be derived from system structure, the underlying model must distinguish clearly between what *exists*, what it is *capable of*, and what *processes* may occur as a result.

ARCO is grounded in a realist ontological framework aligned with the Basic Formal Ontology (BFO). This grounding enforces explicit separation between material entities, dispositions (capabilities), roles, and processes, preventing regulatory classifications from being inferred from implementation detail alone.

This is what allows ARCO to treat capability as something that resolves from structure rather than something asserted by documentation or intent. If the structural prerequisites for a regulated capability are not present, the capability does not exist for regulatory purposes.

---

## Overview

ARCO is a framework for producing **clear, defensible regulatory classifications** for high-stakes AI systems.

ARCO is system-agnostic by design. New AI systems are evaluated by authoring new instance data against the same ontological and reasoning framework; the core ontology, validation rules, and classification logic do not change.  
Instead of generating scores, confidence levels, or probabilistic assessments, ARCO produces **regulatory determinations** that can be traced directly back to the structure and capabilities of the system being evaluated.

**The goal is simple:**

> Replace probabilistic "confidence" with audit-traceable logical determination.

This repository contains the complete reference implementation and supporting materials for that approach.

ARCO is under active development. Ontological commitments and determination mechanics are stable; documentation and additional regulatory regimes, extensions, and integrations are evolving.

---

## Orientation (5-minute entry point)

For readers who want a fast, system-level understanding before diving into the full materials:

**0. Executive overview (non-technical)**  
A concise, business-facing overview of ARCO's purpose, economic value, and positioning for decision-makers.  

→ [01_COMMERCIAL/EXEC_PITCH.md](01_COMMERCIAL/EXEC_PITCH.md)

**1. ARCO as a deployment gate**  
A one-page diagram showing how ARCO functions as a formal regulatory decision point *before* model deployment.  

→ [04_DIAGRAMS_AND_MODELS/arco_deployment_gate.png](04_DIAGRAMS_AND_MODELS/arco_deployment_gate.png)

**2. Where ARCO sits in the governance ecosystem**  
A short narrative explaining how ARCO relates to existing compliance, monitoring, and AI tooling.  

→ [02_SYSTEM_OVERVIEW/arco_positioning.md](02_SYSTEM_OVERVIEW/arco_positioning.md)

**3. EU AI Act classification models (reference diagrams)**  
Visual models showing how Article 6 and Annex III classification criteria are represented and evaluated within ARCO.  

→ [04_DIAGRAMS_AND_MODELS/EUAI_mmd_1.png](04_DIAGRAMS_AND_MODELS/EUAI_mmd_1.png)  
→ [04_DIAGRAMS_AND_MODELS/EUAI_mmd_2.png](04_DIAGRAMS_AND_MODELS/EUAI_mmd_2.png)

---

## What ARCO does

At a high level, ARCO answers a single question:

**Given what this system is capable of, does it meet the legal criteria for a specific regulatory classification?**

---

## Where to start

This repository is structured to support both high-level review and hands-on technical validation.  
Depending on what you are trying to understand, there are three recommended entry paths.

### 🏛️ Phase 1: Methodology (Strategic View)

1. **[ARCO_Assurance_Engine.md](01_COMMERCIAL/ARCO_Assurance_Engine.md)**  
2. **[Command_Center.md](02_SYSTEM_OVERVIEW/Command_Center.md)**  
3. **[Glass_Box_Compliance_White_Paper.md](02_SYSTEM_OVERVIEW/Glass_Box_Compliance_White_Paper.md)**  

### 📄 Phase 2: Technical Deep-Dive

4. **[TechnicalDeck.md](02_SYSTEM_OVERVIEW/TechnicalDeck.md)**  
5. **[ARCO_Technical_Implementation.md](05_TECHNICAL_IMPLEMENTATION/ARCO_Technical_Implementation.md)**  

### ⚙️ Phase 3: Execution (Operational View)

6. **[ARCO_Regulatory_Determination_Case.md](01_COMMERCIAL/ARCO_Regulatory_Determination_Case.md)**  
7. **[ARCO_Pilot_Engagement_Scope.md](01_COMMERCIAL/ARCO_Pilot_Engagement_Scope.md)**  
8. **[run_pipeline.py](03_TECHNICAL_CORE/scripts/run_pipeline.py)**  

---

## Getting started (run the reference pipeline)

This repository includes a reference implementation that demonstrates the full ARCO assurance pipeline in execution.

### Requirements
- Python 3.10 or newer

### Install dependencies
```bash
pip install rdflib pyshacl
