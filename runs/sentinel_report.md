# ARCO Determination Report

- **System**: Sentinel_ID_System
- **System IRI**: https://arco.ai/ontology/core#Sentinel_ID_System
- **Instances file**: C:\Github Repos\ARCO\03_TECHNICAL_CORE\ontology\ARCO_instances_sentinel.ttl
- **Run timestamp (UTC)**: 2026-02-13T01:01:23+00:00
- **Git commit hash**: 6bef956

- **Regime**: EU AI Act (Article 6 / Annex III)
- **Classification state**: ENTAILED
- **Classification label**: HighRiskSystem
- **Entailed class IRI**: https://arco.ai/ontology/core#HighRiskSystem

## Gate Results

| Gate | Result |
|---|---|
| Gate 1 (capability commitment) | PASS |
| Gate 2 (intended use) | PASS |
| Gate 3 (use scenario / affected role) | PASS |

## Check Results

| Check | Result |
|---|---|
| SHACL | PASS (violations: 0) |
| Traceability | PASS |
| Entailment | PASS |
| Latent risk | PASS |

## Evidence Paths

- Predicates used: `http://purl.obolibrary.org/obo/BFO_0000051` and `http://purl.obolibrary.org/obo/RO_0000091`
- Sentinel_ID_System --http://purl.obolibrary.org/obo/BFO_0000051--> Sentinel_FaceID_Module --http://purl.obolibrary.org/obo/RO_0000091--> Sentinel_FaceID_Disposition

## Missing Commitments

- (none)
These are missing ICE commitments required by the Annex III gate pattern; absence is not evidence of absence.
