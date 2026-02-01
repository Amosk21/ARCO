"""
ARCO Compliance Verification Pipeline — BFO/RO Aligned Version (RO:0000091 has_disposition)

Stages:
1) Load ontology + instance data
2) OWL-RL reasoning (materialize entailments)
3) SHACL validation
4) SPARQL audit checks (ASK)
5) Verify HighRiskSystem entailment + show the evidence path that makes it hold

Alignment:
- Primary modeling relation: RO_0000091 has_disposition
- Legacy diagnostic: RO_0000053 bearer_of (kept only to detect older patterns)
"""

from __future__ import annotations

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
    if not HAS_OWLRL:
        sub("REASONING")
        print("owlrl not installed -> skipping reasoning")
        print("Install: pip install owlrl")
        return data_graph, len(data_graph), 0

    sub("REASONING")
    initial = len(data_graph)
    print("Running OWL-RL closure (materializing entailments)...")
    owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(data_graph)
    final = len(data_graph)
    added = final - initial
    print(f"Triples: {initial} -> {final}   (+{added} entailed)")
    return data_graph, initial, added

def run_shacl(data_graph: Graph) -> bool:
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

    return conforms


# ---------------------------
# proof / evidence extraction
# ---------------------------

ASK_ASSERTED_HIGHRISK = """
PREFIX : <https://arco.ai/ontology/core#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
ASK WHERE { :Sentinel_ID_System rdf:type :HighRiskSystem . }
"""

ASK_PRIMARY_PATH = """
PREFIX : <https://arco.ai/ontology/core#>
PREFIX bfo: <http://purl.obolibrary.org/obo/BFO_>
PREFIX ro:  <http://purl.obolibrary.org/obo/RO_>
ASK WHERE {
  :Sentinel_ID_System bfo:0000051 ?component .
  ?component ro:0000091 ?d .
  ?d a :AnnexIIITriggeringCapability .
}
"""

# Legacy diagnostic (FIXED): same shape, different predicate.
ASK_LEGACY_PATH = """
PREFIX : <https://arco.ai/ontology/core#>
PREFIX bfo: <http://purl.obolibrary.org/obo/BFO_>
PREFIX ro:  <http://purl.obolibrary.org/obo/RO_>
ASK WHERE {
  :Sentinel_ID_System bfo:0000051 ?component .
  ?component ro:0000053 ?d .
  ?d a :AnnexIIITriggeringCapability .
}
"""

SELECT_PRIMARY_BINDINGS = """
PREFIX : <https://arco.ai/ontology/core#>
PREFIX bfo: <http://purl.obolibrary.org/obo/BFO_>
PREFIX ro:  <http://purl.obolibrary.org/obo/RO_>
SELECT ?component ?d WHERE {
  :Sentinel_ID_System bfo:0000051 ?component .
  ?component ro:0000091 ?d .
  ?d a :AnnexIIITriggeringCapability .
}
LIMIT 5
"""

def get_primary_bindings(g: Graph) -> list[tuple[str, str]]:
    rows = []
    try:
        qres = g.query(SELECT_PRIMARY_BINDINGS)
        for r in qres:
            rows.append((str(r.component), str(r.d)))
    except Exception:
        return []
    return rows

def verify_high_risk_inference(reasoned: Graph, source: Graph) -> bool:
    hr("ARCO RESULT (ENTAILMENT + PROOF SKETCH)")

    # Before/after: was HighRiskSystem asserted in raw input?
    asserted_pre = run_sparql_ask_inline(source, ASK_ASSERTED_HIGHRISK)

    # After reasoning: is HighRiskSystem present now?
    if HIGH_RISK_INFERENCE_QUERY.exists():
        entailed_post = run_sparql_ask_from_file(reasoned, HIGH_RISK_INFERENCE_QUERY)
    else:
        entailed_post = run_sparql_ask_inline(reasoned, ASK_ASSERTED_HIGHRISK)

    print(f"HighRiskSystem in source data (pre-reasoning):   {asserted_pre}")
    print(f"HighRiskSystem in reasoned graph (post-reason):  {entailed_post}")

    # Evidence checks
    primary_path = run_sparql_ask_inline(reasoned, ASK_PRIMARY_PATH)
    legacy_path = run_sparql_ask_inline(reasoned, ASK_LEGACY_PATH)

    sub("EVIDENCE PATH CHECKS")
    print(f"PRIMARY (RO_0000091 has_disposition): {primary_path}")
    print(f"LEGACY  (RO_0000053 bearer_of):       {legacy_path}")
    print("Note: LEGACY is kept only to detect older data/axioms. This pipeline is RO_0000091-aligned.")

    # If we have the primary path, print concrete bindings so the user can see actual nodes.
    bindings = get_primary_bindings(reasoned)
    if bindings:
        sub("CONCRETE BINDINGS (EXAMPLE NODES)")
        for i, (comp, disp) in enumerate(bindings, 1):
            print(f"{i}) component = {comp}")
            print(f"   disposition/capability = {disp}")

    sub("WHY THIS ENTAILS HighRiskSystem")
    print("Bridge axiom pattern (in ARCO_core.ttl) is effectively:")
    print("  System AND (has_part SOME (Component AND (has_disposition SOME AnnexIIITriggeringCapability)))")
    print("")
    print("Data + reasoning satisfy that pattern, so:")
    print("  Sentinel_ID_System rdf:type HighRiskSystem")
    if not asserted_pre and entailed_post:
        print("  (and it appears only after reasoning -> inferred, not asserted)")

    # Hard enforcement: entailment must have at least one evidence path
    if entailed_post and not (primary_path or legacy_path):
        sub("FAIL")
        print("Entailment is True, but no supporting path was detected.")
        print("That usually indicates predicate mismatch or missing component facts.")
        return False

    if entailed_post:
        sub("SUCCESS")
        print("HighRiskSystem classification is present AND justified by an explicit structural path.")
        return True

    sub("FAIL")
    print("HighRiskSystem was not inferred.")
    print("Common causes:")
    print("  - owlrl not installed (no reasoning step)")
    print("  - bridge axiom uses a different predicate than the instances")
    print("  - missing has_part/component facts or missing AnnexIIITriggeringCapability typing")
    return False


# ---------------------------
# main
# ---------------------------

def main() -> None:
    hr("ARCO COMPLIANCE VERIFICATION PIPELINE (OPERATOR VIEW)")

    sub("LOAD")
    print("Loading: core ontology + governance extension + instance data")
    g_source = load_union_graph(CORE, GOV, INSTANCES)
    print(f"Triples loaded (asserted): {len(g_source)}")

    # clone -> reason over the copy so we can compare pre vs post
    g = clone_graph(g_source)

    g, initial_count, inferred_added = run_reasoning(g)

    shacl_ok = run_shacl(g)

    sub("AUDIT QUERIES (SPARQL ASK)")
    print("Traceability check...")
    traceability_ok = run_sparql_ask_from_file(g, TRACEABILITY_QUERY)
    print(f"Traceability: {traceability_ok}")

    latent_ok = None
    if LATENT_RISK_QUERY.exists():
        print("\nLatent risk detection (hardware path)...")
        latent_ok = run_sparql_ask_from_file(g, LATENT_RISK_QUERY)
        print(f"Latent risk detected: {latent_ok}")

    inference_ok = verify_high_risk_inference(g, g_source)

    hr("SUMMARY")
    print(f"SHACL:         {'PASS' if shacl_ok else 'FAIL'}")
    print(f"Traceability:  {'PASS' if traceability_ok else 'FAIL'}")
    if latent_ok is not None:
        print(f"Latent risk:   {'PASS' if latent_ok else 'FAIL'}")
    print(f"Entailment:    {'PASS' if inference_ok else 'FAIL'}")
    print(f"Entailed triples added: +{inferred_added}")

    all_pass = shacl_ok and traceability_ok and inference_ok
    if latent_ok is not None:
        all_pass = all_pass and latent_ok

    print("\nALL CHECKS PASSED" if all_pass else "\nSOME CHECKS FAILED")


if __name__ == "__main__":
    main()
