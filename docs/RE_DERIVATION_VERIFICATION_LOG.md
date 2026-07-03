# Re-derivation verification log (executed cold load)

This is the committed record of the executed command-line re-derivation described in [`RE_DERIVATION_RECIPE.md`](RE_DERIVATION_RECIPE.md) (Path B): a cold, catalog-based tool load from a fresh working directory containing only the published ontology files, followed by HermiT reasoning on both fixtures, with no ARCO code in the loop. It exists so that a reader who runs the recipe can compare their run against a recorded one. If you follow the recipe and see a different verdict than the ones below, that is a finding; please open an issue with your log.

Executed: 2026-07-03.

## Environment

| Component | Version |
|---|---|
| OS | Windows 11 Pro |
| Java | 25.0.1 (2025-10-21 LTS) |
| Loader / reasoner harness | ROBOT 1.9.10 (OWL-API based), `ROBOT_JAVA_ARGS=-Xmx6G` |
| Python | 3.14.2 |
| rdflib | 7.5.0 |

Python was used only to read the reasoned RDF/XML output and print verdicts. No reasoning and no ARCO pipeline code ran in Python. No ontology IRI resolved over the network during this run; all import resolution was catalog-local (demonstrated by the fail-loud control in step 6).

## Input files

The fresh working directory contained exactly these nine files, copied byte-for-byte from `03_TECHNICAL_CORE/ontology/` with the `imports/` subdirectory layout preserved:

| File | md5 | bytes |
|---|---|---|
| `catalog-v001.xml` | `d116152a2dcc01aa89c6899cb52b56ef` | 1,844 |
| `ARCO_core.ttl` | `86d7f863302f1028c89cc37e0a3fd011` | 24,080 |
| `ARCO_governance_extension.ttl` | `40435e2a192c9caaeca025dbb62e5d7f` | 57,940 |
| `ARCO_instances_sentinel.ttl` | `c51afb65e56aff4ab22a7c877fd8dcd2` | 7,100 |
| `ARCO_instances_verification.ttl` | `7caabd6b59e48562923fc992e1d45405` | 6,851 |
| `imports/bfo-2020.owl` | `a9caafba761ae33a84fbcf2372f5bc79` | 100,088 |
| `imports/ro_bot.owl` | `04d22689d82f2772b0fd360cfe789998` | 296,003 |
| `imports/iao_bot.owl` | `65686cc77eea4c1fba876210f58a9580` | 116,277 |
| `imports/cco_bot.owl` | `99504523c70459f2e2d366306add9560` | 378,937 |

Line-ending note: these hashes are of the files as checked out on the executing machine (Windows). A checkout that converts line endings (for example git `core.autocrlf` on another platform) will change the text-file hashes without changing any triple. The authoritative identity check is a clean git checkout of the commit that ships this log; the content-level comparison points are the triple counts and verdicts below.

## Step 1: cold merge, positive fixture

```
robot merge --catalog catalog-v001.xml --input ARCO_instances_sentinel.ttl --output merged_sentinel.owl
```

Exit 0, wall time under 2 seconds. Output `merged_sentinel.owl`: 854,483 bytes, md5 `9da53a2091a99fd7abde1b39f009391f`. The input fixture is 7,100 bytes; everything else arrived by following `owl:imports` through the catalog (fixture -> governance -> core -> BFO 2020 + the three slim modules).

Resolved-imports confirmation (marker counts in the merged output, `grep -c`):

| Marker | Count |
|---|---|
| `BFO_0000016` (BFO disposition) | 12 |
| `RO_0000091` (has disposition) | 8 |
| `IAO_0000030` (information content entity) | 12 |
| `CommonCoreOntologies/Person` | 6 |
| `AnnexIII1aApplicableSystem` | 7 |
| `Sentinel_ID_System` | 10 |
| `owl:propertyChainAxiom` (all of ro_bot's) | 110 |
| leftover `owl:imports` (closure collapsed) | 0 |

All four foundation modules, core, governance, and the fixture are present: the merge assembled the full union from one input file.

## Step 2: catalog auto-detection control

```
robot merge --input ARCO_instances_sentinel.ttl --output merged_sentinel_auto.owl
```

Exit 0. Output md5 `9da53a2091a99fd7abde1b39f009391f`: byte-identical to the explicit `--catalog` run. ROBOT auto-detects `catalog-v001.xml` sitting next to the input file, so the flag is optional when the catalog is in place.

## Step 3: HermiT reasoning, positive fixture

```
robot reason --reasoner hermit --axiom-generators "ClassAssertion SubClass" --include-indirect true --input merged_sentinel.owl --output reasoned_sentinel.owl
```

Exit 0 (`robot reason` fails on inconsistency; exit 0 means HermiT found the ontology consistent). Wall time 543 seconds (9 m 03 s) on this machine. Output `reasoned_sentinel.owl`: 1,140,228 bytes; 10,240 triples when read back with rdflib.

Verdict extraction (rdflib read of the reasoned graph):

```
Sentinel_ID_System rdf:type :AnnexIII1aApplicableSystem  present? True
Sentinel_ID_System rdf:type :AnnexIII5bApplicableSystem  present? False
Sentinel_ID_System rdf:type :HighRiskSystem  present? True
Sentinel_ID_System rdf:type :System  present? True
```

All types on the individual in the ARCO core namespace: `AnnexIII1aApplicableSystem`, `HighRiskSystem`, `System`.

## Step 4: cold merge + HermiT reasoning, negative fixture (kiosk)

```
robot merge --catalog catalog-v001.xml --input ARCO_instances_verification.ttl --output merged_verification.owl
robot reason --reasoner hermit --axiom-generators "ClassAssertion SubClass" --include-indirect true --input merged_verification.owl --output reasoned_verification.owl
```

Merge: exit 0; `merged_verification.owl` 854,826 bytes, md5 `fc2d61008fa4f251c90a7fa21724c243`. Reason: exit 0 (consistent), wall time 468 seconds (7 m 48 s). Output `reasoned_verification.owl`: 1,139,095 bytes; 10,209 triples when read back with rdflib.

Verdict extraction:

```
VerificationKiosk_001 rdf:type :AnnexIII1aApplicableSystem  present? False
VerificationKiosk_001 rdf:type :AnnexIII5bApplicableSystem  present? False
VerificationKiosk_001 rdf:type :HighRiskSystem  present? False
VerificationKiosk_001 rdf:type :System  present? True
```

All types on the individual in the ARCO core namespace: `System`. Open-world reading: with ClassAssertion generation and `--include-indirect true`, HermiT materialized no Annex III or high-risk type for the kiosk. Those types are not entailed under the current commitments, which is not a claim that the kiosk "cannot" be high risk.

## Step 5: verdict script

The verdict lines above are the verbatim output of the exact Python snippet inlined in the recipe's Path B (step 5 of the command block), run against the two reasoned graphs produced in steps 3 and 4.

## Step 6: fail-loud control (catalog removed)

The same files were copied to a sibling directory without `catalog-v001.xml`:

```
robot merge --input ARCO_instances_sentinel.ttl --output merged_nocat.owl
```

Exit 1, no output file produced. Error:

```
Could not load imported ontology: <https://arco.ai/ontology/governance> Cause: arco.ai
```

This is the pin property working as intended for ROBOT: without the catalog, the load is refused at the first unresolvable import rather than silently fetching an unpinned upstream or silently dropping modules. Other OWL tools may report missing imports and continue with a partial ontology, so confirm the import closure resolved before trusting a load in a different tool.

## Result summary

Cold catalog-based tool load: executed. Loader: ROBOT 1.9.10 (OWL-API). Fresh directory, only the published files. Resolution: 100% catalog-local, zero network. Reasoner: HermiT.

- Positive fixture (`Sentinel_ID_System`): `AnnexIII1aApplicableSystem` and `HighRiskSystem` entailed; `AnnexIII5bApplicableSystem` not entailed. Consistent.
- Negative fixture (`VerificationKiosk_001`): no Annex III type and no `HighRiskSystem` type entailed; only the asserted `System`. Consistent.

These verdicts match the pipeline's OWL-RL results and CI's HermiT cross-check on the same fixtures. For the scope of what was checked and the recorded Pellet memory bound, read the Bounds section of the recipe before quoting any agreement claim.
