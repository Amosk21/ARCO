from __future__ import annotations

from pathlib import Path
from rdflib import BNode, Graph, URIRef
from rdflib.namespace import OWL, RDF
from owlrl import DeductiveClosure, OWLRL_Semantics


REPO_ROOT = Path(__file__).resolve().parents[2]
ONTOLOGY_DIR = REPO_ROOT / "03_TECHNICAL_CORE" / "ontology"

FILES = [
    ONTOLOGY_DIR / "ARCO_core.ttl",
    ONTOLOGY_DIR / "ARCO_governance_extension.ttl",
    ONTOLOGY_DIR / "ARCO_instances_sentinel.ttl",
    ONTOLOGY_DIR / "ARCO_instances_claude3.ttl",
]

ARCO_NS = "https://arco.ai/ontology/core#"

ALLOWED_RELATIONS = {
    URIRef("http://purl.obolibrary.org/obo/RO_0000091"),
    URIRef("http://purl.obolibrary.org/obo/RO_0000057"),
    URIRef("http://www.ontologyrepository.com/CommonCoreOntologies/prescribes"),
    URIRef("http://www.ontologyrepository.com/CommonCoreOntologies/has_output"),
    URIRef("http://purl.obolibrary.org/obo/IAO_0000136"),
    URIRef("http://purl.obolibrary.org/obo/BFO_0000051"),
}


def short(term: URIRef | BNode) -> str:
    value = str(term)
    if "#" in value:
        return value.split("#")[-1]
    return value.rsplit("/", 1)[-1]


def load_graph() -> Graph:
    graph = Graph()
    for file_path in FILES:
        graph.parse(file_path.as_posix(), format="turtle")
    return graph


def clone_graph(graph: Graph) -> Graph:
    copy_graph = Graph()
    for triple in graph:
        copy_graph.add(triple)
    return copy_graph


def is_named_arco_term(term: URIRef | BNode) -> bool:
    if isinstance(term, BNode):
        return False
    return str(term).startswith(ARCO_NS)


def relation_first_graph_triples(graph: Graph) -> list[tuple[URIRef, URIRef, URIRef]]:
    filtered: list[tuple[URIRef, URIRef, URIRef]] = []

    for subject, predicate, obj in graph:
        if predicate in {RDF.type, OWL.sameAs}:
            continue
        if predicate not in ALLOWED_RELATIONS:
            continue
        if not is_named_arco_term(subject):
            continue
        if not is_named_arco_term(obj):
            continue
        filtered.append((subject, predicate, obj))

    return sorted(filtered, key=lambda row: (short(row[0]), short(row[1]), short(row[2])))


def for_system(triples: list[tuple[URIRef, URIRef, URIRef]], marker: str) -> list[tuple[URIRef, URIRef, URIRef]]:
    return [
        triple
        for triple in triples
        if marker in short(triple[0]) or marker in short(triple[2])
    ]


def ask(graph: Graph, query: str) -> bool:
    result = graph.query(query)
    if isinstance(result, bool):
        return result
    rows = list(result)
    return bool(rows[0]) if rows else False


def status(triple: tuple[URIRef, URIRef, URIRef], asserted_set: set[tuple[URIRef, URIRef, URIRef]]) -> str:
    return "asserted" if triple in asserted_set else "entailed"


def print_group(
    title: str,
    triples: list[tuple[URIRef, URIRef, URIRef]],
    asserted_set: set[tuple[URIRef, URIRef, URIRef]],
) -> None:
    print(f"\n{title}: {len(triples)}")
    if not triples:
        print("  (none)")
        return
    for subject, predicate, obj in triples:
        print(
            f"  - [{status((subject, predicate, obj), asserted_set)}] "
            f"{short(subject)} --{short(predicate)}--> {short(obj)}"
        )


def proof_path_for_system(graph: Graph, system_local: str) -> list[tuple[URIRef, URIRef, URIRef]]:
    query = f"""
PREFIX : <https://arco.ai/ontology/core#>
PREFIX bfo: <http://purl.obolibrary.org/obo/BFO_>
PREFIX ro: <http://purl.obolibrary.org/obo/RO_>
PREFIX iao: <http://purl.obolibrary.org/obo/IAO_>
PREFIX cco: <http://www.ontologyrepository.com/CommonCoreOntologies/>
SELECT DISTINCT ?s ?p ?o WHERE {{
  VALUES ?system {{ :{system_local} }}
  VALUES ?p {{ bfo:0000051 ro:0000091 ro:0000057 iao:0000136 cco:prescribes cco:has_output }}
  {{ ?s ?p ?o . FILTER(?s = ?system) }}
  UNION
  {{ ?s ?p ?o . FILTER(?o = ?system) }}
  UNION
  {{ ?system bfo:0000051 ?component . ?component ?p ?o . BIND(?component AS ?s) }}
  UNION
  {{ ?doc iao:0000136 ?system . ?doc ?p ?o . BIND(?doc AS ?s) }}
  UNION
  {{ ?proc ro:0000057 ?system . ?proc ?p ?o . BIND(?proc AS ?s) }}
}}
"""
    rows = graph.query(query)
    results: list[tuple[URIRef, URIRef, URIRef]] = []
    for row in rows:
        results.append((row.s, row.p, row.o))
    return sorted(results, key=lambda row: (short(row[0]), short(row[1]), short(row[2])))


def main() -> None:
    asserted = load_graph()
    asserted_set = set(asserted)
    reasoned = clone_graph(asserted)
    DeductiveClosure(OWLRL_Semantics).expand(reasoned)

    relation_triples = relation_first_graph_triples(reasoned)
    new_relation_triples = [triple for triple in relation_triples if triple not in asserted_set]
    sentinel_relations = for_system(relation_triples, "Sentinel")
    claude_relations = for_system(relation_triples, "Claude")
    sentinel_path = proof_path_for_system(reasoned, "Sentinel_ID_System")
    claude_path = proof_path_for_system(reasoned, "Claude3_System")

    print("RELATION-FIRST PROOF VIEW")
    print("Excluded: rdf:type, owl:sameAs, blank-node scaffolding")
    print("Allowed predicates: has_part, has_disposition, has_participant, is_about, prescribes, has_output")
    print(f"\nAsserted triples: {len(asserted)}")
    print(f"Reasoned triples: {len(reasoned)}")
    print(f"Entailed triples: {len(set(reasoned) - set(asserted))}")
    print(f"Relation-first triples (full reasoned graph): {len(relation_triples)}")
    print(f"Relation-first triples newly entailed: {len(new_relation_triples)}")

    print_group("Sentinel relation-first triples", sentinel_relations, asserted_set)
    print_group("Claude relation-first triples", claude_relations, asserted_set)
    print_group("Sentinel proof-path neighborhood", sentinel_path, asserted_set)
    print_group("Claude proof-path neighborhood", claude_path, asserted_set)

    sentinel_high_risk = ask(
        reasoned,
        """PREFIX : <https://arco.ai/ontology/core#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> ASK { :Sentinel_ID_System rdf:type :HighRiskSystem . }""",
    )
    sentinel_annex = ask(
        reasoned,
        """PREFIX : <https://arco.ai/ontology/core#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> ASK { :Sentinel_ID_System rdf:type :AnnexIII1aApplicableSystem . }""",
    )
    claude_high_risk = ask(
        reasoned,
        """PREFIX : <https://arco.ai/ontology/core#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> ASK { :Claude3_System rdf:type :HighRiskSystem . }""",
    )
    claude_annex = ask(
        reasoned,
        """PREFIX : <https://arco.ai/ontology/core#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> ASK { :Claude3_System rdf:type :AnnexIII1aApplicableSystem . }""",
    )

    print("\nRegulatory class checks")
    print(f"  - sentinel_high_risk: {sentinel_high_risk}")
    print(f"  - sentinel_annex_iii_1a: {sentinel_annex}")
    print(f"  - claude_high_risk: {claude_high_risk}")
    print(f"  - claude_annex_iii_1a: {claude_annex}")


if __name__ == "__main__":
    main()
