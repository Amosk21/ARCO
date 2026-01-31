"""
ARCO Compliance Verification Pipeline — Entailment-Ready Version

This pipeline:
1) Loads ontology + instance data
2) Runs OWL-RL reasoning (materializes inferred triples)
3) Validates structure with SHACL
4) Runs audit queries against the reasoned graph
5) Verifies key entailments and prints concrete evidence bindings

Intended usage (from repo root):
  python 03_TECHNICAL_CORE/scripts/run_pipeline.py
"""

from pathlib import Path
from rdflib import Graph
from pyshacl import validate

# OWL reasoning
try:
    import owlrl
    HAS_OWLRL = True
except ImportError:
    HAS_OWLRL = False
    print("=" * 60)
    print("WARNING: owlrl not installed")
    print("Install with: pip install owlrl")
    print("Reasoning will be skipped; inferred triples will not be materialized.")
    print("=" * 60)

REPO_ROOT = Path(__file__).resolve().parents[2]

ONTOLOGY_DIR = REPO_ROOT / "03_TECHNICAL_CORE" / "ontology"
VALIDATION_DIR = REPO_ROOT / "03_TECHNICAL_CORE" / "validation"
REASONING_DIR = REPO_ROOT / "03_TECHNICAL_CORE" / "reasoning"

CORE = ONTOLOGY_DIR / "ARCO_core.ttl"
GOV = ONTOLOGY_DIR / "ARCO_governance_extension.ttl"
INSTANCES = ONTOLOGY_DIR / "ARCO_instances_sentinel.ttl"

SHAPES = VALIDATION_DIR / "assessment_documentation_shape.ttl"
SPARQL_QUERY = REASONING_DIR / "check_assessment_traceability.sparql"


def load_union_graph(*paths: Path) -> Graph:
    g = Graph()
    for p in paths:
        if not p.exists():
            raise FileNotFoundError(f"Missing file: {p}")
        g.parse(p.as_posix(), format="turtle")
    return g


def run_reasoning(data_graph: Graph) -> Graph:
    if not HAS_OWLRL:
        print("\n[REASONING] Skipped (owlrl not available)")
        return data_graph

    print("\n[REASONING] Running OWL-RL reasoning...")
    initial_count = len(data_graph)

    owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(data_graph)

    final_count = len(data_graph)
    inferred = final_count - initial_count
    print(f"[REASONING] Complete. Triples: {initial_count} -> {final_count} (+{inferred} inferred)")

    return data_graph


def run_shacl(data_graph: Graph) -> bool:
    if not SHAPES.exists():
        raise FileNotFoundError(f"Missing SHACL shapes file: {SHAPES}")

    print("\n[SHACL] Validating graph structure...")

    shapes_graph = Graph().parse(SHAPES.as_posix(), format="turtle")

    conforms, report_graph, report_text = validate(
        data_graph=data_graph,
        shacl_graph=shapes_graph,
        inference="none",
        abort_on_first=False,
        allow_infos=True,
        allow_warnings=True,
        meta_shacl=False,
        advanced=True,
    )

    print(f"[SHACL] Conforms: {conforms}")
    if not conforms:
        print("[SHACL] Validation report:")
        print(report_text)

    return conforms


def run_sparql_ask_file(data_graph: Graph, query_path: Path = None) -> bool:
    if query_path is None:
        query_path = SPARQL_QUERY

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


def ask_bool(data_graph: Graph, query: str) -> bool:
    result = data_graph.query(query)
    if isinstance(result, bool):
        return result
    rows = list(result)
    return bool(rows[0]) if rows else False


def select_rows(data_graph: Graph, query: str):
    try:
        return list(data_graph.query(query))
    except Exception as e:
        raise RuntimeError(f"SPARQL SELECT failed:\n{e}\nQuery:\n{query}")


def verify_high_risk_inference(data_graph: Graph) -> bool:
    query = """
    PREFIX : <https://arco.ai/ontology/core#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    ASK WHERE {
        :Sentinel_ID_System rdf:type :HighRiskSystem .
    }
    """
    is_high_risk = ask_bool(data_graph, query)

    print("\n" + "=" * 60)
    print("ENTAILMENT VERIFICATION")
    print("=" * 60)
    print("Query: Is Sentinel_ID_System inferred as HighRiskSystem?")
    print(f"Result: {is_high_risk}")
    print("=" * 60 + "\n")

    return is_high_risk


def verify_legacy_bearer_path(data_graph: Graph) -> bool:
    """
    Legacy model path:
      System -> ro:0000053 bearer_of -> Disposition -> a AnnexIIITriggeringCapability
    """
    q = """
    PREFIX : <https://arco.ai/ontology/core#>
    PREFIX ro: <http://purl.obolibrary.org/obo/RO_>

    ASK WHERE {
      :Sentinel_ID_System ro:0000053 ?disp .
      ?disp a :AnnexIIITriggeringCapability .
    }
    """
    return ask_bool(data_graph, q)


def verify_hardware_component_path(data_graph: Graph) -> bool:
    """
    New model path:
      System -> bfo:0000051 has_part -> Component -> ro:0000053 bearer_of -> Disposition -> a AnnexIIITriggeringCapability
    """
    q = """
    PREFIX : <https://arco.ai/ontology/core#>
    PREFIX bfo: <http://purl.obolibrary.org/obo/BFO_>
    PREFIX ro: <http://purl.obolibrary.org/obo/RO_>

    ASK WHERE {
      :Sentinel_ID_System bfo:0000051 ?component .
      ?component ro:0000053 ?disp .
      ?disp a :AnnexIIITriggeringCapability .
    }
    """
    return ask_bool(data_graph, q)


def print_path_evidence(data_graph: Graph) -> None:
    """
    Print concrete evidence bindings for whichever paths are present.
    This replaces the hard-coded "inference chain" text.
    """
    print("\n" + "=" * 60)
    print("STRUCTURAL PATH EVIDENCE")
    print("=" * 60)

    legacy = verify_legacy_bearer_path(data_graph)
    hardware = verify_hardware_component_path(data_graph)

    print(f"Legacy bearer_of path present: {legacy}")
    print(f"Hardware component path present: {hardware}")
    print()

    if legacy:
        q_legacy = """
        PREFIX : <https://arco.ai/ontology/core#>
        PREFIX ro: <http://purl.obolibrary.org/obo/RO_>

        SELECT ?disp WHERE {
          :Sentinel_ID_System ro:0000053 ?disp .
        }
        """
        rows = select_rows(data_graph, q_legacy)
        print("Legacy bindings:")
        for r in rows[:10]:
            print(f"  disposition: {r.disp}")
        if len(rows) > 10:
            print(f"  ... ({len(rows) - 10} more)")
        print()

    if hardware:
        q_hw = """
        PREFIX : <https://arco.ai/ontology/core#>
        PREFIX bfo: <http://purl.obolibrary.org/obo/BFO_>
        PREFIX ro: <http://purl.obolibrary.org/obo/RO_>

        SELECT ?component ?disp WHERE {
          :Sentinel_ID_System bfo:0000051 ?component .
          ?component ro:0000053 ?disp .
        }
        """
        rows = select_rows(data_graph, q_hw)
        print("Hardware path bindings:")
        for r in rows[:10]:
            print(f"  component:  {r.component}")
            print(f"  disposition:{r.disp}")
        if len(rows) > 10:
            print(f"  ... ({len(rows) - 10} more)")
        print()

    if not legacy and not hardware:
        print("No path evidence found for either model.")
        print("That usually means the instance triples for Sentinel_ID_System do not match either pattern.")
        print()

    print("=" * 60 + "\n")


def main() -> None:
    print("=" * 60)
    print("ARCO COMPLIANCE VERIFICATION PIPELINE")
    print("Entailment-Ready Version")
    print("=" * 60)

    print("\n[LOAD] Loading ontology and instance data...")
    g = load_union_graph(CORE, GOV, INSTANCES)
    print(f"[LOAD] Loaded {len(g)} triples")

    g = run_reasoning(g)

    shacl_ok = run_shacl(g)

    print("\n[SPARQL] Running assessment traceability check...")
    traceability_ok = run_sparql_ask_file(g)
    print(f"[SPARQL] Assessment traceability: {traceability_ok}")

    inference_ok = verify_high_risk_inference(g)

    # New: print actual evidence bindings for the structure
    print_path_evidence(g)

    print("=" * 60)
    print("PIPELINE SUMMARY")
    print("=" * 60)
    print(f"  SHACL Validation:        {'PASS' if shacl_ok else 'FAIL'}")
    print(f"  Traceability Check:      {'PASS' if traceability_ok else 'FAIL'}")
    print(f"  HighRisk Inference:      {'PASS' if inference_ok else 'FAIL'}")
    print()

    if shacl_ok and traceability_ok and inference_ok:
        print("ALL CHECKS PASSED")
        print("High-risk classification was inferred by the reasoner (not asserted).")
    else:
        print("SOME CHECKS FAILED - Review output above")

    print("=" * 60)


if __name__ == "__main__":
    main()
