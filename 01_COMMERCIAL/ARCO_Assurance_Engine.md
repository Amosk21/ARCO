# The Sentinel Glass-Box Assurance Engine

**Deterministic Regulatory Classification for AI Systems**

*Alex Moskowitz*

---

## 1. What ARCO Does (The Value Proposition)

ARCO provides deterministic classification of AI systems against regulatory criteria (e.g., EU AI Act Article 6 / Annex III), independent of probabilistic model outputs.

Unlike tools or reviews that rely on statistical similarity, checklists, or human judgment alone, ARCO produces logically necessary conclusions: if a system is classified as triggering high-risk conditions, that classification follows as a logical consequence of the explicitly stated facts and defined rules.

This is "glass-box" classification. Every conclusion is inspectable, traceable, and auditable.

---

## 2. What the Client Actually Buys (The Assessment Pipeline)

ARCO is delivered as a structured, three-phase assessment pipeline that moves from unstructured documentation to auditable classification.

### Phase A: Structured Ingestion (Neuro Layer)

**Input**

The client provides existing system documentation: model cards, technical specifications, intended-use descriptions, internal memos, and design artifacts.

**Process**

Large language models are used only as candidate extractors. They scan unstructured documents to identify potential system capabilities (e.g., biometric identification, emotion recognition, profiling).

**Design Principle**

LLMs are not trusted to determine classification. They propose candidates; they never make decisions.

This phase exists to organize reality, not to judge it.

### Phase B: Deterministic Verification (Symbolic Layer)

**Input**

Structured candidates produced in Phase A.

**Process**

Candidates are mapped into the NCOR/ARCO ontology stack, grounded in Basic Formal Ontology (BFO).

Two deterministic mechanisms are applied:

- **SHACL validation** enforces structural completeness and coherence, blocking hallucinated or underspecified claims.
- **SPARQL queries** test whether the modeled system satisfies classification conditions defined in the ontology.

**Design Principle**

If a system triggers high-risk conditions, that result follows necessarily from the explicit assertions and defined classification criteria. There is no statistical confidence score. There is only a deterministic TRUE or FALSE.

### Phase C: Assurance Output (The Artifact)

**Deliverable**

The ARCO Classification Determination Report.

**Contents**

- **Classification:** Regulatory classification outcome (High-Risk path demonstrated; additional risk tiers are architecturally supported)
- **Formal Justification:** Human-readable explanations grounded in explicit regulatory clauses
- **Audit Trail:** A complete log of SHACL validation results and SPARQL query outputs

This artifact is suitable for internal governance, external audits, regulators, and procurement reviews.

---

## 3. Why ARCO Wins (The Differentiator)

| Approach | How It Works | Why It Fails | ARCO Advantage |
|----------|--------------|--------------|----------------|
| Law Firms | Manual review | Slow, expensive, subjective | Deterministic, fast, auditable |
| Tech Consultants | RAG / LLM analysis | Probabilistic, hallucinates classification | Deterministic logic, not prediction |
| SaaS Checklists | Self-attestation | Garbage in, garbage out | Ontological rigor, enforced structure |

Sentinel does not "advise" on classification. It produces deterministic classifications.

---

## 4. How It Is Offered (Commercial Packaging)

ARCO is sold as a productized assurance service, not an open-ended consulting engagement.

**Tier 1: ARCO Audit**

A one-time assessment of an existing system.

*Output:* Classification Determination Report + remediation guidance.

**Tier 2: ARCO Design Partner**

Integration into the client's development lifecycle.

*Output:* Continuous classification checks triggered by architectural changes.

**Tier 3: ARCO Platform**

Licensing of the ontology and classification engine for internal audit or governance teams.

*Output:* In-house deterministic classification capability.

---

## 5. What Makes This Scalable

ARCO converts regulatory classification from a human-driven process into a repeatable determination engine.

---

## 6. What ARCO Is — and Is Not

- ARCO is **not** a chatbot.
- ARCO is **not** a checklist.
- ARCO is **not** probabilistic classification.

ARCO is a glass-box classification engine that produces auditable regulatory determinations from explicit assumptions.

**Probability is not enough.**
