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

---

## 5. Deferred: Temporal Scope Modeling

**Status:** Explicitly deferred. Not modeled in current prototype.

**The Problem:** The EU AI Act undergoes amendment cycles. Annex III conditions may be added, removed, or modified by delegated acts over time. A system classified as high-risk under the current Annex III enumeration might not be high-risk under a future version — and vice versa. The current ARCO model evaluates system dispositions against a single, static snapshot of Annex III.

**What is missing:**

- **Temporal indexing of regulatory content.** `:AnnexIII_Condition_Q1` has no effective date or version stamp. The ontology cannot distinguish "Q1 as enacted 2024-08-01" from "Q1 as amended 2026-03-15."
- **Temporal qualification of determinations.** `:HighRisk_Determination_001` does not record *when* the determination was made or *which version* of the regulatory content it was evaluated against.
- **Temporal qualification of system state.** The system's component-disposition structure is asserted as atemporal fact. In reality, hardware components are added, removed, or upgraded — the disposition profile of a system changes over time.

**Why it is deferred (not omitted):**

BFO 2020 provides a temporal extension (temporalized relations via `at-some-time` / `at-all-times` qualifiers). OWL-RL does not natively support these — implementing them would require either SWRL rules, a custom reasoner extension, or a named-graph-per-snapshot approach. All three add significant complexity for a prototype whose current goal is proving the classification reasoning pattern works at all.

**Recommended future approach:**

1. Version-stamp regulatory ICEs with `dcterms:issued` and `dcterms:valid` date ranges.
2. Qualify determination instances with `dcterms:created` and a `prov:used` link to the specific regulatory version.
3. Adopt a named-graph-per-snapshot strategy for system state, enabling "as-of" queries without breaking the single-graph reasoning pipeline.

**Risk if left permanently unmodeled:** A determination certificate produced today could be invalidated by a regulatory amendment without any mechanism to detect or flag the change. This is an audit gap, not a reasoning gap — the entailment logic is correct for the snapshot it operates on.

---

## 6. Ontological Status of Defined Classes

**HighRiskSystem** and **AnnexIIITriggeringCapability** are *computational defined classes*, not natural universals.

- **HighRiskSystem** is an OWL equivalence axiom (`owl:equivalentClass`) that encodes a regulatory classification rule. No individual is ever *asserted* as a HighRiskSystem — membership is always *inferred* by the OWL-RL reasoner from the bridge axiom. It exists as a computational artifact to enable deterministic entailment, not as a claim about a natural kind.

- **AnnexIIITriggeringCapability** is a union class defined by regulatory enumeration. Its members are whichever CapabilityDisposition subclasses the EU AI Act Annex III designates as triggering conditions. It is extensible: adding a new triggering capability means adding it to the `owl:unionOf` list.

**Why this matters:** A BFO-realist audit might challenge whether these classes "carve nature at its joints." They do not — and are not intended to. They carve *regulation* at its joints, translating legal enumeration into machine-checkable equivalence. This is documented explicitly in `ARCO_core.ttl` via rdfs:comment annotations on both classes.
