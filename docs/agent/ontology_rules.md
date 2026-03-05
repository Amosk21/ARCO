# Ontology Rules

## Hard Constraints (NEVER violate)

1. **BFO/CCO Maximal Alignment**: Every class traces to BFO 2020. Every relation uses BFO or RO IRIs. No invented object properties. New domain classes must be proper subclasses of existing BFO/CCO classes with explicit justification. Reuse CCO IRIs locally with proper OWL typing (`owl:Class`, `owl:ObjectProperty`).

2. **No Ad-Hoc Relations**: No custom object properties. Use existing BFO/RO/IAO/CCO relations. For "intended use," use DirectiveICE + `cco:prescribes` pattern.

3. **Backward Compatibility**: Do not delete existing classes, instances, or inference chains. Sentinel-ID demo must pass after any change. Additions only.

4. **Reality vs. Representation**: Capabilities = reality-side (BFO dispositions in independent continuants). Regulatory provisions/classifications = representation-side (IAO ICEs). Never conflate.

5. **Deterministic Pipeline**: OWL reasoning + SPARQL ASK only. No probabilistic/LLM classification.

6. **Relation Vocabulary**: Use `ro:0000091` (has_disposition), NOT `ro:0000053` (bearer_of).

7. **No Future Particulars**: No instances of unoccurred processes. Intent = directive ICEs about universals (classes), not instantiated future events.

8. **Legal ≠ Biological**: "Natural person" = `NaturalPersonRole ⊑ Role`, not a subclass of Object/Person. No person instances or role-bearing axioms in demo — use `iao:0000136` aboutness only.

## Ontological Patterns

### Intended Use (CCO Directive ICE + prescribes)
```turtle
:IntendedUseSpecification rdfs:subClassOf cco:DirectiveInformationContentEntity .
:Sentinel_IntendedUse_001 a :IntendedUseSpecification ;
  cco:prescribes :RemoteBiometricIdentificationProcessType ;
  iao:0000136 :Sentinel_ID_System ;
  iao:0000136 :RemoteBiometricIdentificationProcessType .
```
Reads: "directive artifact about the system that prescribes a remote biometric identification process type."

### Use Scenario (affected entities)
```turtle
:UseScenarioSpecification rdfs:subClassOf cco:DirectiveInformationContentEntity .
:Sentinel_UseScenario_001 a :UseScenarioSpecification ;
  iao:0000136 :Sentinel_ID_System ;
  iao:0000136 :RemoteBiometricIdentificationProcessType ;
  iao:0000136 cco:Person ;
  iao:0000136 :NaturalPersonRole .
```
Three-gate: capability (reality) + intended use (process prescribed) + scenario (who affected).

### Regulatory Provisions
Annex III conditions are `RegulatoryContent ⊑ cco:DirectiveInformationContentEntity` instances.
- `cco:prescribes` the regulated process type (DirectiveICE → Process — the Three D's pattern)
- `iao:0000136` references ALL regulated universals — capability, process type, affected role (traceability/audit)
- Both relations co-exist on the same instance; `cco:prescribes` is the stronger, semantically precise link

### ICE Typing (Three D's)
- **Directive ICE** (`cco:DirectiveInformationContentEntity`): `RegulatoryContent`, `IntendedUseSpecification`, `UseScenarioSpecification`, `ComplianceObligationSpecification` — prescribe behavior
- **Descriptive ICE** (`cco:DescriptiveInformationContentEntity`): `InformationOutput` (incl. `AssessmentDocumentation`), `ComplianceDetermination` — report states of affairs

### Classification Determination
`HighRiskDetermination` ⊑ `ComplianceDetermination` ⊑ `DescriptiveInformationContentEntity`. Is_about system AND Annex III condition. Output of process (`cco:has_output`).

### Adding a New Annex III Category
Use the three-gate pattern:
1. Add `XCapability ⊑ CapabilityDisposition` to `ARCO_core.ttl`
2. Extend `AnnexIIITriggeringCapability` union in `ARCO_core.ttl` (add new capability)
3. Add `XProcess ⊑ bfo:0000015` to `ARCO_governance_extension.ttl`
4. Add `AnnexIIIXApplicableSystem` with three-gate equivalentClass to `ARCO_governance_extension.ttl`
5. Add instances file `ARCO_instances_X.ttl` with full SHACL-compliant structure
6. Add `AnnexIII_Condition_X` regulatory content instance with `cco:prescribes` + `iao:0000136`
7. Add SPARQL entailment check + cross-category non-entailment checks
8. Update pipeline to load new instances and run new checks

### Component-Level Disposition Tracing
System (ObjectAggregate) `has_part` SystemComponent. SystemComponent `has_disposition` CapabilityDisposition. Traces regulatory exposure to the component bearing the capability.

## What NOT To Do

- Do not rewrite HighRiskSystem equivalentClass axiom (keep capability-based = latent risk)
- Do not model all 8 Annex III categories at once — extend one category at a time, pipeline must pass after each
- Do not create separate files per Annex III item
- Do not add CCO as full import — local stubs with proper OWL typing
- Do not refactor directory structure
- Do not touch CI workflow unless pipeline output format changes
- Do not model NaturalPerson as biological subclass — use `cco:Person` + `NaturalPersonRole ⊑ Role`
- Do not create Person instances or role-bearing axioms — aboutness only
