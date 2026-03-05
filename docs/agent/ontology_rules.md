# Ontology Rules

## Evaluating Any Addition — Three Standards

Before adding any class, relation, axiom, instance, or SPARQL query, evaluate against all three:

### 1. Upper Ontology Compliance
- Every class must trace to BFO 2020. Every relation must use BFO/RO/IAO/CCO IRIs. No invented properties.
- The test: would Barry Smith or John Beverley find this principled? Can the modeling decision be backed by a specific BFO/CCO paper, definition, or formal commitment? If the answer is "I think so" rather than "yes, because [citation/principle]," revisit the decision.
- When in doubt, use a more general existing class rather than creating a new subclass. Specificity must be earned by a genuine ontological distinction, not convenience.

### 2. Genuine Reasoning vs. Pattern Matching
- An inference earns its place only if removing its enabling axiom causes the reasoner to stop drawing the conclusion. Run the negative test: if the conclusion still holds after removing the axiom, the axiom is not doing reasoning work.
- Equivalence axioms (`owl:equivalentClass`) do real reasoning. `rdfs:subClassOf` with a single named superclass and no further restrictions does not — it is taxonomy, not inference.
- If the same pipeline output can be produced by adding a direct `rdf:type` assertion to the instance, the axiom chain is not reasoning — it is documented guessing.

### 3. Business-Owner Traceability
- Every addition must connect to a person who built an AI system and needs a compliance determination under the EU AI Act (or future legislation).
- The test: "This addition tells the business owner [X], because [Y], and without it they would be stuck at [Z]." If you cannot complete that sentence concretely, the addition is not ready.
- Ontological correctness alone is not sufficient justification. A correctly typed class that produces no query result, inference, or certificate content visible to the user adds ontological overhead without value. Build the output first or remove the addition.

---

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
Annex III conditions are ICE instances. `iao:0000136` references ALL regulated universals — capability, process type, affected role. Interoperable across systems.

### Classification Determination
`HighRiskDetermination` ⊑ `ComplianceDetermination` (ICE). Is_about system AND Annex III condition. Output of process (`cco:has_output`).

### Component-Level Disposition Tracing
System (ObjectAggregate) `has_part` SystemComponent. SystemComponent `has_disposition` CapabilityDisposition. Traces regulatory exposure to the component bearing the capability.

## What NOT To Do

- Do not rewrite HighRiskSystem equivalentClass axiom (keep capability-based = latent risk)
- Do not model all 8 Annex III categories — biometrics only
- Do not create separate files per Annex III item
- Do not add CCO as full import — local stubs with proper OWL typing
- Do not refactor directory structure
- Do not touch CI workflow unless pipeline output format changes
- Do not model NaturalPerson as biological subclass — use `cco:Person` + `NaturalPersonRole ⊑ Role`
- Do not create Person instances or role-bearing axioms — aboutness only
