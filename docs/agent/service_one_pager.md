# Applied Ontology Services — Alex Moskowitz

_Working draft — internal. Tighten before sending externally._

---

## What I do

I formalize ambiguous technical and governance language into explicit, machine-tractable structures. The output is deterministic reasoning, not narrative review.

Specifically:

- Convert vague system, policy, or process descriptions into typed class models with explicit assumptions
- Build OWL-based reasoning layers with SHACL validation and SPARQL audit
- Produce traceable, auditable evidence artifacts for governance and compliance questions

The value is not in producing another framework document. It is in producing outputs that survive technical scrutiny and can be re-run, extended, and inspected.

---

## Proof of capability: ARCO

**ARCO** (AI Risk Classification Ontology) is a working OWL-RL classification pipeline grounded in BFO 2020 (ISO/IEC 21838-2) for EU AI Act Annex III risk classification.

**What it does:**

- Classifies AI systems against Annex III categories via formal entailment — not keyword matching, not hardcoded rules
- Three-gate logic: capability type, intended use, use scenario — each independently necessary and regression-tested
- Adversarial test cases (blank nodes, equivalence classes) verify the reasoner works on formal semantics, not string patterns
- Two-layer architecture: OWL-RL for classification, SHACL for documentary validation, SPARQL for audit — each layer independent
- Currently covers 2 of 11 Annex III categories (1a biometric identification, 5b creditworthiness evaluation)

**What it proves:**

- I can build formal ontology at a level that survives technical scrutiny
- I understand the separation between classification logic, structural validation, and audit layers
- I can make legal or regulatory language machine-tractable without overclaiming what the machine decides

**Affiliation:** National Center for Ontological Research (NCOR) — independent contributor

---

## Services

### 1. AI System Classification Structure Review

One AI system. One narrow regulatory or governance question. A structured output you can actually use.

**Deliverables:**

- Explicit system decomposition (what the system is, what it can do, how it is intended to be used)
- Assumption map: what is asserted, what can be inferred, what is underdetermined
- Formal reasoning output where applicable
- Clear limitations statement — what this review does not resolve

**Price:** fixed scope, $2k–$6k depending on system complexity

---

### 2. Semantic Governance Modeling Sprint

Take messy policy, process, or system documentation and produce a structured semantic model.

**Deliverables:**

- Typed class model
- Explicit relation structure
- Constraint and validation layer
- Data requirements map
- Annotated assumption list

**Price:** fixed scope, $2k–$8k

---

### 3. Deterministic Evidence Layer Design

For teams already doing AI governance or compliance work who need their outputs to be auditable and reproducible, not just narrative.

**Deliverables:**

- Definition of what must be asserted, what can be inferred, what must be validated, what stays narrative
- Structured evidence layer design
- Explicit documentation of reasoning chain and its limits

**Price:** fixed scope, $3k–$8k

---

## What I do not do

- Legal determinations or compliance certifications
- Full-coverage EU AI Act auditing (ARCO currently covers 2 of 11 Annex III categories)
- Automated intake or self-serve tooling
- Work that requires a finished product rather than applied expertise

---

## Before sending this externally

- [ ] Add contact information (LinkedIn, email)
- [ ] Decide whether to name NCOR or use softer affiliation language
- [ ] Confirm pricing comfort — lower end for first engagement is fine
- [ ] Remove this checklist
