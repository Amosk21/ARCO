# ARCO  
**Assurance & Regulatory Classification Ontology**

## Overview

ARCO is a framework for producing **clear, defensible regulatory classifications** for high-stakes AI systems.

Instead of generating scores, confidence levels, or probabilistic assessments, ARCO produces **regulatory determinations** that can be traced directly back to the structure and capabilities of the system being evaluated.

**The goal is simple:**

> Replace probabilistic "confidence" with regulator-defensible logical determination.

This repository contains the complete reference implementation and supporting materials for that approach.

---

## Orientation (5-minute entry point)

For readers who want a fast, system-level understanding before diving into the full materials:

**1. ARCO as a deployment gate**  
A one-page diagram showing how ARCO functions as a formal regulatory decision point *before* model deployment.

→ [04_DIAGRAMS_AND_MODELS/arco_deployment_gate.png](04_DIAGRAMS_AND_MODELS/arco_deployment_gate.png)

**2. Where ARCO sits in the governance ecosystem**  
A short narrative explaining how ARCO relates to existing compliance, monitoring, and AI tooling.

→ [02_SYSTEM_OVERVIEW/ARCO_Positioning.pdf](02_SYSTEM_OVERVIEW/ARCO_Positioning.pdf)

**3. Core assurance artifacts**  
The detailed methodology, execution, and outputs are covered in the documents below.

---

## Why ARCO exists

Most AI compliance tools try to answer questions like:

- *How risky does this system appear?*
- *How confident are we that it complies?*
- *What score does the model produce?*

**Those questions break down in regulated environments.**

Regulators, auditors, and courts do not evaluate probability.  
They evaluate **justification**.

ARCO exists to answer a different question:

> *Given what this system is capable of doing, does it meet the legal criteria for a specific regulatory classification, yes or no?*

And to make that answer:

- **Deterministic**  
- **Explainable**  
- **Auditable**  
- **Reproducible**  

---

## What ARCO does

At a high level, ARCO answers a single question:

**Given what this system is capable of, does it meet the legal criteria for a specific regulatory classification?**

It does this as follows:

### 1. Start from system documentation
Hardware, software components, deployment context, and intended use are treated as **evidence, not narrative**.

### 2. Represent system capabilities explicitly
Capabilities are encoded formally, including latent or conditional capabilities that may exist even if they are not currently active.

### 3. Enforce structural completeness
SHACL rules ensure required information is present and nothing material is assumed or inferred informally.

### 4. Apply regulatory logic deterministically
SPARQL queries test whether the encoded system satisfies the relevant legal criteria.

### 5. Produce a traceable determination
Every conclusion can be followed back to explicit facts and rules.

**The output is not advice or opinion.**  
**It is a conclusion that follows logically from the system's structure.**

---

## What this repository represents

This repository is **not** a finished product or automated compliance platform.

It is a **reference-grade assurance methodology and demonstration of capability** that shows:

- How deterministic regulatory classification can be performed
- What artifacts such a process produces
- How reasoning can be validated and audited
- What a regulatory determination looks like in practice

The included pilot materials show how the framework could be operationalized in a real engagement.  
They are intended to demonstrate structure, rigor, and end-to-end reasoning, not to imply full production readiness or automation at scale.

---

## Where to start

This repository is structured to support both high-level review and hands-on technical validation.  
Depending on what you are trying to understand, there are two recommended entry paths.

### 🏛️ Phase 1: Methodology (Strategic View)

*Recommended for leadership, reviewers, and conceptual alignment.*

1. **[ARCO_Assurance_Engine.pdf](01_COMMERCIAL/ARCO_Assurance_Engine.pdf)**  
   Explains why probabilistic approaches break down in regulated domains and introduces the logic-first assurance model.

2. **[Command_Center.pdf](01_COMMERCIAL/Command_Center.pdf)**  
   Provides the operational overview: scope, inputs, outputs, and how the assurance process is structured end to end.

### ⚙️ Phase 2: Execution (Operational View)

*Recommended for technical validation and engagement modeling.*

3. **[ARCO_Regulatory_Determination_Case.pdf](01_COMMERCIAL/ARCO_Regulatory_Determination_Case.pdf)**  
   A concrete example of a regulatory determination produced by the framework, including the final certificate and traceability.

4. **[Pilot_Engagement_Model.pdf](01_COMMERCIAL/ARCO_Pilot_Engagement_Scope.pdf)**  
   Defines how the framework would be deployed in a client setting, including the Statement of Work structure and engagement boundaries.

5. **[run_pipeline.py](03_TECHNICAL_CORE/scripts/run_pipeline.py)**  
   The reference implementation. This script demonstrates ontology ingestion, deterministic reasoning, and SHACL validation in action.

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

This script is a reference execution used to demonstrate ingestion, structural validation, deterministic reasoning, and traceable output, not a production automation tool.

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

