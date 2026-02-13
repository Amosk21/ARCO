from pathlib import Path
from rdflib import Graph
from owlrl import DeductiveClosure, OWLRL_Semantics


def ask(graph: Graph, query: str) -> bool:
    result = graph.query(query)
    if isinstance(result, bool):
        return bool(result)
    rows = list(result)
    return bool(rows[0]) if rows else False


root = Path(__file__).resolve().parents[2]
ontology = root / "03_TECHNICAL_CORE" / "ontology"

files = [
    ontology / "ARCO_core.ttl",
    ontology / "ARCO_governance_extension.ttl",
    ontology / "ARCO_instances_sentinel.ttl",
    ontology / "ARCO_instances_claude3.ttl",
]

g = Graph()
for file_path in files:
    g.parse(file_path.as_posix(), format="turtle")

DeductiveClosure(OWLRL_Semantics).expand(g)

queries = {
    "sentinel_high_risk": """PREFIX : <https://arco.ai/ontology/core#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> ASK { :Sentinel_ID_System rdf:type :HighRiskSystem . }""",
    "sentinel_annex_iii_1a": """PREFIX : <https://arco.ai/ontology/core#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> ASK { :Sentinel_ID_System rdf:type :AnnexIII1aApplicableSystem . }""",
    "claude_high_risk": """PREFIX : <https://arco.ai/ontology/core#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> ASK { :Claude3_System rdf:type :HighRiskSystem . }""",
    "claude_annex_iii_1a": """PREFIX : <https://arco.ai/ontology/core#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> ASK { :Claude3_System rdf:type :AnnexIII1aApplicableSystem . }""",
    "claude_refusal_doc": """PREFIX : <https://arco.ai/ontology/core#> PREFIX iao: <http://purl.obolibrary.org/obo/IAO_> ASK { :Claude3_RefusalBehaviorReport a :AssessmentDocumentation ; iao:0000136 :Claude3_System ; iao:0000136 :RemoteBiometricIdentificationProcess . }""",
}

for name, query in queries.items():
    print(f"{name}: {ask(g, query)}")
