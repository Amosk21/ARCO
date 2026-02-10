# Operationalizing Article 6 of the EU AI Act

## Detecting Latent High-Risk Classification via Ontological Modeling

---

## Problem Context

Article 6 of the EU AI Act classifies systems as High Risk based not only on how they are deployed, but on what they are capable of doing under Annex III conditions.

### Core Risk

In manufacturing contexts, perimeter security drones may bear biometric identification capability at the hardware level, even when that capability is disabled in software. This creates latent regulatory risk.

### Technical Challenge

Legal criteria are expressed in natural language universals ("biometric", "remote", "public space"), while system specifications exist as technical artifacts. Manual review and static documentation cannot reliably track this mismatch.

### Our Approach

ARCO operationalizes Article 6 by representing legal conditions as ontological constraints and evaluating system dispositions against classification criteria, enabling deterministic high-risk classification based on what a system is, not merely what it is configured to do.

---

## Why We Created a Synthetic AI System (Sentinel-ID)

### The Challenge

Real AI systems have proprietary hardware and closed documentation, making them impractical to fully audit or understand in an academic or open setting.

### The Data Problem

Real compliance data is not publicly available, preventing transparent testing of regulatory logic.

### Our Focus

This project tests reasoning correctness, not vendor claims. We need to prove the classification logic works.

### Why Sentinel-ID?

It contains explicit latent biometric capability and its components are fully observable and modeled.

### The Advantage

Sentinel-ID allows us to evaluate Annex III classification criteria deterministically with complete transparency.

### Important Clarification

Sentinel-ID is not a guess about a real system. It is a controlled reference system designed to validate the classification reasoning pipeline.

> A synthetic system gives us the control and observability needed to rigorously test classification logic.

---

## ARCO: Ontological Classification Model (System Overview)

*[Diagram: Shows relationships between Operation, Provider + Documentation, Compliance Output, Reality, and Regulatory ICE layers]*

### Realist Core

BFO/CCO grounding for representing reality-level entities. The Sentinel-ID System has a hardware component (Sentinel FaceID Module) that bears a Biometric Identification Capability modeled as a Disposition. Dispositions inhere in the material component, not the system aggregate. When this disposition is realized in operational processes (e.g., Surveillance Run 001), those processes produce concrete outputs such as FaceData Log 001, establishing a formal link between latent capabilities and their manifestation in real-world operations.

### Regulatory Layer

IAO usage for modeling legal texts as Information Content Entities, not procedural rules. Regulatory provisions such as Annex III Condition Q1 are represented as informational entities that are the subject of classification determinations. The High-Risk Determination 001 is about both the regulatory content and the system's operational outputs, enabling traceable classification links rather than predictive classifications.

### Governance Extension

Governance graph for provider traceability, documentation, and obligation. The Provider Organization bears a Provider Role and participates in the Assessment Documentation Process 001. This process produces Assessment Documentation 001 that is formally linked to the system and the regulatory provisions. A separate Compliance Obligation Specification links the system to the responsible role-bearer and the triggering regulatory condition, making the "who is responsible for what" relationship a first-class artifact.

---

## Why the EU AI Act Must Be Modeled, Not Coded

The EU AI Act is written in natural language for human interpretation, not as executable software instructions. To enable computational reasoning about classification, we must first represent the law correctly.

### Understanding the nature of legal text:

- The Act uses natural language to communicate regulatory intent to people
- Article 6 describes how systems should be evaluated, not computational procedures
- Annex III lists conditions and categories, not executable logic rules
- Direct translation of legal language into code risks fundamental misinterpretation

### The key principle:

In this project, the law serves as a reference model that constrains and guides decisions—not as logic that autonomously makes decisions.

This approach respects what law actually is: a framework for human judgment, not an algorithm.

---

## Why There Are Two EU AI Act Models

The EU AI Act serves two distinct roles, requiring two distinct models.

### Model 1: Classification Structure

- Represents Article 6 and Annex III classification content
- Captures lists, conditions, and classification criteria
- Answers: "What makes a system High Risk?"

### Model 2: Governance & Authority

- Represents who defines, updates, and enforces the rules
- Models EU AI Board, Commission, and delegated acts
- Answers: "Who has authority over these rules, and how they change over time?"

### Why they are separate:

- Classification logic should not change when governance changes
- Governance can evolve without breaking system reasoning

> Key takeaway: Separating regulatory structure from governance preserves clarity, realism, and long-term extensibility.

---

## Article 6 EU AI Act

*[Diagram: Shows governance model with EU AI Board, European Commission, Board Authority Role, Commission Authority Role, Consultation Process, Delegated Act Process, Five-Year Delegation Period, Provider Organization, Provider Role, Assessment Documentation Process, Classification Criteria, Provider Compliance Obligation, ClassificationProcess, Annex III List, Annex III Conditions, Modified Annex III Conditions]*

---

## Assessment Documentation Content Model

*[Diagram: Shows Assessment Documentation Content connected to Union Harmonisation Legislation, Guideline Content, AI System, with paths through Annex I List, Annex III List, Classification Criteria, Classification Process, High-Risk Determination, High-Risk Role, and High-Risk Determination Content]*

---

## EU AI Act: Formal Regulatory Source Model

Article 6 & Annex III represented as ontological classification criteria, not executable logic

### Regulatory Source

EU AI Act provisions modeled as IAO / CCO Information Content Entities (Annex III Lists, Conditions, Classification Criteria)

### Classification Mechanism

Article 6 specifies how systems are evaluated, not outcomes → Referenced by a Classification Process, not procedural rules

### Constraint Role

Regulation governs classification. High-risk determinations occur only when asserted system facts satisfy Annex III conditions

> This regulatory model is referenced by the ARCO ontology to enable deterministic high-risk classification without embedding legal text into code.

---

## The Interpretability Gap

Law describes risk conditions; systems describe what they are built to do.

### Regulatory Reality

- Expressed as natural language universals, not schemas
- Defines risk by capability, not current behavior
- Applies to classes of systems, not individual deployments

### Technical Reality

- Systems are physical assemblies with latent capabilities
- Hardware may support restricted functions even when disabled
- Risk is not explicitly labeled anywhere in system data

Traditional ETL pipelines operate at the schema level, not the semantic level. Purely generative AI is dangerous—LLMs might hallucinate classification outcomes. Latent capability creates latent liability. We need a system that converts probabilistic signal (text) into deterministic fact (logic).

---

## Architecture & Project Alignment

### 3-Stage Architecture

**Stage 1: Interpretation (Neuro)**
LLM extracts capabilities from unstructured text

**Stage 2: Representation (Symbolic)**
BFO grounding represents extracted claims as axioms

**Stage 3: Classification (Logic)**
OWL-RL reasoning infers classifications from bridge axioms; SPARQL queries provide audit confirmation

> Uses LLM for recall, Ontology for precision, Logic for determination

---

## LLMs as Candidate Generators, Not Judges

### RAW OUTPUT

| Aspect | Description |
|--------|-------------|
| **Probabilistic** | LLM proposes candidate capabilities based on legal and technical text |
| **Noisy** | Output may include irrelevant or invalid relationships |
| **Ungrounded** | LLM output is a hypothesis, not a classification conclusion |
| **No Direct Touch** | LLM never touches classification conclusions directly—only proposes possibilities |

### GROUNDED

| Aspect | Description |
|--------|-------------|
| **Typed** | Candidates are mapped to explicit BFO classes and relations |
| **Validated** | Only assertions consistent with BFO constraints are retained |
| **Constrained** | If LLM hallucinates a relationship that violates BFO constraints, system rejects it |
| **Asserted** | Resulting Turtle is machine-readable and reasoner-ready |

> LLMs interpret text. Ontologies define structure and constraints.

---

## Grounding Capability in Reality

### Capability

**BFO** – Disposition inhering in a material component, existing even when latent or inactive

### System

**BFO** – Object Aggregate whose material components bear capability dispositions, independent of software state

### Regulation

**IAO** – Legal information content that refers to and constrains system dispositions

> Capability modeled as Disposition detects regulatory exposure based on what a machine IS, not just what it is DOING – biometric capability exists in hardware even when software is disabled.

---

## Deterministic Classification

The Logic Layer: No AI involved—formal logic only

### Semantic Framework

OWL axioms define class relationships. Systems have material components that bear dispositions via `ro:has_disposition`. Classification is inferred by OWL-RL reasoning from bridge axioms — `HighRiskSystem` fires on capability alone (latent risk detection), while `AnnexIII1aApplicableSystem` requires all three gates: capability + intended use + use scenario.

```turtle
:HighRiskSystem owl:equivalentClass [
  owl:intersectionOf (
    :System
    [ owl:onProperty bfo:0000051 ;   # has part
      owl:someValuesFrom [
        owl:onProperty ro:0000091 ;  # has disposition
        owl:someValuesFrom :AnnexIIITriggeringCapability
      ]
    ]
  )
] .
```

### Classification Evaluation

SPARQL ASK queries serve as audit confirmations that entailments materialized correctly. The classification itself is an OWL entailment, not a pattern match:

```sparql
ASK WHERE {
  :Sentinel_ID_System rdf:type :AnnexIII1aApplicableSystem .
}
```

### Logical Consequence

If the structural prerequisites exist, classification follows as an OWL entailment — not asserted, derived.

### Auditability

This is deterministic evaluation, not approximation. Every classification traces back to specific component dispositions, intended use directives, and use scenario specifications.

---

## Operational Validation & Governance

### OWL-RL: Entailment-First Classification

Classifications like `HighRiskSystem` and `AnnexIII1aApplicableSystem` are inferred by the OWL-RL reasoner from bridge axioms — not asserted in the data. This means classification is a logical consequence of system structure, not a label someone attached.

### SHACL: Documentary Completeness

SHACL validates the reasoned graph for structural completeness: assessment documentation links to system and regulatory content, intended use specifications prescribe process types, use scenario specifications reference affected entities. Invalid or incomplete graphs are rejected before audit.

### SPARQL: Audit Confirmation

SPARQL ASK queries confirm that expected entailments materialized. They serve as audit instruments — the classification itself is an OWL entailment, and the queries verify it.

### Governance Extension

The governance extension links classification determinations to real-world responsibility.

Each classification is traceable from the system, through the provider role, to the responsible organization. Compliance Obligation Specifications make the "who bears responsibility for what" relationship explicit and queryable.

> OWL handles classification. SHACL enforces documentary completeness. SPARQL provides audit traceability. Governance links everything to accountable entities.

---

## Why Glass-Box Classification Scales

### Healthcare

Clinical AI systems embed latent diagnostic and biometric capabilities. Regulatory classification depends on provable alignment between system capabilities and approved clinical use, not post-hoc model explanations.

### Finance

Financial systems contain dormant decision pathways that can activate regulatory obligations. Glass-box classification separates what a system can do from what it is authorized to do, enabling deterministic audit and accountability.

### Defense

Defense systems are regulated based on capability, not deployment intent. Classification requires traceable proof that classified capabilities are detected and governed before operational use.

> The neuro-symbolic pattern scales because it enforces a hard boundary between probabilistic interpretation and deterministic validation, enabling classification reasoning wherever latent capability creates regulatory exposure.

---

## From Black-Box to Glass-Box

*[Image: AI Compliance Automation displayed in a glass display case]*

**Thank you.**

---

## Appendix: Key Terminology

| Term | Definition |
|------|------------|
| **Disposition** | A BFO realizable entity that inheres in a bearer and may or may not be realized in a process |
| **Classification** | Categorical assignment of regulatory status based on structural criteria |
| **SHACL** | Shapes Constraint Language for validating RDF graph structure |
| **SPARQL ASK** | Boolean query returning TRUE/FALSE for audit traceability |
| **ICE** | Information Content Entity (IAO) – representation-side artifacts |
| **Bearer** | The entity in which a disposition inheres |
