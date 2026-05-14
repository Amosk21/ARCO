# ARCO Stack Versions

Single source-of-truth for every version pin in ARCO. Every row cites its source file. Every row has a verification command or a CI step that fails if the pin drifts.

**Last reviewed:** 2026-05-14

This doc exists because ARCO claims deterministic regulatory classification, and "deterministic" means every layer of the stack — ontology, reasoner, runtime, CI — must be pinned and reproducible. A drift on any row is a determinism leak.

---

## Foundational ontology imports

The reality-side commitments ARCO classifies against. Each is pinned to a specific upstream release and either loaded as a full local file (BFO) or extracted as a ROBOT BOT slim module from a pinned upstream (RO, IAO, CCO).

| Ontology | Pinned version | IRI namespace | Source file | How regenerated |
|---|---|---|---|---|
| BFO | 2020 (ISO/IEC 21838-2:2021) | `http://purl.obolibrary.org/obo/BFO_` | `03_TECHNICAL_CORE/ontology/imports/bfo-2020.owl` | Full local file, no extraction; matches IAO's own pattern of full-importing BFO |
| RO | release `2025-12-17` | `http://purl.obolibrary.org/obo/RO_` | `03_TECHNICAL_CORE/ontology/imports/ro_bot.owl` + `imports/seeds/ro_seed.txt` | `robot extract --method BOT` against pinned upstream RO release |
| IAO | release `2026-03-30` | `http://purl.obolibrary.org/obo/IAO_` | `03_TECHNICAL_CORE/ontology/imports/iao_bot.owl` + `imports/seeds/iao_seed.txt` | `robot extract --method BOT` against pinned upstream IAO release |
| CCO | v1.7-2024-11-03 (pre-v2.0 namespace migration; semantic-name IRI scheme) | `http://www.ontologyrepository.com/CommonCoreOntologies/` | `03_TECHNICAL_CORE/ontology/imports/cco_bot.owl` + `imports/seeds/cco_seed.txt` | `robot extract --method BOT` against `CommonCoreOntologiesMerged.ttl` from `github.com/CommonCoreOntology/CommonCoreOntologies` at the `v1.7-2024-11-03` release tag. Current upstream latest: v2.1-2026-04-04 (uses the new `https://www.commoncoreontologies.org/` namespace and numeric-ID IRIs; not adopted) |

Provenance commit: `a4f56be` ("experiment: replace full upstream imports with ROBOT BOT slim modules") records the original extraction provenance and rationale.

Detailed import rationale: `docs/ARCO_imports_rationale.md`.

CCO v2.x namespace migration is a deferred decision (deliberate stay-on-v1.7 pin to preserve namespace stability across instance fixtures; would require updating every `cco:` prefix in every ARCO TTL file plus annotation-property migrations). The OPEN_PROBLEMS row that tracked this was reverted; if prioritized, a new row should be added. Migration target would be CCO v2.1-2026-04-04 (current upstream latest, same namespace as v2.0).

ARCO's own `owl:versionIRI` is NOT yet set on `ARCO_core.ttl` or `ARCO_governance_extension.ttl` — tracked as OPEN_PROBLEMS X.8.

---

## Reasoning tooling (CI verification layer)

The two-reasoner verification: ARCO's Python pipeline uses OWL-RL (via owlrl) for classification; CI's ROBOT validation runs HermiT (OWL 2 DL) as an independent cross-check.

| Tool | Pinned version | Where pinned | What it verifies |
|---|---|---|---|
| ROBOT | v1.9.10 | `.github/workflows/robot-validate.yml:45` (`ROBOT_VERSION` env var) | DL profile validation + HermiT consistency + per-fixture HermiT vs OWL-RL agreement |
| HermiT | bundled with ROBOT v1.9.10 | (via ROBOT) | OWL 2 DL reasoner; independent classification check |
| owlrl (Python) | 7.1.4 | `requirements.txt:3` | OWL-RL profile reasoner used by the production pipeline |
| pyshacl | 0.31.0 | `requirements.txt:2` | SHACL validation (Layer 2 documentary-completeness checks) |
| rdflib | 7.6.0 | `requirements.txt:1` | RDF graph parsing, manipulation, SPARQL execution |

---

## CI runtime tooling

Pinned in `.github/workflows/*.yml`. CI build environment.

| Tool | Pinned version | Where pinned |
|---|---|---|
| Java | 17 (Temurin distribution) | `.github/workflows/robot-validate.yml:65` and `:215` (via `actions/setup-java@v4` `java-version: '17'`) |
| Python (validate workflow) | 3.11 | `.github/workflows/robot-validate.yml:235` |
| Python (demo workflow) | 3.10 | `.github/workflows/arco-demo.yml:28` |
| Python (smoke workflow) | 3.10 | `.github/workflows/arco-smoke-test.yml:21` |
| OS runner | ubuntu-latest | All three workflows |

Note: ARCO's two demo / smoke workflows pin Python 3.10; the validate workflow pins 3.11. Inconsistency not currently load-bearing (the pipeline is stable on both) but worth aligning in a future cleanup.

---

## Node.js (CI runtime for GitHub Actions) — URGENT, Node 20 EOL approaching

This is the most time-bound versioning work in the stack. Every GitHub Action used in ARCO's CI is a JavaScript action that runs on a Node.js runtime supplied by the GitHub Actions runner. ARCO's currently-pinned action versions all run on Node.js 20, which is being deprecated.

**Timeline (per GitHub's 2025-09-19 deprecation announcement):**
- **2026-06-02:** Node 20 actions force-bumped to Node 24 by default. ARCO's actions may behave unpredictably until verified on Node 24.
- **2026-09-16:** Node 20 removed from the runner. Any action still on a Node 20 version stops working.

ARCO must complete the action bump before 2026-09-16 (and ideally before 2026-06-02 to avoid the force-bump surprise) or CI breaks completely. Every push to main currently surfaces deprecation warnings on every workflow run.

| Action | Current ARCO pin | Runs on | Where pinned | Bump target |
|---|---|---|---|---|
| actions/checkout | @v4 | Node 20 | all three workflows | @v5 (Node 24-supporting; verify in upstream release notes) |
| actions/setup-python | @v5 | Node 20 | all three workflows | @v6 (Node 24-supporting; verify) |
| actions/setup-java | @v4 | Node 20 | `robot-validate.yml:62`, `:213` | @v5 (Node 24-supporting; verify) |
| actions/cache | @v4 | Node 20 | `robot-validate.yml:69`, `:219` | @v5 (Node 24-supporting; verify) |
| actions/upload-artifact | @v4 | Node 20 | `arco-demo.yml:115`, `robot-validate.yml:137`, `:177` | @v5 (Node 24-supporting; verify) |
| actions/upload-pages-artifact | @v3 | Node 20 | `arco-demo.yml:123` | Verify current latest supports Node 24 |
| actions/deploy-pages | @v4 | Node 20 | `arco-demo.yml:137` | Verify current latest supports Node 24 |

**The Node.js version IS load-bearing for ARCO's CI** — it's the runtime that executes every action that checks out the code, installs Java, installs Python, caches dependencies, uploads artifacts, and deploys to GitHub Pages. The Python pipeline runs INSIDE a container set up by these Node-based actions; if the actions stop working, the pipeline doesn't run.

**Verification discipline for the bump PR (each action verified individually):**
1. Read the upstream action's GitHub release notes to confirm the target version supports Node 24
2. Pin the target version in the workflow file
3. Push to a branch (current `ci/node-24-bump-2026-05-11` is the place)
4. Confirm CI passes with the new pin
5. Confirm the deprecation warning is gone for that specific action

**Interim opt-in option (per GitHub's deprecation post):** setting `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true` env var on the runner forces all Node 20 actions to run on Node 24 NOW, without changing action versions. Useful as a smoke test to confirm ARCO's actions work on Node 24 before pinning the new majors. NOT a durable fix; the action bump is still required before Node 20 is removed.

---

## Node.js (KGC presentation deck — separate concern)

The KGC 2026 presentation deck at `KB/talks/kgc-2026-thesis/deck/` uses Node.js + Slidev/Vite for local presentation tooling. The deck has no CI of its own, doesn't run on the ARCO pipeline's runtime, and is not part of the determinism contract.

| Tool | Pinned version | Where pinned |
|---|---|---|
| Node.js (local) | unpinned (uses system Node) | n/a; deck assumes recent Node |
| Slidev / Vite | per `package.json` | `KB/talks/kgc-2026-thesis/deck/package.json` |

Versioning concerns for the deck (e.g., npm dep upgrades) travel separately from the CI Node 24 issue above.

---

## Certificate output versioning (representation layer)

The certificate is a four-layer artifact; each layer has its own version. Detailed governance: `docs/certificate/versioning.md`.

| Layer | Field name | Current version | Where pinned | Advance on |
|---|---|---|---|---|
| Determination packet schema | `packet_schema_version` (`determination_packet.json`) | 1.4 | `run_pipeline.py:2504` `schema_version` constant (future location: `pipeline_output_v2.py` per `output_manifest_v2.yaml:31`); emitted into `determination_packet.json` | Field added/removed/renamed; enum values changed. Last bumped by PR #68: added `asserted_dispositions_outside_regulated_union` + `asserted_prescribed_processes_outside_regulated_union` so the packet mirrors the same fields already in evidence.json and certificate.txt EVIDENCE PATH on negative runs |
| Summary schema | `schema_version` (`summary.json`) | 1.4 | `run_pipeline.py` summary emission block | Field added/removed/renamed; enum values changed. Last bumped by PR #68 Wave 2: added `regulatory_alignment` field; applied ternary `_status_label` enums to `entailment` (`PRESENT` / `NOT_PRESENT` / `NOT_RUN`), `latent_risk` (`DETECTED` / `NOT_DETECTED` / `NOT_RUN`), and `obligation` / `regulatory_alignment` (`PASS` / `FAIL` / `NOT_APPLICABLE` / `NOT_RUN`) |
| Evidence schema | `schema_version` (`evidence.json`) | 1.4 | `run_pipeline.py` evidence emission block | Bare-list -> object restructure (PR #68 Wave 2): `regulated_capability_bindings` + `asserted_dispositions_outside_regulated_union` + `asserted_prescribed_processes_outside_regulated_union` |
| Certificate template | `certificate_template_version` | (per renderer) | Renderer code; emitted into certificate footer | Visually/semantically meaningful layout change |
| Language spec | `language_spec_version` | (per spec) | `docs/certificate/language/certificate_language_spec.md` frontmatter | Template string change, "Avoid" rule change, OWA framing change |
| Per-category profile | `profile_version` | (per profile) | `docs/certificate/category-profiles/annex_iii_*.md` YAML frontmatter | Axiom claim change, plain-language template change, source citation change |

All four use semver (MAJOR.MINOR.PATCH).

The four-line version block in the certificate footer is what an auditor needs to reproduce a certificate.

---

## What's not pinned but should be

These are gaps tracked as OPEN_PROBLEMS rows:

- **ARCO's own `owl:versionIRI`** — not set on `ARCO_core.ttl` or `ARCO_governance_extension.ttl`. Manifest field `ontology_version_iri` cannot emit usefully today. Tracked as OPEN_PROBLEMS X.8.
- **Pipeline code version** (git commit / tag) emitted in certificate footer — not yet wired. Cross-references certificate `docs/certificate/versioning.md` "Out of scope here" section.
- **Python 3.10 vs 3.11 alignment** between workflows — minor inconsistency; not blocking but worth aligning.

---

## Verification commands

Each verification command below should pass at the pinned version and fail (or warn) if drift occurs.

```bash
# ROBOT version pinned
grep "ROBOT_VERSION: v1.9.10" .github/workflows/robot-validate.yml

# Python deps pinned to exact versions (no >=, no ~)
grep -E "==" requirements.txt
grep -vE "==|^$|^#" requirements.txt  # should return nothing

# Ontology slim modules present at expected paths
ls 03_TECHNICAL_CORE/ontology/imports/bfo-2020.owl
ls 03_TECHNICAL_CORE/ontology/imports/iao_bot.owl
ls 03_TECHNICAL_CORE/ontology/imports/ro_bot.owl
ls 03_TECHNICAL_CORE/ontology/imports/cco_bot.owl

# Pipeline runs green
python 03_TECHNICAL_CORE/scripts/run_pipeline.py | grep "ALL CHECKS PASSED"
```

---

## Maintenance

When a pin changes:
1. Update the relevant source file (CI workflow, requirements.txt, ontology imports, etc.)
2. Update this doc's matching row
3. Bump "Last reviewed" date
4. Note the bump in the PR description and in any relevant `LIMITATIONS.md` disclosure (e.g., for slim-module regen)
5. Confirm CI passes with the new pin before merge

If a pin is added (a new dependency, a new tool), add a new row with the same shape as the existing rows. No row gets removed without a deprecation pass — older rows can be marked "DEPRECATED, see X" but should not silently disappear.
