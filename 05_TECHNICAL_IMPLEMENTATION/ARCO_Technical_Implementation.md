# ARCO: Technical Implementation & Architectural Decisions

**System:** Neuro-Symbolic Regulatory Classification Engine  
**Version:** 1.0 (Prototype)  
**Date:** December 22, 2025

---

## 1. Architectural Decision: Modeling Latent Risk via BFO Dispositions

**The Problem:** Traditional classification tags (e.g., "High Risk: True") fail to capture conditional capabilities. A system may have hardware for biometric identification (High Risk) that is currently disabled via software.

**The Solution:** Dispositions are modeled as BFO Realizable Entities that inhere in material components, not in the system aggregate directly. The system relates to its components via `bfo:has_part`, and each component carries its dispositions via `ro:has_disposition`. This traces regulatory exposure to the specific component responsible.

**Impact:** Latent capability is detected even when software is configured to "Off," and the evidence path traces through the specific component that bears the disposition.

### Implementation Artifact (ARCO_core.ttl)

```turtle
:System rdf:type owl:Class ;
  rdfs:label "AI System" ;
  rdfs:subClassOf bfo:0000027 ; # Object Aggregate
  rdfs:subClassOf [
    a owl:Restriction ;
    owl:onProperty bfo:0000051 ; # has part
    owl:someValuesFrom :SystemComponent
  ] .

:HardwareComponent rdf:type owl:Class ;
  rdfs:subClassOf :SystemComponent ;
  rdfs:subClassOf [
    a owl:Restriction ;
    owl:onProperty ro:0000091 ; # has disposition
    owl:someValuesFrom :CapabilityDisposition
  ] .
```

---

## 2. Architectural Decision: Structural Integrity via SHACL

**The Problem:** OWL Reasoners (Open World Assumption) are poor at validating data completeness. They infer missing data rather than flagging it as an error.

**The Solution:** We inject a SHACL Validation Layer (pyshacl) prior to the classification evaluation. This enforces a "Closed World" constraint on the graph, rejecting any AssessmentDocumentation that fails to link a System to its Regulatory Content.

**Impact:** Prevents "Garbage In, True Out" scenarios where incomplete data passes audit silently.

### Implementation Artifact (assessment_documentation_shape.ttl)

```turtle
#################################################################
# Shape: Enforce Linkage between System and Regulation
#################################################################

:AssessmentDocumentationShape
  a sh:NodeShape ;
  sh:targetClass :AssessmentDocumentation ;

  sh:property [
    sh:path iao:0000136 ;          # is about
    sh:class :System ;
    sh:minCount 1 ;                # Constraint: Must explicitly link to System
  ] ;

  sh:property [
    sh:path iao:0000136 ;          # is about
    sh:class :RegulatoryContent ;
    sh:minCount 1 ;                # Constraint: Must explicitly link to Regulation
  ] .
```

---

## 3. Architectural Decision: Deterministic Audit via SPARQL ASK

**The Problem:** Auditors require binary (Pass/Fail) verdicts. Standard knowledge graph queries (SELECT) return lists that require post-processing interpretation, introducing ambiguity.

**The Solution:** We utilize SPARQL ASK queries which return a boolean `xsd:boolean` value. The query pattern matches whether classification conditions are satisfied.

**Impact:** The output is mathematically deterministic and machine-readable (JSON Boolean).

### Implementation Artifact (check_assessment_traceability.sparql)

```sparql
PREFIX : <https://arco.ai/ontology/core#>
PREFIX iao: <http://purl.obolibrary.org/obo/IAO_>

# Objective: Verify if AssessmentDoc connects System to Annex III Condition
ASK WHERE {
  :AssessmentDoc_001 iao:0000136 :Sentinel_ID_System .
  :AssessmentDoc_001 iao:0000136 :AnnexIII_Condition_Q1 .
}

# Output: TRUE (Verification Successful)
```

---

## 4. Execution Pipeline

**Orchestration:** The Python runtime (rdflib + pyshacl + owlrl) manages load, reasoning, validation, and audit in sequence.

### Pipeline Sequence (run_pipeline.py)

```
1. LOAD      — Parse core ontology + governance extension + instance data
2. REASON    — OWL-RL closure (owlrl) materializes entailments
3. SHACL     — Structural validation against the reasoned graph
4. AUDIT     — SPARQL ASK queries verify entailment results
5. CERTIFY   — Emit regulatory determination certificate + artifacts
```

The pipeline runs seven checks: SHACL conformance, traceability, latent risk detection, intended use modeling, Annex III 1(a) entailment, obligation linkage, and HighRiskSystem entailment.

OWL-RL reasoning runs first because classifications like `HighRiskSystem` and `AnnexIII1aApplicableSystem` are inferred from bridge axioms, not asserted. SHACL validates the reasoned graph. SPARQL queries serve as audit confirmations that the expected entailments materialized.

**Design Principle:** OWL handles classification. SHACL enforces documentary completeness. SPARQL provides audit traceability. Together they produce deterministic, auditable regulatory determinations.
