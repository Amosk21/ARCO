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

import json
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

def get_primary_bindings(g: Graph) -> list[tuple[str, str]]:
    rows = []
    try:
        qres = g.query(_select_primary_bindings())
        for r in qres:
            rows.append((str(r.component), str(r.d)))
    except Exception:
        return []
    return rows

def verify_high_risk_inference(reasoned: Graph, source: Graph) -> tuple[bool, bool, bool, list[tuple[str, str]]]:
    """Returns (inference_ok, asserted_pre, entailed_post, bindings)."""
    hr("ARCO RESULT (ENTAILMENT + PROOF SKETCH)")

    # Before/after: was HighRiskSystem asserted in raw input?
    asserted_pre = run_sparql_ask_inline(source, _ask_highrisk())

    # After reasoning: is HighRiskSystem present now?
    if HIGH_RISK_INFERENCE_QUERY.exists():
        entailed_post = run_sparql_ask_from_file(reasoned, HIGH_RISK_INFERENCE_QUERY)
    else:
        entailed_post = run_sparql_ask_inline(reasoned, _ask_highrisk())

    print(f"HighRiskSystem in source data (pre-reasoning):   {asserted_pre}")
    print(f"HighRiskSystem in reasoned graph (post-reason):  {entailed_post}")

    # Evidence check (primary path only — legacy bearer_of removed)
    primary_path = run_sparql_ask_inline(reasoned, _ask_primary_path())

    sub("EVIDENCE PATH CHECK")
    print(f"has_disposition path (RO:0000091): {primary_path}")

    # Concrete bindings
    bindings = get_primary_bindings(reasoned)
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
# main
# ---------------------------

def _pf(ok: bool) -> str:
    return "PASS" if ok else "FAIL"

def main() -> None:
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
    traceability_ok = run_sparql_ask_from_file(g, TRACEABILITY_QUERY)
    print(f"Traceability: {traceability_ok}")

    latent_ok = None
    if LATENT_RISK_QUERY.exists():
        print("\nLatent risk detection (hardware path)...")
        latent_ok = run_sparql_ask_from_file(g, LATENT_RISK_QUERY)
        print(f"Latent risk detected: {latent_ok}")

    intended_use_ok = None
    if INTENDED_USE_QUERY.exists():
        print("\nIntended use + use scenario (three-gate check)...")
        intended_use_ok = run_sparql_ask_from_file(g, INTENDED_USE_QUERY)
        print(f"Intended use modeled: {intended_use_ok}")

    annex_iii_1a_ok = None
    if ANNEX_III_1A_QUERY.exists():
        print("\nAnnex III 1(a) entailment (OWL-inferred, audit only)...")
        annex_iii_1a_ok = run_sparql_ask_from_file(g, ANNEX_III_1A_QUERY)
        print(f"Annex III 1(a) applicable: {annex_iii_1a_ok}")

    inference_ok, asserted_pre, entailed_post, bindings = verify_high_risk_inference(g, g_source)

    # ---------------------------------------------------------------
    # SUMMARY (existing)
    # ---------------------------------------------------------------
    hr("SUMMARY")
    print(f"SHACL:         {_pf(shacl_ok)}")
    print(f"Traceability:  {_pf(traceability_ok)}")
    if latent_ok is not None:
        print(f"Latent risk:   {_pf(latent_ok)}")
    if intended_use_ok is not None:
        print(f"Intended use:  {_pf(intended_use_ok)}")
    if annex_iii_1a_ok is not None:
        print(f"Annex III 1a:  {_pf(annex_iii_1a_ok)}")
    print(f"Entailment:    {_pf(inference_ok)}")
    print(f"Entailed triples added: +{inferred_added}")

    all_pass = shacl_ok and traceability_ok and inference_ok
    if latent_ok is not None:
        all_pass = all_pass and latent_ok
    if intended_use_ok is not None:
        all_pass = all_pass and intended_use_ok
    if annex_iii_1a_ok is not None:
        all_pass = all_pass and annex_iii_1a_ok

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
        print(f"  ANNEX III 1(a):          {'VERIFIED (ENTAILED)' if annex_iii_1a_ok else 'NOT VERIFIED'}")
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
        cert_lines.append(f"  ANNEX III 1(a):          {'VERIFIED (ENTAILED)' if annex_iii_1a_ok else 'NOT VERIFIED'}")
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
        "annex_iii_1a": (_pf(annex_iii_1a_ok) if annex_iii_1a_ok is not None else "N/A"),
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
