# ARCO  
**Assurance & Regulatory Classification Ontology**

## Why this exists (Design-time governance)

The core problem in AI governance is not a lack of rules, transparency, or oversight. It is that systems are built without an explicit, shared model of what exists, what those things are capable of, and which processes can occur as a result. Early modeling choices quietly define reality for the system, fixing what can be perceived, optimized, or ignored. Because those choices are treated as technical configuration rather than structural commitments, they escape ownership and governance. By the time monitoring, audits, or ethics are applied, the ontology has already done the governing.

Regulatory frameworks increasingly classify systems by capability, not configuration. Liability attaches to what a system is able to do, not only to what it happens to be doing. The real leverage point is design time, where continuants, capabilities, roles, and processes can still be made explicit, inspectable, and contestable.

### Regulatory classification as a design-time problem

Modern AI regulation increasingly classifies systems by *capability*, not by configuration or stated intent. Under the EU Artificial Intelligence Act, this shift is explicit: Article 6 and Annex III define high-risk status in terms of what a system is structurally capable of doing, regardless of whether those capabilities are currently enabled.

ARCO operates on top of this regulatory reality.

Rather than treating regulatory classification as an interpretive or post-hoc exercise, ARCO formalizes Article 6 and Annex III criteria as explicit, capability-based conditions that can be evaluated at design time, using a general assurance architecture designed for capability-based regulation.

This framing establishes the minimum foundation required for ARCO to function: a shared, explicit model of system structure, capabilities, and regulatory triggers that can be inspected, validated, and reasoned over deterministically.

### Ontological grounding (why structure matters)

For regulatory classification to be derived from system structure, the underlying model must distinguish clearly between what *exists*, what it is *capable of*, and what *processes* may occur as a result.

ARCO is grounded in a realist ontological framework aligned with the Basic Formal Ontology (BFO). This grounding enforces explicit separation between material entities, dispositions (capabilities), roles, and processes, preventing regulatory classifications from being inferred from informal descriptions, policy language, or implementation detail alone.

This is what allows ARCO to treat capability as something that resolves from structure rather than something asserted by documentation or intent. If the structural prerequisites for a regulated capability are not present, the capability does not exist for regulatory purposes.

## Overview

ARCO is a framework for producing **clear, defensible regulatory classifications** for high-stakes AI systems.

Instead of generating scores, confidence levels, or probabilistic assessments, ARCO produces **regulatory determinations** that can be traced directly back to the structure and capabilities of the system being evaluated.

**The goal is simple:**

> Replace probabilistic "confidence" with regulator-defensible logical determination.

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

*Recommended for leadership, reviewers, and conceptual alignment.*

1. **[ARCO_Assurance_Engine.md](01_COMMERCIAL/ARCO_Assurance_Engine.md)**  
   Explains why probabilistic approaches break down in regulated domains and introduces the logic-first assurance model.

2. **[Command_Center.md](02_SYSTEM_OVERVIEW/Command_Center.md)**  
   Foundational doctrine covering the technical logic, modeling commitments, implementation layers, and strategic positioning.

3. **[Glass_Box_Compliance_White_Paper.md](02_SYSTEM_OVERVIEW/Glass_Box_Compliance_White_Paper.md)**  
   Academic framing of ontological classification for regulatory risk, covering the conceptual approach and epistemic boundaries.

### 📄 Phase 2: Technical Deep-Dive

*Recommended for technical reviewers who want to understand the architecture before touching code.*

4. **[TechnicalDeck.md](02_SYSTEM_OVERVIEW/TechnicalDeck.md)**  
   Comprehensive technical presentation covering the problem context, architecture, BFO grounding, the Sentinel-ID worked example, and operational validation.

5. **[ARCO_Technical_Implementation.md](05_TECHNICAL_IMPLEMENTATION/ARCO_Technical_Implementation.md)**  
   Detailed architectural decisions: modeling latent risk via BFO dispositions, structural integrity via SHACL, deterministic audit via SPARQL ASK, and the execution pipeline.

### ⚙️ Phase 3: Execution (Operational View)

*Recommended for technical validation and engagement modeling.*

6. **[ARCO_Regulatory_Determination_Case.md](01_COMMERCIAL/ARCO_Regulatory_Determination_Case.md)**  
   A concrete example of a regulatory determination produced by the framework, including the final certificate and traceability.

7. **[ARCO_Pilot_Engagement_Scope.md](01_COMMERCIAL/ARCO_Pilot_Engagement_Scope.md)**  
   Defines how the framework would be deployed in a client setting: 4-week engagement, fixed deliverables, explicit exclusions. This shows what operationalization looks like.

8. **[run_pipeline.py](03_TECHNICAL_CORE/scripts/run_pipeline.py)**  
   The reference implementation. This script demonstrates ontology ingestion, deterministic evaluation, and SHACL validation in action.

---

## Getting started (run the reference pipeline)

This repository includes a reference implementation that demonstrates the full ARCO assurance pipeline in execution.

### Requirements
- Python 3.10 or newer

### Install dependencies
From the repository root:

```bash
pip install rdflib pyshacl
```

### Run the pipeline
```bash
python 03_TECHNICAL_CORE/scripts/run_pipeline.py
```

### What you should see

**Loaded triples:** `<number>`  
Confirms the ontology and instance graphs loaded correctly.

**SPARQL ASK result:** `True` / `False`  
Confirms the regulatory logic query executed successfully.

**SHACL conforms:** `True` / `False`  
Indicates whether the provided instance data satisfies the required documentation constraints.

**A `False` result does not indicate a system error.**  
It means the SHACL validator identified missing or inconsistent required information, which is the intended behavior of the assurance process. The printed validation report shows exactly what is missing or invalid.

This script is a reference execution used to demonstrate ingestion, structural validation, deterministic evaluation, and traceable output—not a production automation tool.

---

## Repository structure

```
ARCO/
├── 01_COMMERCIAL/
│   ├── ARCO_Assurance_Engine.md      # Core methodology
│   ├── ARCO_Pilot_Engagement_Scope.md # Engagement model
│   ├── ARCO_Regulatory_Determination_Case.md # Worked example
│   └── EXEC_PITCH.md                 # Executive overview
├── 02_SYSTEM_OVERVIEW/
│   ├── arco_positioning.md           # Ecosystem positioning
│   ├── Command_Center.md             # Foundational doctrine
│   ├── Glass_Box_Compliance_White_Paper.md # Academic framing
│   └── TechnicalDeck.md              # Technical presentation
├── 03_TECHNICAL_CORE/
│   ├── ontology/                     # ARCO ontologies (TTL)
│   ├── reasoning/                    # SPARQL queries
│   ├── scripts/                      # Pipeline implementation
│   └── validation/                   # SHACL shapes
├── 04_DIAGRAMS_AND_MODELS/           # Architecture diagrams, visual assets
└── 05_TECHNICAL_IMPLEMENTATION/
    └── ARCO_Technical_Implementation.md # Architectural decisions
```

---

## What ARCO is not

ARCO is **not**:

- A probabilistic risk scoring tool  
- A checklist generator  
- A substitute for legal counsel  
- A plug-and-play compliance dashboard  

ARCO is best understood as a **formal assurance instrument**, similar in spirit to safety cases used in aerospace or medical systems, applied to AI regulatory classification.

---

## Status

ARCO is presented here as a **reference-grade methodology and capability demonstration**.

The technical foundation is intentionally explicit and auditable.  
Future work focuses on validation, deployment, and refinement through real-world use.

---

## Contact

Alex Moskowitz  
[LinkedIn](https://www.linkedin.com/in/alex-moskowitz/) · [Email](alex.moskowitz97@gmail.com)

*Interested in AI governance, regulatory technology, or applying formal methods to compliance problems? Let's talk.*
