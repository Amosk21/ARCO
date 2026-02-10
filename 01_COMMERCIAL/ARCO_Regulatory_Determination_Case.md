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

Under Article 6 and Annex III, AI systems intended to be used for remote biometric identification of natural persons are classified as High-Risk. Full Annex III 1(a) classification requires three conditions:

1. The system bears a biometric identification capability (reality-side disposition)
2. An intended use specification prescribes the regulated process type (directive ICE)
3. A use scenario specification constrains the affected entities (directive ICE)

Capability alone triggers latent risk detection. All three gates together trigger full Annex III applicability.

**The regulatory question evaluated is:**

> Does Sentinel-ID satisfy all three Annex III 1(a) classification conditions?

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

### 4.3 OWL-RL Reasoning

OWL bridge axioms define class-level equivalences that the reasoner uses to infer classifications. `HighRiskSystem` is inferred from capability alone. `AnnexIII1aApplicableSystem` is inferred when all three gates are satisfied. Classifications are derived, not asserted.

### 4.4 Audit Queries (SPARQL ASK)

Boolean ASK queries confirm that the expected entailments materialized. They serve as audit instruments over the reasoned graph — verifying traceability, intended use modeling, Annex III applicability, and obligation linkage.

---

## 5. Determination Logic and Results

### 5.1 Structural Validation Result

All required system components passed SHACL validation.

This confirms:
- The system description is structurally complete
- No required regulatory attributes are missing
- No classification is derived from assumed documentation gaps

### 5.2 Entailment Result

After OWL-RL reasoning, the following classifications are inferred (not asserted):

- `Sentinel_ID_System rdf:type HighRiskSystem` — from capability alone (latent risk)
- `Sentinel_ID_System rdf:type AnnexIII1aApplicableSystem` — from all three gates

SPARQL audit queries confirm both entailments materialized: `TRUE`.

### 5.3 Ontological Consequence

**Given**:
- A system whose hardware component bears a biometric identification disposition (Gate 1)
- An intended use specification prescribing remote biometric identification (Gate 2)
- A use scenario specification constraining affected entities to natural persons (Gate 3)

**It follows by logical necessity that**:

> **Sentinel-ID is classified as a High-Risk AI System under Article 6 and as Annex III 1(a) applicable under the EU AI Act.**

This conclusion is invariant under deployment configuration. Each gate is independently necessary — removing any one prevents the Annex III 1(a) classification from being inferred.

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
- Latent biometric identification capability (hardware component bears BiometricIdentificationCapability)
- Intended use prescribing the regulated process type (remote biometric identification)
- Use scenario constraining affected entities (natural persons)
- Compliance obligation linking the system to the responsible provider role

---

## 7. Traceability and Reproducibility

### 7.1 Audit Trace

The determination is supported by:
- OWL-RL entailment producing inferred classifications from bridge axioms
- SHACL validation confirming documentary completeness over the reasoned graph
- SPARQL ASK audit queries confirming traceability, intended use, Annex III applicability, and obligation linkage
- Gate-removal regression tests proving each gate is independently necessary

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
