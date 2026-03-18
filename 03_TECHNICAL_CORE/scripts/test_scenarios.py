"""
Multi-scenario regression test for ARCO classification pipeline.

Runs three systems through OWL-RL reasoning and verifies expected outcomes:
  1. Sentinel_ID_System     — HighRisk YES, 1(a) YES, 5(b) NO   (biometric identification)
  2. CreditScorer_001       — HighRisk YES, 1(a) NO,  5(b) YES  (creditworthiness evaluation)
  3. VerificationKiosk_001  — HighRisk NO,  1(a) NO,  5(b) NO   (verification only — negative case)

This proves:
  - Positive entailment works for two distinct Annex III categories
  - Cross-category isolation: biometric system is NOT creditworthiness, and vice versa
  - Negative case: a system with a non-triggering capability is NOT classified as high-risk
"""

from __future__ import annotations

import sys
from pathlib import Path
from rdflib import Graph, Namespace

try:
    import owlrl
except ImportError:
    print("ERROR: owlrl is required. Install: pip install owlrl")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parents[2]
ONTOLOGY_DIR = REPO_ROOT / "03_TECHNICAL_CORE" / "ontology"

BFO_2020 = ONTOLOGY_DIR / "imports" / "bfo-2020.owl"
CORE = ONTOLOGY_DIR / "ARCO_core.ttl"
GOV = ONTOLOGY_DIR / "ARCO_governance_extension.ttl"

ARCO = Namespace("https://arco.ai/ontology/core#")
RDF_NS = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

# ── Scenario definitions ──────────────────────────────────────────────

SCENARIOS = [
    {
        "name": "Sentinel_ID_System",
        "label": "Sentinel (biometric identification — positive 1a)",
        "instances": ONTOLOGY_DIR / "ARCO_instances_sentinel.ttl",
        "system": ARCO["Sentinel_ID_System"],
        "expected": {
            "HighRiskSystem": True,
            "AnnexIII1aApplicableSystem": True,
            "AnnexIII5bApplicableSystem": False,
        },
    },
    {
        "name": "CreditScorer_001",
        "label": "Credit Scorer (creditworthiness — positive 5b)",
        "instances": ONTOLOGY_DIR / "ARCO_instances_creditscoring.ttl",
        "system": ARCO["CreditScorer_001"],
        "expected": {
            "HighRiskSystem": True,
            "AnnexIII1aApplicableSystem": False,
            "AnnexIII5bApplicableSystem": True,
        },
    },
    {
        "name": "VerificationKiosk_001",
        "label": "Verification Kiosk (1:1 verification — negative case)",
        "instances": ONTOLOGY_DIR / "ARCO_instances_verification.ttl",
        "system": ARCO["VerificationKiosk_001"],
        "expected": {
            "HighRiskSystem": False,
            "AnnexIII1aApplicableSystem": False,
            "AnnexIII5bApplicableSystem": False,
        },
    },
]


def load_and_reason(instance_file: Path) -> Graph:
    g = Graph()
    for p in (BFO_2020, CORE, GOV, instance_file):
        if not p.exists():
            raise FileNotFoundError(f"Missing: {p}")
        fmt = "xml" if p.suffix == ".owl" else "turtle"
        g.parse(p.as_posix(), format=fmt)
    initial = len(g)
    owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(g)
    return g, initial, len(g)


def check_type(g: Graph, individual, cls_name: str) -> bool:
    return (individual, RDF_NS["type"], ARCO[cls_name]) in g


def main() -> None:
    print("=" * 72)
    print("ARCO MULTI-SCENARIO REGRESSION TEST")
    print("=" * 72)

    all_pass = True

    for scenario in SCENARIOS:
        print(f"\n--- {scenario['label'].upper()} ---")
        instance_file = scenario["instances"]
        system = scenario["system"]

        g, initial, final = load_and_reason(instance_file)
        print(f"  Triples: {initial} -> {final} (+{final - initial})")

        for cls_name, expected in scenario["expected"].items():
            actual = check_type(g, system, cls_name)
            ok = actual == expected
            status = "OK" if ok else "FAIL"
            print(f"  {cls_name}: {actual} (expected {expected}) [{status}]")
            if not ok:
                all_pass = False

    print()
    print("=" * 72)
    if all_pass:
        print("ALL SCENARIO TESTS PASSED")
        print("Positive cases entail correctly. Negative case does not entail.")
        print("Cross-category isolation verified.")
    else:
        print("SOME SCENARIO TESTS FAILED")
    print("=" * 72)

    if not all_pass:
        sys.exit(1)


if __name__ == "__main__":
    main()
