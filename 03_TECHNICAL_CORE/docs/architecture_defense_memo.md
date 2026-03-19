# ARCO Architecture Defense Memo

**Date:** 2026-03-19
**Scope:** Stability check on six core modeling decisions
**Not:** a redesign, legal review, BFO paper, or extension plan

---

## 1. What ARCO currently does

ARCO takes hand-authored instance data describing an AI system — its hardware components, their capabilities, the provider's intended use documentation, and the affected population — and runs OWL-RL reasoning to determine whether that system falls into a regulated category under EU AI Act Annex III. The output is a deterministic, traceable classification: either the reasoner entails class membership or it does not.

Today this works for two Annex III categories: 1(a) remote biometric identification and 5(b) creditworthiness evaluation. A third instance file (biometric verification) demonstrates a correct negative: a system that has a capability but does *not* trigger Annex III classification because the capability type is wrong. The pipeline produces a certificate, evidence trace, and HTML view.

Classification is done entirely by OWL-RL entailment. SHACL validates that documentary artifacts are structurally complete. SPARQL ASK queries inspect the reasoned graph as an audit layer. These three layers have distinct authority: OWL classifies, SHACL checks structure, SPARQL audits. None substitutes for another.

ARCO does not claim to cover the full EU AI Act. It does not perform LLM-based extraction. It does not handle multi-system scenarios, prohibited AI (Article 5), or jurisdictions outside the EU AI Act. Instance data must currently be hand-authored.

---

## 2. Why the three-gate pattern exists

### Gate 1 — Capability

**Regulatory idea:** Annex III categories are about systems that *can do* certain things. A system with no biometric identification capability cannot be regulated as a biometric identification system, regardless of what its documentation says.

**Why a separate gate:** Capability is a fact about reality, not about documentation. Separating it ensures that classification requires the system to actually have the relevant capability, not just claim it.

**Status:** Legally implied requirement made explicit by ARCO. The Act conditions every Annex III category on what the system is "intended to be used for," which presupposes the system has the relevant capability. The Act does not hand you a "capability gate" directly — ARCO makes that implicit precondition into a formal, testable requirement.

### Gate 2 — Intended use (prescribed process type)

**Regulatory idea:** The Act regulates systems "intended to be used for" specific processes. A system with biometric identification capability that is documented as intended for access control (verification) is not the same as one documented for remote identification of unknown persons.

**Why a separate gate:** Intent is not a physical fact — it is a provider's declared commitment, expressed in documentation. Separating it from capability ensures ARCO distinguishes what a system *can* do from what it is *claimed to be for*.

**Status:** Legally implied decomposition. The Act does not say "check the intended use document separately." But the Act's language conditions on documented intent, and that intent is about a specific process type, not just any process. ARCO makes that implicit structure explicit and type-checkable.

### Gate 3 — Affected population (use scenario)

**Regulatory idea:** Annex III categories also condition on *who* is affected. Biometric identification of natural persons triggers regulation; biometric identification of, say, livestock does not.

**Why a separate gate:** The affected-party condition is distinct from both capability and intended process. A system could have the right capability and the right intended process but operate in a context where the affected population doesn't trigger the regulation.

**Status:** Legally implied, with a more ARCO-specific encoding than Gates 1 and 2. The Act clearly conditions on affected parties, but the exact way ARCO represents "about the NaturalPersonRole category" is an ARCO modeling choice, not something directly readable from the legal text.

---

## 3. Why each gate is modeled this way

### Gate 1: Capability as disposition on a hardware component

**Current pattern:**
```
System has_part some (SystemComponent and has_disposition some BiometricIdentificationCapability)
```

**Strongest defense:** BFO dispositions are the correct ontological category for capabilities — a disposition is something that inheres in a material entity and can be realized in a process. `has_disposition` (RO:0000091) is the standard RO relation for this. Requiring the disposition to inhere in a component (not the system abstractly, not in software) enforces BFO's rule that dispositions inhere in independent continuants only.

**Main weakness:** The Act does not require component-level decomposition. It talks about "AI systems," not about hardware modules bearing dispositions. The decomposition into System → SystemComponent → Disposition is an ARCO design choice that enables finer-grained tracing but is not legally compelled. A simpler pattern (system bears disposition directly) would also be defensible under a different reading of BFO, though it would lose component-level traceability.

**Why ARCO still uses it:** The component decomposition is testable, produces meaningful evidence paths (which component bears which capability), and aligns with how real AI systems are actually structured. It also prevents the category error of putting dispositions on information artifacts (software). The cost is modeling complexity; the benefit is precision and traceability.

### Gate 2: Intended use as directive ICE + `cco:prescribes` + typed process

**Current pattern:**
```
IntendedUseSpecification is_about System
  AND cco:prescribes some RemoteBiometricIdentificationProcess
```
(Accessed via inverse aboutness from the system)

**Strongest defense:** Intended use in the EU AI Act is fundamentally documentary — it is what the provider declares, not what happens in practice. Modeling it as a directive information content entity (CCO's DirectiveICE) that *prescribes* a specific process type captures exactly this: a document that says "this system is intended for process X." The `someValuesFrom` on the process class performs genuine type-checking — the prescribed process must be an instance of the right class, not just any process. This was tested: substituting a wrong process type correctly breaks the gate (verified by mutation test in `test_gate_removal.py`).

**Main weakness:** The inverse aboutness pattern (`[owl:inverseOf iao:0000136]`) is valid OWL 2 DL but depends on the reasoner materializing inverse restrictions. owlrl does this; other OWL-RL reasoners may not. This is a portability risk, not a correctness issue. The `cco:prescribes` relation is a local stub — ARCO declares it without importing full CCO. If full CCO is ever imported, the stub must be checked for compatibility.

**Why ARCO still uses it:** The alternative — checking only for *existence* of an intended use document — would be a documentary-existence gate, not a content gate. ARCO specifically rejected that pattern because it cannot distinguish "intended for biometric identification" from "intended for spam filtering." The type-checking via `someValuesFrom` is what makes Gate 2 meaningful rather than ceremonial.

### Gate 3: Affected role category via `owl:hasValue` on NaturalPersonRole

**Current pattern:**
```
UseScenarioSpecification is_about System
  AND is_about NaturalPersonRole  [owl:hasValue]
```
(Accessed via inverse aboutness from the system)

**Strongest defense:** The Act conditions on affected parties as a category ("natural persons"), not on specific individuals. Using `owl:hasValue :NaturalPersonRole` treats the class IRI as a concept-individual (OWL 2 punning) to express "this scenario is about the natural-person role category." This is the correct semantic intent: the regulation targets a kind of affected party, not a particular person.

**Main weakness:** This is the most ARCO-specific encoding of the three gates. The `hasValue` + punning pattern is valid OWL 2 but unusual. It means the instance data must assert `iao:0000136 :NaturalPersonRole` (aboutness targeting the class IRI), which is an encoding convention that an instance author must know. It is also not obvious that `iao:0000136` (is_about) is the right relation for "this scenario affects people in this role category" — `is_about` is an IAO relation designed for information artifacts being *about* things, not for processes *affecting* things. The use is defensible (the scenario *specification* is about the role category) but stretches the standard reading of `is_about`.

**Why ARCO still uses it:** The alternatives are worse. Creating a custom relation (e.g., `affects_role`) violates ARCO's no-custom-properties rule and has no BFO/RO grounding. Using `someValuesFrom` would require instance tokens of NaturalPersonRole (specific role-bearer instances), which introduces unnecessary particulars for what is genuinely a category-level condition. `hasValue` on the class-as-individual is the least-bad encoding for a category-level aboutness claim using only standard relations.

---

## 4. Stable vs provisional choices

### Stable
Choices we currently have enough reason to preserve:

- **Three-gate decomposition itself.** The Act conditions on capability, intended use, and affected population. Separating these into independently necessary gates is a direct reflection of the regulatory structure. Each gate's independence is verified by regression test.
- **Capability as BFO disposition.** This is standard BFO; dispositions are what capabilities *are* in a realist ontology. No reason to change.
- **Intended use as directive ICE.** Provider intent in the Act is documentary and prescriptive. DirectiveICE is the right CCO category.
- **`cco:prescribes` + `someValuesFrom` for Gate 2 type-checking.** This is what makes Gate 2 a content gate rather than an existence gate. The mutation tests confirm it works. Weakening it would be a regression.
- **Reality/representation separation.** Dispositions in independent continuants, specifications in ICEs. This is load-bearing for the entire architecture. If it blurs, the distinction between "what the system can do" and "what documents say" collapses.
- **OWL-RL for classification, SHACL/SPARQL for validation/audit.** Layer separation prevents audit logic from silently becoming classification logic. This is an architectural invariant.
- **`HighRiskSystem` as a latent-risk class (Gate 1 only).** It captures "this system has a triggering capability" without requiring full documentary evidence. Useful as an early warning / pre-documentation classifier, provided it is not described or treated as identical to the final legal category of "high-risk AI system" under the Act — it is ARCO's formal precondition flag, not a complete legal determination.

### Provisional
Choices that work now but should not be treated as sacred:

- **Gate 3's `owl:hasValue` + punning pattern.** It works, it's not wrong, but it is the most ARCO-specific encoding and the one most likely to need revision if a better pattern emerges or if OWL 2 punning causes problems at scale. Treat as "current best encoding," not "settled."
- **`iao:0000136` (is_about) for the scenario → role-category link in Gate 3.** Defensible but stretchy. If a future version introduces a more precise relation for "specification addresses category X," that would be an upgrade, not a correction.
- **Inverse aboutness in the equivalentClass axioms.** Correct OWL 2 DL, works in owlrl, but reasoner-portability is untested. If ARCO ever needs to run on a different reasoner, this is the first thing to check.
- **CCO terms as local stubs.** Necessary for now (full CCO import has known blockers), but the stubs are a form of debt. They work only because ARCO uses a small number of CCO terms in a controlled way. This does not scale indefinitely.
- **Component-level decomposition in Gate 1.** Defensible and useful, but not legally compelled. If a future system type doesn't decompose cleanly into hardware components bearing dispositions (e.g., a purely cloud-based service), the pattern may need adjustment. The current encoding assumes a material bearer exists.
- **`AnnexIIITriggeringCapability` as a regulatory grouping class.** Works cleanly for extension via subclassing. But it is an ARCO invention, not a BFO natural kind. Its justification is purely legal-structural. If the legal structure changes, the class changes.

---

## 5. Decision

**Architecture stable, extend carefully.**

The three-gate pattern, the reality/representation split, the disposition-based capability modeling, and the layer separation are all defensible and should be preserved. Gate 3's encoding is the most provisional element, but it is not wrong — it is a local design choice that works and is tested. No redesign is needed before adding a third Annex III category.

The two conditions for safe extension are:
1. Each new category must follow the existing extension protocol and pass gate-removal regression tests, confirming the pattern actually generalizes (not just theoretically).
2. Gate 3's encoding should be monitored — if it starts producing surprising behavior or requiring increasingly tortured instance data as categories are added, that is the signal to revisit it.
