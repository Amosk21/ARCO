# ARCO Regulatory Readiness Pilot

**Type:** Fixed-Scope Deterministic Classification Assessment  
**Duration:** 4 Weeks  
**Fee:** $25,000 USD

---

## 1. Scope of Work

ARCO will perform a deterministic regulatory classification of one (1) AI-enabled system designated by the Client.

The classification is conducted exclusively through formal ontological representation, structural validation, and deterministic query evaluation using the ARCO Assurance Framework.

The assessment is:

- Grounded in BFO distinctions (Material Entity, Disposition, Realization)
- Extended with domain-specific regulatory capability classes
- Evaluated against EU AI Act Article 6 and Annex III

No probabilistic scoring, heuristic assessment, or statistical estimation is used at any stage.

---

## 2. Deliverables

ARCO delivers exactly three artifacts.

### A. Regulatory Classification Certificate (PDF)

A formal statement of regulatory classification outcome derived from:

- The system's structurally encoded capabilities
- The classification conditions defined in Annex III

The certificate explicitly identifies the dispositions that trigger the classification.

> **Note:** High-Risk classification path is fully demonstrated; additional risk tiers are architecturally supported.

### B. Traceability Log (Machine-Readable)

A reproducible audit artifact generated directly from:

- OWL-RL entailment results
- SHACL validation results
- SPARQL ASK audit query outputs

This log demonstrates that the classification is a function of formal constraints, not discretionary judgment.

### C. Gap Analysis Report (PDF)

A precise enumeration of:

- System components
- Encoded capabilities
- Structural features

that instantiated the regulatory classification conditions, expressed in ontological terms.

---

## 3. Execution Schedule

### Week 1 — Ingestion and Boundary Definition

System documentation is mapped to explicit ontological instances.

The system boundary is fixed. No implicit assumptions are introduced.

### Week 2 — Structural Admissibility (SHACL)

SHACL constraints enforce documentation completeness and prohibit inferred or assumed capabilities.

### Week 3 — Deterministic Classification (OWL-RL Reasoning + SPARQL Audit)

OWL-RL reasoning infers regulatory classifications from bridge axioms defined in the ontology. Classifications like `HighRiskSystem` and `AnnexIII1aApplicableSystem` are entailed from system structure, not asserted.

SPARQL ASK queries then confirm that the expected entailments materialized, providing audit traceability.

### Week 4 — Determination and Handover

Final artifacts are issued.

No iterative interpretation or remediation is performed.

---

## 4. Exclusions

This engagement does not include:

- Remediation or system redesign
- Legal interpretation or advice
- Access to a hosted software platform

This is a white-glove classification determination, not a software license.

---

---

# ARCO Regulatory Classification Case

**Framework:** ARCO (Assurance & Regulatory Classification Ontology)  
**Regulatory Regime:** EU Artificial Intelligence Act  
**Relevant Provisions:** Article 6, Annex III  
**System Evaluated:** Sentinel-ID (Reference Instance)

---

## 1. Purpose

This document records a formal regulatory classification produced by the ARCO Assurance Framework.

It answers a single question:

> Given the system's structural capabilities, does a High-Risk classification under the EU AI Act follow from the asserted facts?

This classification is not probabilistic, advisory, or a legal opinion.

It is the result of formal ontological reasoning under fixed constraints.

---

## 2. System Encoding

Sentinel-ID is a reference system used to demonstrate classification mechanics.

The system includes material components that bear dispositions enabling:

- Capture of facial features
- Extraction of biometric templates
- Comparison against identity representations

No assumption is made that these capabilities are currently realized.

---

## 3. Regulatory Criterion

Under Article 6 and Annex III, AI systems intended to be used for remote biometric identification of natural persons are classified as High-Risk. Full Annex III 1(a) classification requires three conditions:

1. The system bears a biometric identification capability (reality-side disposition)
2. An intended use specification prescribes the regulated process type (directive ICE)
3. A use scenario specification constrains the affected entities (directive ICE)

Capability alone triggers latent risk detection. All three gates together trigger full Annex III applicability.

---

## 4. ARCO Classification Pipeline

### 4.1 Ontological Representation

System components and capabilities are encoded as instances aligned to BFO categories:

- Material Entities
- Dispositions
- Potential Realizations

### 4.2 Structural Validation (SHACL)

SHACL constraints enforce:

- Explicit declaration of sensing and processing components
- Completeness of system documentation
- Prohibition of inferred or assumed capabilities

Only structurally admissible systems proceed.

### 4.3 OWL-RL Reasoning

OWL bridge axioms define class-level equivalences that the reasoner uses to infer classifications. `HighRiskSystem` is inferred from capability alone. `AnnexIII1aApplicableSystem` is inferred when all three gates are satisfied. Classifications are derived, not asserted.

### 4.4 Audit Queries (SPARQL ASK)

Boolean ASK queries confirm that the expected entailments materialized. They serve as audit instruments over the reasoned graph — verifying traceability, intended use modeling, Annex III applicability, and obligation linkage.

---

## 5. Classification Result

After OWL-RL reasoning, the following classifications are inferred:

- `Sentinel_ID_System rdf:type HighRiskSystem` — from capability alone (latent risk)
- `Sentinel_ID_System rdf:type AnnexIII1aApplicableSystem` — from all three gates

SPARQL audit queries confirm both entailments materialized: `TRUE`.

From this, it follows that:

> Sentinel-ID is classified as a High-Risk AI System under Article 6 and as Annex III 1(a) applicable under the EU AI Act.

This conclusion is invariant under configuration, deployment, or intent. Each gate is independently necessary.

---

## 6. Auditability and Reproducibility

Any third party with access to:

- The ARCO ontology
- The Sentinel-ID instance data
- The published SHACL and SPARQL artifacts

can reproduce this classification without discretionary judgment.

---

## 7. Scope Note

This classification:

- Establishes regulatory classification outcome
- Does not recommend mitigation
- Does not assess proportionality
- Does not substitute for legal counsel

---

## 8. Conclusion

This case demonstrates that ARCO produces regulatory classifications as formal consequences of system structure, grounded in ontological commitments and auditable at every step.
