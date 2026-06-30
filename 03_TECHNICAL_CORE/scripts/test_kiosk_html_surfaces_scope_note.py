"""
test_kiosk_html_surfaces_scope_note.py — regression test for M-DefDiscipline-1.

The essence-vs-aboutness annotation pass moved the regulatory carve-out conclusion
("out of scope of Annex III 1(a) ...") OUT of skos:definition (which the negative-case
certificate renders) and INTO skos:scopeNote. Without a matching emitter change, the
plain-English carve-out would silently disappear from the rendered output — the cut
would be realist-correct but produce an emission-completeness regression (flagged by
the Smith realist gate in the M-DefDiscipline-1 adversarial review).

This test pins the emitter behavior, and pins it tightly:

  - It reads the scope notes from the EMITTED reasoned graph (runs/demo/reasoned_graph.ttl),
    the same graph the HTML emitter queries — not a hardcoded literal. So the test verifies
    the rendered string against the graph source, not against itself.
  - It asserts BOTH the Gate-1 (capability) and Gate-2 (process) scope notes appear verbatim.
    A break in either render path now fails (the earlier single-phrase assertion could pass
    on one path while the other broke).
  - Its precondition actually checks that the carve-out lives in skos:scopeNote and NOT in
    skos:definition, so the test genuinely exercises the scopeNote emission path.

Run from repo root:
    python 03_TECHNICAL_CORE/scripts/test_kiosk_html_surfaces_scope_note.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from rdflib import Graph, URIRef
from rdflib.namespace import SKOS

REPO_ROOT = Path(__file__).resolve().parents[2]
PIPELINE = REPO_ROOT / "03_TECHNICAL_CORE" / "scripts" / "run_pipeline.py"
KIOSK_TTL = REPO_ROOT / "03_TECHNICAL_CORE" / "ontology" / "ARCO_instances_verification.ttl"
HTML_OUTPUT = REPO_ROOT / "runs" / "demo" / "determination_view.html"
REASONED_GRAPH = REPO_ROOT / "runs" / "demo" / "reasoned_graph.ttl"

ARCO = "https://arco.ai/ontology/core#"
# The kiosk asserts a 1:1 verification capability (Gate-1 path) and a 1:1 verification
# process (Gate-2 path). Both must surface their regulatory scope.
CAP = URIRef(ARCO + "BiometricVerificationCapability")
PROC = URIRef(ARCO + "BiometricVerificationProcess")
SCOPE_LABEL = "Its regulatory scope, from the ontology:"
CARVE_OUT_MARKER = "Out of scope of Annex III 1(a)"


def _one(g: Graph, cls: URIRef, pred) -> str | None:
    vals = [str(o) for o in g.objects(cls, pred)]
    return vals[0] if vals else None


def main() -> int:
    result = subprocess.run(
        [
            sys.executable,
            str(PIPELINE),
            "--instances",
            str(KIOSK_TTL),
            "--system",
            "VerificationKiosk_001",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"FAIL: pipeline exit {result.returncode}")
        print(result.stdout[-500:])
        print(result.stderr[-500:])
        return 1

    if not HTML_OUTPUT.exists() or not REASONED_GRAPH.exists():
        print("FAIL: expected outputs (determination_view.html and/or reasoned_graph.ttl) not generated")
        return 1

    # Source of truth: the emitted reasoned graph the HTML emitter queries.
    g = Graph()
    g.parse(REASONED_GRAPH.as_posix(), format="turtle")
    cap_scope = _one(g, CAP, SKOS.scopeNote)
    proc_scope = _one(g, PROC, SKOS.scopeNote)

    # PRECONDITION (the one the first version of this test was missing): the carve-out must
    # live in skos:scopeNote and NOT in skos:definition. Otherwise the test is not exercising
    # the scopeNote emission path at all.
    if not cap_scope or not proc_scope:
        print("PRECONDITION FAIL: capability and/or process skos:scopeNote missing from the graph.")
        return 1
    if CARVE_OUT_MARKER not in cap_scope or CARVE_OUT_MARKER not in proc_scope:
        print("PRECONDITION FAIL: the carve-out marker is not in the capability/process scopeNote.")
        return 1
    for cls in (CAP, PROC):
        defn = _one(g, cls, SKOS.definition) or ""
        if CARVE_OUT_MARKER in defn:
            print(
                f"PRECONDITION FAIL: the carve-out is still in skos:definition of {cls}; "
                "the test would not be exercising the scopeNote emission path."
            )
            return 1

    html = HTML_OUTPUT.read_text(encoding="utf-8")

    # Assert the render label plus the EXACT scope note of BOTH paths, verbatim from the graph.
    missing = []
    if SCOPE_LABEL not in html:
        missing.append(f"render label {SCOPE_LABEL!r}")
    if cap_scope not in html:
        missing.append(f"capability scopeNote (Gate-1 path), verbatim: {cap_scope!r}")
    if proc_scope not in html:
        missing.append(f"process scopeNote (Gate-2 path), verbatim: {proc_scope!r}")
    if missing:
        print(
            "FAIL: negative-case HTML does not surface the graph-backed scope notes verbatim "
            "(M-DefDiscipline-1 emission-completeness gate)."
        )
        for m in missing:
            print(f"  missing: {m}")
        return 1

    print(
        "PASS: kiosk HTML surfaces the exact skos:scopeNote of BOTH the capability (Gate-1) "
        "and process (Gate-2) paths, verbatim from the emitted reasoned graph."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
