# Re-derive the classification yourself (stranger's recipe)

**Status: DRAFT (P6 batch 3, 2026-07-02). Proposed landing: `docs/RE_DERIVATION_RECIPE.md`, with `rederive.py` beside it at `docs/rederive.py`.** (Not under `03_TECHNICAL_CORE/scripts/`: that directory is governed by the output-provenance manifest, and this script is a reader's tool, not pipeline emission.) This recipe presumes the batch-3 catalog (`batch3_catalog/catalog-v001.xml`) and imports-closure patch (`batch3_imports_closure.patch`) have landed. Both fixture paths below were verified against executed runs; per-path execution status is stated inline.

---

## What you re-derive

ARCO claims a reader can take the axioms and the input facts and re-derive the classification with a standard OWL 2 DL reasoner, with no ARCO code in the loop. Concretely:

| Fixture (input facts) | Individual | Expected result after reasoning |
|---|---|---|
| `ARCO_instances_sentinel.ttl` (positive) | `Sentinel_ID_System` | Inferred types include `AnnexIII1aApplicableSystem` and `HighRiskSystem`. `AnnexIII5bApplicableSystem` is not among them. |
| `ARCO_instances_verification.ttl` (negative, walk-up verification kiosk) | `VerificationKiosk_001` | No Annex III type and no `HighRiskSystem` type is inferred. The only class-membership the reasoner derives for the individual is the asserted `System`. Open-world reading: those types are **not entailed** under the current commitments, which is different from a claim that the kiosk "cannot" be high risk. |

Files that constitute the reasoning input, all under `03_TECHNICAL_CORE/ontology/`:

```
catalog-v001.xml                  IRI-to-file map (the arco.ai IRIs are intentionally
                                  not registered on the web; this file is how tools
                                  resolve them locally, and loads fail loudly without it)
ARCO_core.ttl                     core classes + bridge axiom (declares the imports)
ARCO_governance_extension.ttl     the three-gate defined classes
ARCO_instances_sentinel.ttl       positive fixture
ARCO_instances_verification.ttl   negative fixture
imports/bfo-2020.owl              BFO 2020 (ISO/IEC 21838-2:2021)
imports/ro_bot.owl                RO slim module (release 2025-12-17)
imports/iao_bot.owl               IAO slim module (release 2026-03-30)
imports/cco_bot.owl               CCO slim module (release v1.7-2024-11-03)
```

Keep the directory layout intact. The catalog maps IRIs to paths relative to its own location.

---

## Path A: Protege (point and click)

*Execution status: desk-checked against catalog semantics and emulated by the executed OWL-API runs in `batch3_cold_load_log.txt`, which assemble exactly the ontology Protege would assemble. Not yet click-executed; Protege is not installed on the authoring machine. The owner executes this path once and attaches a screenshot (see `batch3_acceptance.md`).*

1. Clone the repository. Do not move the ontology files out of the tree.
2. Open Protege 5.6.x. File, Open, select `03_TECHNICAL_CORE/ontology/ARCO_instances_sentinel.ttl`.
3. Protege auto-detects `catalog-v001.xml` in the same folder. In the Active Ontology tab, the Ontology imports panel should show the governance ontology and, through it, core, BFO 2020, and the three slim modules, all resolved to local files. If any import renders red, open Preferences, "Imported ontologies", and point Protege at `catalog-v001.xml` explicitly.
4. Reasoner menu: select **HermiT** (bundled with Protege), then Start reasoner. Do not select Pellet for this load; the bundled Pellet lineage runs out of memory preparing the RO slim's 110 property-chain axioms (see the bound at the end of this document).
5. Entities tab, Individuals, select `Sentinel_ID_System`. In the Description pane under "Types", inferred types render on a pale yellow background. Expect **`AnnexIII1aApplicableSystem`** and **`HighRiskSystem`** alongside the asserted `System`. `AnnexIII5bApplicableSystem` should not appear.
6. Negative control: File, Open in new window, `ARCO_instances_verification.ttl`, same reasoner steps. `VerificationKiosk_001` shows only the asserted `System`; no Annex III type appears among the inferred types.
7. Both loads should report the ontology consistent (no red "inconsistent ontology" banner) and no unsatisfiable classes under owl:Nothing.

## Path B: command line, clean environment (owlready2 + Pellet)

*Execution status: executed 2026-07-01 in the P3.4 clean room (runs A2, B, C, D, E; raw logs archived at `p3_4_cleanroom_archive/`). This is the path that adds a third reasoner engine, Pellet, with zero ARCO code in the loop.*

Prerequisites: Python 3.11 or later, Java 11 or later on PATH.

```
mkdir rederive_arco && cd rederive_arco && mkdir ontology_files
python -m venv venv
venv/Scripts/pip install owlready2 rdflib        # (Linux/macOS: venv/bin/pip)

# copy the 8 ontology files (NOT the catalog; see note below) FLAT into ontology_files/:
#   bfo-2020.owl ro_bot.owl iao_bot.owl cco_bot.owl
#   ARCO_core.ttl ARCO_governance_extension.ttl
#   ARCO_instances_sentinel.ttl ARCO_instances_verification.ttl

# copy rederive.py (ships beside this recipe) into rederive_arco/, then:
venv/Scripts/python rederive.py pos_closure ARCO_instances_sentinel.ttl     pellet --no-bots
venv/Scripts/python rederive.py neg_closure ARCO_instances_verification.ttl pellet --no-bots
venv/Scripts/python rederive.py pos_full    ARCO_instances_sentinel.ttl     hermit
venv/Scripts/python rederive.py neg_full    ARCO_instances_verification.ttl hermit
```

What the script does, and why it exists: owlready2 reads neither Turtle nor XML catalogs, so `rederive.py` first merges the files with rdflib, **strips all `owl:imports` triples** (the IRIs are intentionally dead on the web; in a merged file they would only make an imports-following loader error), serializes to N-Triples, then loads that into owlready2 and runs the selected reasoner over the merged axioms. Assembly is rdflib only; reasoning is the Java reasoner; no ARCO Python is imported at any point.

Flags:

- `--no-bots` reasons over BFO + core + governance + fixture only (the pre-closure imports web). Use this for Pellet.
- `--no-ro` reasons over the full union minus `ro_bot.owl`. Also Pellet-safe.
- no flag = full 8-file union. Use this for HermiT only.

Expected output, positive fixture (verbatim from the executed Pellet run):

```
CONSISTENT: True
unsatisfiable classes: none
Sentinel_ID_System asserted+inferred is_a (direct): [core.System, core.AnnexIII1aApplicableSystem]
ENTAILED Sentinel_ID_System rdf:type :AnnexIII1aApplicableSystem ? True
ENTAILED Sentinel_ID_System rdf:type :AnnexIII5bApplicableSystem ? False
ENTAILED Sentinel_ID_System rdf:type :HighRiskSystem ? True
```

Expected output, negative fixture:

```
CONSISTENT: True
unsatisfiable classes: none
ENTAILED VerificationKiosk_001 rdf:type :AnnexIII1aApplicableSystem ? False
ENTAILED VerificationKiosk_001 rdf:type :AnnexIII5bApplicableSystem ? False
ENTAILED VerificationKiosk_001 rdf:type :HighRiskSystem ? False
```

## Path C: two commands with ROBOT (executed OWL-API receipt)

*Execution status: executed end-to-end 2026-07-02 in a fresh directory containing only the published files; full log with hashes and timings at `batch3_cold_load_log.txt`.*

If you have [ROBOT](http://robot.obolibrary.org/) (the OBO release tool, OWL-API based), the catalog does all the assembly work and no merging script is needed. From `03_TECHNICAL_CORE/ontology/`:

```
robot merge  --catalog catalog-v001.xml --input ARCO_instances_sentinel.ttl --output merged.owl
robot reason --reasoner hermit --axiom-generators "ClassAssertion SubClass" \
             --include-indirect true --input merged.owl --output reasoned.owl
```

The single fixture input pulls in the entire pinned closure through the catalog (852 KB merged from a 7 KB input in the executed run). `reasoned.owl` then contains the materialized class assertions; look for the fixture individual's `rdf:type` entries. Same commands with `ARCO_instances_verification.ttl` for the negative. Exit 0 on `robot reason` means HermiT found the ontology consistent. Expect roughly 5 to 10 minutes per reasoning run.

---

## Bounds (read before quoting any agreement claim)

1. **Three engines, stated precisely.** OWL-RL (the pipeline's rule-based reasoner), HermiT (tableau; run independently by CI via ROBOT, by the clean room via owlready2, and by the cold load via ROBOT from catalog resolution), and Pellet 2.3.1 (tableau; clean room only) produce the same verdicts on both fixtures above: positive entails 1(a) and the high-risk flag, negative entails neither, both graphs consistent with zero unsatisfiable classes.
2. **The Pellet bound.** Pellet 2.3.1 (the build bundled with owlready2) never reasoned over the full union: it runs out of memory in role-box preparation (FSM determinization) over `ro_bot.owl`'s 110 `owl:propertyChainAxiom` declarations, at both 2 GB and 12 GB heap. Its agreement is demonstrated on the imports-closure and union-minus-RO assemblies only. A control run isolated the blocker to `ro_bot`, not to any ARCO axiom. The receipt that excluding the RO module does not change these verdicts: HermiT over the full union returns identical results on both fixtures. This holds for the checked fixtures and classes; nothing structurally guarantees it for future axioms, which is why CI re-runs HermiT on the full union for every fixture.
3. **What was checked.** Membership for three named classes plus consistency and unsatisfiability, per fixture. Not a full classification diff against the pipeline's reasoned graph.
4. **The negative is open-world.** "Not entailed under current commitments" is the strongest true statement. No path in this recipe supports "the kiosk cannot be high risk."
