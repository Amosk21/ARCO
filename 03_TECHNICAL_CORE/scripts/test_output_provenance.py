"""
test_output_provenance.py — ARCO output provenance contract test.

Reads `output_manifest_v2.yaml` and verifies that the commitment-shaped values
the pipeline emits actually trace to their declared provenance sources, by
running the pipeline and re-deriving the values independently.

Run from repo root:
    python 03_TECHNICAL_CORE/scripts/test_output_provenance.py

What each check ACTUALLY does:

1.  **Forbidden source patterns** (static lint, <1s) — the manifest declares
    forbidden Python source shapes (Sentinel-default fallbacks, hardcoded
    determination IRIs, scope-qualifier f-strings, hidden AND aggregators,
    LIMIT 1 without ORDER BY). The check greps `run_pipeline.py` source for
    them. Failure = the emitter source contains a forbidden pattern.

2.  **End-to-end field provenance** (~10s per pipeline run) — for every
    certificate-grade (fixture, system) pair (imported from
    `hermit_cross_check.py` CERTIFICATE_GRADE_SCENARIOS, the single anchor
    list), the check:
      a. runs `run_pipeline.py --instances <ttl> --system <name>` as a
         subprocess and snapshots the seven emitted files out of `runs/demo/`
         into a temp dir;
      b. parses the emitted `reasoned_graph.ttl` into rdflib;
      c. for each `graph_backed` field in the manifest, executes the field's
         DECLARED `source_query` against that emitted reasoned graph (binding
         `?system` exactly as the pipeline does, via initBindings) and
         compares the query-derived value against the value actually emitted
         in `summary.json` / `determination_packet.json` / `certificate.txt`
         per the manifest's value_path / rendering declarations.
    Mismatch = failure naming the field, fixture, expected-from-graph value,
    and found-in-output value. Fields whose declared source is not a SPARQL
    query (or whose value never reaches the emitted artifacts) are SKIPPED
    with an explicit printed reason — the skip list is part of the output,
    never silent. run_metadata and documentary manifest blocks are not
    value-verified here (they are not reasoner claims); Check 1's lint and
    Check 4 cover their forbidden patterns.

3.  **Cross-fixture leak sweep** (uses Check 2's snapshots; no extra pipeline
    runs) — derives, from the fixture TTLs themselves, the set of
    ARCO-namespace local names exclusive to each fixture (present in that
    fixture, absent from every other fixture and from the core/governance
    ontology), then sweeps every fixture's emitted outputs for tokens
    belonging exclusively to OTHER fixtures. The six emitter-composed files
    are raw-text swept; `reasoned_graph.ttl` is swept at the RDF-term level
    (foreign ARCO-namespace IRIs as graph nodes), because fixture-header
    documentation literals may legitimately mention other fixtures by name
    and are loader-carried source content, not emitter output.

4.  **Manifest internal consistency** (<1s) — every aggregate's constituent
    field_ref must name a field declared somewhere in the manifest.

Self-test (negative controls, runs as part of main() by default; disable with
--no-self-test for debugging only):
    (a) tampers one graph_backed value in a COPY of an emitted summary.json
        and asserts Check 2 catches it;
    (b) injects another fixture's exclusive token into a COPY of an emitted
        certificate.txt and asserts Check 3 catches it.
    A green run therefore carries proof that the checks CAN go red.

Runtime: ~10s per pipeline run locally (7 runs: 6 fixtures, flag-tests twice)
plus ~1s verification per run — about 1.5-3 minutes total on a dev machine;
expect 2-3x that on a CI runner. The full certificate-grade set is the
default and the mode CI runs.

Side effect and cleanup: the pipeline writes to the shared `runs/demo/`
directory. Fixtures are run with Sentinel LAST, so on completion `runs/demo/`
is left in the default-Sentinel state (identical to a bare
`python run_pipeline.py` run, modulo the run_id timestamp).
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

try:
    import yaml
except ImportError:
    print("FAIL: PyYAML required. pip install pyyaml", file=sys.stderr)
    sys.exit(2)

from rdflib import Graph, URIRef

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / "03_TECHNICAL_CORE" / "scripts"
ONTOLOGY = REPO_ROOT / "03_TECHNICAL_CORE" / "ontology"
REASONING = REPO_ROOT / "03_TECHNICAL_CORE" / "reasoning"

MANIFEST_PATH = SCRIPTS / "output_manifest_v2.yaml"
PIPELINE_PATH = SCRIPTS / "run_pipeline.py"
OUTPUT_DIR = REPO_ROOT / "runs" / "demo"

ARCO_NS = "https://arco.ai/ontology/core#"

# Single anchor list for certificate-grade (fixture, systems) pairs — imported,
# never copied (the drift a second table here would create is the same disease
# this test exists to catch).
sys.path.insert(0, str(SCRIPTS))
from hermit_cross_check import CERTIFICATE_GRADE_SCENARIOS  # noqa: E402

# The seven files run_pipeline.py emits on every run. Snapshotting only this
# set keeps stale strays in runs/demo out of the leak sweep.
EMITTED_FILES = (
    "summary.json",
    "determination_packet.json",
    "certificate.txt",
    "evidence.json",
    "determination_view.html",
    "shacl_report.txt",
    "reasoned_graph.ttl",
)

# Ontology stack loaded by the pipeline (used to reconstruct the asserted
# pre-reasoning triple count for the entailed_triples_added field).
ONTOLOGY_STACK = (
    ONTOLOGY / "imports" / "bfo-2020.owl",
    ONTOLOGY / "imports" / "iao_bot.owl",
    ONTOLOGY / "imports" / "ro_bot.owl",
    ONTOLOGY / "imports" / "cco_bot.owl",
    ONTOLOGY / "ARCO_core.ttl",
    ONTOLOGY / "ARCO_governance_extension.ttl",
)

# Context ASKs needed only to mirror the emitter's NOT_APPLICABLE label logic
# for obligation_check / regulatory_alignment_check (run_pipeline.py
# non_applicable_run). These are the pipeline's own audit queries.
ANNEX_1A_QUERY = REASONING / "check_annex_iii_1a_entailment.sparql"
ANNEX_5B_QUERY = REASONING / "check_annex_iii_5b_entailment.sparql"


# =====================================================================
# Reporters
# =====================================================================

class Failure:
    def __init__(self, check: str, fixture: str, detail: str):
        self.check = check
        self.fixture = fixture
        self.detail = detail

    def __str__(self) -> str:
        return f"  [{self.check}] {self.fixture}: {self.detail}"


def hr(title: str) -> None:
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


# =====================================================================
# Manifest loading
# =====================================================================

def load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        print(f"FATAL: manifest not found at {MANIFEST_PATH}", file=sys.stderr)
        sys.exit(2)
    with MANIFEST_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# =====================================================================
# Check 1 — forbidden source patterns
# =====================================================================

def check_forbidden_source_patterns(manifest: dict) -> list[Failure]:
    """Grep the pipeline source for patterns the manifest forbids."""
    failures: list[Failure] = []
    forbidden = manifest.get("forbidden_source_patterns", [])
    if not PIPELINE_PATH.exists():
        return [Failure("source-pattern", "all", f"pipeline source not found: {PIPELINE_PATH}")]
    source = PIPELINE_PATH.read_text(encoding="utf-8")
    for entry in forbidden:
        pattern = entry.get("pattern")
        why = entry.get("why", "")
        if not pattern:
            continue
        try:
            if re.search(pattern, source, re.MULTILINE):
                failures.append(Failure(
                    "source-pattern",
                    "run_pipeline.py",
                    f"forbidden pattern matches: /{pattern}/  ({why})",
                ))
        except re.error as e:
            failures.append(Failure(
                "source-pattern",
                "run_pipeline.py",
                f"manifest pattern is invalid regex: /{pattern}/  ({e})",
            ))
    return failures


# =====================================================================
# Check 2 — end-to-end field provenance
# =====================================================================

class Snapshot:
    """One pipeline run's emitted artifacts plus the parsed reasoned graph."""

    def __init__(self, fixture: str, system: str, snap_dir: Path,
                 reasoned: Graph, asserted_count: int):
        self.fixture = fixture
        self.system = system
        self.dir = snap_dir
        self.reasoned = reasoned
        self.asserted_count = asserted_count
        self.summary = json.loads((snap_dir / "summary.json").read_text(encoding="utf-8"))
        self.packet = json.loads((snap_dir / "determination_packet.json").read_text(encoding="utf-8"))
        self.cert_text = (snap_dir / "certificate.txt").read_text(encoding="utf-8")
        self.shacl_report = (snap_dir / "shacl_report.txt").read_text(encoding="utf-8")

    @property
    def tag(self) -> str:
        return f"{self.fixture}::{self.system}"

    def system_iri(self) -> URIRef:
        return URIRef(f"{ARCO_NS}{self.system}")


def _short(iri: str) -> str:
    """Mirror run_pipeline._short: IRI -> local name for display."""
    if not iri:
        return iri
    if "://" not in iri:
        return "Anonymous Entity (Blank Node)"
    return iri.rsplit("#", 1)[-1] if "#" in iri else iri.rsplit("/", 1)[-1]


def _exec_ask(g: Graph, query_path: Path, system_iri: URIRef) -> bool:
    """Mirror run_pipeline.run_sparql_ask_for_system (initBindings on ?system)."""
    q = query_path.read_text(encoding="utf-8").strip()
    result = g.query(q, initBindings={"system": system_iri})
    if getattr(result, "askAnswer", None) is not None:
        return bool(result.askAnswer)
    rows = list(result)
    return bool(rows[0]) if rows else False


def _exec_select(g: Graph, query_path: Path, system_iri: URIRef) -> list[dict]:
    """Mirror run_pipeline.run_sparql_select_for_system (rows as str dicts)."""
    q = query_path.read_text(encoding="utf-8").strip()
    result = g.query(q, initBindings={"system": system_iri})
    rows: list[dict] = []
    for r in result:
        row: dict = {}
        for var in result.vars:
            val = r[var]
            row[str(var)] = str(val) if val is not None else None
        rows.append(row)
    return rows


def _cert_value(cert_text: str, label: str) -> str | None:
    """Return the value after `label` on the certificate line carrying it."""
    for line in cert_text.splitlines():
        s = line.strip()
        if s.startswith(label):
            return s[len(label):].strip()
    return None


def _declared_query(field_decl: dict) -> Path | None:
    sq = field_decl.get("source_query", "")
    if not sq:
        return None
    return REPO_ROOT / "03_TECHNICAL_CORE" / sq


def _compare(failures: list[Failure], field: str, snap: Snapshot,
             location: str, expected, found) -> int:
    """Record one expected-vs-found comparison; returns 1 (comparison count)."""
    if expected != found:
        failures.append(Failure(
            "field-provenance", snap.tag,
            f"field '{field}' at {location}: expected-from-graph={expected!r} "
            f"found-in-output={found!r}",
        ))
    return 1


def _packet_gate(packet: dict, gate_id: str) -> dict:
    for gate in packet.get("gates", []):
        if gate.get("id") == gate_id:
            return gate.get("evidence", {})
    return {}


def verify_fields(manifest: dict, snap: Snapshot) -> tuple[list[Failure], list[str], dict]:
    """Execute every graph_backed field's declared source_query against the
    snapshot's emitted reasoned graph and compare with the emitted values.

    Returns (failures, skip_lines, comparisons_per_field).
    """
    failures: list[Failure] = []
    skips: list[str] = []
    ncomp: dict = {}
    sysiri = snap.system_iri()
    g = snap.reasoned

    def ask_declared(decl: dict) -> bool | None:
        qpath = _declared_query(decl)
        if qpath is None or not qpath.exists():
            failures.append(Failure(
                "field-provenance", snap.tag,
                f"field '{decl.get('field')}' declares source_query "
                f"'{decl.get('source_query')}' but the file does not exist",
            ))
            return None
        return _exec_ask(g, qpath, sysiri)

    def select_declared(decl: dict) -> list[dict] | None:
        qpath = _declared_query(decl)
        if qpath is None or not qpath.exists():
            failures.append(Failure(
                "field-provenance", snap.tag,
                f"field '{decl.get('field')}' declares source_query "
                f"'{decl.get('source_query')}' but the file does not exist",
            ))
            return None
        return _exec_select(g, qpath, sysiri)

    # Emitter label context needed only for the NOT_APPLICABLE ternary labels
    # (mirrors run_pipeline.py non_applicable_run). The two annex ASKs are
    # re-executed on the emitted graph; shacl_ok is taken from the emitted
    # summary because pyshacl is not a SPARQL query (see shacl_conforms skip).
    annex_1a = _exec_ask(g, ANNEX_1A_QUERY, sysiri)
    annex_5b = _exec_ask(g, ANNEX_5B_QUERY, sysiri)
    non_applicable = (snap.summary.get("shacl") == "PASS") and not annex_1a and not annex_5b

    for decl in manifest.get("graph_backed", []) or []:
        field = decl.get("field")
        n = 0

        if field == "primary_classification":
            rows = select_declared(decl)
            if rows is None:
                continue
            locals_ = [_short(r["cls"]) for r in rows if r.get("cls")]
            rendered = (", ".join(locals_) if locals_ else
                        "No ARCO classification within currently modeled categories: Annex III 1(a) and 5(b).")
            n += _compare(failures, field, snap, "summary.json:primary_arco_classes",
                          locals_, snap.summary.get("primary_arco_classes"))
            n += _compare(failures, field, snap, "determination_packet.json:primary_arco_classes",
                          locals_, snap.packet.get("primary_arco_classes"))
            n += _compare(failures, field, snap, "summary.json:classification",
                          rendered, snap.summary.get("classification"))
            n += _compare(failures, field, snap, "determination_packet.json:primary_arco_classification",
                          rendered, snap.packet.get("primary_arco_classification"))
            n += _compare(failures, field, snap, "certificate.txt:PRIMARY ARCO CLASSIFICATION",
                          rendered, _cert_value(snap.cert_text, "PRIMARY ARCO CLASSIFICATION:"))

        elif field == "latent_risk_flag":
            present = ask_declared(decl)
            if present is None:
                continue
            summary_form = f"HighRiskSystem ({'PRESENT' if present else 'NOT PRESENT'})"
            n += _compare(failures, field, snap, "summary.json:latent_risk_flag",
                          summary_form, snap.summary.get("latent_risk_flag"))
            n += _compare(failures, field, snap, "determination_packet.json:latent_risk_flag",
                          "PRESENT" if present else "NOT_PRESENT",
                          snap.packet.get("latent_risk_flag"))
            n += _compare(failures, field, snap, "certificate.txt:LATENT-RISK FLAG",
                          summary_form, _cert_value(snap.cert_text, "LATENT-RISK FLAG:"))

        elif field == "gate_1_capability":
            rows = select_declared(decl)
            if rows is None:
                continue
            ev = _packet_gate(snap.packet, "gate_1")
            if rows:
                cap_uri = rows[0].get("cap_class") or ""
                exp = {
                    "cap_type_uri": cap_uri,
                    "cap_type_label": rows[0].get("cap_label") or _short(cap_uri),
                    "component_uri": rows[0].get("component") or "",
                    "disposition_uri": rows[0].get("disposition") or "",
                }
            else:
                exp = {"cap_type_uri": "", "cap_type_label": "",
                       "component_uri": "", "disposition_uri": ""}
            for key, val in exp.items():
                n += _compare(failures, field, snap,
                              f"determination_packet.json:gates[gate_1].evidence.{key}",
                              val, ev.get(key))

        elif field == "gate_2_prescribed_process":
            rows = select_declared(decl)
            if rows is None:
                continue
            ev = _packet_gate(snap.packet, "gate_2")
            if rows:
                ptype = rows[0].get("process_class") or ""
                exp = {
                    "ius_uri": rows[0].get("ius") or "",
                    "process_uri": rows[0].get("process") or "",
                    "process_type_uri": ptype,
                    "process_type_label": rows[0].get("process_label") or _short(ptype),
                }
            else:
                exp = {"ius_uri": "", "process_uri": "",
                       "process_type_uri": "", "process_type_label": ""}
            for key, val in exp.items():
                n += _compare(failures, field, snap,
                              f"determination_packet.json:gates[gate_2].evidence.{key}",
                              val, ev.get(key))

        elif field == "gate_3_designated_role":
            rows = select_declared(decl)
            if rows is None:
                continue
            ev = _packet_gate(snap.packet, "gate_3")
            if rows:
                role = rows[0].get("role_iri") or ""
                exp = {
                    "uss_uri": rows[0].get("uss") or "",
                    "role_uri": role,
                    "role_label": rows[0].get("role_label") or _short(role),
                }
            else:
                exp = {"uss_uri": "", "role_uri": "", "role_label": ""}
            for key, val in exp.items():
                n += _compare(failures, field, snap,
                              f"determination_packet.json:gates[gate_3].evidence.{key}",
                              val, ev.get(key))

        elif field == "determination_node":
            rows = select_declared(decl)
            if rows is None:
                continue
            expected = rows[0].get("det") if rows else None
            n += _compare(failures, field, snap, "summary.json:determination_node_uri",
                          expected, snap.summary.get("determination_node_uri"))
            n += _compare(failures, field, snap, "determination_packet.json:determination_node_uri",
                          expected, snap.packet.get("determination_node_uri"))

        elif field == "traceability_check":
            ok = ask_declared(decl)
            if ok is None:
                continue
            n += _compare(failures, field, snap, "summary.json:traceability",
                          "PASS" if ok else "FAIL", snap.summary.get("traceability"))

        elif field == "latent_risk_check":
            ok = ask_declared(decl)
            if ok is None:
                continue
            n += _compare(failures, field, snap, "summary.json:latent_risk",
                          "DETECTED" if ok else "NOT_DETECTED", snap.summary.get("latent_risk"))

        elif field == "intended_use_check":
            ok = ask_declared(decl)
            if ok is None:
                continue
            n += _compare(failures, field, snap, "summary.json:intended_use",
                          "PASS" if ok else "FAIL", snap.summary.get("intended_use"))

        elif field == "obligation_check":
            ok = ask_declared(decl)
            if ok is None:
                continue
            expected = "PASS" if ok else ("NOT_APPLICABLE" if non_applicable else "FAIL")
            n += _compare(failures, field, snap, "summary.json:obligation",
                          expected, snap.summary.get("obligation"))

        elif field == "regulatory_alignment_check":
            ok = ask_declared(decl)
            if ok is None:
                continue
            expected = "PASS" if ok else ("NOT_APPLICABLE" if non_applicable else "FAIL")
            n += _compare(failures, field, snap, "summary.json:regulatory_alignment",
                          expected, snap.summary.get("regulatory_alignment"))

        elif field == "derogation_flag":
            ok = ask_declared(decl)
            if ok is None:
                continue
            n += _compare(failures, field, snap, "summary.json:flag_derogation_candidate",
                          ok, snap.summary.get("flag_derogation_candidate"))
            n += _compare(failures, field, snap, "determination_packet.json:flag_derogation_candidate",
                          ok, snap.packet.get("flag_derogation_candidate"))

        elif field == "fraud_exclusion_flag":
            ok = ask_declared(decl)
            if ok is None:
                continue
            n += _compare(failures, field, snap, "summary.json:flag_fraud_exclusion_candidate",
                          ok, snap.summary.get("flag_fraud_exclusion_candidate"))
            n += _compare(failures, field, snap, "determination_packet.json:flag_fraud_exclusion_candidate",
                          ok, snap.packet.get("flag_fraud_exclusion_candidate"))

        elif field == "entailed_triples_added":
            # Not a SPARQL query; manifest declares post_minus_pre_triple_count.
            # Reconstructed mechanically: len(emitted reasoned graph) minus
            # len(ontology stack + fixture parsed fresh). Exact on all fixtures.
            expected = len(snap.reasoned) - snap.asserted_count
            n += _compare(failures, field, snap, "summary.json:entailed_triples_added",
                          expected, snap.summary.get("entailed_triples_added"))
            n += _compare(failures, field, snap, "determination_packet.json:inferred_triples_added",
                          expected, snap.packet.get("inferred_triples_added"))
            n += _compare(failures, field, snap, "certificate.txt:ENTAILED TRIPLES ADDED",
                          f"+{expected}", _cert_value(snap.cert_text, "ENTAILED TRIPLES ADDED:"))

        elif field == "shacl_conforms":
            # Declared source is pyshacl_validate_result — not a SPARQL query;
            # re-deriving it means re-running the validation stage, not
            # checking emission. Cross-artifact consistency IS asserted:
            # summary.json:shacl must agree with shacl_report.txt:conforms.
            skips.append(
                "shacl_conforms — source is pyshacl_validate_result (not a SPARQL "
                "query); cross-artifact consistency summary.json:shacl vs "
                "shacl_report.txt:conforms asserted instead"
            )
            report_conforms = snap.shacl_report.splitlines()[0].strip() if snap.shacl_report else ""
            expected = "PASS" if report_conforms == "conforms: True" else "FAIL"
            _compare(failures, field, snap,
                     "summary.json:shacl (vs shacl_report.txt:conforms)",
                     expected, snap.summary.get("shacl"))
            continue

        elif field == "union_subclass_sync_check":
            skips.append(
                "union_subclass_sync_check — pipeline evaluates it against the "
                "pre-reasoning ASSERTED graph (L3.11), and the result is "
                "operator-stdout only; it is not emitted in summary.json / "
                "determination_packet.json, so there is no emitted value to verify"
            )
            continue

        else:
            skips.append(
                f"{field} — no verifier implemented for this manifest field; "
                "add one to verify_fields() before relying on it"
            )
            continue

        ncomp[field] = ncomp.get(field, 0) + n

    return failures, skips, ncomp


def run_pipeline_snapshot(fixture: str, system: str, snap_dir: Path,
                          base_graph: Graph) -> tuple[Snapshot | None, list[Failure], float]:
    """Run the pipeline for one (fixture, system) pair and snapshot runs/demo."""
    failures: list[Failure] = []
    fixture_path = ONTOLOGY / fixture
    if not fixture_path.exists():
        return None, [Failure("pipeline-run", f"{fixture}::{system}",
                              f"fixture not found: {fixture_path}")], 0.0
    t0 = time.monotonic()
    proc = subprocess.run(
        [sys.executable, str(PIPELINE_PATH),
         "--instances", str(fixture_path), "--system", system],
        cwd=str(REPO_ROOT), capture_output=True, text=True, errors="replace",
    )
    elapsed = time.monotonic() - t0
    if proc.returncode != 0:
        tail = "\n".join((proc.stdout or "").splitlines()[-15:])
        return None, [Failure("pipeline-run", f"{fixture}::{system}",
                              f"run_pipeline.py exited {proc.returncode}; stdout tail:\n{tail}")], elapsed

    snap_dir.mkdir(parents=True, exist_ok=True)
    for name in EMITTED_FILES:
        src = OUTPUT_DIR / name
        if not src.exists():
            failures.append(Failure("pipeline-run", f"{fixture}::{system}",
                                    f"expected emitted file missing after run: runs/demo/{name}"))
            continue
        shutil.copy2(src, snap_dir / name)
    # Keep operator stdout for diagnostics (NOT part of the leak sweep —
    # the sweep covers emitted artifacts, not console output).
    (snap_dir / "pipeline_stdout.txt").write_text(proc.stdout or "", encoding="utf-8")
    if failures:
        return None, failures, elapsed

    reasoned = Graph()
    reasoned.parse((snap_dir / "reasoned_graph.ttl").as_posix(), format="turtle")

    # Asserted pre-reasoning count: ontology stack (pre-parsed once) + fixture.
    asserted = Graph()
    for t in base_graph:
        asserted.add(t)
    asserted.parse(fixture_path.as_posix(), format="turtle")

    snap = Snapshot(fixture, system, snap_dir, reasoned, len(asserted))
    return snap, failures, elapsed


# =====================================================================
# Check 3 — cross-fixture leak sweep
# =====================================================================

def arco_local_names(ttl_path: Path) -> set[str]:
    """All ARCO-namespace local names appearing as terms in a turtle file."""
    g = Graph()
    g.parse(ttl_path.as_posix(), format="turtle")
    names: set[str] = set()
    for s, p, o in g:
        for term in (s, p, o):
            if isinstance(term, URIRef) and str(term).startswith(ARCO_NS):
                local = str(term).split("#", 1)[-1]
                if local:
                    names.add(local)
    return names


def derive_exclusive_tokens(fixtures: list[str]) -> dict[str, set[str]]:
    """Per fixture: ARCO local names present in that fixture's TTL, absent
    from every other fixture's TTL and from the core/governance ontology."""
    ontology_locals: set[str] = set()
    for p in (ONTOLOGY / "ARCO_core.ttl", ONTOLOGY / "ARCO_governance_extension.ttl"):
        ontology_locals |= arco_local_names(p)
    per_fixture = {f: arco_local_names(ONTOLOGY / f) for f in fixtures}
    exclusive: dict[str, set[str]] = {}
    for f in fixtures:
        others: set[str] = set()
        for g_name, toks in per_fixture.items():
            if g_name != f:
                others |= toks
        exclusive[f] = per_fixture[f] - ontology_locals - others
    return exclusive


def sweep_snapshot_for_leaks(snap_dir: Path, own_fixture: str, tag: str,
                             exclusive: dict[str, set[str]],
                             reasoned: Graph | None) -> list[Failure]:
    """Sweep one snapshot's emitted outputs for tokens exclusive to OTHER
    fixtures.

    The six emitter-composed files are raw-text swept (word-boundary match on
    the full local name). `reasoned_graph.ttl` is swept at the RDF-TERM level
    instead (foreign ARCO-namespace IRIs appearing as graph nodes): the
    reasoned graph is serialized straight from loader+closure before any
    emission code runs, so the only way a foreign fixture's token can appear
    there as TEXT without being a real leak is inside a documentation literal
    the fixture's own source file carries (e.g. the creditscoring header's
    OWA cross-reference to Sentinel_ID_System). A foreign IRI as a graph
    term, by contrast, is always a leak.
    """
    failures: list[Failure] = []
    texts = {
        name: (snap_dir / name).read_text(encoding="utf-8", errors="replace")
        for name in EMITTED_FILES
        if name != "reasoned_graph.ttl" and (snap_dir / name).exists()
    }
    graph_locals: set[str] = set()
    if reasoned is not None:
        for s, p, o in reasoned:
            for term in (s, p, o):
                if isinstance(term, URIRef) and str(term).startswith(ARCO_NS):
                    graph_locals.add(str(term).split("#", 1)[-1])
    for other_fixture, tokens in exclusive.items():
        if other_fixture == own_fixture or not tokens:
            continue
        pattern = re.compile(
            r"(?<![A-Za-z0-9_])(?:" +
            "|".join(re.escape(t) for t in sorted(tokens)) +
            r")(?![A-Za-z0-9_])"
        )
        for name, text in texts.items():
            m = pattern.search(text)
            if m:
                failures.append(Failure(
                    "cross-fixture-leak", tag,
                    f"token '{m.group(0)}' (exclusive to {other_fixture}) "
                    f"found in emitted {name}",
                ))
        for leaked in sorted(graph_locals & tokens):
            failures.append(Failure(
                "cross-fixture-leak", tag,
                f"IRI local name '{leaked}' (exclusive to {other_fixture}) "
                f"present as a graph term in emitted reasoned_graph.ttl",
            ))
    return failures


# =====================================================================
# Check 4 — manifest internal consistency
# =====================================================================

def check_manifest_consistency(manifest: dict) -> list[Failure]:
    """Manifest itself must be valid: every aggregator's constituents must
    name fields that exist in the manifest."""
    failures: list[Failure] = []
    all_fields: set[str] = set()
    for block in ("run_metadata", "graph_backed", "documentary", "aggregates"):
        for entry in manifest.get(block, []) or []:
            f = entry.get("field")
            if f:
                all_fields.add(f)
    for entry in manifest.get("aggregates", []) or []:
        for c in entry.get("constituents", []) or []:
            ref = c.get("field_ref")
            if ref and ref not in all_fields:
                failures.append(Failure(
                    "manifest-consistency",
                    "n/a",
                    f"aggregate '{entry.get('field')}' references constituent '{ref}' which is not declared in any block",
                ))
    return failures


# =====================================================================
# Self-test — negative controls (tamper detection)
# =====================================================================

def run_self_test(manifest: dict, snapshots: list[Snapshot],
                  exclusive: dict[str, set[str]], workdir: Path) -> list[Failure]:
    """Prove the checks can go red: tamper COPIES of emitted outputs and
    assert the verifiers catch the tampering. Uses already-snapshotted
    outputs; no extra pipeline runs."""
    failures: list[Failure] = []
    if not snapshots:
        return [Failure("self-test", "n/a", "no snapshots available to tamper")]
    base = snapshots[0]

    # (a) Tamper one graph_backed value in a COPY of summary.json.
    tamper_dir = workdir / "selftest_tamper"
    shutil.copytree(base.dir, tamper_dir)
    summary_path = tamper_dir / "summary.json"
    tampered = json.loads(summary_path.read_text(encoding="utf-8"))
    tampered["traceability"] = "FAIL" if tampered.get("traceability") == "PASS" else "PASS"
    summary_path.write_text(json.dumps(tampered, indent=2) + "\n", encoding="utf-8")
    tampered_snap = Snapshot(base.fixture, base.system, tamper_dir,
                             base.reasoned, base.asserted_count)
    caught, _, _ = verify_fields(manifest, tampered_snap)
    if not any("traceability_check" in f.detail for f in caught):
        failures.append(Failure(
            "self-test", base.tag,
            "NEGATIVE CONTROL FAILED: tampered summary.json:traceability was "
            "NOT caught by the field-provenance check — Check 2 cannot go red",
        ))

    # (b) Inject another fixture's exclusive token into a COPY of certificate.txt.
    donor = next((f for f, toks in sorted(exclusive.items())
                  if f != base.fixture and toks), None)
    if donor is None:
        failures.append(Failure("self-test", base.tag,
                                "no foreign exclusive token available to inject"))
    else:
        token = sorted(exclusive[donor])[0]
        inject_dir = workdir / "selftest_inject"
        shutil.copytree(base.dir, inject_dir)
        cert_path = inject_dir / "certificate.txt"
        cert_path.write_text(
            cert_path.read_text(encoding="utf-8") + f"\n  {token}\n",
            encoding="utf-8",
        )
        caught = sweep_snapshot_for_leaks(inject_dir, base.fixture,
                                          base.tag + " (tampered copy)",
                                          exclusive, base.reasoned)
        if not any(token in f.detail for f in caught):
            failures.append(Failure(
                "self-test", base.tag,
                f"NEGATIVE CONTROL FAILED: injected foreign token '{token}' in "
                "certificate.txt copy was NOT caught by the leak sweep — "
                "Check 3 cannot go red",
            ))
    return failures


# =====================================================================
# Driver
# =====================================================================

def main() -> int:
    parser = argparse.ArgumentParser(description="ARCO output provenance contract test")
    parser.add_argument(
        "--no-self-test", action="store_true",
        help="Skip the negative-control self-test (debugging only; CI runs it).",
    )
    args = parser.parse_args()

    t_start = time.monotonic()
    manifest = load_manifest()
    all_failures: list[Failure] = []

    hr("ARCO Output Provenance Contract Test")
    print(f"Manifest: {MANIFEST_PATH.relative_to(REPO_ROOT)}")
    print(f"Pipeline: {PIPELINE_PATH.relative_to(REPO_ROOT)}")
    print(f"Manifest version: {manifest.get('manifest_version')}")

    hr("Check 1 — forbidden source patterns (lint over run_pipeline.py)")
    f1 = check_forbidden_source_patterns(manifest)
    for fail in f1:
        print(fail)
    print(f"Check 1: {len(f1)} failures")
    all_failures.extend(f1)

    hr("Check 2 — end-to-end field provenance (pipeline runs + declared-query re-execution)")
    # Run order: Sentinel LAST, so runs/demo is left in default-Sentinel state.
    scenarios: list[tuple[str, str]] = []
    sentinel_runs: list[tuple[str, str]] = []
    for fixture, systems in CERTIFICATE_GRADE_SCENARIOS:
        for system in systems:
            if fixture == "ARCO_instances_sentinel.ttl":
                sentinel_runs.append((fixture, system))
            else:
                scenarios.append((fixture, system))
    scenarios.extend(sentinel_runs)

    print("Pre-parsing ontology stack (for asserted-count reconstruction)...")
    base_graph = Graph()
    for p in ONTOLOGY_STACK:
        base_graph.parse(p.as_posix(), format="xml" if p.suffix == ".owl" else "turtle")

    snapshots: list[Snapshot] = []
    field_totals: dict = {}
    skip_lines: set[str] = set()
    workdir = Path(tempfile.mkdtemp(prefix="arco_provenance_"))
    try:
        for fixture, system in scenarios:
            tag = f"{fixture}::{system}"
            snap_dir = workdir / f"{Path(fixture).stem}__{system}"
            snap, run_failures, elapsed = run_pipeline_snapshot(fixture, system, snap_dir, base_graph)
            all_failures.extend(run_failures)
            if snap is None:
                print(f"  {tag}: PIPELINE RUN FAILED ({elapsed:.1f}s)")
                continue
            f2, skips, ncomp = verify_fields(manifest, snap)
            all_failures.extend(f2)
            skip_lines.update(skips)
            for k, v in ncomp.items():
                field_totals[k] = field_totals.get(k, 0) + v
            snapshots.append(snap)
            total_cmp = sum(ncomp.values())
            print(f"  {tag}: run {elapsed:.1f}s, "
                  f"{len(ncomp)} fields / {total_cmp} value comparisons, "
                  f"{len(f2)} mismatches")
            for fail in f2:
                print(fail)

        verified_fields = sorted(field_totals)
        print(f"\nCheck 2: {len(snapshots)}/{len(scenarios)} pipeline runs verified; "
              f"{len(verified_fields)} graph_backed fields value-verified per run; "
              f"{sum(field_totals.values())} total comparisons")
        if skip_lines:
            print("Skipped fields (explicit, with reason):")
            for line in sorted(skip_lines):
                print(f"  SKIPPED: {line}")
        print("run_metadata / documentary manifest blocks: not value-verified "
              "(not reasoner claims; covered by Check 1 lint + Check 4).")

        hr("Check 3 — cross-fixture leak sweep (tokens derived from fixture TTLs)")
        fixture_names = sorted({f for f, _ in scenarios})
        exclusive = derive_exclusive_tokens(fixture_names)
        n_tokens = sum(len(v) for v in exclusive.values())
        f3: list[Failure] = []
        for snap in snapshots:
            f3.extend(sweep_snapshot_for_leaks(snap.dir, snap.fixture, snap.tag,
                                               exclusive, snap.reasoned))
        for fail in f3:
            print(fail)
        print(f"Check 3: {len(snapshots)} snapshots swept against {n_tokens} "
              f"fixture-exclusive tokens from {len(fixture_names)} fixtures; "
              f"{len(f3)} leaks")
        all_failures.extend(f3)

        hr("Check 4 — manifest internal consistency")
        f4 = check_manifest_consistency(manifest)
        for fail in f4:
            print(fail)
        print(f"Check 4: {len(f4)} failures")
        all_failures.extend(f4)

        hr("Self-test — negative controls (tampered copies must go red)")
        if args.no_self_test:
            self_test_result = "SKIPPED (--no-self-test)"
        elif not snapshots:
            self_test_result = "NOT RUN (no snapshots)"
            all_failures.append(Failure("self-test", "n/a", "no snapshots to tamper"))
        else:
            fst = run_self_test(manifest, snapshots, exclusive, workdir)
            for fail in fst:
                print(fail)
            all_failures.extend(fst)
            self_test_result = "PASS (tampered value caught; injected token caught)" if not fst else "FAIL"
        print(f"Self-test: {self_test_result}")
    finally:
        shutil.rmtree(workdir, ignore_errors=True)

    hr("Summary")
    elapsed_total = time.monotonic() - t_start
    print(f"Pipeline runs executed:    {len(snapshots)}/{len(scenarios)} "
          f"(certificate-grade set from hermit_cross_check.py; Sentinel last, "
          f"so runs/demo is left in default-Sentinel state)")
    print(f"Fields value-verified:     {len(field_totals)} graph_backed fields per run "
          f"({sum(field_totals.values())} comparisons total)")
    print(f"Fields skipped w/ reason:  {len(skip_lines)}")
    print(f"Self-test:                 {self_test_result}")
    print(f"Total failures:            {len(all_failures)}")
    print(f"Runtime:                   {elapsed_total:.0f}s")

    return 1 if all_failures else 0


if __name__ == "__main__":
    sys.exit(main())
