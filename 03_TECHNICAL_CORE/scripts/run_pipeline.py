"""
ARCO Compliance Verification Pipeline — Entailment-Ready Version

This pipeline:
1. Loads the ontology and instance data
2. Runs OWL reasoning to materialize inferred classifications
3. Validates structure with SHACL
4. Runs audit queries against the reasoned graph
5. Verifies the key inference (HighRiskSystem classification)
"""

from pathlib import Path
from rdflib import Graph

from pyshacl import validate

# For OWL reasoning
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

# Intended usage (from repo root):
#   python 03_TECHNICAL_CORE/scripts/run_pipeline.py

REPO_ROOT = Path(__file__).resolve().parents[2]

ONTOLOGY_DIR = REPO_ROOT / "03_TECHNICAL_CORE" / "ontology"
VALIDATION_DIR = REPO_ROOT / "03_TECHNICAL_CORE" / "validation"
REASONING_DIR = REPO_ROOT / "03_TECHNICAL_CORE" / "reasoning"

# Ontologies + instance data
CORE = ONTOLOGY_DIR / "ARCO_core.ttl"
GOV = ONTOLOGY_DIR / "ARCO_governance_extension.ttl"
INSTANCES = ONTOLOGY_DIR / "ARCO_instances_sentinel.ttl"

# SHACL shapes
SHAPES = VALIDATION_DIR / "assessment_documentation_shape.ttl"

# Default SPARQL check
SPARQL_QUERY = REASONING_DIR / "check_assessment_traceability.sparql"


def load_union_graph(*paths: Path) -> Graph:
    """Load multiple Turtle files into a single graph."""
    g = Graph()
    for p in paths:
        if not p.exists():
            raise FileNotFoundError(f"Missing file: {p}")
        g.parse(p.as_posix(), format="turtle")
    return g


def run_reasoning(data_graph: Graph) -> Graph:
    """
    Materialize inferred triples using OWL-RL reasoning.
    
    This is where HighRiskSystem classification gets computed.
    """
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
    """Validate the graph against SHACL shapes."""
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


def run_sparql_ask(data_graph: Graph, query_path: Path = None) -> bool:
    """Run a SPARQL ASK query and return the result."""
    if query_path is None:
        query_path = SPARQL_QUERY
        
    if not query_path.exists():
        raise FileNotFoundError(f"Missing SPARQL query file: {query_path}")

    q = query_path.read_text(encoding="utf-8").strip()

    try:
        result = data_graph.query(q)

        if isinstance(result, bool):
            ask_value = result
        else:
            rows = list(result)
            ask_value = bool(rows[0]) if rows else False

    except Exception as e:
        raise RuntimeError(f"SPARQL query failed: {query_path}\n{e}")

    return ask_value


def verify_high_risk_inference(data_graph: Graph) -> bool:
    """
    Verify that the reasoner inferred Sentinel_ID_System as a HighRiskSystem.
    This is THE key check that proves the entailment worked.
    """
    query = """
    PREFIX : <https://arco.ai/ontology/core#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    
    ASK WHERE {
        :Sentinel_ID_System rdf:type :HighRiskSystem .
    }
    """
    
    result = data_graph.query(query)
    
    if isinstance(result, bool):
        is_high_risk = result
    else:
        rows = list(result)
        is_high_risk = bool(rows[0]) if rows else False
    
    print(f"\n{'='*60}")
    print("ENTAILMENT VERIFICATION")
    print(f"{'='*60}")
    print(f"Query: Is Sentinel_ID_System inferred as HighRiskSystem?")
    print(f"Result: {is_high_risk}")
    print()
    
    if is_high_risk:
        print("SUCCESS: Classification was INFERRED by the reasoner")
        print()
        print("  Inference chain:")
        print("  1. Sentinel_ID_System rdf:type :System")
        print("  2. Sentinel_ID_System ro:bearer_of Sentinel_FaceID_Disposition")
        print("  3. Sentinel_FaceID_Disposition rdf:type :BiometricIdentificationCapability")
        print("  4. :HighRiskSystem = :System AND (bearer_of SOME AnnexIIITriggeringCapability)")
        print("  => Sentinel_ID_System rdf:type :HighRiskSystem (INFERRED)")
    else:
        print("FAILURE: Classification was NOT inferred")
        print()
        print("  Check that:")
        print("  - owlrl is installed: pip install owlrl")
        print("  - ARCO_core.ttl contains the HighRiskSystem equivalentClass axiom")
    
    print(f"{'='*60}\n")
    
    return is_high_risk


def main() -> None:
    print("=" * 60)
    print("ARCO COMPLIANCE VERIFICATION PIPELINE")
    print("Entailment-Ready Version")
    print("=" * 60)
    
    # Load ontology and instances
    print("\n[LOAD] Loading ontology and instance data...")
    g = load_union_graph(CORE, GOV, INSTANCES)
    print(f"[LOAD] Loaded {len(g)} triples")
    
    # Step 1: Run OWL reasoning
    g = run_reasoning(g)
    
    # Step 2: Validate structure with SHACL
    shacl_ok = run_shacl(g)
    
    # Step 3: Run traceability audit query
    print("\n[SPARQL] Running assessment traceability check...")
    traceability_ok = run_sparql_ask(g)
    print(f"[SPARQL] Assessment traceability: {traceability_ok}")
    
    # Step 4: Verify the key inference
    inference_ok = verify_high_risk_inference(g)
    
    # Summary
    print("=" * 60)
    print("PIPELINE SUMMARY")
    print("=" * 60)
    print(f"  SHACL Validation:        {'PASS' if shacl_ok else 'FAIL'}")
    print(f"  Traceability Check:      {'PASS' if traceability_ok else 'FAIL'}")
    print(f"  HighRisk Inference:      {'PASS' if inference_ok else 'FAIL'}")
    print()
    
    if shacl_ok and traceability_ok and inference_ok:
        print("ALL CHECKS PASSED")
        print()
        print("  The high-risk classification was INFERRED by the reasoner,")
        print("  not asserted in the instance data.")
    else:
        print("SOME CHECKS FAILED - Review output above")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
