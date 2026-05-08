"""
Multi-scenario regression test for ARCO classification pipeline.

Runs five systems through OWL-RL reasoning and verifies expected outcomes:
  1. Sentinel_ID_System     — HighRisk YES, 1(a) YES, 5(b) NO   (biometric identification)
  2. CreditScorer_001       — HighRisk YES, 1(a) NO,  5(b) YES  (creditworthiness evaluation)
  3. VerificationKiosk_001  — HighRisk NO,  1(a) NO,  5(b) NO   (verification only — negative case)
  4. DecoySystem_001        — HighRisk YES, 1(a) YES, 5(b) NO   (equivalency decoy — anti-pattern-matching)
  5. GhostSystem_001        — HighRisk YES, 1(a) YES, 5(b) NO   (blank node ghost — anonymous disposition)

Adversarial tests (4-5) prove the pipeline does real OWL reasoning:
  - Test 4: Disposition typed only as :WeirdScanner (owl:equivalentClass BiometricIdentificationCapability).
    If the reasoner does real equivalence, Gate 1 fires. Pattern matching on IRI names would fail.
  - Test 5: Disposition is a blank node (anonymous individual). owl:someValuesFrom requires only
    existence, not a named IRI. Entailment must still fire.

SCOPE NOTE — Adversarial scenarios (4-5):
  These are classification-core entailment tests only.  They verify that the
  OWL-RL reasoner produces the correct rdf:type entailments (HighRiskSystem,
  AnnexIII1aApplicableSystem) under non-trivial conditions.  Their TTL files
  are intentionally minimal: they carry enough structure for the reasoner to
  fire the three-gate equivalentClass axiom, but they do NOT include the full
  documentary infrastructure (provider roles, assessment documentation, etc.)
  required by the audit layer (SPARQL ASK queries in run_pipeline.py).

  Running the full pipeline on these scenarios will show classification PASS
  but audit FAIL.  This is expected and correct: these TTLs are intentionally
  minimal, isolating reasoning behaviour without the full documentary
  infrastructure (provider roles, assessment documentation) that the audit
  layer requires.
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
IAO_BOT = ONTOLOGY_DIR / "imports" / "iao_bot.owl"
RO_BOT = ONTOLOGY_DIR / "imports" / "ro_bot.owl"
CCO_BOT = ONTOLOGY_DIR / "imports" / "cco_bot.owl"
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
    # ── Adversarial tests ──────────────────────────────────────────────
    {
        "name": "DecoySystem_001",
        "label": "ADVERSARIAL: Equivalency Decoy (WeirdScanner EQUIV BiometricIdentificationCapability)",
        "instances": ONTOLOGY_DIR / "ARCO_instances_adversarial_decoy.ttl",
        "system": ARCO["DecoySystem_001"],
        "expected": {
            "HighRiskSystem": True,           # equivalence must propagate
            "AnnexIII1aApplicableSystem": True,  # all 3 gates satisfied via equivalence
            "AnnexIII5bApplicableSystem": False,
        },
    },
    {
        "name": "GhostSystem_001",
        "label": "ADVERSARIAL: Blank Node Ghost (anonymous disposition)",
        "instances": ONTOLOGY_DIR / "ARCO_instances_adversarial_blanknode.ttl",
        "system": ARCO["GhostSystem_001"],
        "expected": {
            "HighRiskSystem": True,           # someValuesFrom satisfied by blank node
            "AnnexIII1aApplicableSystem": True,  # all 3 gates satisfied
            "AnnexIII5bApplicableSystem": False,
        },
    },
]


def load_and_reason(instance_file: Path) -> Graph:
    g = Graph()
    for p in (BFO_2020, IAO_BOT, RO_BOT, CCO_BOT, CORE, GOV, instance_file):
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
