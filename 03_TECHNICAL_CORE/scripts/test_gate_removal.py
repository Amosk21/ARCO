"""
Gate-removal regression test for the three-gate Annex III 1(a) classification.

Removes each gate's key triple independently, re-reasons, and confirms
AnnexIII1aApplicableSystem disappears. Also verifies that HighRiskSystem
(capability-only axiom) is unaffected by gates 2 and 3.
"""

from __future__ import annotations

import sys
from pathlib import Path
from rdflib import Graph, URIRef, Namespace

try:
    import owlrl
except ImportError:
    print("ERROR: owlrl is required. Install: pip install owlrl")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parents[2]
ONTOLOGY_DIR = REPO_ROOT / "03_TECHNICAL_CORE" / "ontology"

CORE = ONTOLOGY_DIR / "ARCO_core.ttl"
GOV = ONTOLOGY_DIR / "ARCO_governance_extension.ttl"
INSTANCES = ONTOLOGY_DIR / "ARCO_instances_sentinel.ttl"

ARCO = Namespace("https://arco.ai/ontology/core#")
RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
IAO = Namespace("http://purl.obolibrary.org/obo/IAO_")
RO = Namespace("http://purl.obolibrary.org/obo/RO_")

# The triple removals that knock out each gate
GATE_REMOVALS = {
    "gate1_capability": (
        ARCO["Sentinel_FaceID_Module"],
        RO["0000091"],                       # has_disposition
        ARCO["Sentinel_FaceID_Disposition"],
    ),
    "gate2_intended_use": (
        ARCO["Sentinel_IntendedUse_001"],
        IAO["0000136"],                      # is_about
        ARCO["Sentinel_ID_System"],
    ),
    "gate3_use_scenario": (
        ARCO["Sentinel_UseScenario_001"],
        IAO["0000136"],                      # is_about
        ARCO["Sentinel_ID_System"],
    ),
}

# Expected entailment results after each gate removal
EXPECTED = {
    "gate1_capability": {
        "AnnexIII1aApplicableSystem": False,
        "HighRiskSystem": False,    # capability-only axiom also breaks
    },
    "gate2_intended_use": {
        "AnnexIII1aApplicableSystem": False,
        "HighRiskSystem": True,     # HighRiskSystem only needs capability
    },
    "gate3_use_scenario": {
        "AnnexIII1aApplicableSystem": False,
        "HighRiskSystem": True,     # HighRiskSystem only needs capability
    },
}


def load_graph() -> Graph:
    g = Graph()
    for p in (CORE, GOV, INSTANCES):
        if not p.exists():
            raise FileNotFoundError(f"Missing: {p}")
        g.parse(p.as_posix(), format="turtle")
    return g


def reason(g: Graph) -> Graph:
    owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(g)
    return g


def check_type(g: Graph, individual: URIRef, cls: URIRef) -> bool:
    return (individual, RDF["type"], cls) in g


def run_test(gate_name: str, triple_to_remove: tuple) -> dict:
    """Remove one triple, reason, check entailments."""
    g = load_graph()
    s, p, o = triple_to_remove

    # Verify the triple exists before removing
    if (s, p, o) not in g:
        return {"gate": gate_name, "error": f"Triple not found: ({s}, {p}, {o})"}

    g.remove((s, p, o))
    reason(g)

    system = ARCO["Sentinel_ID_System"]
    results = {
        "gate": gate_name,
        "removed": f"<{s}> <{p}> <{o}>",
        "AnnexIII1aApplicableSystem": check_type(g, system, ARCO["AnnexIII1aApplicableSystem"]),
        "HighRiskSystem": check_type(g, system, ARCO["HighRiskSystem"]),
    }
    return results


def main() -> None:
    print("=" * 72)
    print("ARCO GATE-REMOVAL REGRESSION TEST")
    print("=" * 72)

    # Baseline: full graph should have both entailments
    print("\n--- BASELINE (all gates present) ---")
    g_full = load_graph()
    initial = len(g_full)
    reason(g_full)
    system = ARCO["Sentinel_ID_System"]

    annex_ok = check_type(g_full, system, ARCO["AnnexIII1aApplicableSystem"])
    hr_ok = check_type(g_full, system, ARCO["HighRiskSystem"])

    print(f"  Triples: {initial} -> {len(g_full)}")
    print(f"  AnnexIII1aApplicableSystem: {annex_ok}")
    print(f"  HighRiskSystem:             {hr_ok}")

    if not annex_ok or not hr_ok:
        print("\nFAIL: Baseline entailments missing. Cannot test gate removal.")
        sys.exit(1)

    print("  Baseline: OK")

    # Gate removal tests
    all_pass = True
    for gate_name, triple in GATE_REMOVALS.items():
        print(f"\n--- {gate_name.upper()} ---")
        result = run_test(gate_name, triple)

        if "error" in result:
            print(f"  ERROR: {result['error']}")
            all_pass = False
            continue

        expected = EXPECTED[gate_name]
        for cls_name, expected_val in expected.items():
            actual = result[cls_name]
            status = "OK" if actual == expected_val else "FAIL"
            if status == "FAIL":
                all_pass = False
            print(f"  {cls_name}: {actual} (expected {expected_val}) [{status}]")

    # Summary
    print("\n" + "=" * 72)
    if all_pass:
        print("ALL GATE-REMOVAL TESTS PASSED")
        print("Each gate is independently necessary for AnnexIII1aApplicableSystem.")
    else:
        print("SOME GATE-REMOVAL TESTS FAILED")
        sys.exit(1)
    print("=" * 72)


if __name__ == "__main__":
    main()
