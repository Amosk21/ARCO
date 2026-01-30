# ARCO Regulatory Determination Case

**Deterministic Risk Classification Under the EU AI Act**

| Field | Value |
|-------|-------|
| System Evaluated | Sentinel-ID (Reference Instance) |
| Assessment Framework | ARCO (Assurance & Regulatory Classification Ontology) |
| Regulatory Regime | EU Artificial Intelligence Act |
| Relevant Provisions | Article 6, Annex III |
| Assessment Type | Formal Ontological Determination |
| Assessment Date | [Insert Date] |

---

## 1. Purpose

This document records a formal regulatory classification produced using the ARCO Assurance Framework.

It answers one question:

> **Does the evaluated system fall under the EU AI Act's High-Risk classification as a matter of logical necessity, and can that conclusion be deterministically justified and audited?**

This determination is not probabilistic, advisory, or a subjective legal opinion. It is the result of formal ontological representation, structural validation, and deterministic logical evaluation.

---

## 2. System Under Evaluation

### 2.1 System Description

Sentinel-ID is a reference AI-enabled system used to demonstrate regulatory determination mechanics.

The system includes material components that bear dispositions enabling:
- Capture of human facial features
- Extraction of biometric templates
- Comparison against identity representations

The system may be deployed in controlled-access environments.

### 2.2 Realization vs. Capability

The system is not assumed to be actively configured for biometric identification.

ARCO explicitly distinguishes between:
- **Realized Functions**: what the system is currently configured to do
- **Dispositions (Capabilities)**: what the system is capable of doing by virtue of its structure

Regulatory classification under the EU AI Act depends on capability, not intent or configuration.

---

## 3. Regulatory Criterion

Under Article 6 and Annex III, AI systems that bear the disposition to perform biometric identification of natural persons in regulated contexts are classified as High-Risk.

This criterion applies regardless of whether the capability is currently enabled.

**The regulatory question evaluated is:**

> Does Sentinel-ID bear a biometric identification disposition as defined under Annex III?

---

## 4. ARCO Determination Pipeline

### 4.1 Ontological Representation

System components, capabilities, and relations are encoded as instances in the ARCO Knowledge Graph, aligned to BFO distinctions between:
- Material Entities
- Dispositions
- Realizations

### 4.2 Structural Validation (SHACL)

SHACL constraints enforce:
- Completeness of system documentation
- Explicit declaration of sensing and processing components
- Prohibition of implicit or assumed capabilities

Only structurally admissible system representations proceed to evaluation.

### 4.3 Deterministic Evaluation (SPARQL ASK)

Boolean ASK queries test whether the encoded system satisfies the necessary and sufficient conditions for Annex III classification.

### 4.4 Semantic Framework (OWL)

OWL axioms define the class-level semantics (e.g., System bears CapabilityDisposition) that underpin classification logic. The semantic structure ensures that classification criteria are formally defined and consistently interpreted.

> **Note**: In the reference implementation, the determination artifact is explicitly modeled to demonstrate the output structure. Production deployments may invoke OWL reasoning to derive classifications automatically from capability assertions.

---

## 5. Determination Logic and Results

### 5.1 Structural Validation Result

All required system components passed SHACL validation.

This confirms:
- The system description is structurally complete
- No required regulatory attributes are missing
- No classification is derived from assumed documentation gaps

### 5.2 Deterministic Query Result

**SPARQL ASK Query**: Does the assessment documentation link the system to the relevant Annex III regulatory condition?

**Result**: `TRUE`

This result confirms the documentation links the system to the relevant regulatory condition. The underlying capability (BiometricIdentificationCapability) is modeled as a disposition borne by the system.

### 5.3 Ontological Consequence

**Given**:
- A system that bears a biometric identification disposition
- A regulatory framework that classifies such dispositions as High-Risk

**It follows by logical necessity that**:

> **Sentinel-ID is classified as a High-Risk AI System under Article 6 and Annex III of the EU AI Act.**

This conclusion is invariant under deployment configuration or stated intent.

> **Note**: In this reference case, the determination is explicitly modeled to demonstrate the artifact format. The logical necessity derives from the ontological structure: any system bearing BiometricIdentificationCapability satisfies Annex III classification conditions.

---

## 6. Determination Outcome

### 6.1 Regulatory Status

**Final Determination: HIGH-RISK AI SYSTEM**

This determination is:
- Deterministic
- Reproducible
- Auditable
- Independent of discretionary human judgment after encoding

### 6.2 Triggering Conditions

The classification is triggered by:
- Latent biometric identification capability
- Structural sufficiency to perform regulated biometric tasks
- Ontological alignment with Annex III criteria

---

## 7. Traceability and Reproducibility

### 7.1 Audit Trace

The determination is supported by:
- SHACL validation logs confirming structural admissibility
- SPARQL ASK query outputs demonstrating satisfaction of risk criteria
- Ontological mappings linking system capabilities to regulatory concepts

### 7.2 Independent Reproduction

Any third party with access to the following artifacts can independently reproduce this determination:
- The ARCO ontology
- The Sentinel-ID instance data
- The associated SHACL and SPARQL artifacts

No proprietary heuristics or opaque judgment is involved.

---

## 8. Scope Note

This determination:
- **Establishes** regulatory classification
- **Does not** recommend mitigation measures
- **Does not** assess proportionality or exemptions
- **Does not** substitute for legal counsel

---

## 9. Conclusion

This Determination Case demonstrates that ARCO produces regulatory classifications that are traceable to explicit system structure and regulatory criteria.

The result is grounded in ontological commitments, evaluated through deterministic queries, and auditable at every step.

This document serves as the reference determination against which all supporting ARCO artifacts derive their purpose.
