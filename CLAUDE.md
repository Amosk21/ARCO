# ARCO — Project Constitution

ARCO = BFO/CCO-aligned OWL ontology for deterministic EU AI Act risk classification. OWL-RL reasoning + SHACL validation + SPARQL ASK produce outputs. No LLMs in the classification pipeline.

## Validate After Every Change

```bash
python 03_TECHNICAL_CORE/scripts/run_pipeline.py
```

Must print "ALL CHECKS PASSED" and exit 0. Run after each coherent unit of change. Do not batch changes to triples, shapes, or queries.

## Global Invariants (never violate regardless of task)

1. **Deterministic pipeline** — OWL-RL + SHACL + SPARQL only. LLMs may assist with candidate extraction; they do not drive classification.
2. **Two-layer architecture** — OWL-RL produces the classification (entailment). SPARQL ASK queries inspect the reasoned graph as an audit/documentation layer. These are not the same thing. Never describe SPARQL queries as classification logic.
3. **Content-sensitive documentary gates** — Gate 2 (prescribed process type) and Gate 3 (role category) check specific typed content via `owl:someValuesFrom` and `owl:hasValue`. Document existence is not sufficient.
4. **No cross-layer contradiction** — A certificate must not display "VERIFIED" for a classification while an audit query returns FAIL for the same condition. Diagnose the failing layer; do not paper over it.
5. **Reality/representation separation** — Capabilities = reality-side (BFO dispositions in independent continuants). Determinations/specifications = representation-side (IAO ICEs). Never conflate.
6. **No custom object properties** — BFO/RO/IAO/CCO relations only. `ro:0000091` has_disposition, not `ro:0000053` bearer_of.
7. **Sentinel-ID demo must pass** — All work produces additions. Do not delete existing classes, instances, or inference chains.

## Architectural Memory

### Classes — Reality-Side (`ARCO_core.ttl`)
- `System` ⊑ ObjectAggregate — has_part some SystemComponent
- `SystemComponent` ⊑ Object; `HardwareComponent` ⊑ SystemComponent — has_disposition some CapabilityDisposition
- `CapabilityDisposition` ⊑ Disposition; `BiometricIdentificationCapability` ⊑ CapabilityDisposition
- `SoftwareArtifact` ⊑ ICE — NOT a SystemComponent; dispositions inhere in hardware, not in information artifacts

### Classes — Representation-Side (`ARCO_core.ttl`)
- `ComplianceDetermination` ⊑ ICE; `HighRiskDetermination` ⊑ ComplianceDetermination

### Classes — Governance (`ARCO_governance_extension.ttl`)
- `IntendedUseSpecification`, `UseScenarioSpecification`, `ComplianceObligationSpecification` ⊑ DirectiveICE
- `ProviderOrganization` ⊑ Organization; `ProviderRole`, `DeployerRole` ⊑ Role
- `NaturalPersonRole` ⊑ Role; `RemoteBiometricIdentificationProcess` ⊑ Process
- `AnnexIII1aApplicableSystem` ≡ 3-gate equivalentClass (capability + prescribed process type + role category)

### Bridge Axioms
- `AnnexIIITriggeringCapability` ≡ union(BiometricIdentificationCapability) — biometrics only
- `HighRiskSystem` ≡ System ∩ has_part some (SystemComponent ∩ has_disposition some AnnexIIITriggeringCapability)
- Gate 2: `owl:someValuesFrom :RemoteBiometricIdentificationProcess` — type-checks the prescribed process token
- Gate 3: `owl:hasValue :NaturalPersonRole` — checks role category (universal), not a role-bearer instance

### Relations
`bfo:0000051` has_part · `ro:0000091` has_disposition · `iao:0000136` is_about · `cco:prescribes` · `cco:has_output` · `ro:0000057` has_participant · `ro:0000087` has_role

### Pipeline Flow
Load TTL → OWL-RL → SHACL → SPARQL ASK (audit layer) → certificate → `runs/demo/`

## Repo Map and Scoped Rules

Each directory contains a `CLAUDE.md` with rules specific to that area. Read it before editing files there.

| Area | Path | Scoped rules govern |
|------|------|---------------------|
| Core ontology | `03_TECHNICAL_CORE/ontology/` | Classes, bridge axioms, instances, BFO alignment |
| SHACL validation | `03_TECHNICAL_CORE/validation/` | Documentary completeness shapes |
| SPARQL audit | `03_TECHNICAL_CORE/reasoning/` | Post-reasoning audit checks, audit/classification distinction |
| Pipeline / scripts | `03_TECHNICAL_CORE/scripts/` | Python pipeline, CI, certificate output |
| Business / outward docs | `01_COMMERCIAL/`, `02_SYSTEM_OVERVIEW/`, `README.md` | Tone, accuracy, writing rules |

Detailed reference files (read when the task requires it, not by default):
- `docs/agent/ontology_rules.md` — full ontology hard constraints and patterns
- `docs/agent/coding_rules.md` — pipeline and CI rules
- `docs/agent/eu_ai_act_rules.md` — Annex III structure, derogation, Article 6
- `docs/agent/writing_rules.md` — outward-facing tone and accuracy rules
- `docs/agent/extension_protocol.md` — mandatory protocol for every new Annex III category addition

## Context Rules

- Use Architectural Memory above before reading TTL files. Do not re-derive architecture.
- Grep within `03_TECHNICAL_CORE/` only. No repo-wide scanning.
- Minimal patches. No full rewrites unless requested.
- **NEVER autoload**: `runs/demo/*`, `03_TECHNICAL_CORE/.venv/`, generated artifacts, logs, `ONTOLOGY_REVIEW.md`, `DESIGN_REVIEW_BRIEF.md`

## Determination Layer Precedence

For regulatory classification, layer authority is strictly ordered:

1. **OWL-RL entailment** — authoritative source for all regulatory determinations
2. **SHACL** — validates structural completeness of documentary artifacts only; does not classify
3. **SPARQL ASK** — audit/documentation layer; inspects the reasoned graph; does not classify

SPARQL and SHACL must never replicate, override, or serve as a substitute for OWL classification logic.

## Diagnose Before Rewriting

When a contradiction, failing check, or unexpected result appears:

1. Identify which layer is responsible — ontology axiom, instance data, SHACL shape, SPARQL query, or certificate formatter
2. Diagnose the root cause in that layer
3. Apply the minimal fix to the responsible layer only
4. Re-run the pipeline and confirm no cross-layer contradiction was introduced

Do not simultaneously edit ontology, SHACL, and SPARQL to make a failing check pass — that masks the root cause and can introduce hidden inconsistencies.

## Cross-Layer Safety Rule

Any change touching classification logic, gate conditions, audit queries, ontology semantics, or certificate output must be checked for contradiction risk across the full determination chain before finalizing. If a change at one layer could produce misleading output at another layer, diagnose and fix both sides — do not patch only the symptom.
