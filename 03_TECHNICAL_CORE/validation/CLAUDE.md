# SHACL Rules — `03_TECHNICAL_CORE/validation/`

Governs: `assessment_documentation_shape.ttl`

## What SHACL Does in This Pipeline

SHACL enforces structural completeness of documentary artifacts. It does NOT classify systems.

- SHACL FAIL = documentary record is structurally incomplete
- OWL classification FAIL = system does not satisfy the statutory condition
- These are independent failure modes. A system can be OWL-classified as high-risk with imperfect documentation, and a document can be SHACL-conformant while the system is not OWL-classified.

Do not conflate SHACL conformance with classification correctness.

## Pre-Edit Checklist

- [ ] New shapes use named IRIs (stable, traceable in audit reports) — not blank nodes
- [ ] `sh:targetClass` points to the correct class
- [ ] All property shapes include `sh:path`, `sh:minCount`, `sh:name`, `sh:description`
- [ ] SHACL failure does not silently block a valid OWL classification — verify they are genuinely independent
- [ ] Sentinel-ID SHACL still conforms after changes
- [ ] Pipeline passes: `python 03_TECHNICAL_CORE/scripts/run_pipeline.py`

## Hard Stops

**Named shapes only** — Blank-node shapes produce validation reports referencing anonymous nodes. Audit tools cannot trace them. Every property shape must have a stable IRI (e.g., `:PS_IUS_Prescribes`).

**No SPARQL-in-SHACL for primary conformance** — SPARQL-based SHACL constraints add a second query-engine dependency inside the validation layer. Justify explicitly with written rationale if added.

**SHACL ≠ classification engine** — Do not write SHACL constraints that replicate the OWL gate conditions. Gates are in the OWL equivalentClass axiom. SHACL checks that documentary artifacts exist and are structurally complete.

## Good / Bad Examples

```
Bad:  sh:property [ sh:path cco:prescribes ; sh:minCount 1 ] .  (blank node — anonymous in reports)
Good: :PS_IUS_Prescribes a sh:PropertyShape ;
        sh:path cco:prescribes ; sh:minCount 1 ;
        sh:name "Intended use prescribes process type" ;
        sh:description "Every IntendedUseSpecification must prescribe at least one process type." .
      :IntendedUseSpecificationShape sh:property :PS_IUS_Prescribes .
```
