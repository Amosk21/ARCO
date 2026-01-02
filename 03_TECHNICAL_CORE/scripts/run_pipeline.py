from pathlib import Path

from rdflib import Graph
from pyshacl import validate

# Intended usage (from repo root):
#   python 03_TECHNICAL_CORE/scripts/run_pipeline.py
#
# Note: Because paths are resolved from __file__, it will also work if run elsewhere,
# as long as the repo structure is intact.

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

# Default SPARQL check (swap filename here if you want a different query)
SPARQL_QUERY = REASONING_DIR / "check_assessment_traceability.sparql"


def load_union_graph(*paths: Path) -> Graph:
    g = Graph()
    for p in paths:
        if not p.exists():
            raise FileNotFoundError(f"Missing file: {p}")
        g.parse(p.as_posix(), format="turtle")
    return g


def run_shacl(data_graph: Graph) -> None:
    if not SHAPES.exists():
        raise FileNotFoundError(f"Missing SHACL shapes file: {SHAPES}")

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
    print("SHACL conforms:", conforms)
    print(report_text)


def run_sparql_ask(data_graph: Graph) -> None:
    if not SPARQL_QUERY.exists():
        raise FileNotFoundError(f"Missing SPARQL query file: {SPARQL_QUERY}")

    q = SPARQL_QUERY.read_text(encoding="utf-8").strip()

    try:
        result = data_graph.query(q)

        # RDFLib usually returns a bool for ASK, but handle odd shapes defensively.
        if isinstance(result, bool):
            ask_value = result
        else:
            rows = list(result)
            ask_value = bool(rows[0]) if rows else False

    except Exception as e:
        raise RuntimeError(f"SPARQL query failed: {SPARQL_QUERY}\n{e}")

    print("SPARQL ASK result:", ask_value)


def main() -> None:
    g = load_union_graph(CORE, GOV, INSTANCES)
    print("Loaded triples:", len(g))

    run_sparql_ask(g)
    run_shacl(g)


if __name__ == "__main__":
    main()
