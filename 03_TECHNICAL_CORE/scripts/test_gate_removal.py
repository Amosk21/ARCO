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
CCO = Namespace("http://www.ontologyrepository.com/CommonCoreOntologies/")

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
    # Content-based gate failures (Gap A regression tests):
    # Gate 2 must require cco:prescribes the regulated process, not just existence of IUS.
    "gate2_prescribes_removed": (
        ARCO["Sentinel_IntendedUse_001"],
        CCO["prescribes"],                   # cco:prescribes
        ARCO["RemoteBiometricIdentificationProcess"],
    ),
    # Gate 3 must require iao:is_about NaturalPersonRole, not just existence of USS.
    "gate3_missing_role": (
        ARCO["Sentinel_UseScenario_001"],
        IAO["0000136"],                      # is_about
        ARCO["NaturalPersonRole"],
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
    "gate2_prescribes_removed": {
        "AnnexIII1aApplicableSystem": False,  # prescribes removed -> Gate 2 fails
        "HighRiskSystem": True,               # capability unchanged
    },
    "gate3_missing_role": {
        "AnnexIII1aApplicableSystem": False,  # NaturalPersonRole removed -> Gate 3 fails
        "HighRiskSystem": True,               # capability unchanged
    },
}

# Mutation tests: remove one triple and add a replacement (wrong value).
# These verify that wrong content, not just absence, also breaks the gate.
GATE_MUTATIONS = {
    "gate2_wrong_process_type": {
        "remove": (
            ARCO["Sentinel_IntendedUse_001"],
            CCO["prescribes"],
            ARCO["RemoteBiometricIdentificationProcess"],
        ),
        "add": (
            ARCO["Sentinel_IntendedUse_001"],
            CCO["prescribes"],
            ARCO["SomeOtherProcess"],          # wrong process type
        ),
        "expected": {
            "AnnexIII1aApplicableSystem": False,  # Gate 2 fails: wrong process
            "HighRiskSystem": True,               # capability unchanged
        },
    },
    "gate3_wrong_role_type": {
        "remove": (
            ARCO["Sentinel_UseScenario_001"],
            IAO["0000136"],
            ARCO["NaturalPersonRole"],
        ),
        "add": (
            ARCO["Sentinel_UseScenario_001"],
            IAO["0000136"],
            ARCO["SomeOtherRole"],              # wrong role
        ),
        "expected": {
            "AnnexIII1aApplicableSystem": False,  # Gate 3 fails: wrong role
            "HighRiskSystem": True,               # capability unchanged
        },
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


def run_mutation_test(gate_name: str, mutation: dict) -> dict:
    """Remove one triple, add a replacement with wrong content, reason, check entailments."""
    g = load_graph()
    remove_triple = mutation["remove"]
    add_triple = mutation["add"]

    s, p, o = remove_triple
    if (s, p, o) not in g:
        return {"gate": gate_name, "error": f"Triple to remove not found: ({s}, {p}, {o})"}

    g.remove((s, p, o))
    g.add(add_triple)
    reason(g)

    system = ARCO["Sentinel_ID_System"]
    return {
        "gate": gate_name,
        "mutated": f"replaced <{o}> with <{add_triple[2]}>",
        "AnnexIII1aApplicableSystem": check_type(g, system, ARCO["AnnexIII1aApplicableSystem"]),
        "HighRiskSystem": check_type(g, system, ARCO["HighRiskSystem"]),
    }


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

    # Mutation tests: wrong content (not just absence) also breaks the gate
    print("\n--- CONTENT-MUTATION TESTS (Gap A regression) ---")
    for gate_name, mutation in GATE_MUTATIONS.items():
        print(f"\n--- {gate_name.upper()} ---")
        result = run_mutation_test(gate_name, mutation)

        if "error" in result:
            print(f"  ERROR: {result['error']}")
            all_pass = False
            continue

        print(f"  Mutation: {result['mutated']}")
        expected = mutation["expected"]
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
        print("Wrong content (not just absence) also breaks the gate.")
    else:
        print("SOME GATE-REMOVAL TESTS FAILED")
        sys.exit(1)
    print("=" * 72)


if __name__ == "__main__":
    main()
