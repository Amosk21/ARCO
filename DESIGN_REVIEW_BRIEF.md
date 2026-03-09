# ARCO: Technical State Briefing for Cross-Model Design Review

## What this is

ARCO is a BFO/CCO-aligned OWL ontology that produces deterministic EU AI Act risk classifications. The pipeline is: load TTL files → OWL-RL reasoning (owlrl) → SHACL validation → SPARQL ASK queries → certificate artifact. There are no LLMs in the classification pipeline. The system is designed so that a company building an AI product can run this pipeline against their system description and receive a defensible, traceable output: "Your system is (or is not) Annex III 1(a) applicable under the EU AI Act, and here is the reasoning chain."

The ontology upper layer is BFO 2020 + RO + IAO + CCO. No custom object properties are used where a standard one exists. The design standard is: if Barry Smith or John Beverley reviewed a modeling decision, they should find it principled and non-arbitrary.

---

## The three non-negotiable design standards

Every addition must satisfy all three before entering the pipeline:

1. **Upper ontology compliance** — Every class, relation, and axiom must be defensible against BFO/CCO/RO/IAO literature. Non-obvious decisions require a comment citing the justification.

2. **Genuine reasoning, not pattern matching** — An inference is only real if removing the enabling axiom causes the reasoner to stop drawing the conclusion. If the same output can be achieved by hardcoding the answer in instance data, it is not reasoning. Every addition must be tested: what does the reasoner infer, what does it not infer, and why is that the correct logical consequence?

3. **Business-owner traceability** — Every addition must connect to a person who built an AI system and needs a compliance determination. If you cannot state "this tells the business owner X, because Y, and without it they would be stuck at Z" — it does not belong in the pipeline. Ontological correctness is necessary but not sufficient.

---

## Chronological change log: what was built and why

### Foundation commits

**Phase 1a — SystemComponent class, System restriction broadened**

```turtle
# Before
:System rdfs:subClassOf [ owl:onProperty bfo:0000051 ; owl:someValuesFrom :HardwareComponent ]

# After
:SystemComponent rdfs:subClassOf bfo:0000030 .  # Object
:HardwareComponent rdfs:subClassOf :SystemComponent .
:System rdfs:subClassOf [ owl:onProperty bfo:0000051 ; owl:someValuesFrom :SystemComponent ]
```

Why: Annex III covers systems with various component types. Restricting to HardwareComponent blocked future extensibility. SystemComponent as an intermediate is BFO-compliant since these are all material objects (bfo:Object).

**Phase 1b/1c — Determination typing fixed**

```turtle
# Before
:HighRisk_Determination_001 rdf:type :ComplianceDetermination

# After
:HighRisk_Determination_001 rdf:type :HighRiskDetermination
```

Why: The SHACL shape targeted `:HighRiskDetermination`. Typing the instance at the superclass prevented shape resolution and obscured the logical chain. The system's classification as `:HighRiskSystem` is inferred by the reasoner; the determination artifact is a separate representation-side thing that documents the result.

---

### The governance layer build (Phase 1–4)

**Phase 1 — CCO DirectiveICE pattern + process and role classes**

Added to `ARCO_governance_extension.ttl`:

```turtle
cco:DirectiveInformationContentEntity rdf:type owl:Class ;
  rdfs:subClassOf iao:0000030 .  # Information Content Entity

cco:prescribes rdf:type owl:ObjectProperty .

:IntendedUseSpecification rdf:type owl:Class ;
  rdfs:subClassOf cco:DirectiveInformationContentEntity ;
  rdfs:subClassOf [ owl:onProperty cco:prescribes ; owl:someValuesFrom bfo:0000015 ] ;
  rdfs:subClassOf [ owl:onProperty iao:0000136 ; owl:someValuesFrom :System ] .

:UseScenarioSpecification rdf:type owl:Class ;
  rdfs:subClassOf cco:DirectiveInformationContentEntity ;
  rdfs:subClassOf [ owl:onProperty iao:0000136 ; owl:someValuesFrom :System ] ;
  rdfs:subClassOf [ owl:onProperty iao:0000136 ; owl:someValuesFrom bfo:0000023 ] .  # Role

:RemoteBiometricIdentificationProcess rdfs:subClassOf bfo:0000015 .  # Process
:NaturalPersonRole rdfs:subClassOf bfo:0000023 .  # Role
```

Critical design decision: Class-level restrictions use the general superclass (`bfo:0000015 Process`, `bfo:0000023 Role`) not the specific subclass. This keeps the schema extensible to Annex III 1(b), 1(c), etc. without rewriting class axioms. Specific process and role types are on instance data, not the class.

Added instances:

```turtle
:Sentinel_IntendedUse_001 rdf:type :IntendedUseSpecification ;
  cco:prescribes :RemoteBiometricIdentificationProcess ;
  iao:0000136 :Sentinel_ID_System .

:Sentinel_UseScenario_001 rdf:type :UseScenarioSpecification ;
  iao:0000136 :Sentinel_ID_System ;
  iao:0000136 :NaturalPersonRole .
```

---

**Phase 2 — Three-gate `AnnexIII1aApplicableSystem` OWL equivalentClass axiom**

This is the core classification mechanism. Full axiom:

```turtle
:AnnexIII1aApplicableSystem owl:equivalentClass [
  rdf:type owl:Class ;
  owl:intersectionOf (
    :System

    # Gate 1 (reality-side): biometric capability via component
    [ rdf:type owl:Restriction ;
      owl:onProperty bfo:0000051 ;               # has_part
      owl:someValuesFrom [
        rdf:type owl:Class ;
        owl:intersectionOf (
          :SystemComponent
          [ rdf:type owl:Restriction ;
            owl:onProperty ro:0000091 ;          # has_disposition
            owl:someValuesFrom :BiometricIdentificationCapability
          ]
        )
      ]
    ]

    # Gate 2 (representation-side): intended use spec is_about this system
    [ rdf:type owl:Restriction ;
      owl:onProperty [ rdf:type owl:ObjectProperty ; owl:inverseOf iao:0000136 ] ;
      owl:someValuesFrom :IntendedUseSpecification
    ]

    # Gate 3 (representation-side): use scenario spec is_about this system
    [ rdf:type owl:Restriction ;
      owl:onProperty [ rdf:type owl:ObjectProperty ; owl:inverseOf iao:0000136 ] ;
      owl:someValuesFrom :UseScenarioSpecification
    ]
  )
] .
```

Why anonymous inverse: OWL 2 DL permits anonymous inverse property expressions. owlrl materializes them. Verified with `test_gate_removal.py` which removes each gate independently and asserts the entailment breaks.

Why `equivalentClass` not `subClassOf`: `equivalentClass` enables both directions — any system meeting all three gates gets classified automatically by the reasoner. This is the genuine reasoning requirement.

Added SPARQL audit query:

```sparql
# check_annex_iii_1a_entailment.sparql
ASK WHERE {
  :Sentinel_ID_System rdf:type :AnnexIII1aApplicableSystem .
}
```

---

**Phase 3 — SHACL shapes for documentary artifacts**

```turtle
:IntendedUseSpecificationShape a sh:NodeShape ;
  sh:targetClass :IntendedUseSpecification ;
  sh:property [
    sh:path cco:prescribes ;
    sh:minCount 1 ;
    sh:name "Must prescribe a process type"
  ] ;
  sh:property [
    sh:path iao:0000136 ;
    sh:minCount 1 ;
    sh:name "Must be about at least one entity"
  ] .

:UseScenarioSpecificationShape a sh:NodeShape ;
  sh:targetClass :UseScenarioSpecification ;
  sh:property [
    sh:path iao:0000136 ;
    sh:minCount 2 ;
    sh:name "Must reference system and affected role (minCount 2)"
  ] .
```

Why SHACL is separate from OWL classification: SHACL enforces that documentary artifacts are structurally complete. It does not classify. If SHACL fails, the documentary record is incomplete. If OWL classification fails, the system is not applicable. These are separate failure modes.

---

**Phase 3b — Compliance obligation layer**

```turtle
:ComplianceObligationSpecification rdfs:subClassOf cco:DirectiveInformationContentEntity ;
  rdfs:subClassOf [ owl:onProperty iao:0000136 ; owl:someValuesFrom :System ] ;
  rdfs:subClassOf [ owl:onProperty iao:0000136 ; owl:someValuesFrom bfo:0000023 ] .  # Role

:ProviderObligation_001 rdf:type :ComplianceObligationSpecification ;
  iao:0000136 :Sentinel_ID_System ;
  iao:0000136 :ProviderRole_001 ;
  iao:0000136 :AnnexIII_Condition_Q1 .
```

```sparql
# check_obligation_link.sparql
ASK WHERE {
  ?obs rdf:type :ComplianceObligationSpecification ;
    iao:0000136 :Sentinel_ID_System ;
    iao:0000136 ?role .
  ?role rdf:type/rdfs:subClassOf* bfo:0000023 .
}
```

Why this exists: Annex III classification tells you whether a system is regulated. The obligation layer tells you who is responsible. Provider vs. deployer obligations differ under the EU AI Act. Without this, a business owner knows their system is high-risk but has no ontological anchor for "and I, specifically, must do X."

---

**Phase 4 — SHACL refactor: named property shapes with stable IRIs**

```turtle
# Before (blank node — anonymous in validation reports)
sh:property [
  sh:path cco:prescribes ;
  sh:minCount 1
] .

# After (named, stable IRI — traceable in audit reports)
:PS_IUS_Prescribes a sh:PropertyShape ;
  sh:path cco:prescribes ;
  sh:minCount 1 ;
  sh:name "Intended use prescribes process type" ;
  sh:description "Every IntendedUseSpecification must prescribe at least one process type via cco:prescribes." .

:IntendedUseSpecificationShape sh:property :PS_IUS_Prescribes .
```

Zero logic change. Blank-node shapes produce validation reports referencing anonymous nodes; named shapes produce reports referencing stable IRIs that audit tools can trace.

---

**Gate-removal regression test — `test_gate_removal.py`**

```python
def test_gate1_removal():
    g = build_graph_without_disposition_triple()
    apply_owlrl(g)
    assert (ARCO.Sentinel_ID_System, RDF.type, ARCO.AnnexIII1aApplicableSystem) not in g

def test_gate2_removal():
    g = build_graph_without_intended_use()
    apply_owlrl(g)
    assert (ARCO.Sentinel_ID_System, RDF.type, ARCO.AnnexIII1aApplicableSystem) not in g

def test_gate3_removal():
    g = build_graph_without_use_scenario()
    apply_owlrl(g)
    assert (ARCO.Sentinel_ID_System, RDF.type, ARCO.AnnexIII1aApplicableSystem) not in g

def test_all_gates_present():
    g = build_full_graph()
    apply_owlrl(g)
    assert (ARCO.Sentinel_ID_System, RDF.type, ARCO.AnnexIII1aApplicableSystem) in g
```

This is the genuine reasoning verification. Removing any single gate breaks the entailment. All four sub-tests pass.

---

**Final commit this session — `cco:prescribes` on regulatory condition + alignment SPARQL**

Before this commit, `AnnexIII_Condition_Q1` used only `iao:0000136` (is_about) for both informational aboutness and normative prescription:

```turtle
# Before
:AnnexIII_Condition_Q1 rdf:type :RegulatoryContent ;
  iao:0000136 :BiometricIdentificationCapability ;
  iao:0000136 :RemoteBiometricIdentificationProcess ;
  iao:0000136 :NaturalPersonRole .
```

`iao:0000136` is a non-normative informational relation — it expresses that a document is about something, not that it prescribes or mandates anything. A regulatory provision is a DirectiveICE; it does not merely reference the process it regulates, it prescribes it. Using `iao:0000136` for both purposes collapses the distinction between a reference and a directive.

```turtle
# After
:AnnexIII_Condition_Q1 rdf:type :RegulatoryContent ;
  cco:prescribes :RemoteBiometricIdentificationProcess ;      # normative
  iao:0000136 :BiometricIdentificationCapability ;            # informational
  iao:0000136 :RemoteBiometricIdentificationProcess ;         # informational (traceability)
  iao:0000136 :NaturalPersonRole .                            # informational
```

Added `check_regulatory_alignment.sparql`:

```sparql
ASK WHERE {
  # What the law prescribes
  :AnnexIII_Condition_Q1 cco:prescribes ?processType .

  # What the provider's documentation prescribes for this system
  ?ius a :IntendedUseSpecification ;
    cco:prescribes ?processType ;
    iao:0000136 :Sentinel_ID_System .
}
```

This query confirms: does the process type the law prescribes match the process type in the provider's documented intended use?

---

## The audit problem: Gap A — RESOLVED

> **Status as of 2026-03-08:** Gap A has been resolved via Option A (tightened Gate 2). Gate 2 now uses `owl:someValuesFrom :RemoteBiometricIdentificationProcess` with a properly typed process token, eliminating the false-negative risk and the certificate contradiction. Gate 3 retains `owl:hasValue :NaturalPersonRole` intentionally — scenario specs reference the role category (universal), not a role-bearer token. The SPARQL audit layer is now explicitly distinguished from the OWL classification layer in all files. Regression tests confirm each gate remains independently necessary. The section below is preserved for architectural context.

---

**Location:** The relationship between `check_regulatory_alignment.sparql` and the `AnnexIII1aApplicableSystem` OWL axiom.

**The problem, precisely (historical):**

Gate 2 of the three-gate equivalentClass axiom is:

```turtle
[ rdf:type owl:Restriction ;
  owl:onProperty [ rdf:type owl:ObjectProperty ; owl:inverseOf iao:0000136 ] ;
  owl:someValuesFrom :IntendedUseSpecification
]
```

This gate is satisfied when there exists any instance of `:IntendedUseSpecification` that has `iao:0000136 :Sentinel_ID_System`. It does not check what that IntendedUseSpecification `cco:prescribes`. The class-level restriction on `IntendedUseSpecification` requires it to prescribe some `bfo:0000015` (Process), but not any specific subclass of Process.

The new `check_regulatory_alignment.sparql` checks whether the process type in the provider's documentation matches the process type in the law. These two checks are logically independent.

**Concrete failure scenario:**

A company's system has `BiometricIdentificationCapability` (gate 1 passes). Their documentation contains an `IntendedUseSpecification` that `cco:prescribes :OnSiteFingerprintScanningProcess`. There is a `UseScenarioSpecification` about the system (gate 3 passes).

- Gate 1: PASS (capability exists)
- Gate 2: PASS (an IntendedUseSpecification is_about the system — process type not checked)
- Gate 3: PASS (a UseScenarioSpecification is_about the system)

Result: `Sentinel_ID_System rdf:type AnnexIII1aApplicableSystem` — **ENTAILED**.

But: `check_regulatory_alignment.sparql` returns **FALSE** — the law prescribes `RemoteBiometricIdentificationProcess`, the documentation prescribes `OnSiteFingerprintScanningProcess`.

The pipeline outputs "ANNEX III 1(a): VERIFIED" and "Reg. aligned: FAIL" simultaneously. To an auditor this is a contradiction.

**Why this matters beyond the academic:**

The EU AI Act Annex III 1(a) condition is: "AI systems intended to be used for the remote biometric identification of natural persons." The word "intended" is operative. Classification depends not just on capability but on documented intended use. A system capable of remote biometric identification but documented as intended for on-site fingerprint enrollment is not covered under 1(a). Gate 2 cannot distinguish these cases — it only checks that documentation exists, not that it is aligned with the specific regulatory trigger.

Downstream consequences:
- A company with a genuinely non-covered system may receive an incorrect high-risk classification
- A company with a covered system and defective documentation may receive a correct classification for wrong reasons — equally problematic legally
- The alignment check added in the last commit is decorative rather than classificatory

---

## Three candidate solutions

### Option A: Tighten Gate 2 in the OWL axiom to require specific process type

```turtle
# Current Gate 2
[ rdf:type owl:Restriction ;
  owl:onProperty [ rdf:type owl:ObjectProperty ; owl:inverseOf iao:0000136 ] ;
  owl:someValuesFrom :IntendedUseSpecification
]

# Option A: Gate 2 replacement
[ rdf:type owl:Restriction ;
  owl:onProperty [ rdf:type owl:ObjectProperty ; owl:inverseOf iao:0000136 ] ;
  owl:someValuesFrom [
    rdf:type owl:Class ;
    owl:intersectionOf (
      :IntendedUseSpecification
      [ rdf:type owl:Restriction ;
        owl:onProperty cco:prescribes ;
        owl:someValuesFrom :RemoteBiometricIdentificationProcess
      ]
    )
  ]
]
```

Gate 2 is only satisfied when an IntendedUseSpecification both (a) is_about the system and (b) prescribes specifically `RemoteBiometricIdentificationProcess`. If documentation prescribes a different process type, gate 2 fails, the entailment breaks, and the system is not classified as `AnnexIII1aApplicableSystem`.

Tradeoffs: This hardcodes one specific process type into the Annex III 1(a) axiom, breaking the design principle that class-level restrictions stay general. To cover 1(b), 1(c), etc. you would need separate equivalentClass axioms for each subclause — arguably architecturally correct (1(a), 1(b), 1(c) are distinct statutory applicability classes) but a departure from the current extensibility-first design. The `check_regulatory_alignment.sparql` query becomes redundant for the case it was designed to catch.

---

### Option B: SHACL constraint that blocks misaligned documentation

```turtle
:AlignedIntendedUseShape a sh:NodeShape ;
  sh:targetClass :IntendedUseSpecification ;
  sh:sparql [
    a sh:SPARQLConstraint ;
    sh:message "IntendedUseSpecification prescribes a process type not covered by any applicable regulatory condition" ;
    sh:select """
      SELECT $this WHERE {
        $this cco:prescribes ?processType .
        FILTER NOT EXISTS {
          ?condition rdf:type :RegulatoryContent ;
            cco:prescribes ?processType .
        }
      }
    """
  ] .
```

SHACL validation fails when documentation is misaligned. The pipeline halts at the SHACL stage before reaching OWL classification.

Tradeoffs: SHACL failure is a softer failure than classification failure. The OWL reasoner still infers `AnnexIII1aApplicableSystem` — the pipeline reports non-conformance but the classification still ran. Whether this is correct depends on intended use: for self-assessment (fix documentation first) this is appropriate; for regulatory determination (block classification) it is not. SPARQL-based SHACL constraints also add computational complexity and a second SPARQL engine dependency inside the validation layer.

---

### Option C: Accept design as intentional — two distinct outputs, improve certificate communication

Retain the current architecture where `HighRiskSystem` (capability-based, latent risk, inferred from reality-side disposition alone) and `AnnexIII1aApplicableSystem` (three-gate, full statutory applicability) are two distinct outputs with different thresholds. `check_regulatory_alignment.sparql` is a documentation quality audit alongside them.

Certificate would explicitly communicate:

- **Latent risk:** `HighRiskSystem = TRUE` — This system bears capability that, if combined with appropriate documentation, would trigger Annex III 1(a). Reason: BiometricIdentificationCapability in component.
- **Statutory applicability:** `AnnexIII1aApplicableSystem = TRUE/FALSE` — Documentation + capability satisfies the three-gate statutory test.
- **Documentation alignment:** `ALIGNED = TRUE/FALSE` — Process type in documentation matches process type prescribed by applicable regulatory condition.

Under this design, misaligned documentation produces `AnnexIII1aApplicableSystem = TRUE` but `ALIGNED = FALSE`: the system is classified but documentation is defective — a different kind of failure than not being classified.

Tradeoffs: Defensible if the intent is to detect all systems that could be Annex III 1(a) applicable based on documentary completeness, and flag documentation quality separately. But it creates a logical tension: a regulator reading "ANNEX III 1(a): VERIFIED" will not expect "Reg. aligned: FAIL" on the same certificate without very precise language explaining the distinction. The communication burden falls on the certificate rather than the logic.

---

## Current pipeline state (all checks passing — updated 2026-03-08)

Two-layer architecture. Classification layer produces the determination; audit layer inspects the result.

**Classification layer (OWL-RL entailment):**

| Check | Mechanism | What it verifies |
|---|---|---|
| SHACL conforms | pyshacl | Documentary shapes: IntendedUse, UseScenario, Obligation structurally complete |
| HighRiskSystem entailment | OWL-RL | System rdf:type HighRiskSystem — inferred from capability alone (latent risk) |
| Annex III 1(a) entailment | OWL-RL | System rdf:type AnnexIII1aApplicableSystem — inferred from all three content-checking gates |

**Audit documentation layer (SPARQL ASK on reasoned graph):**

| Check | Mechanism | What it verifies |
|---|---|---|
| Traceability | SPARQL ASK | HighRisk_Determination_001 is_about Sentinel_ID_System |
| Latent risk | SPARQL ASK | HighRiskSystem entailment present (hardware path) |
| Intended use | SPARQL ASK | IUS prescribes a process typed as RemoteBiometricIdentificationProcess; USS references NaturalPersonRole |
| Obligation link | SPARQL ASK | ComplianceObligationSpecification links system to role |
| Reg. aligned | SPARQL ASK | Provider's process token is of the same type the law prescribes — type-level alignment, not IRI matching |

Current counts: 324 asserted → 1066 entailed (+742).

---

## Questions for cross-model review

1. Is Gap A a real logical problem in the design, or is the current architecture defensible as-is with better certificate communication (Option C)?

2. Of the three options, which is most consistent with the principle that classification should be genuine OWL entailment rather than SPARQL pattern matching — specifically, should Gate 2 carry the full burden of regulatory specificity (Option A), or is it architecturally cleaner to separate classification concerns from documentation quality concerns (Options B/C)?

3. Are there design patterns in OWL/SHACL/SPARQL pipelines for regulatory compliance that you would apply here that differ from what has been built?

4. The `IntendedUseSpecification` class-level restriction uses `bfo:0000015` (general Process) rather than the specific regulated process type. Is this the right call for extensibility, or does it create a classification loophole that is worse than the coupling introduced by a specific process type in the axiom?

5. From the standpoint of a company relying on the ARCO certificate for regulatory purposes — is the distinction between `HighRiskSystem` (latent risk) and `AnnexIII1aApplicableSystem` (statutory applicability) clearly enough separated in the current design that misalignment between the two outputs would not mislead rather than inform?

No preferred direction is being pushed. The question is: what do you see that has not been seen here, what is the most defensible and downstream-consistent architecture, and how should we think about the tradeoffs between logical tightness, extensibility, and certificate clarity?
