"""
Gate-removal regression test for the three-gate Annex III classification.

For each modeled Annex III category (1(a) and 5(b)), removes each gate's key
triple independently, re-reasons, and confirms the category's applicable-system
class disappears. Also verifies that HighRiskSystem (capability-only axiom) is
unaffected by gates 2 and 3.

Symmetric coverage across categories verifies that the three-gate pattern
generalizes; no gate in either category is decorative.
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

ARCO = Namespace("https://arco.ai/ontology/core#")
RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
IAO = Namespace("http://purl.obolibrary.org/obo/IAO_")
RO = Namespace("http://purl.obolibrary.org/obo/RO_")
CCO = Namespace("http://www.ontologyrepository.com/CommonCoreOntologies/")

# ---------------------------------------------------------------------------
# Annex III 1(a) — Sentinel fixture
# ---------------------------------------------------------------------------
CATEGORY_1A = {
    "label": "Annex III 1(a) — Sentinel (Biometric Identification)",
    "instances": ONTOLOGY_DIR / "ARCO_instances_sentinel.ttl",
    "system": ARCO["Sentinel_ID_System"],
    "applicable_class": ARCO["AnnexIII1aApplicableSystem"],
    "gate_removals": {
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
        # Content-based gate failures
        "gate2_prescribes_removed": (
            ARCO["Sentinel_IntendedUse_001"],
            CCO["prescribes"],
            ARCO["Sentinel_RBIP_Process"],       # the typed process token
        ),
        "gate3_missing_role": (
            ARCO["Sentinel_UseScenario_001"],
            CCO["designates"],
            ARCO["NaturalPersonRole"],
        ),
    },
    "expected": {
        "gate1_capability": {
            "applicable": False,
            "HighRiskSystem": False,    # capability-only axiom also breaks
        },
        "gate2_intended_use": {
            "applicable": False,
            "HighRiskSystem": True,     # HighRiskSystem only needs capability
        },
        "gate3_use_scenario": {
            "applicable": False,
            "HighRiskSystem": True,
        },
        "gate2_prescribes_removed": {
            "applicable": False,
            "HighRiskSystem": True,
        },
        "gate3_missing_role": {
            "applicable": False,
            "HighRiskSystem": True,
        },
    },
    "gate_mutations": {
        "gate2_wrong_process_type": {
            "remove": (
                ARCO["Sentinel_IntendedUse_001"],
                CCO["prescribes"],
                ARCO["Sentinel_RBIP_Process"],
            ),
            "add": (
                ARCO["Sentinel_IntendedUse_001"],
                CCO["prescribes"],
                ARCO["SomeOtherProcess"],
            ),
            "expected": {"applicable": False, "HighRiskSystem": True},
        },
        "gate3_wrong_designation_target": {
            "remove": (
                ARCO["Sentinel_UseScenario_001"],
                CCO["designates"],
                ARCO["NaturalPersonRole"],
            ),
            "add": (
                ARCO["Sentinel_UseScenario_001"],
                CCO["designates"],
                ARCO["SomeOtherRole"],
            ),
            "expected": {"applicable": False, "HighRiskSystem": True},
        },
    },
}

# ---------------------------------------------------------------------------
# Annex III 5(b) — CreditScorer fixture
# Symmetric coverage with the 1(a) block above. Each gate-removal verifies a
# gate that is independently necessary for AnnexIII5bApplicableSystem.
# ---------------------------------------------------------------------------
CATEGORY_5B = {
    "label": "Annex III 5(b) — CreditScorer (Creditworthiness Evaluation)",
    "instances": ONTOLOGY_DIR / "ARCO_instances_creditscoring.ttl",
    "system": ARCO["CreditScorer_001"],
    "applicable_class": ARCO["AnnexIII5bApplicableSystem"],
    "gate_removals": {
        "gate1_capability": (
            ARCO["CreditScorer_Processing_Module"],
            RO["0000091"],                       # has_disposition
            ARCO["CreditScorer_Eval_Disposition"],
        ),
        "gate2_intended_use": (
            ARCO["CreditScorer_IntendedUse_001"],
            IAO["0000136"],                      # is_about
            ARCO["CreditScorer_001"],
        ),
        "gate3_use_scenario": (
            ARCO["CreditScorer_UseScenario_001"],
            IAO["0000136"],                      # is_about
            ARCO["CreditScorer_001"],
        ),
        # Content-based gate failures
        "gate2_prescribes_removed": (
            ARCO["CreditScorer_IntendedUse_001"],
            CCO["prescribes"],
            ARCO["CreditScorer_EvalProcess_Token"],
        ),
        "gate3_missing_role": (
            ARCO["CreditScorer_UseScenario_001"],
            CCO["designates"],
            ARCO["NaturalPersonRole"],
        ),
    },
    "expected": {
        "gate1_capability": {
            "applicable": False,
            "HighRiskSystem": False,
        },
        "gate2_intended_use": {
            "applicable": False,
            "HighRiskSystem": True,
        },
        "gate3_use_scenario": {
            "applicable": False,
            "HighRiskSystem": True,
        },
        "gate2_prescribes_removed": {
            "applicable": False,
            "HighRiskSystem": True,
        },
        "gate3_missing_role": {
            "applicable": False,
            "HighRiskSystem": True,
        },
    },
    "gate_mutations": {
        "gate2_wrong_process_type": {
            "remove": (
                ARCO["CreditScorer_IntendedUse_001"],
                CCO["prescribes"],
                ARCO["CreditScorer_EvalProcess_Token"],
            ),
            "add": (
                ARCO["CreditScorer_IntendedUse_001"],
                CCO["prescribes"],
                ARCO["SomeOtherProcess"],
            ),
            "expected": {"applicable": False, "HighRiskSystem": True},
        },
        "gate3_wrong_designation_target": {
            "remove": (
                ARCO["CreditScorer_UseScenario_001"],
                CCO["designates"],
                ARCO["NaturalPersonRole"],
            ),
            "add": (
                ARCO["CreditScorer_UseScenario_001"],
                CCO["designates"],
                ARCO["SomeOtherRole"],
            ),
            "expected": {"applicable": False, "HighRiskSystem": True},
        },
    },
}

CATEGORIES = [CATEGORY_1A, CATEGORY_5B]


def load_graph(instances_path: Path) -> Graph:
    g = Graph()
    for p in (CORE, GOV, instances_path):
        if not p.exists():
            raise FileNotFoundError(f"Missing: {p}")
        g.parse(p.as_posix(), format="turtle")
    return g


def reason(g: Graph) -> Graph:
    owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(g)
    return g


def check_type(g: Graph, individual: URIRef, cls: URIRef) -> bool:
    return (individual, RDF["type"], cls) in g


def run_mutation_test(category: dict, gate_name: str, mutation: dict) -> dict:
    """Remove one triple, add a replacement with wrong content, reason, check entailments."""
    g = load_graph(category["instances"])
    remove_triple = mutation["remove"]
    add_triple = mutation["add"]

    s, p, o = remove_triple
    if (s, p, o) not in g:
        return {"gate": gate_name, "error": f"Triple to remove not found: ({s}, {p}, {o})"}

    g.remove((s, p, o))
    g.add(add_triple)
    reason(g)

    system = category["system"]
    return {
        "gate": gate_name,
        "mutated": f"replaced <{o}> with <{add_triple[2]}>",
        "applicable": check_type(g, system, category["applicable_class"]),
        "HighRiskSystem": check_type(g, system, ARCO["HighRiskSystem"]),
    }


def run_test(category: dict, gate_name: str, triple_to_remove: tuple) -> dict:
    """Remove one triple, reason, check entailments."""
    g = load_graph(category["instances"])
    s, p, o = triple_to_remove

    if (s, p, o) not in g:
        return {"gate": gate_name, "error": f"Triple not found: ({s}, {p}, {o})"}

    g.remove((s, p, o))
    reason(g)

    system = category["system"]
    return {
        "gate": gate_name,
        "removed": f"<{s}> <{p}> <{o}>",
        "applicable": check_type(g, system, category["applicable_class"]),
        "HighRiskSystem": check_type(g, system, ARCO["HighRiskSystem"]),
    }


def run_category(category: dict) -> bool:
    """Run baseline + gate-removal + mutation tests for one Annex III category.

    Returns True iff every assertion in this category passes.
    """
    label = category["label"]
    applicable_name = category["applicable_class"].split("#")[-1]

    print("\n" + "=" * 72)
    print(label)
    print("=" * 72)

    # Baseline
    print("\n--- BASELINE (all gates present) ---")
    g_full = load_graph(category["instances"])
    initial = len(g_full)
    reason(g_full)
    system = category["system"]

    applicable_ok = check_type(g_full, system, category["applicable_class"])
    hr_ok = check_type(g_full, system, ARCO["HighRiskSystem"])

    print(f"  Triples: {initial} -> {len(g_full)}")
    print(f"  {applicable_name}: {applicable_ok}")
    print(f"  HighRiskSystem:             {hr_ok}")

    if not applicable_ok or not hr_ok:
        print("\nFAIL: Baseline entailments missing. Cannot test gate removal.")
        return False

    print("  Baseline: OK")

    all_pass = True

    # Gate removal tests
    for gate_name, triple in category["gate_removals"].items():
        print(f"\n--- {gate_name.upper()} ---")
        result = run_test(category, gate_name, triple)

        if "error" in result:
            print(f"  ERROR: {result['error']}")
            all_pass = False
            continue

        expected = category["expected"][gate_name]
        for key, expected_val in expected.items():
            cls_label = applicable_name if key == "applicable" else key
            actual = result[key]
            status = "OK" if actual == expected_val else "FAIL"
            if status == "FAIL":
                all_pass = False
            print(f"  {cls_label}: {actual} (expected {expected_val}) [{status}]")

    # Mutation tests
    print("\n--- CONTENT-MUTATION TESTS ---")
    for gate_name, mutation in category["gate_mutations"].items():
        print(f"\n--- {gate_name.upper()} ---")
        result = run_mutation_test(category, gate_name, mutation)

        if "error" in result:
            print(f"  ERROR: {result['error']}")
            all_pass = False
            continue

        print(f"  Mutation: {result['mutated']}")
        expected = mutation["expected"]
        for key, expected_val in expected.items():
            cls_label = applicable_name if key == "applicable" else key
            actual = result[key]
            status = "OK" if actual == expected_val else "FAIL"
            if status == "FAIL":
                all_pass = False
            print(f"  {cls_label}: {actual} (expected {expected_val}) [{status}]")

    return all_pass


def main() -> None:
    print("=" * 72)
    print("ARCO GATE-REMOVAL REGRESSION TEST")
    print("=" * 72)

    all_pass = True
    for category in CATEGORIES:
        if not run_category(category):
            all_pass = False

    print("\n" + "=" * 72)
    if all_pass:
        print("ALL GATE-REMOVAL TESTS PASSED")
        print("Each gate is independently necessary for AnnexIII1aApplicableSystem")
        print("and AnnexIII5bApplicableSystem. Wrong content (not just absence) also")
        print("breaks the gate. Coverage is symmetric across the two modeled Annex III")
        print("categories.")
    else:
        print("SOME GATE-REMOVAL TESTS FAILED")
        sys.exit(1)
    print("=" * 72)


if __name__ == "__main__":
    main()
