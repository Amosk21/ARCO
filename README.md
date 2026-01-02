# ARCO
AI Regulation &amp; Compliance Ontology
ARCO — Assurance & Regulatory Classification Ontology
Status: Pilot-Ready (v1 Core)
Owner: Alex Moskowitz

====================================================
CONTEXT
====================================================

This repository contains the complete IP stack for ARCO, a deterministic assurance framework for regulatory classification of high-stakes AI systems.

ARCO moves beyond governance commentary and probabilistic compliance tooling into a deployable, auditable capability.

The core objective is simple:

Replace probabilistic “confidence” with regulator-defensible logical determination.

ARCO does not provide advice, scores, or likelihoods.
It produces binding regulatory classifications as a matter of logical necessity.

====================================================
WHAT ARCO DOES
====================================================

ARCO produces a formal regulatory determination for an AI system by:

- Interpreting system documentation
- Encoding system capabilities into a formal ontology
- Enforcing structural admissibility with SHACL
- Evaluating regulatory criteria via deterministic logic
- Producing a traceable audit log of the reasoning path

The output is not opinion.
It is a logically forced conclusion derived from system structure.

====================================================
RECOMMENDED READING ORDER
(HIGH-LEVEL → CONCRETE)
====================================================

For first-time reviewers, read in the following order:

1. /01_COMMERCIAL/ARCO_Assurance_Engine.pdf
   Conceptual overview of Glass-Box Assurance and why probabilistic tools fail in regulated domains.

2. /01_COMMERCIAL/StakeholderDeck.pdf
   Executive-level explanation of latent capability risk (disposition vs. realization).

3. /01_COMMERCIAL/ARCO_Regulatory_Determination_Case.pdf
   Concrete example of ARCO’s output using the Sentinel reference system.

4. /01_COMMERCIAL/ARCO_Pilot_Engagement_Scope.pdf
   Fixed-scope Statement of Work defining how ARCO is deployed commercially.

====================================================
DOCUMENT LAYERS AND PURPOSE
====================================================

----------------------------------------------------
COMMERCIAL LAYER (BUYER-FACING)
----------------------------------------------------

Location: /01_COMMERCIAL/

ARCO_Pilot_Engagement_Scope.pdf
Role: Statement of Work
Defines price ($25k), scope (1 system), timeline (4 weeks), and deliverables.
Use to close pilot engagements.

ARCO_Regulatory_Determination_Case.pdf
Role: Sample Deliverable
Shows exactly what the client receives: a determination certificate, audit trace, and gap analysis.
Attach as Appendix A to the Pilot SOW.

ARCO_Assurance_Engine.pdf
Role: Positioning Paper
Establishes the distinction between deterministic assurance and probabilistic governance tools.

StakeholderDeck.pdf
Role: Executive Pitch
Visual, non-technical explanation of latent capability risk.

----------------------------------------------------
SYSTEM OVERVIEW
----------------------------------------------------

Location: /02_SYSTEM_OVERVIEW/

TechnicalDeck.pdf
Role: Architecture Manual
Detailed walkthrough of pipeline design and reasoning flow.

ARCO_Technical_Implementation.pdf
Role: Implementation Reference
Bridges conceptual architecture to concrete technical artifacts.

CommandCenter.pdf
Role: Strategic Doctrine
Defines what ARCO is and is not.

----------------------------------------------------
TECHNICAL CORE (THE IP)
----------------------------------------------------

Location: /03_TECHNICAL_CORE/

Core Ontologies (.ttl)
- ARCO_core_gold_fixed_v3.ttl
- ARCO_governance_extension_fixed_v3.ttl

Instance Data (.ttl)
- ARCO_instances_gold_extended_fixed_v3.ttl

Validation Shapes (.ttl)
- assessment_documentation_shape.ttl

Audit Queries (.sparql)
- check_assessment_traceability.sparql
- ask_assessment_doc_process_wiring.sparql
- ask_provider_role_inheres_in_org.sparql

Execution Scripts (.py)
- run_checks.py

Together these implement the neuro-symbolic pipeline:
Interpretation → Representation → Validation → Inference → Trace

----------------------------------------------------
DIAGRAMS AND MODELS
----------------------------------------------------

Location: /04_DIAGRAMS_AND_MODELS/

Graph and architecture visualizations used across decks and documentation.

----------------------------------------------------
REFERENCE MATERIAL
----------------------------------------------------

Location: /90_REFERENCE/

Glass_Box_Compliance_White_Paper.pdf
Academic framing of deterministic assurance.

NCOR_Defense_Dossier.pdf
Contextual reference material.

----------------------------------------------------
PERSONAL / NON-FRONT-FACING
----------------------------------------------------

Location: /personal/

Internal documents not part of the ARCO product surface.

====================================================
CURRENT STATUS
====================================================

Technical:
Complete enough to demonstrate non-trivial, deterministic regulatory reasoning.

Commercial:
Ready for pilot deployment as a fixed-scope assessment.

Primary Focus Going Forward:
Sequencing, packaging, and execution — not expanding the ontology surface area.
