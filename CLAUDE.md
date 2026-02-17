# ARCO — Claude Code Instructions

ARCO = BFO/CCO-aligned OWL ontology for deterministic EU AI Act risk classification. OWL-RL reasoning + SHACL validation + SPARQL ASK produce outputs. No LLMs in the pipeline.

## Build & Verify

```bash
pip install -r requirements.txt
python 03_TECHNICAL_CORE/scripts/run_pipeline.py
```

Run after every change. Must print "ALL CHECKS PASSED" and exit 0.

## Context Selection

### PRIORITY (auto-load for technical tasks)
- `03_TECHNICAL_CORE/ontology/*.ttl` — Ontology + instances
- `03_TECHNICAL_CORE/validation/*.ttl` — SHACL shapes
- `03_TECHNICAL_CORE/scripts/run_pipeline.py` — Pipeline
- `03_TECHNICAL_CORE/reasoning/*.sparql` — SPARQL ASK queries

### SECONDARY (only if explicitly needed)
- `01_COMMERCIAL/`, `02_SYSTEM_OVERVIEW/`, `04_DIAGRAMS_AND_MODELS/`, `05_TECHNICAL_IMPLEMENTATION/`
- `README.md`, `ONTOLOGY_REVIEW.md`, `.github/workflows/`

### NEVER AUTOLOAD
- `runs/demo/*`, `03_TECHNICAL_CORE/.venv/`, generated artifacts, logs

## Architectural Memory

### Classes — Reality-Side (`ARCO_core.ttl`)
- `System` ⊑ ObjectAggregate — has_part some SystemComponent
- `SystemComponent` ⊑ Object; `HardwareComponent` ⊑ SystemComponent — has_disposition some CapabilityDisposition
- `CapabilityDisposition` ⊑ Disposition; `BiometricIdentificationCapability` ⊑ CapabilityDisposition
- `SoftwareArtifact` ⊑ ICE — NOT a SystemComponent

### Classes — Representation-Side (`ARCO_core.ttl`)
- `ComplianceDetermination` ⊑ ICE; `HighRiskDetermination` ⊑ ComplianceDetermination

### Classes — Governance (`ARCO_governance_extension.ttl`)
- `IntendedUseSpecification`, `UseScenarioSpecification`, `ComplianceObligationSpecification` ⊑ DirectiveICE
- `ProviderOrganization` ⊑ Organization; `ProviderRole`, `DeployerRole` ⊑ Role
- `NaturalPersonRole` ⊑ Role; `RemoteBiometricIdentificationProcess` ⊑ Process
- `AnnexIII1aApplicableSystem` ≡ 3-gate (capability + intended use + scenario)

### Bridge Axioms
- `AnnexIIITriggeringCapability` ≡ union(BiometricIdentificationCapability)
- `HighRiskSystem` ≡ System ∩ has_part some (has_disposition some AnnexIIITriggeringCapability)

### Relations (all BFO/RO/IAO/CCO — no custom properties)
`bfo:0000051` has_part · `ro:0000091` has_disposition · `iao:0000136` is_about · `cco:prescribes` · `cco:has_output` · `ro:0000057` has_participant · `ro:0000087` has_role

### Pipeline Flow
Load TTL → OWL-RL → SHACL → SPARQL ASK → certificate → `runs/demo/`

## Execution Rules

- Use Architectural Memory before reading files. Do not re-derive architecture.
- No repo-wide scanning. Grep within `03_TECHNICAL_CORE/` only.
- Minimal patches. No full rewrites unless requested.
- After every change, run pipeline. Do not batch changes to triples/shapes.
- If usage is low: save state, short summary, stop.

## Detail Files (load only when needed)

| File | Read when... |
|------|-------------|
| `docs/agent/ontology_rules.md` | Editing TTL, adding classes/relations, modeling new concepts |
| `docs/agent/coding_rules.md` | Modifying pipeline, scripts, CI, repo structure |
| `docs/agent/eu_ai_act_rules.md` | Working on Annex III, Article 6, classification logic |
