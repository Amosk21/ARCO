# ARCO — Claude Code Project Instructions

## Project Identity

ARCO (Assurance & Regulatory Classification Ontology) is a BFO/CCO-aligned ontological framework for deterministic AI system risk classification under the EU AI Act. It produces regulatory determinations as logical consequences of modeled system structure, not probabilistic assessments.

## Repository Structure

```
03_TECHNICAL_CORE/
  ontology/
    ARCO_core.ttl              — Core ontology (BFO-aligned classes, bridge axioms)
    ARCO_governance_extension.ttl — Provider roles, documentation workflow
    ARCO_instances_sentinel.ttl   — Sentinel-ID demo system instances
  validation/
    assessment_documentation_shape.ttl — SHACL shapes
  reasoning/
    check_high_risk_inference.sparql
    check_assessment_traceability.sparql
    detect_latent_risk.sparql
    ask_provider_role_inheres_in_org.sparql
  scripts/
    run_pipeline.py            — Main execution pipeline
```

## Tech Stack

- Python 3.10+, rdflib, pyshacl, owlrl
- OWL 2 (Turtle syntax), SHACL, SPARQL ASK queries
- OWL-RL reasoning profile via owlrl library
- GitHub Actions CI (`.github/workflows/arco-demo.yml`)

## Build & Verify Commands

```bash
pip install -r requirements.txt
python 03_TECHNICAL_CORE/scripts/run_pipeline.py
```

Pipeline must: load ontology + instances → run OWL-RL reasoning → run SHACL validation → run all SPARQL ASK queries → emit REGULATORY DETERMINATION CERTIFICATE → write artifacts to runs/demo/

## Hard Constraints (NEVER violate these)

1. **BFO/CCO Maximal Alignment**: Every class must trace to a BFO 2020 category. Every relation must use BFO or RO IRIs. No invented object properties. If CCO provides an applicable class or relation, use it. If a new domain class is needed, it must be a proper subclass of an existing BFO/CCO class with explicit justification. When reusing CCO IRIs locally (without full import), declare them with proper OWL typing (`owl:Class`, `owl:ObjectProperty`) — not just `rdfs:label` triples.

2. **No Ad-Hoc Relations**: Do NOT create custom object properties like `intended_for_use_in`, `deployed_in_context`, `affects_persons`, etc. Use existing BFO/RO/IAO/CCO relations. When modeling "intended use," use the CCO Directive Information Content Entity + `cco:prescribes` pattern (see Ontological Patterns below).

3. **Backward Compatibility**: Do not delete existing classes, instances, or inference chains. The Sentinel-ID demo must continue to pass all existing checks after any change. New additions must be additive.

4. **Reality vs. Representation Separation**: System capabilities are reality-side (BFO dispositions inhering in independent continuants). Regulatory provisions, plans, and classifications are representation-side (IAO Information Content Entities). Never conflate these.

5. **Deterministic Pipeline**: Classification must be derivable via OWL reasoning + SPARQL ASK queries. No probabilistic, scoring, or LLM-based classification in the pipeline itself.

6. **Relation Vocabulary**: Use `ro:0000091` (has_disposition) for disposition relations, NOT `ro:0000053` (bearer_of). This is already established in the codebase.

7. **No Future Particulars**: Do NOT create instances of processes that have not occurred. Intent is represented via directive information entities that are *about* universals (classes), not as instantiated future events. If modeling "the system is intended for biometric identification," create a Directive ICE that `cco:prescribes` a process *type* (class) — not a process instance.

8. **Legal Categories Are Not Biological Kinds**: "Natural person" is a legal designation under EU law, not a biological universal. Model it as `NaturalPersonRole ⊑ bfo:0000023 (Role)`, not as a subclass of Object or Person. Anchor the role to a person continuant (`cco:Person`) so readers know what kind of entity bears it, but do NOT create person instances or role-bearing axioms for the demo. This applies to any legal status or classification.

## Ontological Patterns (Use These)

### Modeling "Intended Use" (CCO-Aligned)

The EU AI Act classifies systems based on "intended use" (Annex III: "AI systems intended to be used for..."). In BFO/CCO, intended use is NOT a relation from system to context. It is a **Directive Information Content Entity** that **prescribes** a process type.

**CCO Pattern**: `cco:DirectiveInformationContentEntity` uses `cco:prescribes` (domain: DirectiveICE, range: Entity). The `prescribes` relation means "serves as a rule or guide for an Occurrent, or serves as a model for a Continuant."

**Implementation**:
```turtle
# Class level (in governance extension)
:IntendedUseSpecification rdfs:subClassOf cco:DirectiveInformationContentEntity .

# Instance level
:Sentinel_IntendedUse_001 a :IntendedUseSpecification ;
  cco:prescribes :RemoteBiometricIdentificationProcessType ;
  iao:0000136 :Sentinel_ID_System ;
  iao:0000136 :RemoteBiometricIdentificationProcessType .
```

This means: "There exists a directive information artifact that is about the Sentinel system and that prescribes a remote biometric identification process type."

### Modeling Use Scenario Context (CCO-Aligned)

Annex III items specify not just capability and process, but **affected entities** ("of natural persons"). This context is modeled as a separate Directive ICE — a `UseScenarioSpecification` — that constrains the realization context. It is `iao:0000136` (is_about) the system, the process type, the person universal, and the legal role:

```turtle
:UseScenarioSpecification rdfs:subClassOf cco:DirectiveInformationContentEntity .

:Sentinel_UseScenario_001 a :UseScenarioSpecification ;
  iao:0000136 :Sentinel_ID_System ;
  iao:0000136 :RemoteBiometricIdentificationProcessType ;
  iao:0000136 cco:Person ;
  iao:0000136 :NaturalPersonRole .
```

This reads: "the scenario concerns persons, specifically under the legal designation natural person." It gives a **three-gate** Annex III classification: capability (reality-side) + intended use (process prescribed) + scenario (who is affected).

### Modeling Regulatory Provisions

Annex III conditions are ICE instances. They use `iao:0000136` (is_about) to reference ALL universals they regulate — capability, process type, and affected role. This makes conditions interoperable across systems (different AI systems can be evaluated against the same regulatory condition without bespoke mapping).

### Modeling Classification Determination

`HighRiskDetermination` is a subclass of `ComplianceDetermination` (which is an ICE). It is `iao:0000136` (is_about) the system AND the Annex III condition. It is the **output** of a process (`cco:has_output`).

### Component-Level Disposition Tracing

AI systems (ObjectAggregate) `bfo:0000051` (has_part) SystemComponents. SystemComponents `ro:0000091` (has_disposition) CapabilityDispositions. This traces regulatory exposure to the component that bears the capability — the "latent capability" insight. Preserve this pattern.

## EU AI Act Alignment Requirements

### Annex III Structure
Every Annex III item follows the pattern: "AI systems **intended to be used** for [capability/process] **of** [affected entities] in [domain context]". Full classification requires:
- The system bears the relevant capability disposition (reality-side)
- There exists an intended use specification prescribing the regulated process type (directive ICE)
- There exists a use scenario specification constraining the realization context to affected entities (directive ICE)

### Article 6(3) Derogation
An Annex III system may NOT be high-risk if it "does not pose a significant risk of harm" — specifically if:
- (a) intended to perform a narrow procedural task
- (b) intended to improve the result of a previously completed human activity
- (c) intended to detect decision-making patterns without replacing/influencing assessment
- (d) intended to perform a preparatory task

**Exception to the exception**: profiling of natural persons ALWAYS triggers high-risk.

Model derogation claims as ICE artifacts (descriptive, asserting non-significance) that can be queried.

### Annex III Category 1 — Biometrics (Current Focus)
- 1(a): Remote biometric identification systems (NOT verification-only)
- 1(b): Biometric categorisation by sensitive attributes
- 1(c): Emotion recognition

The Sentinel-ID demo covers 1(a). The exclusion for "biometric verification the sole purpose of which is to confirm identity" is important and should eventually be modelable.

## Current Known Issues (Fix These)

**NOTE: The pipeline (Phase 0) is already fixed and working.** It runs OWL-RL reasoning, all SPARQL queries, SHACL validation, emits the certificate, and prints "ALL CHECKS PASSED." The issues below are what remain:

1. **Instance typing**: `HighRisk_Determination_001` is typed as `:ComplianceDetermination` but should be `:HighRiskDetermination` (which subclasses it).

2. **No intended use modeling**: Current bridge axiom fires on capability alone without intended use context. This is ontologically incomplete per Annex III.

3. **Hardware-only component constraint**: `SystemShape` SHACL requires hardware components only. Should allow broader `SystemComponent` class.

## Regression Testing

Run `python 03_TECHNICAL_CORE/scripts/run_pipeline.py` after every coherent unit of change. Pass criteria: OWL-RL reasoning runs, all SPARQL queries return True, SHACL conforms, certificate emits, "ALL CHECKS PASSED" prints, exit 0. If a step breaks the pipeline, fix it before proceeding. Do not batch changes that touch existing triples, restrictions, or shapes — test immediately.

## What NOT To Do

- Do not rewrite the HighRiskSystem OWL equivalentClass axiom yet (keep capability-based inference as "latent risk detection")
- Do not model all 8 Annex III categories — biometrics only for now
- Do not create a separate file for every Annex III item
- Do not add CCO as a full import (too heavy) — declare needed CCO classes/relations locally with their IRIs and proper OWL typing
- Do not refactor directory structure
- Do not touch GitHub Actions workflow files unless pipeline output format changes require it
- Do not model NaturalPerson as a biological subclass — if you need a person universal, use `cco:Person`; represent "natural person" as `NaturalPersonRole ⊑ bfo:Role`
- Do not create Person instances or role-bearing axioms for the demo — use aboutness (`iao:0000136`) only
