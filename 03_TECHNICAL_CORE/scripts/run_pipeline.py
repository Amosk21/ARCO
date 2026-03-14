"""
ARCO Compliance Verification Pipeline — BFO/RO Aligned (RO:0000091 has_disposition)

Stages:
1) Load ontology + instance data
2) OWL-RL reasoning (materialize entailments)
3) SHACL validation
4) SPARQL audit checks (ASK)
5) Verify HighRiskSystem entailment + evidence path
6) Print regulatory determination certificate

Modeling relation: RO_0000091 has_disposition (per OBO Foundry / RO best practice)
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from rdflib import Graph
from pyshacl import validate

try:
    import owlrl
    HAS_OWLRL = True
except ImportError:
    HAS_OWLRL = False

REPO_ROOT = Path(__file__).resolve().parents[2]

ONTOLOGY_DIR = REPO_ROOT / "03_TECHNICAL_CORE" / "ontology"
VALIDATION_DIR = REPO_ROOT / "03_TECHNICAL_CORE" / "validation"
REASONING_DIR = REPO_ROOT / "03_TECHNICAL_CORE" / "reasoning"

CORE = ONTOLOGY_DIR / "ARCO_core.ttl"
GOV = ONTOLOGY_DIR / "ARCO_governance_extension.ttl"
INSTANCES = ONTOLOGY_DIR / "ARCO_instances_sentinel.ttl"

SHAPES = VALIDATION_DIR / "assessment_documentation_shape.ttl"

TRACEABILITY_QUERY = REASONING_DIR / "check_assessment_traceability.sparql"
LATENT_RISK_QUERY = REASONING_DIR / "detect_latent_risk.sparql"
HIGH_RISK_INFERENCE_QUERY = REASONING_DIR / "check_high_risk_inference.sparql"
INTENDED_USE_QUERY = REASONING_DIR / "check_intended_use.sparql"
ANNEX_III_1A_QUERY = REASONING_DIR / "check_annex_iii_1a_entailment.sparql"
ANNEX_III_5B_QUERY = REASONING_DIR / "check_annex_iii_5b_entailment.sparql"
OBLIGATION_QUERY = REASONING_DIR / "check_obligation_link.sparql"
REGULATORY_ALIGNMENT_QUERY = REASONING_DIR / "check_regulatory_alignment.sparql"

OUTPUT_DIR = REPO_ROOT / "runs" / "demo"

# --- System under evaluation (change this one line for a different system) ---
SYSTEM_LOCAL = "Sentinel_ID_System"
SYSTEM_IRI = f"https://arco.ai/ontology/core#{SYSTEM_LOCAL}"
ARCO_NS = "https://arco.ai/ontology/core#"


# ---------------------------
# helpers
# ---------------------------

def hr(title: str, width: int = 72) -> None:
    print("\n" + "=" * width)
    print(title)
    print("=" * width)

def sub(title: str, width: int = 72) -> None:
    print("\n" + "-" * width)
    print(title)
    print("-" * width)

def load_union_graph(*paths: Path) -> Graph:
    g = Graph()
    for p in paths:
        if not p.exists():
            raise FileNotFoundError(f"Missing file: {p}")
        g.parse(p.as_posix(), format="turtle")
    return g

def clone_graph(g: Graph) -> Graph:
    h = Graph()
    for t in g:
        h.add(t)
    return h

def run_sparql_ask_inline(data_graph: Graph, query: str) -> bool:
    result = data_graph.query(query)
    if isinstance(result, bool):
        return result
    rows = list(result)
    return bool(rows[0]) if rows else False

def run_sparql_ask_from_file(data_graph: Graph, query_path: Path) -> bool:
    if not query_path.exists():
        raise FileNotFoundError(f"Missing SPARQL query file: {query_path}")
    q = query_path.read_text(encoding="utf-8").strip()

    try:
        result = data_graph.query(q)
        if isinstance(result, bool):
            return result
        rows = list(result)
        return bool(rows[0]) if rows else False
    except Exception as e:
        raise RuntimeError(f"SPARQL query failed: {query_path}\n{e}")

def run_sparql_ask_for_system(data_graph: Graph, query_path: Path, system_local: str) -> bool:
    """Run a SPARQL ASK file query, substituting the sentinel placeholder with the actual system IRI."""
    if not query_path.exists():
        raise FileNotFoundError(f"Missing SPARQL query file: {query_path}")
    q = query_path.read_text(encoding="utf-8").strip()
    if system_local != "Sentinel_ID_System":
        q = q.replace(":Sentinel_ID_System", f":{system_local}")
    try:
        result = data_graph.query(q)
        if isinstance(result, bool):
            return result
        rows = list(result)
        return bool(rows[0]) if rows else False
    except Exception as e:
        raise RuntimeError(f"SPARQL query failed: {query_path}\n{e}")


# ---------------------------
# reasoning / validation
# ---------------------------

def run_reasoning(data_graph: Graph) -> tuple[Graph, int, int]:
    sub("REASONING")
    if not HAS_OWLRL:
        raise RuntimeError(
            "owlrl is not installed, but this pipeline requires reasoning.\n"
            "Install: pip install owlrl"
        )

    initial = len(data_graph)
    print("Running OWL-RL closure (materializing entailments)...")
    owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(data_graph)
    final = len(data_graph)
    added = final - initial
    print(f"Triples: {initial} -> {final}   (+{added} entailed)")
    return data_graph, initial, added

def run_shacl(data_graph: Graph) -> tuple[bool, str]:
    sub("SHACL")
    if not SHAPES.exists():
        raise FileNotFoundError(f"Missing SHACL shapes file: {SHAPES}")

    print("Validating SHACL shapes against the reasoned graph...")
    shapes_graph = Graph().parse(SHAPES.as_posix(), format="turtle")

    conforms, _, report_text = validate(
        data_graph=data_graph,
        shacl_graph=shapes_graph,
        inference="none",
        abort_on_first=False,
        allow_infos=True,
        allow_warnings=True,
        meta_shacl=False,
        advanced=True,
    )

    print(f"Conforms: {conforms}")
    if not conforms:
        print("\nSHACL report:\n")
        print(report_text)

    return conforms, str(report_text) if report_text else ""


# ---------------------------
# proof / evidence extraction
# ---------------------------

def _ask_highrisk(sys: str = SYSTEM_LOCAL) -> str:
    return f"""
PREFIX : <{ARCO_NS}>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
ASK WHERE {{ :{sys} rdf:type :HighRiskSystem . }}
"""

def _ask_primary_path(sys: str = SYSTEM_LOCAL) -> str:
    return f"""
PREFIX : <{ARCO_NS}>
PREFIX bfo: <http://purl.obolibrary.org/obo/BFO_>
PREFIX ro:  <http://purl.obolibrary.org/obo/RO_>
ASK WHERE {{
  :{sys} bfo:0000051 ?component .
  ?component ro:0000091 ?d .
  ?d a :AnnexIIITriggeringCapability .
}}
"""

def _select_primary_bindings(sys: str = SYSTEM_LOCAL) -> str:
    return f"""
PREFIX : <{ARCO_NS}>
PREFIX bfo: <http://purl.obolibrary.org/obo/BFO_>
PREFIX ro:  <http://purl.obolibrary.org/obo/RO_>
SELECT ?component ?d WHERE {{
  :{sys} bfo:0000051 ?component .
  ?component ro:0000091 ?d .
  ?d a :AnnexIIITriggeringCapability .
}}
LIMIT 5
"""

def _short(iri: str) -> str:
    """Shorten an IRI to its local name for display."""
    return iri.rsplit("#", 1)[-1] if "#" in iri else iri.rsplit("/", 1)[-1]

def get_primary_bindings(g: Graph, system_local: str = "Sentinel_ID_System") -> list[tuple[str, str]]:
    rows = []
    try:
        qres = g.query(_select_primary_bindings(system_local))
        for r in qres:
            rows.append((str(r.component), str(r.d)))
    except Exception:
        return []
    return rows

def verify_high_risk_inference(reasoned: Graph, source: Graph) -> tuple[bool, bool, bool, list[tuple[str, str]]]:
    """Returns (inference_ok, asserted_pre, entailed_post, bindings)."""
    hr("ARCO RESULT (ENTAILMENT + PROOF SKETCH)")

    # Before/after: was HighRiskSystem asserted in raw input?
    asserted_pre = run_sparql_ask_inline(source, _ask_highrisk(SYSTEM_LOCAL))

    # After reasoning: is HighRiskSystem present now?
    if HIGH_RISK_INFERENCE_QUERY.exists():
        entailed_post = run_sparql_ask_for_system(reasoned, HIGH_RISK_INFERENCE_QUERY, SYSTEM_LOCAL)
    else:
        entailed_post = run_sparql_ask_inline(reasoned, _ask_highrisk(SYSTEM_LOCAL))

    print(f"HighRiskSystem in source data (pre-reasoning):   {asserted_pre}")
    print(f"HighRiskSystem in reasoned graph (post-reason):  {entailed_post}")

    # Evidence check (primary path only — legacy bearer_of removed)
    primary_path = run_sparql_ask_inline(reasoned, _ask_primary_path(SYSTEM_LOCAL))

    sub("EVIDENCE PATH CHECK")
    print(f"has_disposition path (RO:0000091): {primary_path}")

    # Concrete bindings
    bindings = get_primary_bindings(reasoned, SYSTEM_LOCAL)
    if bindings:
        sub("CONCRETE BINDINGS")
        for i, (comp, disp) in enumerate(bindings, 1):
            print(f"{i}) component = {_short(comp)}")
            print(f"   disposition/capability = {_short(disp)}")

    sub("WHY THIS ENTAILS HighRiskSystem")
    print("Bridge axiom (ARCO_core.ttl):")
    print("  HighRiskSystem = System AND (has_part SOME (has_disposition SOME AnnexIIITriggeringCapability))")
    if not asserted_pre and entailed_post:
        print(f"  => {SYSTEM_LOCAL} rdf:type HighRiskSystem  (INFERRED, not asserted)")
    elif entailed_post:
        print(f"  => {SYSTEM_LOCAL} rdf:type HighRiskSystem  (ASSERTED)")

    # Hard enforcement: entailment must have at least one evidence path
    if entailed_post and not primary_path:
        sub("FAIL")
        print("Entailment is True, but no supporting evidence path was detected.")
        print("Likely cause: predicate mismatch or missing component facts.")
        return False, asserted_pre, entailed_post, bindings

    if entailed_post:
        sub("SUCCESS")
        print("HighRiskSystem classification is present AND justified by an explicit structural path.")
        return True, asserted_pre, entailed_post, bindings

    sub("FAIL")
    print("HighRiskSystem was not inferred.")
    print("Common causes:")
    print("  - owlrl not installed (no reasoning step)")
    print("  - bridge axiom uses a different predicate than the instances")
    print("  - missing has_part/component facts or missing AnnexIIITriggeringCapability typing")
    return False, asserted_pre, entailed_post, bindings


# ---------------------------
# HTML view
# ---------------------------

def write_html_view(
    output_dir: Path,
    system_local: str,
    classification_mode: str,
    bindings: list,
    shacl_ok: bool,
    traceability_ok: bool,
    latent_ok,
    intended_use_ok,
    annex_iii_1a_ok,
    annex_iii_5b_ok,
    obligation_ok,
    reg_alignment_ok,
    inferred_added: int,
    all_pass: bool,
    summary_raw: str,
    evidence_raw: str,
) -> None:
    """Write a self-contained static HTML determination view to output_dir."""

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # ── strip node labels ──────────────────────────────────────────
    comp_label = _short(bindings[0][0]) if bindings else "—"
    disp_label = _short(bindings[0][1]) if bindings else "—"
    comp_iri   = bindings[0][0] if bindings else ""
    disp_iri   = bindings[0][1] if bindings else ""

    # ── badges ─────────────────────────────────────────────────────
    if classification_mode == "INFERRED":
        mode_badge = '<span class="badge bi">INFERRED</span>'
        result_node_cls = "nr-high"
        result_label = "HighRiskSystem"
    elif classification_mode == "ASSERTED":
        mode_badge = '<span class="badge ba">ASSERTED</span>'
        result_node_cls = "nr-high"
        result_label = "HighRiskSystem"
    else:
        mode_badge = '<span class="badge bn">NOT PRESENT</span>'
        result_node_cls = "nr-none"
        result_label = "NOT PRESENT"

    overall_badge = '<span class="badge bp">ALL PASS</span>' if all_pass else '<span class="badge bf">SOME FAIL</span>'

    def _b(val, t="PASS", f="FAIL"):
        if val is None: return '<span class="badge bn">N/A</span>'
        return f'<span class="badge {"bp" if val else "bf"}">{t if val else f}</span>'

    def _annex(val):
        if val is None: return '<span class="badge bn">N/A</span>'
        return '<span class="badge bp">VERIFIED (ENTAILED)</span>' if val else '<span class="badge bn">NOT APPLICABLE</span>'

    # ── audit rows (check | layer | result) ───────────────────────
    audit_rows = [
        ("SHACL conformance",       "classification / structure", _b(shacl_ok)),
        ("HighRiskSystem entailment","classification / OWL-RL",   _b(shacl_ok and all_pass)),
        ("Annex III 1(a)",          "classification / OWL-RL",   _annex(annex_iii_1a_ok)),
        ("Annex III 5(b)",          "classification / OWL-RL",   _annex(annex_iii_5b_ok)),
        ("Traceability",            "audit / SPARQL",             _b(traceability_ok)),
        ("Latent risk",             "audit / SPARQL",             _b(latent_ok, "DETECTED", "NOT DETECTED") if latent_ok is not None else '<span class="badge bn">N/A</span>'),
        ("Intended use modelled",   "audit / SPARQL",             _b(intended_use_ok)),
        ("Obligation linked",       "audit / SPARQL",             _b(obligation_ok)),
        ("Regulatory alignment",    "audit / SPARQL",             _b(reg_alignment_ok)),
    ]
    audit_html = "\n".join(
        f'      <tr><td>{chk}</td><td class="layer">{layer}</td><td>{badge}</td></tr>'
        for chk, layer, badge in audit_rows
    )

    # ── strip node helper ─────────────────────────────────────────
    def node(cls, type_label, label, iri=""):
        iri_attr = f' title="{iri}"' if iri else ""
        return f'<div class="node {cls}"{iri_attr}><span class="ntype">{type_label}</span><span class="nlabel">{label}</span></div>'

    def edge(rel, iri_label=""):
        sub_span = f'<span class="eiri">{iri_label}</span>' if iri_label else ""
        return f'<div class="edge"><span class="earrow">→</span><span class="erel">{rel}</span>{sub_span}</div>'

    # Strip nodes — AnnexIIITriggeringCapability is a structural presentation
    # assumption: the disposition is classified as this type by the bridge axiom
    # in ARCO_core.ttl. Not directly readable from evidence.json.
    strip_html = (
        node("ns", "System", system_local)
        + edge("has_part", "bfo:0000051")
        + node("nc", "SystemComponent", comp_label, comp_iri)
        + edge("has_disposition", "ro:0000091")
        + node("nd", "Disposition", disp_label, disp_iri)
        + edge("rdf:type ⊆")
        + node("nt", "AnnexIIITriggeringCapability", "(bridge axiom) ‡")
        + edge("OWL-RL ⊢")
        + node(result_node_cls, "Classification", result_label)
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ARCO — {system_local} — Determination View</title>
<style>
:root {{
  --bg:#0f1117; --sf:#1a1d27; --bd:#2a2d3d; --tx:#e0e4f0; --mu:#6b7280;
  --pass:#22c55e; --fail:#ef4444; --inf:#818cf8; --ass:#f59e0b;
}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Courier New',monospace;background:var(--bg);color:var(--tx);padding:2rem;max-width:1100px;margin:0 auto;line-height:1.5}}
h1{{font-size:1.3rem;font-weight:700;margin-bottom:.3rem}}
h2{{font-size:.75rem;font-weight:600;color:var(--mu);text-transform:uppercase;letter-spacing:.07em;margin:1.6rem 0 .6rem}}
.meta{{color:var(--mu);font-size:.8rem;margin-bottom:1.6rem}}
/* badges */
.badge{{font-size:.65rem;padding:.18rem .45rem;border-radius:3px;font-weight:700;letter-spacing:.04em;white-space:nowrap}}
.bi{{background:#312e81;color:var(--inf)}} .ba{{background:#451a03;color:var(--ass)}}
.bn{{background:#1f2937;color:var(--mu)}}  .bp{{background:#14532d;color:var(--pass)}}
.bf{{background:#450a0a;color:var(--fail)}}
/* banner */
.banner{{display:flex;align-items:center;flex-wrap:wrap;gap:.6rem;background:var(--sf);border:1px solid var(--bd);padding:.7rem 1.1rem;border-radius:6px;margin-bottom:1.6rem;font-size:1rem;font-weight:600}}
/* strip */
.strip{{display:flex;align-items:center;flex-wrap:wrap;gap:0;background:var(--sf);border:1px solid var(--bd);padding:1.2rem 1rem;border-radius:8px;overflow-x:auto}}
.node{{display:flex;flex-direction:column;align-items:center;padding:.6rem .85rem;border-radius:6px;min-width:120px;text-align:center;gap:.25rem}}
.ntype{{color:var(--mu);font-size:.6rem;text-transform:uppercase;letter-spacing:.05em}}
.nlabel{{font-weight:600;font-size:.75rem;word-break:break-word}}
.ns{{background:#1e3a5f;border:1px solid #2563eb}}
.nc{{background:#134e4a;border:1px solid #0d9488}}
.nd{{background:#431407;border:1px solid #b45309}}
.nt{{background:#2e1065;border:1px solid #7c3aed}}
.nr-high{{background:#450a0a;border:1px solid #dc2626}}
.nr-none{{background:#1f2937;border:1px solid #374151}}
.edge{{display:flex;flex-direction:column;align-items:center;padding:0 .4rem;min-width:72px;text-align:center;gap:.15rem}}
.earrow{{font-size:1.1rem;color:#4b5563}}
.erel{{font-size:.6rem;color:var(--mu)}}
.eiri{{font-size:.55rem;color:#374151}}
/* audit table */
table{{width:100%;border-collapse:collapse;font-size:.82rem}}
th{{text-align:left;padding:.45rem .7rem;border-bottom:1px solid var(--bd);color:var(--mu);font-size:.7rem;text-transform:uppercase;letter-spacing:.04em}}
td{{padding:.45rem .7rem;border-bottom:1px solid var(--bd)}}
tr:last-child td{{border-bottom:none}}
.layer{{color:var(--mu);font-size:.75rem}}
/* triples counter */
.triples{{display:inline-block;background:var(--sf);border:1px solid var(--bd);padding:.5rem 1rem;border-radius:6px;font-size:.85rem;margin-bottom:1rem}}
.triples span{{color:var(--inf);font-weight:700}}
/* not-yet */
.notyet{{background:var(--sf);border:1px solid var(--bd);border-left:3px solid #374151;padding:.9rem 1.1rem;border-radius:6px}}
.notyet ul{{list-style:none;color:var(--mu);font-size:.82rem;margin-top:.4rem}}
.notyet li::before{{content:"— "}}
.notyet li{{padding:.15rem 0}}
/* footnote */
.fn{{font-size:.72rem;color:var(--mu);margin-top:.5rem}}
/* raw json */
details{{margin-top:1.2rem}}
summary{{cursor:pointer;color:var(--mu);font-size:.82rem;padding:.4rem 0;user-select:none}}
summary:hover{{color:var(--tx)}}
pre{{background:var(--sf);border:1px solid var(--bd);padding:.9rem;border-radius:6px;font-size:.72rem;overflow-x:auto;margin-top:.5rem;white-space:pre-wrap;word-break:break-all;line-height:1.5}}
/* footer */
footer{{margin-top:2rem;padding-top:1rem;border-top:1px solid var(--bd);color:var(--mu);font-size:.72rem}}
</style>
</head>
<body>

<h1>ARCO — Regulatory Determination View</h1>
<p class="meta">System: <strong>{system_local}</strong> &nbsp;|&nbsp; Regime: EU AI Act Article 6 / Annex III &nbsp;|&nbsp; Generated: {ts}</p>

<div class="banner">
  Classification: <strong>{result_label}</strong>
  {mode_badge}
  {overall_badge}
</div>

<h2>Determination Path</h2>
<section class="strip">
{strip_html}
</section>
<p class="fn">‡ AnnexIIITriggeringCapability is a structural presentation assumption derived from the bridge axiom in ARCO_core.ttl. It is not directly readable from evidence.json — it is the type the disposition must satisfy for HighRiskSystem entailment to fire.</p>

<h2>Audit &amp; Classification Results</h2>
<table>
  <thead><tr><th>Check</th><th>Layer</th><th>Result</th></tr></thead>
  <tbody>
{audit_html}
  </tbody>
</table>

<div class="triples" style="margin-top:1rem">OWL-RL entailed triples added: <span>+{inferred_added}</span></div>

<h2>Not Yet Available (Option B)</h2>
<div class="notyet">
  <ul>
    <li>Gate-level status (Gate 1 / 2 / 3 individual pass/fail)</li>
    <li>Per-node provenance: which triples were asserted vs. entailed</li>
    <li>Full inference sub-graph for this determination path</li>
    <li>Regulatory alignment detail (which axiom produced each step)</li>
  </ul>
</div>

<h2>Raw Outputs</h2>
<details>
  <summary>summary.json</summary>
  <pre>{summary_raw}</pre>
</details>
<details>
  <summary>evidence.json</summary>
  <pre>{evidence_raw}</pre>
</details>

<footer>
  ARCO Compliance Verification Pipeline &nbsp;|&nbsp; OWL-RL + SHACL + SPARQL &nbsp;|&nbsp; {ts}<br>
  Classification is authoritative from OWL-RL entailment only. SPARQL rows are audit/documentation layer.
</footer>

</body>
</html>
"""
    (output_dir / "determination_view.html").write_text(html, encoding="utf-8")


# ---------------------------
# main
# ---------------------------

def _pf(ok: bool) -> str:
    return "PASS" if ok else "FAIL"

def main() -> None:
    parser = argparse.ArgumentParser(description="ARCO Compliance Verification Pipeline")
    parser.add_argument(
        "--system", default="Sentinel_ID_System",
        help="Local name of the system under evaluation (default: Sentinel_ID_System)"
    )
    parser.add_argument(
        "--instances", default=None,
        help="Path to instance TTL file (default: ARCO_instances_sentinel.ttl)"
    )
    args = parser.parse_args()

    global SYSTEM_LOCAL, SYSTEM_IRI, INSTANCES
    SYSTEM_LOCAL = args.system
    SYSTEM_IRI = f"{ARCO_NS}{SYSTEM_LOCAL}"
    if args.instances is not None:
        INSTANCES = Path(args.instances)

    hr("ARCO COMPLIANCE VERIFICATION PIPELINE (OPERATOR VIEW)")

    sub("LOAD")
    print("Loading: core ontology + governance extension + instance data")
    g_source = load_union_graph(CORE, GOV, INSTANCES)
    print(f"Triples loaded (asserted): {len(g_source)}")

    # clone -> reason over the copy so we can compare pre vs post
    g = clone_graph(g_source)

    g, initial_count, inferred_added = run_reasoning(g)

    shacl_ok, shacl_report_text = run_shacl(g)

    sub("AUDIT QUERIES (SPARQL ASK)")
    print("Traceability check...")
    traceability_ok = run_sparql_ask_for_system(g, TRACEABILITY_QUERY, SYSTEM_LOCAL)
    print(f"Traceability: {traceability_ok}")

    latent_ok = None
    if LATENT_RISK_QUERY.exists():
        print("\nLatent risk detection (hardware path)...")
        latent_ok = run_sparql_ask_for_system(g, LATENT_RISK_QUERY, SYSTEM_LOCAL)
        print(f"Latent risk detected: {latent_ok}")

    intended_use_ok = None
    if INTENDED_USE_QUERY.exists():
        print("\nIntended use + use scenario (three-gate check)...")
        intended_use_ok = run_sparql_ask_for_system(g, INTENDED_USE_QUERY, SYSTEM_LOCAL)
        print(f"Intended use modeled: {intended_use_ok}")

    annex_iii_1a_ok = None
    if ANNEX_III_1A_QUERY.exists():
        print("\nAnnex III 1(a) entailment (OWL-inferred, audit only)...")
        annex_iii_1a_ok = run_sparql_ask_for_system(g, ANNEX_III_1A_QUERY, SYSTEM_LOCAL)
        print(f"Annex III 1(a) applicable: {annex_iii_1a_ok}")

    annex_iii_5b_ok = None
    if ANNEX_III_5B_QUERY.exists():
        print("\nAnnex III 5(b) entailment (OWL-inferred, audit only)...")
        annex_iii_5b_ok = run_sparql_ask_for_system(g, ANNEX_III_5B_QUERY, SYSTEM_LOCAL)
        print(f"Annex III 5(b) applicable: {annex_iii_5b_ok}")

    obligation_ok = None
    if OBLIGATION_QUERY.exists():
        print("\nObligation link (provider/deployer responsibility)...")
        obligation_ok = run_sparql_ask_for_system(g, OBLIGATION_QUERY, SYSTEM_LOCAL)
        print(f"Obligation linked: {obligation_ok}")

    reg_alignment_ok = None
    if REGULATORY_ALIGNMENT_QUERY.exists():
        print("\nRegulatory alignment (law prescribes == intended use prescribes)...")
        reg_alignment_ok = run_sparql_ask_for_system(g, REGULATORY_ALIGNMENT_QUERY, SYSTEM_LOCAL)
        print(f"Regulatory aligned: {reg_alignment_ok}")

    inference_ok, asserted_pre, entailed_post, bindings = verify_high_risk_inference(g, g_source)

    # ---------------------------------------------------------------
    # SUMMARY
    # Two-layer architecture: classification (OWL-RL) vs. audit (SPARQL).
    # Classification rows are OWL-entailed — gate-removal tests verify them.
    # Audit rows inspect declared documentary content on the reasoned graph;
    # they do not produce and cannot affect the classification result.
    # ---------------------------------------------------------------
    hr("SUMMARY")
    print("  [classification layer — OWL-RL entailment]")
    print(f"SHACL:         {_pf(shacl_ok)}")
    print(f"Entailment:    {_pf(inference_ok)}")
    if annex_iii_1a_ok is not None:
        print(f"Annex III 1a:  {'VERIFIED (ENTAILED)' if annex_iii_1a_ok else 'NOT APPLICABLE'} (OWL-entailed)")
    if annex_iii_5b_ok is not None:
        print(f"Annex III 5b:  {'VERIFIED (ENTAILED)' if annex_iii_5b_ok else 'NOT APPLICABLE'} (OWL-entailed)")
    print()
    print("  [audit documentation layer — SPARQL ASK on reasoned graph]")
    print(f"Traceability:  {_pf(traceability_ok)}")
    if latent_ok is not None:
        print(f"Latent risk:   {_pf(latent_ok)}")
    if intended_use_ok is not None:
        print(f"Intended use:  {_pf(intended_use_ok)}")
    if obligation_ok is not None:
        print(f"Obligation:    {_pf(obligation_ok)}")
    if reg_alignment_ok is not None:
        print(f"Reg. aligned:  {_pf(reg_alignment_ok)}")
    print(f"Entailed triples added: +{inferred_added}")

    # Annex III category checks (1a, 5b) are informational cross-category audit lines.
    # HighRiskSystem entailment (inference_ok) already covers the classification result.
    # Neither category check is included in all_pass: a system entailed as 5(b) but not
    # 1(a) (or vice versa) is not a failure — it reflects correct cross-category isolation.
    all_pass = shacl_ok and traceability_ok and inference_ok
    if latent_ok is not None:
        all_pass = all_pass and latent_ok
    if intended_use_ok is not None:
        all_pass = all_pass and intended_use_ok
    if obligation_ok is not None:
        all_pass = all_pass and obligation_ok
    if reg_alignment_ok is not None:
        all_pass = all_pass and reg_alignment_ok

    print("\nALL CHECKS PASSED" if all_pass else "\nSOME CHECKS FAILED")

    # ---------------------------------------------------------------
    # REGULATORY DETERMINATION CERTIFICATE
    # ---------------------------------------------------------------
    if not asserted_pre and entailed_post:
        classification_mode = "INFERRED"
    elif asserted_pre and entailed_post:
        classification_mode = "ASSERTED"
    else:
        classification_mode = "NOT PRESENT"

    # Derive triggering capability class from bindings
    trigger_display = "N/A"
    if bindings:
        trigger_display = _short(bindings[0][1])

    # Build evidence path strings (up to 3)
    evidence_lines = []
    for comp, disp in bindings[:3]:
        evidence_lines.append(f"  {SYSTEM_LOCAL} -> {_short(comp)} -> {_short(disp)}")

    hr("REGULATORY DETERMINATION CERTIFICATE")
    print(f"  SYSTEM:                  {SYSTEM_LOCAL}")
    print(f"  REGIME:                  EU AI Act (Article 6 / Annex III)")
    if classification_mode in ("INFERRED", "ASSERTED"):
        print(f"  CLASSIFICATION:          HighRiskSystem ({classification_mode})")
    else:
        print(f"  CLASSIFICATION:          {classification_mode}")
    print(f"  TRIGGERING CAPABILITY:   {trigger_display}")
    if evidence_lines:
        print(f"  EVIDENCE PATH:")
        for line in evidence_lines:
            print(line)
    else:
        print(f"  EVIDENCE PATH:           (none detected)")
    print(f"  SHACL:                   {_pf(shacl_ok)}")
    print(f"  TRACEABILITY:            {_pf(traceability_ok)}")
    if latent_ok is not None:
        print(f"  LATENT RISK:             {'DETECTED' if latent_ok else 'NOT DETECTED'}")
    if intended_use_ok is not None:
        print(f"  INTENDED USE:            {_pf(intended_use_ok)}")
    if annex_iii_1a_ok is not None:
        print(f"  ANNEX III 1(a):          {'VERIFIED (ENTAILED)' if annex_iii_1a_ok else 'NOT APPLICABLE'}")
    if annex_iii_5b_ok is not None:
        print(f"  ANNEX III 5(b):          {'VERIFIED (ENTAILED)' if annex_iii_5b_ok else 'NOT APPLICABLE'}")
    if obligation_ok is not None:
        print(f"  OBLIGATION:              {_pf(obligation_ok)}")
    print(f"  ENTAILED TRIPLES ADDED:  +{inferred_added}")
    print("=" * 72)

    # ---------------------------------------------------------------
    # WRITE OUTPUT FILES (runs/demo/)
    # ---------------------------------------------------------------
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # certificate.txt
    cert_lines = []
    cert_lines.append("=" * 72)
    cert_lines.append("REGULATORY DETERMINATION CERTIFICATE")
    cert_lines.append("=" * 72)
    cert_lines.append(f"  SYSTEM:                  {SYSTEM_LOCAL}")
    cert_lines.append(f"  REGIME:                  EU AI Act (Article 6 / Annex III)")
    if classification_mode in ("INFERRED", "ASSERTED"):
        cert_lines.append(f"  CLASSIFICATION:          HighRiskSystem ({classification_mode})")
    else:
        cert_lines.append(f"  CLASSIFICATION:          {classification_mode}")
    cert_lines.append(f"  TRIGGERING CAPABILITY:   {trigger_display}")
    if evidence_lines:
        cert_lines.append(f"  EVIDENCE PATH:")
        for line in evidence_lines:
            cert_lines.append(line)
    else:
        cert_lines.append(f"  EVIDENCE PATH:           (none detected)")
    cert_lines.append(f"  SHACL:                   {_pf(shacl_ok)}")
    cert_lines.append(f"  TRACEABILITY:            {_pf(traceability_ok)}")
    if latent_ok is not None:
        cert_lines.append(f"  LATENT RISK:             {'DETECTED' if latent_ok else 'NOT DETECTED'}")
    if intended_use_ok is not None:
        cert_lines.append(f"  INTENDED USE:            {_pf(intended_use_ok)}")
    if annex_iii_1a_ok is not None:
        cert_lines.append(f"  ANNEX III 1(a):          {'VERIFIED (ENTAILED)' if annex_iii_1a_ok else 'NOT APPLICABLE'}")
    if annex_iii_5b_ok is not None:
        cert_lines.append(f"  ANNEX III 5(b):          {'VERIFIED (ENTAILED)' if annex_iii_5b_ok else 'NOT APPLICABLE'}")
    if obligation_ok is not None:
        cert_lines.append(f"  OBLIGATION:              {_pf(obligation_ok)}")
    cert_lines.append(f"  ENTAILED TRIPLES ADDED:  +{inferred_added}")
    cert_lines.append("=" * 72)
    (OUTPUT_DIR / "certificate.txt").write_text("\n".join(cert_lines) + "\n", encoding="utf-8")

    # summary.json
    summary = {
        "system": SYSTEM_LOCAL,
        "regime": "EU AI Act (Article 6 / Annex III)",
        "classification": f"HighRiskSystem ({classification_mode})" if classification_mode in ("INFERRED", "ASSERTED") else classification_mode,
        "shacl": _pf(shacl_ok),
        "traceability": _pf(traceability_ok),
        "latent_risk": (_pf(latent_ok) if latent_ok is not None else "N/A"),
        "intended_use": (_pf(intended_use_ok) if intended_use_ok is not None else "N/A"),
        "annex_iii_1a": ("VERIFIED (ENTAILED)" if annex_iii_1a_ok else ("NOT APPLICABLE" if annex_iii_1a_ok is not None else "N/A")),
        "annex_iii_5b": ("VERIFIED (ENTAILED)" if annex_iii_5b_ok else ("NOT APPLICABLE" if annex_iii_5b_ok is not None else "N/A")),
        "obligation": (_pf(obligation_ok) if obligation_ok is not None else "N/A"),
        "entailment": _pf(inference_ok),
        "entailed_triples_added": inferred_added,
        "all_checks_passed": all_pass,
    }
    (OUTPUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    # evidence.json
    evidence = [
        {"component": _short(comp), "disposition": _short(disp), "component_iri": comp, "disposition_iri": disp}
        for comp, disp in bindings
    ]
    (OUTPUT_DIR / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")

    # determination_view.html
    write_html_view(
        output_dir=OUTPUT_DIR,
        system_local=SYSTEM_LOCAL,
        classification_mode=classification_mode,
        bindings=bindings,
        shacl_ok=shacl_ok,
        traceability_ok=traceability_ok,
        latent_ok=latent_ok,
        intended_use_ok=intended_use_ok,
        annex_iii_1a_ok=annex_iii_1a_ok,
        annex_iii_5b_ok=annex_iii_5b_ok,
        obligation_ok=obligation_ok,
        reg_alignment_ok=reg_alignment_ok,
        inferred_added=inferred_added,
        all_pass=all_pass,
        summary_raw=json.dumps(summary, indent=2),
        evidence_raw=json.dumps(evidence, indent=2),
    )

    # shacl_report.txt
    shacl_out = f"conforms: {shacl_ok}\n"
    if shacl_report_text:
        shacl_out += "\n" + shacl_report_text
    (OUTPUT_DIR / "shacl_report.txt").write_text(shacl_out, encoding="utf-8")

    sub("OUTPUT FILES")
    for f in sorted(OUTPUT_DIR.iterdir()):
        print(f"  {f.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
