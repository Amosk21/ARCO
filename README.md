# ARCO  
Assurance & Regulatory Classification Ontology

## Overview

ARCO is a framework for producing **clear, defensible regulatory classifications** for high-stakes AI systems.

Instead of generating scores, confidence levels, or probabilistic assessments, ARCO produces **regulatory determinations** that can be traced directly back to the structure and capabilities of the system being evaluated.

The goal is simple:

Replace probabilistic “confidence” with regulator-defensible logical determination.

This repository contains the complete reference implementation and supporting materials for that approach.

---

## Why ARCO exists

Most AI compliance tools try to answer questions like:

- How risky does this system appear?
- How confident are we that it complies?
- What score does the model produce?

Those questions break down in regulated environments.

Regulators, auditors, and courts do not evaluate probability.  
They evaluate **justification**.

ARCO exists to answer a different question:

Given what this system is capable of doing, does it meet the legal criteria for a specific regulatory classification, yes or no?

And to make that answer:

- Deterministic  
- Explainable  
- Auditable  
- Reproducible  

---

## What ARCO does

At a high level, ARCO works as follows:

1. Start from system documentation  
    Hardware, software components, deployment context, and intended use.

2. Represent system capabilities explicitly  
    Capabilities are modeled formally, including latent capabilities that exist even if they are not currently enabled.

3. Enforce structural completeness  
    SHACL rules ensure required information is explicit and nothing is assumed or inferred informally.

4. Apply regulatory logic deterministically  
    SPARQL queries test whether the encoded system satisfies legal criteria.

5. Produce a traceable determination  
    Every conclusion can be followed back to explicit facts and rules.

The output is not advice or opinion.  
    It is a conclusion that follows logically from system structure.

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

---

### Phase 1: Methodology (Strategic View)

Recommended for leadership, reviewers, and conceptual alignment.

1. **ARCO_Assurance_Engine.pdf**  
   Explains why probabilistic approaches break down in regulated domains and introduces the logic-first assurance model.

2. **CommandCenter.pdf**  
   Provides the operational overview: scope, inputs, outputs, and how the assurance process is structured end to end.

---

### Phase 2: Execution (Operational View)

Recommended for technical validation and engagement modeling.

3. **ARCO_Regulatory_Determination_Case.pdf**  
   A concrete example of a regulatory determination produced by the framework, including the final certificate and traceability.

4. **01_COMMERCIAL / Pilot_Engagement_Model**  
   Defines how the framework would be deployed in a client setting, including the Statement of Work structure and engagement boundaries.

5. **03_TECHNICAL_CORE / scripts / run_pipeline.py**  
   The reference implementation. This script demonstrates ontology ingestion, deterministic reasoning, and SHACL validation in action.


---

## What ARCO is not

ARCO is not:

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








