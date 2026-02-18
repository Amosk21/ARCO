# ARCO Ontology Review — BFO Alignment Audit

**Date:** 2026-02-16
**Scope:** Review all branches with ontology changes against BFO/CCO alignment, ARCO design constraints, and overclaiming risk.
**Standard:** Would Barry Smith / John Beverley sign off on this? Does it overclaim what ARCO can currently demonstrate?

---

## Branches Reviewed

| Branch | Core TTL changes | Verdict |
|--------|-----------------|---------|
| `main` (current) | Baseline — passes all checks | **CLEAN** |
| `claude/add-org-data-a2zuL` | 12 new classes, 1 new property, 318-line Claude 3 instance file | **PROBLEMS** |
| `relation-first-proof-view` | Three-gate pattern, SoftwareArtifact, conservative Claude 3 | **MOSTLY SOUND** |
| `claude/check-branch-visibility-keTrC` | Scoped disposition inverse | **SOUND** |
| `Component_Bearer` | Component-bearer pattern shift | **SUPERSEDED by main** |

---

## Branch: `claude/add-org-data-a2zuL` — DETAILED FINDINGS

This is the GraphRAG-extracted, auto-generated ontology extension. It models Claude 3 as a real system and claims two independent high-risk inference paths. The ambition is right but the execution has serious ontological problems.

### PROBLEM 1: VisionCapability ⊑ BiometricIdentificationCapability

**What it claims:** Any system with vision capability inherently has biometric identification capability.

```turtle
:VisionCapability rdf:type owl:Class ;
  rdfs:subClassOf :MultimodalCapability ;
  rdfs:subClassOf :BiometricIdentificationCapability .
```

**Why this is wrong:** This is a false subsumption. Vision capability is a general sensory modality — it includes reading documents, interpreting charts, classifying landscapes. Biometric identification is a specific forensic application that requires not just "seeing" but extracting, encoding, and matching biometric templates against a reference database. A camera pointed at a field has vision capability. It does not have biometric identification capability.

The EU AI Act Annex III 1(a) targets "AI systems intended to be used for the real-time and post remote biometric identification of natural persons." The operative concept is *biometric identification* — not *vision*. A system that can see images does not thereby identify persons biometrically, any more than a system that can generate text thereby produces legal contracts.

**BFO problem:** In BFO, subsumption means every instance of the subclass is necessarily an instance of the superclass. If VisionCapability ⊑ BiometricIdentificationCapability, then *every* vision disposition is a biometric identification disposition. This is empirically false. A document-scanning vision system has no biometric identification disposition.

**Barry Smith would say:** "You have confused a genus with one of its species. Vision is not a species of biometric identification — if anything, biometric identification capability is a species of vision capability that additionally requires template-matching infrastructure. The subsumption goes the wrong way, and even reversed it would need qualification."

**What to do:** Remove this subsumption entirely. If a specific system has both vision AND biometric identification capability, assert both dispositions independently. Do not derive one from the other via class hierarchy.

---

### PROBLEM 2: Custom object property `hasSystemicRiskIndicator`

```turtle
:hasSystemicRiskIndicator rdf:type owl:ObjectProperty ;
  rdfs:domain :GeneralPurposeAICapability ;
  rdfs:range :SystemicRiskIndicator .
```

**Why this is wrong:** CLAUDE.md hard constraint #2 says "No Ad-Hoc Relations: Do NOT create custom object properties." The project rule is explicit: use existing BFO/RO/IAO/CCO relations.

SystemicRiskIndicator is an ICE (information content entity). A capability disposition is a BFO Disposition. The relation between a disposition and an information entity *about* that disposition is `iao:0000136` (is_about) — the indicator is *about* the capability. There is no need for a custom property.

**What to do:** Delete `hasSystemicRiskIndicator`. Model the relationship as: `SystemicRiskIndicator iao:0000136 SomeCapability`.

---

### PROBLEM 3: ModelComponent ⊑ bfo:0000030 (Object)

```turtle
:ModelComponent rdf:type owl:Class ;
  rdfs:subClassOf bfo:0000030 ; # Object
```

**Why this is questionable:** A trained AI model (weights + architecture) is not a material entity. The weights are information — they are patterns that can be copied, transferred, and concretized on different hardware. In BFO terms, a trained model is a Generically Dependent Continuant (GDC) — it depends on some material bearer for its existence but is not itself material.

The `relation-first-proof-view` branch got this right: it models software/models as `SoftwareArtifact ⊑ iao:0000030` (ICE, which is a GDC). The dispositions inhere in the *hardware that concretizes the model*, not in the model itself.

**Barry Smith would say:** "A model is an information artifact. You cannot kick it. It has no mass, no spatial extent. It is a generically dependent continuant that is concretized in material bearers. Dispositions inhere in independent continuants (BFO axiom). If your model is an ICE, it cannot bear dispositions."

**What to do:** Follow the `relation-first-proof-view` approach — models are SoftwareArtifacts (ICE). Dispositions inhere in the hardware infrastructure that concretizes them.

---

### PROBLEM 4: Scope creep — 8 new Annex III capability categories

The branch adds: GeneralPurposeAICapability, MultimodalCapability, VisionCapability, AutonomousAgentCapability, ComputerUseCapability, ContentGenerationCapability, CodeGenerationCapability, ReasoningCapability, MultilingualCapability.

It also expands `AnnexIIITriggeringCapability` to include AutonomousAgentCapability (Annex III category 2).

**CLAUDE.md says:** "Do not model all 8 Annex III categories — biometrics only for now."

**Why this is risky beyond the rule violation:** Each new capability class needs its own justification for BFO placement, its own subsumption relationships validated, and its own test cases. The biometric classification chain took months of careful alignment work. Adding 8 more in one commit with auto-generated subsumptions means 8 more places where a false subsumption (like VisionCapability ⊑ BiometricIdentificationCapability) can silently produce wrong regulatory determinations.

**What to do:** Strip back to biometrics. If you want to demonstrate Claude 3 as a second system, model it with the capabilities you can *currently* validate: biometric identification (if the evidence supports it) or declare the classification underdetermined (which is itself a valid and interesting ARCO result).

---

### PROBLEM 5: Overclaiming — "two independent inference paths"

The branch claims Claude 3 is high-risk via two paths:
1. Vision → BiometricIdentification (Annex III 1a)
2. ComputerUse → AutonomousAgent (Annex III 2)

Path 1 depends on the false VisionCapability ⊑ BiometricIdentificationCapability subsumption (Problem 1).

Path 2 depends on AutonomousAgentCapability being in the AnnexIIITriggeringCapability union, which was not in the original design and violates the "biometrics only" constraint.

**What ARCO can actually demonstrate today:** The Sentinel-ID system is correctly classified as high-risk because it has a component with an explicitly modeled biometric identification capability. That is a clean, defensible result. Claiming the same for Claude 3 via an auto-generated subsumption chain is not defensible — it is the inference engine producing a result from wrong inputs.

---

### PROBLEM 6: AnnexIIITriggeringCapability union expanded without justification

**Before (main):**
```turtle
owl:unionOf ( :BiometricIdentificationCapability )
```

**After (this branch):**
```turtle
owl:unionOf (
  :BiometricIdentificationCapability
  :AutonomousAgentCapability
)
```

This changes the bridge axiom so that any system with a component bearing AutonomousAgentCapability is automatically classified HighRiskSystem. That is a massive scope change to the core inference engine. It was done without separate validation, without SPARQL tests for false positives, and without checking whether AutonomousAgentCapability is properly defined relative to Annex III category 2.

**What to do:** Revert to single-member union (biometrics only). When you're ready to add Annex III category 2, do it as a deliberate, tested, documented extension — not bundled with 11 other changes.

---

## Branch: `relation-first-proof-view` — DETAILED FINDINGS

This branch is more careful. It implements the three-gate classification pattern from CLAUDE.md and takes a conservative approach to Claude 3.

### SOUND: Software as ICE (SoftwareArtifact)

Models trained models as `SoftwareArtifact ⊑ iao:0000030`. Dispositions inhere in hardware. This is BFO-correct.

### SOUND: Claude 3 classified as UNDERDETERMINED

The Claude 3 instance file on this branch does NOT assert biometric identification capability for Claude 3. It models vision as "static image understanding" — a generic capability that does not subsume biometric identification. Result: the three-gate check does not fire, and Claude 3 gets an UNDERDETERMINED classification.

This is honest. It says: "We can model the system, but the evidence does not currently support all three gates for Annex III 1(a) classification." That is a legitimate and interesting ARCO output.

### SOUND: Three-gate directive ICE pattern

IntendedUseSpecification and UseScenarioSpecification follow the CCO Directive ICE pattern exactly as specified in CLAUDE.md. The three gates (capability + intended use + scenario) are formally modeled and queryable.

### MINOR CONCERN: Scoped `disposition_inheres_in` inverse

The branch adds a scoped inverse property. The justification (avoiding role contamination from a global inverse) is valid, but it is a custom property not in RO. It is documented and justified, so it is not a hard constraint violation, but it should be flagged for future review if the RO adds an official inverse.

### CONCERN: Scope of core TTL changes

This branch also adds classes to core: SystemComponent, SoftwareArtifact, and makes frozen design decision comments. These are already on main (they were merged). The three-gate classes (IntendedUseSpecification, UseScenarioSpecification, NaturalPersonRole, etc.) are in the governance extension and are well-justified by the CLAUDE.md patterns.

---

## Branch: `claude/check-branch-visibility-keTrC`

Adds the scoped `disposition_of` inverse with extensive documentation. Sound. Low risk. The documentation of defined class vs. asserted class status for HighRiskSystem and AnnexIIITriggeringCapability is useful.

---

## Current `main` — Baseline Assessment

Main is clean. The ontology has:
- Proper BFO alignment (System ⊑ ObjectAggregate, dispositions ⊑ Disposition, ICEs properly separated)
- Single Annex III category (biometrics) with working inference
- Component-level disposition tracing
- All SPARQL checks passing
- SHACL conforming
- No custom object properties (all relations are BFO/RO/IAO/CCO)

**Main is the gold standard. Any merge must preserve this.**

---

## Summary: What Can Be Merged vs. What Cannot

### Safe to merge (after review):
- `relation-first-proof-view` three-gate pattern additions (governance extension classes, SHACL shapes, SPARQL queries)
- `relation-first-proof-view` conservative Claude 3 instances (if desired as second demo)
- `relation-first-proof-view` pipeline enhancements (multi-profile, JSON output)

### NOT safe to merge without significant rework:
- `claude/add-org-data-a2zuL` in its current form — too many BFO violations and overclaims

### Specific items from `claude/add-org-data-a2zuL` that could be salvaged:
- SafetyPolicy, SafetyEvaluationProcess, SafetyEvaluationReport class hierarchy (governance extension) — these are well-structured ICE classes
- ModelCard class — useful, properly subclassed under AssessmentDocumentation
- DeployerOrganization / DeployerRole — sound BFO pattern
- The *structure* of the Claude 3 instance file (system + components + provider + documentation workflow) — but needs capability dispositions fixed and ModelComponent replaced with SoftwareArtifact + HardwareComponent

### Must be deleted / reverted:
- VisionCapability ⊑ BiometricIdentificationCapability subsumption
- hasSystemicRiskIndicator custom property
- ModelComponent class (replace with existing SoftwareArtifact pattern)
- AnnexIIITriggeringCapability union expansion
- All 8 frontier AI capability subclasses (scope violation)
- GPAISystemicRiskCapability defined class (depends on deleted property)

---

## Design Principle for Future Work

ARCO's value is that it produces **correct** regulatory determinations from **correct** structural models. A wrong determination from wrong subsumptions is worse than no determination at all — it gives false confidence.

The right approach for adding a new system (like Claude 3):
1. Model the system structure (components, infrastructure) using existing classes
2. Assert only the dispositions you have direct evidence for
3. If the three-gate classification fires, report it
4. If it does not fire, report UNDERDETERMINED — that is a valid result
5. Never invent class subsumptions to force a desired classification outcome
