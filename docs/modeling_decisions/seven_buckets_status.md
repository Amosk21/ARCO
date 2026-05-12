# Seven Buckets Status — What ARCO Populates and What It Refuses to Claim

## Purpose

The Seven Buckets framework at `CLAUDE.md` § The Seven Buckets is the structural completeness check for ARCO's modeling. Each bucket is a question any complete model of a thing must answer; failing to populate (or to honestly disclose a scope cut on) any bucket means a missing structural piece. This diagram records what ARCO currently populates, what is in progress, and what is deliberately scope-cut, with citations.

## Diagram

```mermaid
flowchart TB
  classDef populated fill:#dcfce7,stroke:#15803d,color:#052e16
  classDef inProgress fill:#fffbe6,stroke:#7c5e10,color:#3f2a00,stroke-dasharray:3 3
  classDef partial fill:#fef9c3,stroke:#a16207,color:#3f2a00
  classDef scopeCut fill:#fee2e2,stroke:#b91c1c,color:#450a0a,stroke-dasharray:5 4

  B1["BUCKET 1<br/>What is it?<br/>Material entities (Independent Continuants)<br/><br/>POPULATED<br/>:System :SystemComponent :HardwareComponent<br/>:ProviderOrganization cco:Person"]:::populated

  B2["BUCKET 2<br/>How is it?<br/>Qualities (Specifically Dependent Continuants)<br/><br/>IN PROGRESS<br/>Inscription qualities on source documents<br/>cco:InformationQualityEntity pattern<br/>scoped in conversation, seed pending<br/>(L1.2 reverted; re-add with corrected v1.7 IRIs)"]:::inProgress

  B3["BUCKET 3<br/>What can it do?<br/>Realizable entities (function, disposition, role)<br/><br/>POPULATED<br/>:CapabilityDisposition ⊑ bfo:0000016<br/>(latent-capacity target, NOT Function)<br/>:ProviderRole :DeployerRole :NaturalPersonRole"]:::populated

  B4["BUCKET 4<br/>What is happening?<br/>Processes (Occurrents)<br/><br/>POPULATED (typed tokens)<br/>:RemoteBiometricIdentificationProcess<br/>:CreditworthinessEvaluationProcess<br/>:BiometricVerificationProcess :AssessmentDocumentationProcess<br/>Kiosk has no realization (design-time scope)<br/>Sentinel asserts realization triple"]:::populated

  B5["BUCKET 5<br/>When and where is it?<br/>Temporal regions and sites<br/><br/>SCOPE CUT<br/>Design-time classifier does not model<br/>runtime context. Disclosed at LIMITATIONS.<br/>Activates only on extension to<br/>deployment-monitoring scope."]:::scopeCut

  B6["BUCKET 6<br/>How do we know?<br/>Generically Dependent Continuants (ICEs)<br/><br/>POPULATED (typed instances)<br/>:IntendedUseSpecification :UseScenarioSpecification<br/>:ComplianceDetermination :HighRiskDetermination<br/>:AssessmentDocumentation :RegulatoryContent<br/><br/>CONCRETIZATION IN PROGRESS<br/>ICEs not yet anchored to inscription bearers<br/>(L1.2 closes this; same row as Bucket 2)"]:::inProgress

  B7["BUCKET 7<br/>What grounds risk or capability?<br/>Material basis + realization<br/><br/>PARTIAL<br/>Sentinel exercises bfo:0000055 realization<br/>(:Surveillance_Run_001 realizes :Sentinel_FaceID_Disposition<br/>at ARCO_instances_sentinel.ttl:83-87)<br/>Kiosk no realization (deliberate; design-time)<br/>Deeper material-basis chain queued (Path Gamma)"]:::partial

  THESIS["ARCO thesis (CLAUDE.md line 11)<br/>Surfaces LATENT DISPOSITIONS at DESIGN TIME"]:::populated

  AND_CHECK["The AND is structural<br/><br/>A complete capability answer needs:<br/>System (B1) AND Capability (B3) AND<br/>Material basis (B7) AND Processes (B4) AND<br/>Temporal boundaries (B5 scope-cut) AND<br/>Evidence (B6) AND Inscriptions (B2)"]:::partial

  THESIS --> B3
  THESIS --> B7
  B1 --> AND_CHECK
  B2 -.->|"closes when L1.2 lands"| AND_CHECK
  B3 --> AND_CHECK
  B4 --> AND_CHECK
  B5 -.->|"scope-cut, not gap"| AND_CHECK
  B6 --> AND_CHECK
  B7 --> AND_CHECK
```

## Status legend

- **POPULATED** (green) — the bucket has instance commitments in the running graph; the pipeline exercises them; the entailment or audit they support fires.
- **IN PROGRESS** (yellow dashed) — the modeling decision is locked, the canon-grounding is verified, the design is in conversation, but the code or seed-list expansion has not yet committed. The bucket has the slot but not the instances.
- **PARTIAL** (yellow solid) — the bucket has some instance commitments but is not fully exercised; some structural pieces remain queued.
- **SCOPE CUT** (red dashed) — deliberately not modeled at current scope; disclosed in `LIMITATIONS.md` with rationale; would mis-extend ARCO's design-time framing to model.

## Verification table

| Bucket | Status | Verified against | OPEN_PROBLEMS reference |
|---|---|---|---|
| 1. Material entities | POPULATED | `ARCO_core.ttl:58-82`, `ARCO_governance_extension.ttl:45-64, 144-150`; `cco:Person` and `cco:Organization` at `cco_seed.txt:1, 8` | none |
| 2. Qualities (SDC) | IN PROGRESS | Pattern verified at CCO v1.7 `cco:InformationQualityEntity` (canonical IRI); seeds NOT in current `cco_seed.txt` (8 entries); L1.2 row reverted | L1.1 (ledger), L1.2 (reverted, planned for re-add) |
| 3. Realizable entities | POPULATED | `ARCO_core.ttl:84-105`; `:NaturalPersonRole` at `ARCO_governance_extension.ttl:323-327`; Disposition not Function per BFO 2020 [064-001] (canonical line at `bfo-2020.owl:1326-1327`); X.11 rationale-comment fix landed at `ARCO_core.ttl:26-38`; component-level bearer rationale at `LIMITATIONS.md §3.5` (three-stacked: traceability, hardware-software amalgam simplification, software-configurable deployment scope); see `decisions_justification_map.md` entries F2, S2 for the full justification map | none — Disposition framing locked per X.11 verdict |
| 4. Processes | POPULATED | `ARCO_governance_extension.ttl:290-321`; Sentinel realization at `ARCO_instances_sentinel.ttl:83-87`; kiosk has no realization (design-time scope) | L2.1 (bare token disclosure, DISCLOSED+BLOCKED) |
| 5. Temporal/site | SCOPE CUT | Disclosed at `LIMITATIONS.md` (design-time framing) | none — deliberate cut |
| 6. ICEs | POPULATED as typed; CONCRETIZATION IN PROGRESS | `ARCO_core.ttl:137-152`, `ARCO_governance_extension.ttl:113-130, 233-333`; concretization triples to bearer particulars not yet asserted on any fixture | L2.2 (`cco:is_tokenized_by`), L1.2 (kiosk concretization, reverted) |
| 7. Material basis + realization | PARTIAL | `ARCO_instances_sentinel.ttl:83-87` exercises `bfo:0000055`; kiosk omits by scope; deeper material-basis chain queued | Path Gamma (no explicit row yet; X.11 finding 5 queued as architectural redesign) |

## Notes on the THESIS arrow

The thesis (`CLAUDE.md` line 11) names latent dispositions at design time as ARCO's value proposition. The diagram links the thesis to Bucket 3 (the disposition class) and Bucket 7 (the material basis grounding the latent capacity). Both are load-bearing for the value claim. The X.11 review's finding 1 — proposed re-typing `:CapabilityDisposition` as `bfo:0000034 Function` — was verified WRONG; Disposition is the correct parent for the latent-capability target, because Function would narrow ARCO out of the latent case.

## What this diagram does NOT show

- Class hierarchies under each bucket (e.g., the full subclass tree from `bfo:0000023 Role` to `:ProviderRole` and `:NaturalPersonRole`). See `value_chain.md` and the ARCO_core / ARCO_governance_extension files for those.
- The OWL axiom shape of the three-gate classifier. See `three_gate_classifier.md`.
- The CDO question / certificate value chain. See `value_chain.md`.
- Fixture-by-fixture coverage. The verification table cites Sentinel and Kiosk specifically; fuller fixture coverage lives in the eventual `fixtures_map.md` (not yet authored).
- Accountability-to-individual extension. Queued in conversation, no OPEN_PROBLEMS row yet, not currently in any bucket's populated state.

## When to update

- Bucket 2 / Bucket 6 concretization transitions to POPULATED when L1.2 re-lands in `OPEN_PROBLEMS.md` and the inscription work commits.
- Bucket 5 transitions out of SCOPE CUT only if ARCO extends to monitor-deployment scope; if so, this whole diagram needs revising.
- Bucket 7 transitions from PARTIAL to POPULATED when the deeper material-basis chain (Path Gamma or its successor) commits.
- The X.11 verdict on the Disposition / Function question is locked; revisit only if a future BFO 2020 release changes the Function elucidation in `bfo-2020.owl`.
