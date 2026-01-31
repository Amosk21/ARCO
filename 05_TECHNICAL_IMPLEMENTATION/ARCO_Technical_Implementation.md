# ARCO: Technical Implementation & Architectural Decisions

**System:** Neuro-Symbolic Regulatory Classification Engine  
**Version:** 1.0 (Prototype)  
**Date:** December 22, 2025

---

## 1. Architectural Decision: Modeling Latent Risk via BFO Dispositions

**The Problem:** Traditional classification tags (e.g., "High Risk: True") fail to capture conditional capabilities. A system may have hardware for biometric identification (High Risk) that is currently disabled via software.

**The Solution:** We utilize BFO 2.0 Dispositions to model capability as a "Realizable Entity" that inheres in the hardware (Object Aggregate), independent of its current Process realization.

**Impact:** This allows the system to flag "Latent Liability" even when the software is configured to "Off."

### Implementation Artifact (ARCO_core.ttl)

```turtle
#################################################################
# REALITY-SIDE UNIVERSALS (BFO)
# Decision: Model System as Object Aggregate bearing Dispositions
#################################################################

:System rdf:type owl:Class ;
  rdfs:label "AI System" ;
  rdfs:subClassOf bfo:0000027 ; # Object Aggregate
  rdfs:subClassOf [
    a owl:Restriction ;
    owl:onProperty ro:0000053 ; # bearer of
    owl:someValuesFrom :CapabilityDisposition
  ] .

:BiometricIdentificationCapability rdf:type owl:Class ;
  rdfs:label "Biometric Identification Capability" ;
  rdfs:comment "A capability-disposition whose realizations include identifying or verifying individuals via biometric characteristics." ;
  rdfs:subClassOf :CapabilityDisposition .

# Note: This exists whether realized in a process or not.
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

## 4. Execution Pipeline (Neuro-Symbolic Bridge)

**Orchestration:** The Python runtime (rdflib + pyshacl) manages the transition from probabilistic extraction (LLM-generated instances) to deterministic validation.

### Pipeline Code (run_pipeline.py)

```python
def main() -> None:
    g = load_union_graph(CORE, GOV, INSTANCES)
    print("Loaded triples:", len(g))

    # Step 1: Classification Evaluation (SPARQL)
    run_sparql_ask(g)
    
    # Step 2: Structural Validation (SHACL)
    # Only valid structures produce reliable classifications
    run_shacl(g)
```

**Design Principle:** SHACL validation ensures structural completeness. SPARQL ASK queries test whether classification conditions are satisfied. Together they produce deterministic, auditable regulatory determinations.
