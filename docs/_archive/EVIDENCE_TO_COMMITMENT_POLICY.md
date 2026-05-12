# Evidence to Commitment Policy

> **ARCO classifies reviewed ontological commitments, not source documents, vendor claims, extracted text, or LLM interpretations.**

**Status:** v0 draft — 2026-05-09. Subject to revision after first hand-authored example ledger and human modeling session.
**Purpose:** define which source evidence may support which ARCO assertion, which evidence is insufficient, and which kinds of claims must remain `cco:DescriptiveICE` (claims about reality) rather than reality-side particulars.
**Scope boundary:** this policy governs how external source documents (vendor docs, marketing, architecture diagrams, deployment specs, conformity declarations) are bridged into ARCO's instance TTL. It does **not** govern the ARCO-internal classification logic, which is fixed by `ARCO_governance_extension.ttl` and CLAUDE.md invariants.

## Central rule

**Provider-submitted documents may generate claim ICEs. They do not, by themselves, license assertions about reality-side dispositions, bearers, realized processes, deployment contexts, or legal exceptions.**

Promotion of a claim to a reality-side ARCO commitment is rare and conditional. The conditions are stated explicitly in this document. There is no automation path that bypasses them.

## Why this policy exists

ARCO's classifier expects already-adjudicated facts: a `:System`, a `:HardwareComponent`, a material-ish bearer, a `:CapabilityDisposition`, a prescribed process token, a use-scenario ICE, a designated role universal. **Real-world source documents do not supply these.** They supply product claims, marketing verbs, architecture hints, deployment contexts, screenshots, "supports X," "may be used for Y," and legal hedging.

Bridging the two is **adjudication, not extraction.** A naive automated pipeline that converts vendor text into ARCO triples without explicit adjudication produces a provenance-decorated artifact that *looks* like reality and *isn't*. That outcome is worse than no automation at all, because it inherits ARCO's formal-trust signals while smuggling in unreviewed claims.

This policy exists to make the adjudication explicit and disciplined.

## Hard guardrails

1. **No automated extraction may write directly to reality-side ARCO instance TTL.** Automated tools may produce `cco:DescriptiveICE` claim artifacts; human review converts a subset of those to ARCO commitments.

2. **Every ARCO instance triple in `03_TECHNICAL_CORE/ontology/ARCO_instances_*.ttl` must trace to a human-adjudicated decision.** The decision and its evidence must be inspectable.

3. **SaaS / API / cloud-only systems are out of v1 scope.** ARCO's current bearer model assumes hardware components in a deployed system the provider controls. Cloud APIs break this — the bearer is contested between the API endpoint, the running service instance, the underlying infrastructure, and the deploying integrator. v1 covers on-premise, device-like, or single-deployment systems where a hardware bearer is unambiguous.

4. **No LLM output may feed OWL-RL classification.** LLMs may surface candidate claims, summarize source evidence, or assist in adjudication-write-ups. They do not produce reality-side assertions. CLAUDE.md invariant 1 (deterministic).

5. **Marketing language is never sufficient on its own.** "Supports facial recognition" / "AI-powered" / "intended for" require corroboration from a technical artifact (datasheet, architecture diagram, integration spec) before any reality-side commitment.

## Evidence taxonomy

Evidence types ranked by what they may support.

### Tier 1 — High confidence (may support reality-side assertions)

- **Vendor technical documentation** with named hardware components and their functions (e.g. "the SQ-3 sensor performs facial template extraction on-device"). Cite document, version, page.
- **Architecture diagrams** that name components and data flow.
- **Conformity declarations** under EU directives (CE marking, Article 47 declarations under the AI Act). These are quasi-legal artifacts that the provider has signed.
- **Independently-tested benchmark reports** (e.g. NIST FRVT entries) that name the system under test and its function.

### Tier 2 — Medium confidence (may support claims; conditional reality-side)

- **Public datasheets** without independent verification.
- **Vendor marketing material** that explicitly names a function (e.g. "performs 1:N biometric identification") AND identifies a deployment context.
- **Product manuals** describing operator workflow.

Tier 2 evidence may support a reality-side assertion only when corroborated by a Tier 1 source. Standalone, it produces a `cco:DescriptiveICE` claim, not an ARCO commitment.

### Tier 3 — Low confidence (claim-only)

- **Marketing slogans** without technical specifics ("AI-powered", "smart", "intelligent").
- **Screenshots** of vendor sites or apps.
- **Blog posts**, press releases, conference summaries.
- **Reseller listings** with copy-paste vendor descriptions.
- **"Supports X" / "may be used for X" / "compatible with X"** without integration spec.

Tier 3 evidence never produces an ARCO commitment. It may produce a claim artifact for tracking what the vendor said publicly, used for audit trails (e.g. "the vendor has publicly claimed Y") but not for classification.

### Tier 4 — Insufficient

- **Inferred capabilities** ("this looks like a facial recognition system based on its product photo").
- **Aggregations of low-confidence sources** ("five blogs say it does X, so it does X").
- **LLM extractions** without human adjudication.
- **Translations or paraphrases** that lose technical specificity.

Tier 4 evidence does not enter ARCO at any layer. It may seed a research request to the vendor for Tier 1 corroboration.

## What evidence may support which ARCO assertion

Per ARCO assertion type:

### Reality side

| ARCO assertion | Minimum evidence required | Notes |
|---|---|---|
| `:System rdf:type :System` | Tier 1 product identification + deployment description | The "system" must be a specific named deployment, not a product family. |
| `:Component rdf:type :HardwareComponent` | Tier 1 architecture diagram or technical doc that names the component | If the component is "the cloud API," reject — out of v1 scope. |
| `bfo:0000051` (has-part) chain from `:System` to `:Component` | Same as `:Component` | The has-part triples encode the system's deployment topology. |
| `ro:0000091` (has-disposition) chain from `:Component` to a disposition particular | Tier 1 evidence that the component physically performs the function | Marketing language alone is not sufficient. The disposition is a real SDC; the evidence must support that the bearer can manifest the function. |
| Disposition typed as a specific `:*Capability` subclass | Tier 1 + Tier 2 corroboration for the specific kind | E.g. distinguishing identification from verification requires both a technical claim of the workflow (1:N vs 1:1) AND a deployment description that confirms it. |
| `:HardwareComponent` IRI with a stable identifier | Always required | No anonymous (blank-node) dispositions or components in certificate-grade data. |

### Representation side

| ARCO assertion | Minimum evidence required | Notes |
|---|---|---|
| `:IntendedUseSpecification rdf:type ...` | Tier 1 or Tier 2 vendor document stating intended use | The IUS is itself an ICE about the system; the evidence is the documentary source. |
| `cco:prescribes` from IUS to a process type | The intended-use document must explicitly name the process type, OR a clearly equivalent description | Inference here is risky; prefer documents that use the regulated language. |
| `:UseScenarioSpecification` referencing a role category | Vendor document or deployment-context evidence naming the affected entity class | "For natural persons" / "for individuals" / "for customers" maps to `:NaturalPersonRole`. |
| `cco:DescriptiveICE` claim artifact | Any tier (Tier 3 sources may seed claims for audit trail) | Claims do not imply commitments. They are records of what was asserted, by whom, with what backing. |
| `:HighRiskDetermination` ICE | Always generated by the pipeline; never authored manually | Output of classification, not input. |

## What stays as a claim ICE (never reality)

Even with strong evidence, certain assertions stay representation-side:

- **Vendor self-certifications** ("we comply with GDPR"). Stays as a `:DescriptiveICE`. Compliance is a legal-institutional state, not a physical property.
- **Article 6(3) derogation claims**. Stay as `:DerogationClaim` ICEs. ARCO does not adjudicate the legal claim; it surfaces it. This is queued as `modeling_decisions_queue.md` Q7 — do not formalize as OWL consequence.
- **5(b) fraud-detection exclusion claims**. Same as derogation. Queued as Q8.
- **Provider role / deployer role assignments**. These are conferred by registration, not by physical state. Per the role/disposition litmus (Capabilities §3.1).

## What requires human review (always)

These cases must not be automated under any circumstances:

1. **SaaS / API / cloud-only systems.** Out of v1 scope. Until the bearer model is adjudicated in a human modeling session, these systems do not enter ARCO.
2. **Hardware-software amalgam edge cases.** Per Capabilities §4 — when the bearer of a capability is genuinely a running composite (running model on running hardware), the decomposition into `:HardwareComponent` and `:SoftwareArtifact` requires human judgment. The simplification used in `LIMITATIONS.md §3.5` works for the kiosk / device case; for novel deployments it is not a default.
3. **Cross-deployment classification.** When evidence suggests the same product is sold in two configurations (e.g. on-prem and cloud), each deployment is a distinct `:System`. Human reviews which configuration the source describes.
4. **Article 5 prohibition vs Annex III high-risk routing.** Real-time RBI in a public space is Article 5 prohibited, not Annex III high-risk. ARCO does not currently distinguish (LIMITATIONS §3.7.c). Human reviews whether the system is real-time and where deployed before any 1(a) commitment.
5. **Article 6(3) derogation candidacy.** Surfaces as `:DerogationClaim` flag; legal review decides. Never assert "this system qualifies for derogation" as a reality-side fact.
6. **5(b) fraud-detection exclusion candidacy.** Same.
7. **Determinate vs determinable capability classification.** When the source evidence supports "biometric identification" but doesn't distinguish 1:1 verification from 1:N identification, human disambiguation is required. The verification vs identification distinction is load-bearing for ARCO's 1(a) classification.

## What must never feed OWL classification

These are hard NOs. Any pipeline that violates them is broken:

- **Unreviewed LLM-extracted assertions.** LLM output may surface candidates; human adjudication writes triples.
- **Aggregated low-confidence claims** as if they were facts.
- **Marketing language directly converted to typed dispositions.**
- **Cross-document inferences without human approval.**
- **Pattern-matched component names without technical backing** (e.g. seeing the word "module" in a datasheet does not produce a `:HardwareComponent` triple).

## v1 scope: the kiosk biometric example

The first hand-authored evidence ledger covers exactly one case:

> **A device-like biometric access kiosk distinguishing 1:1 verification from 1:N identification.**

This case is chosen because:
- The bearer is unambiguous (a hardware device).
- The capability distinction (verification vs identification) maps cleanly to ARCO's existing classes (`:BiometricVerificationCapability` vs `:BiometricIdentificationCapability`).
- The 1(a) trigger depends on the distinction.
- Sentinel-ID already covers identification; the kiosk is the verification-only counterpart, and verification kiosks are already a fixture (`ARCO_instances_verification.ttl`).

The example proves: **ARCO can adjudicate the 1(a) trigger from realistic source evidence, when the source case fits ARCO's bearer assumptions.**

It does **not** prove ARCO can handle SaaS, API-only, or amalgam cases. Those are out of v1 scope.

## Implementation phasing

Per `KB/00_INBOX_RAW/Substack+Linkedin/...` and the user's policy-first stance:

1. **Phase 0 (this doc, v0).** Policy stated. No tooling. No examples beyond the existing fixtures.
2. **Phase 1 (next).** One hand-authored evidence ledger for the kiosk biometric case, covering one verification-only system, one identification system, and the discriminating evidence between them. Format: per-triple, name source document, page, tier, adjudication notes. Goal: prove the policy is usable on a real case.
3. **Phase 2 (only after Phase 1 reveals patterns).** Consider light tooling: a manual review interface, a claim-vs-commitment ledger schema, structured citation fields. No automation.
4. **Phase 3 (only after Phase 2 stabilizes).** Consider LLM-assisted candidate surfacing — never assertion. Output is always a candidate for human review, never a commitment.

There is no automation roadmap that bypasses Phase 1 + Phase 2. Skipping is exactly the failure mode this policy exists to prevent.

## What this policy is not

- It is not a vendor-facing document. It explains ARCO's discipline to the team, not to the systems being classified.
- It is not legal authority. The legal scope boundaries live in `LIMITATIONS.md §1` and `§8`. This policy is the operational discipline for getting source documents into ARCO.
- It is not a replacement for the `extension_protocol.md`. New Annex III categories still go through the protocol. This policy governs how a *single instance* gets adjudicated, not how a category is added.
- It is not the place to expand ARCO's bearer model. SaaS / API / amalgam handling is queued in `runs/loop/2026-05-09_beverley-research/modeling_decisions_queue.md`. Until those decisions land, the v1 scope holds.

## Cross-references

- `LIMITATIONS.md §1, §3.5, §3.7, §5` — scope boundaries that constrain this policy.
- `docs/agent/extension_protocol.md` (gitignored agent guidance) — protocol for adding new Annex III categories.
- `runs/loop/2026-05-09_beverley-research/modeling_decisions_queue.md` — queued modeling questions, including SaaS bearer model.
- `KB/20_COMPILED/evaluator-lenses/defensible-determination-chain.md` — the trust-chain framing this policy operationalizes.
- `03_TECHNICAL_CORE/ontology/ARCO_instances_verification.ttl` — existing verification kiosk fixture for the v1 example case.

## Open questions for v1 ledger work

1. What citation format gives auditors enough provenance without becoming a parallel ontology? (Source document + version + page + adjudicator + adjudication date + tier seems minimal.)
2. Where does the ledger live? In `KB/` (gitignored), `docs/` (tracked), or `03_TECHNICAL_CORE/evidence_ledgers/` (new tracked dir)?
3. How do claim ICEs get linked to their source-document evidence in the TTL? `iao:0000136` aboutness chains exist; the question is whether the source-document is itself an ICE in the graph or stays in the ledger out-of-band.
4. What's the audit query that would surface "this `:System` instance has triples that don't trace to ledger entries"? (A hygiene check, not a classification gate.)

These are next-iteration questions, not v0 blockers.
