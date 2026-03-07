# ARCO Change Review: Gap A Fix
## Commit `f5440a4` — Branch `claude/sql-ontology-graphrag-s4DIH`

---

## 1. What Changed

Two files were modified. No files were created or deleted.

---

### File 1: `03_TECHNICAL_CORE/ontology/ARCO_governance_extension.ttl`

**What changed:** The `owl:equivalentClass` axiom for `:AnnexIII1aApplicableSystem` — specifically Gates 2 and 3.

#### Gate 2 — Before

```turtle
# Gate 2 (representation-side): intended use spec exists about this system
[ rdf:type owl:Restriction ;
  owl:onProperty [ rdf:type owl:ObjectProperty ; owl:inverseOf iao:0000136 ] ;
  owl:someValuesFrom :IntendedUseSpecification
]
```

Gate 2 was satisfied whenever **any** `IntendedUseSpecification` existed that had `iao:0000136` (is_about) pointing to the system. It did not check what that specification actually prescribed.

#### Gate 2 — After

```turtle
# Gate 2 (representation-side): intended use spec is_about this system AND prescribes the
# regulated process for Annex III 1(a). cco:prescribes carries the statutory prescriptive
# force; iao:0000136 (aboutness) is retained on the class but is not the load-bearing gate
# condition. owl:hasValue is used because instance data uses class IRIs as punned individuals
# (interim modeling choice — cleaner alternative: process-type tokens as class instances).
[ rdf:type owl:Restriction ;
  owl:onProperty [ rdf:type owl:ObjectProperty ; owl:inverseOf iao:0000136 ] ;
  owl:someValuesFrom [
    rdf:type owl:Class ;
    owl:intersectionOf (
      :IntendedUseSpecification
      [ rdf:type owl:Restriction ;
        owl:onProperty cco:prescribes ;
        owl:hasValue :RemoteBiometricIdentificationProcess
      ]
    )
  ]
]
```

Gate 2 now requires the `IntendedUseSpecification` to both (a) `iao:0000136` the system and (b) `cco:prescribes :RemoteBiometricIdentificationProcess`. Both conditions must hold simultaneously.

---

#### Gate 3 — Before

```turtle
# Gate 3 (representation-side): scenario spec exists about this system
[ rdf:type owl:Restriction ;
  owl:onProperty [ rdf:type owl:ObjectProperty ; owl:inverseOf iao:0000136 ] ;
  owl:someValuesFrom :UseScenarioSpecification
]
```

Gate 3 was satisfied whenever **any** `UseScenarioSpecification` existed that `iao:0000136` the system. It did not check what role or context that specification described.

#### Gate 3 — After

```turtle
# Gate 3 (representation-side): scenario spec is_about this system AND is_about the relevant
# affected role for Annex III 1(a). owl:hasValue used for same punning reason as Gate 2.
[ rdf:type owl:Restriction ;
  owl:onProperty [ rdf:type owl:ObjectProperty ; owl:inverseOf iao:0000136 ] ;
  owl:someValuesFrom [
    rdf:type owl:Class ;
    owl:intersectionOf (
      :UseScenarioSpecification
      [ rdf:type owl:Restriction ;
        owl:onProperty iao:0000136 ;
        owl:hasValue :NaturalPersonRole
      ]
    )
  ]
]
```

Gate 3 now requires the `UseScenarioSpecification` to both (a) `iao:0000136` the system and (b) `iao:0000136 :NaturalPersonRole`. Both conditions must hold simultaneously.

---

#### `rdfs:comment` on `:AnnexIII1aApplicableSystem` — Updated

The class comment was updated to document:
- The tightened gate semantics
- The `owl:hasValue` interim modeling choice and its justification
- The existence of the gate-removal regression test

---

### File 2: `03_TECHNICAL_CORE/scripts/test_gate_removal.py`

**What changed:** Added `CCO` namespace, two new removal tests added to `GATE_REMOVALS`/`EXPECTED`, a new `GATE_MUTATIONS` dict, a `run_mutation_test()` function, and updated `main()` to run mutation tests.

**Net result:** 3 existing removal tests → 5 removal tests + 2 mutation tests = **9 total test assertions** (up from 3, plus baseline).

New tests added:

| Test name | What it does | AnnexIII1a expected | HighRiskSystem expected |
|---|---|---|---|
| `gate2_prescribes_removed` | Removes `cco:prescribes :RemoteBiometricIdentificationProcess` | False | True |
| `gate3_missing_role` | Removes `iao:0000136 :NaturalPersonRole` | False | True |
| `gate2_wrong_process_type` | Replaces process with `:SomeOtherProcess` | False | True |
| `gate3_wrong_role_type` | Replaces role with `:SomeOtherRole` | False | True |

All 9 tests pass.

---

## 2. Why This Change Was Made

### The problem (Gap A)

The pre-change `AnnexIII1aApplicableSystem` equivalentClass axiom contained a logical weakness. Gate 2 required only that some `IntendedUseSpecification` existed and `iao:0000136` the system. Gate 3 required only that some `UseScenarioSpecification` existed and `iao:0000136` the system.

`iao:0000136` (`is_about`) is an informational reference relation — it says a document is *about* something. It does not assert what the document *prescribes* or *mandates*. A regulatory applicability determination under Annex III 1(a) requires not just that documentation exists, but that it documents the *specific regulated use type*.

**Concrete failure scenario (pre-change):** A system with a biometric capability, an `IntendedUseSpecification` that `cco:prescribes :FingerprintEnrollmentProcess`, and a `UseScenarioSpecification` about employees would satisfy all three gates and be classified `AnnexIII1aApplicableSystem`. The pipeline would then run `check_regulatory_alignment.sparql` (which checks whether the law and the documentation prescribe the same process type), find they do not match, and output:

```
ANNEX III 1(a): VERIFIED (ENTAILED)
Reg. aligned: FAIL
```

That is a direct contradiction on the same certificate. A system is classified as statutorily applicable while simultaneously failing the check that confirms it is aligned with the applicable statute.

### The fix

Making `cco:prescribes` load-bearing in Gate 2 means the gate is only satisfied when the documentation content matches the statutory trigger. `iao:is_about` remains on the `IntendedUseSpecification` class definition (for informational reference) but no longer alone determines statutory classification.

Making `iao:0000136 :NaturalPersonRole` required in Gate 3 means the scenario documentation must explicitly reference the affected party type required by Annex III 1(a) — not just reference the system generically.

### Design rationale: `owl:hasValue` vs `owl:someValuesFrom`

The instance data uses class IRIs as object fillers via OWL 2 punning:

```turtle
:Sentinel_IntendedUse_001 cco:prescribes :RemoteBiometricIdentificationProcess .
```

Here `:RemoteBiometricIdentificationProcess` is simultaneously a class (with `rdfs:subClassOf bfo:0000015`) and an individual (used as a triple object). `owl:someValuesFrom :RemoteBiometricIdentificationProcess` would require the filler to be an *instance of* the class, but the class IRI itself is not typed as its own instance (`RemoteBiometricIdentificationProcess rdf:type RemoteBiometricIdentificationProcess` is not in the graph). `owl:hasValue :RemoteBiometricIdentificationProcess` matches the specific named individual directly, which is what the instance data provides.

This is documented in the comment as an interim engineering choice. The cleaner alternative — using process-type tokens (`arco:RBIP_Token_001 rdf:type :RemoteBiometricIdentificationProcess`) — is deferred because it would require instance data changes and is a separate improvement.

---

## 3. Audit of Downstream and Current Effects

### 3.1 Immediate effects — what changes in pipeline output

| Check | Pre-change | Post-change |
|---|---|---|
| `AnnexIII1aApplicableSystem` entailment | True (Sentinel) | True (Sentinel — instance data already correct) |
| `check_regulatory_alignment.sparql` | True | True |
| Certificate contradiction possible | Yes | No |
| `HighRiskSystem` entailment | True | True (unchanged) |
| Entailed triples | +737 | +737 |
| ALL CHECKS PASSED | Yes | Yes |

The Sentinel instance already had `cco:prescribes :RemoteBiometricIdentificationProcess` and `iao:0000136 :NaturalPersonRole` in its data, so no instance data change was needed. The pipeline output is identical for the Sentinel case — the fix only affects what the axiom *requires*, not what it currently entails for the correct instance.

---

### 3.2 Effect on `HighRiskSystem` separation

**No change.** `HighRiskSystem` is defined in `ARCO_core.ttl` with a capability-only axiom:

```turtle
:HighRiskSystem owl:equivalentClass [
  owl:intersectionOf (
    :System
    [ owl:onProperty bfo:0000051 ;
      owl:someValuesFrom [
        owl:onProperty ro:0000091 ;
        owl:someValuesFrom :AnnexIIITriggeringCapability
      ]
    ]
  )
]
```

This has no documentation gates. `HighRiskSystem` is entailed by capability alone. The regression tests confirm that in every misalignment scenario (wrong process, wrong role, missing role, missing prescribes triple), `HighRiskSystem` remains `True` while `AnnexIII1aApplicableSystem` becomes `False`. The layered output is now behaviorally verified, not just structurally claimed.

---

### 3.3 Effect on future system instances added to the pipeline

**Breaking change for incorrectly documented instances.** Any future instance that:
- Has biometric capability (Gate 1 passes)
- Has an `IntendedUseSpecification` that does NOT `cco:prescribes :RemoteBiometricIdentificationProcess` (Gate 2 fails)
- Or has a `UseScenarioSpecification` that does NOT `iao:0000136 :NaturalPersonRole` (Gate 3 fails)

...will NOT be classified `AnnexIII1aApplicableSystem`. Pre-change, such an instance would have been classified regardless.

This is the intended behavior. The pre-change classification was wrong; the post-change behavior is correct.

**For correctly documented instances** (documentation aligned with the statute), no change in behavior.

---

### 3.4 Effect on the planned Verification Exclusion + Annex III 5(b) extension

The previous plan (BiometricVerificationCapability exclusion + CreditworthinessEvaluationCapability + `AnnexIII5bApplicableSystem`) is unaffected in principle but now has a tighter template to follow.

When `AnnexIII5bApplicableSystem` is created, Gate 2 of that class must use `owl:hasValue :CreditworthinessEvaluationProcess` (or whatever the regulated process is for 5(b)). The pattern is now established and documented. The extensibility argument for keeping class-level restrictions general (using `bfo:0000015 Process`) still holds at the *class definition* level; the statutory specificity belongs in the *equivalentClass gate axiom* for each clause-specific applicability class.

---

### 3.5 Effect on SHACL validation

**No change.** SHACL shapes were not modified. The SHACL layer validates structural completeness of documentation artifacts (existence, cardinality, required properties). It does not classify. The Gap A fix correctly keeps statutory classification in OWL, not SHACL.

---

### 3.6 Effect on SPARQL audit queries

**`check_regulatory_alignment.sparql` is now logically redundant for the Sentinel case** — if `AnnexIII1aApplicableSystem` is entailed, Gate 2 required `cco:prescribes :RemoteBiometricIdentificationProcess`, which is exactly what the alignment query checks. Both will always agree. The query is retained as audit corroboration and for human-readable certificate output. It is harmless and adds traceability.

No other SPARQL queries are affected.

---

### 3.7 Remaining modeling debt

One issue was identified but not resolved in this change:

**`owl:hasValue` + class-IRI-as-individual punning.** The use of class IRIs as object fillers in `cco:prescribes` and `iao:0000136` is an interim pattern. It works under OWL 2 + owlrl, but it is less semantically clean than having actual process-type tokens as instances of their classes. A future fix would:

1. Add instance tokens: `arco:RBIP_Token_001 rdf:type :RemoteBiometricIdentificationProcess`
2. Change instance data: `cco:prescribes arco:RBIP_Token_001`
3. Change gate restriction: `owl:someValuesFrom :RemoteBiometricIdentificationProcess`

This would make Gate 2 use genuine type-checking rather than named-individual matching. This is deferred — it requires coordinated instance data + axiom changes and is a separate improvement.

---

## 4. Verification Results

```
Pipeline:              ALL CHECKS PASSED (+737 entailed triples)
Gate-removal tests:    9/9 PASS
Certificate output:    ANNEX III 1(a): VERIFIED / Reg. aligned: PASS (always together)
```

The certificate contradiction (verified + aligned fail simultaneously) is structurally eliminated for the current ontology and query pair. It is not merely suppressed in display — it cannot be produced by the OWL reasoner given the tightened axiom.
