# Re-derive the classification yourself (stranger's recipe)

## What you re-derive

ARCO claims a reader can take the axioms and the input facts and re-derive the classification with a standard OWL 2 DL reasoner, with no ARCO code in the loop. Concretely:

| Fixture (input facts) | Individual | Expected result after reasoning |
|---|---|---|
| `ARCO_instances_sentinel.ttl` (positive) | `Sentinel_ID_System` | Inferred types include `AnnexIII1aApplicableSystem` and `HighRiskSystem`. `AnnexIII5bApplicableSystem` is not among them. |
| `ARCO_instances_verification.ttl` (negative, walk-up verification kiosk) | `VerificationKiosk_001` | None of the three target classes (`AnnexIII1aApplicableSystem`, `AnnexIII5bApplicableSystem`, `HighRiskSystem`) appears among the inferred types. The individual keeps its asserted `System` type plus the upper-ontology supertypes the closure derives for every individual. Open-world reading: those types are **not entailed** under the current commitments, which is different from a claim that the kiosk "cannot" be high risk. |

Files that constitute the reasoning input, all under `03_TECHNICAL_CORE/ontology/`:

```
catalog-v001.xml                  IRI-to-file map (the arco.ai IRIs are currently
                                  unregistered, so nothing resolves online today;
                                  this file is the authoritative mapping to the
                                  pinned local files, regardless of what that
                                  domain serves in the future)
ARCO_core.ttl                     core classes + bridge axiom (declares the imports)
ARCO_governance_extension.ttl     the three-gate defined classes
ARCO_instances_sentinel.ttl       positive fixture
ARCO_instances_verification.ttl   negative fixture
imports/bfo-2020.owl              BFO 2020 (ISO/IEC 21838-2:2021)
imports/ro_bot.owl                RO slim module (release 2025-12-17)
imports/iao_bot.owl               IAO slim module (release 2026-03-30)
imports/cco_bot.owl               CCO slim module (release v1.7-2024-11-03)
```

Keep the directory layout intact. The catalog maps IRIs to paths relative to its own location. Without the catalog, ROBOT refuses the load at the first unresolvable import; other OWL tools may report missing imports and continue with a partial ontology, so confirm the import closure resolved before trusting a load.

---

## Path A: Protege (point and click)

*This path is specified but has not yet been click-executed by the maintainer; the command-line path below was executed end-to-end. If you execute the Protege path and see a different result, please open an issue.*

1. Clone the repository. Do not move the ontology files out of the tree.
2. Open Protege 5.6.x. File, Open, select `03_TECHNICAL_CORE/ontology/ARCO_instances_sentinel.ttl`.
3. Protege auto-detects `catalog-v001.xml` in the same folder. In the Active Ontology tab, the Ontology imports panel should show the governance ontology and, through it, core, BFO 2020, and the three slim modules, all resolved to local files. If any import renders red, open Preferences, "Imported ontologies", and point Protege at `catalog-v001.xml` explicitly.
4. Reasoner menu: select **HermiT** (bundled with Protege), then Start reasoner. Do not select Pellet for this load; the bundled Pellet lineage runs out of memory preparing the RO slim's 110 property-chain axioms (see the Bounds section below).
5. Entities tab, Individuals, select `Sentinel_ID_System`. In the Description pane under "Types", inferred types render on a pale yellow background. Expect **`AnnexIII1aApplicableSystem`** and **`HighRiskSystem`** alongside the asserted `System`. `AnnexIII5bApplicableSystem` should not appear.
6. Negative control: File, Open in new window, `ARCO_instances_verification.ttl`, same reasoner steps. For `VerificationKiosk_001`, expect the inferred-types pane to show upper-ontology supertypes (the reasoner derives these for every individual, so a populated pane is normal) but NONE of `AnnexIII1aApplicableSystem`, `AnnexIII5bApplicableSystem`, or `HighRiskSystem`.
7. Both loads should report the ontology consistent (no red "inconsistent ontology" banner) and no unsatisfiable classes under owl:Nothing.

## Path B: command line with ROBOT (executed end-to-end)

*Execution status: executed end-to-end from a fresh directory containing only the published files, with every import resolved through the catalog and no ARCO code in the loop. A dated record of that run (tool versions, timings, verdicts, merged-closure hashes) is the [Reference run](#reference-run-pinned-snapshot-2026-07-03) section at the end of this document; compare your own run against it.*

Prerequisites: Java 11 or later on PATH; [ROBOT](http://robot.obolibrary.org/) (`robot.jar`, the OBO release tool, OWL-API based; the executed run used ROBOT 1.9.10); Python 3 with `rdflib` for reading the reasoned output. Assembly and reasoning are ROBOT only; Python only prints the verdicts, and no ARCO Python is imported at any point.

The commands below are the sequence that was executed, verbatim except for machine-local paths:

```
# 1. Fresh working directory; copy in the nine published files, layout preserved:
#      catalog-v001.xml
#      ARCO_core.ttl                    ARCO_governance_extension.ttl
#      ARCO_instances_sentinel.ttl      ARCO_instances_verification.ttl
#      imports/bfo-2020.owl   imports/ro_bot.owl
#      imports/iao_bot.owl    imports/cco_bot.owl

# 2. venv for the verdict-reading step only
python -m venv venv
venv/Scripts/pip install rdflib          # (Linux/macOS: venv/bin/pip)

# 3. Positive fixture: merge, then reason. The single fixture input pulls in
#    the entire pinned closure through the catalog (fixture -> governance ->
#    core -> BFO 2020 + the three slim modules); the merge collapses the
#    imports, so no owl:imports triples survive in the merged output.
java -jar robot.jar merge --catalog catalog-v001.xml \
    --input ARCO_instances_sentinel.ttl --output merged_sentinel.owl
java -jar robot.jar reason --reasoner hermit \
    --axiom-generators "ClassAssertion SubClass" --include-indirect true \
    --input merged_sentinel.owl --output reasoned_sentinel.owl

# 4. Negative fixture: same two commands.
java -jar robot.jar merge --catalog catalog-v001.xml \
    --input ARCO_instances_verification.ttl --output merged_verification.owl
java -jar robot.jar reason --reasoner hermit \
    --axiom-generators "ClassAssertion SubClass" --include-indirect true \
    --input merged_verification.owl --output reasoned_verification.owl

# 5. Read the verdicts out of the reasoned graphs.
venv/Scripts/python - <<'EOF'
import rdflib
CORE = "https://arco.ai/ontology/core#"
for fname, ind in [("reasoned_sentinel.owl", "Sentinel_ID_System"),
                   ("reasoned_verification.owl", "VerificationKiosk_001")]:
    g = rdflib.Graph(); g.parse(fname)
    types = {str(o) for o in g.objects(rdflib.URIRef(CORE + ind), rdflib.RDF.type)}
    for c in ["AnnexIII1aApplicableSystem", "AnnexIII5bApplicableSystem",
              "HighRiskSystem", "System"]:
        print(f"{ind} rdf:type :{c}  present? {CORE + c in types}")
EOF
```

What you should see, from the executed run (exact values in the [Reference run](#reference-run-pinned-snapshot-2026-07-03) snapshot below):

- `robot merge` exits 0 in seconds. The merged output is roughly 850 KB from a roughly 7 KB fixture input; everything beyond the fixture arrived via the catalog-resolved imports chain.
- The `--catalog` flag is optional here: ROBOT auto-detects `catalog-v001.xml` beside the input file. The executed run confirmed the flag-less merge output is byte-identical to the explicit `--catalog` run.
- `robot reason` exits 0 only if HermiT finds the ontology consistent (it fails on inconsistency). Expect roughly 5 to 10 minutes per reasoning run.
- Fail-loud control: the same merge run from a directory without `catalog-v001.xml` exits nonzero at the first unresolvable import ("Could not load imported ontology: <https://arco.ai/ontology/governance>") and produces no output file. It does not silently fetch an unpinned upstream or silently drop modules.

Expected verdicts, positive fixture (verbatim from the executed run):

```
Sentinel_ID_System rdf:type :AnnexIII1aApplicableSystem  present? True
Sentinel_ID_System rdf:type :AnnexIII5bApplicableSystem  present? False
Sentinel_ID_System rdf:type :HighRiskSystem  present? True
Sentinel_ID_System rdf:type :System  present? True
```

Expected verdicts, negative fixture:

```
VerificationKiosk_001 rdf:type :AnnexIII1aApplicableSystem  present? False
VerificationKiosk_001 rdf:type :AnnexIII5bApplicableSystem  present? False
VerificationKiosk_001 rdf:type :HighRiskSystem  present? False
VerificationKiosk_001 rdf:type :System  present? True
```

---

## Bounds (read before quoting any agreement claim)

1. **Three engines, stated precisely.** OWL-RL (the pipeline's rule-based reasoner), HermiT (tableau; run independently by CI via ROBOT on every push, by this recipe's catalog-resolved ROBOT cold load, and by a separate run through the owlready2 Python bridge), and Pellet 2.3.1 (tableau; owlready2 bridge run only) produce the same verdicts on both fixtures above: positive entails 1(a) and the high-risk flag, negative entails neither, both graphs consistent with zero unsatisfiable classes.
2. **The Pellet bound.** Pellet 2.3.1 (the build bundled with owlready2) never reasoned over the full union: it runs out of memory in role-box preparation (FSM determinization) over `ro_bot.owl`'s 110 `owl:propertyChainAxiom` declarations, at both 2 GB and 12 GB heap. Its agreement is demonstrated on the imports-closure and union-minus-RO assemblies only. A control run isolated the blocker to `ro_bot`, not to any ARCO axiom. The receipt that excluding the RO module does not change these verdicts: HermiT over the full union returns identical results on both fixtures. This holds for the checked fixtures and classes; nothing structurally guarantees it for future axioms, which is why CI re-runs HermiT on the full union for every fixture.
3. **What was checked.** Membership for three named classes plus consistency and unsatisfiability, per fixture. Not a full classification diff against the pipeline's reasoned graph.
4. **The negative is open-world.** "Not entailed under current commitments" is the strongest true statement. No path in this recipe supports "the kiosk cannot be high risk."

---

## Reference run (pinned snapshot, 2026-07-03)

This is a dated snapshot of one executed Path B run, recorded so you can compare your own run against it. Timings and text-file hashes vary across machines and line-ending settings; a different verdict is a finding, so please open an issue with your log.

- Tools: ROBOT 1.9.10 (`ROBOT_JAVA_ARGS=-Xmx6G`), Java 25.0.1, Python 3.14.2, rdflib 7.5.0, Windows 11.
- Merged closure md5: `9da53a2091a99fd7abde1b39f009391f` (`merged_sentinel.owl`, 854,483 bytes); `fc2d61008fa4f251c90a7fa21724c243` (`merged_verification.owl`, 854,826 bytes).
- Wall-clock: each merge under 2 seconds; HermiT reasoning 543 s (positive fixture), 468 s (negative fixture).
- Verdicts, positive fixture (`Sentinel_ID_System`): `AnnexIII1aApplicableSystem` True, `AnnexIII5bApplicableSystem` False, `HighRiskSystem` True, `System` True; consistent.
- Verdicts, negative fixture (`VerificationKiosk_001`): `AnnexIII1aApplicableSystem` False, `AnnexIII5bApplicableSystem` False, `HighRiskSystem` False, `System` True; consistent.

The CI closure check (`.github/workflows/robot-validate.yml`, step "Catalog import-closure check") re-verifies on every push that the catalog-resolved import chain equals the explicit file union, so the import-chain claim is re-derived continuously rather than only recorded in this snapshot.
