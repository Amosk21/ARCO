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

  Running the full pipeline on the 5(b) decoy (WeirdCalcSystem) will show
  classification PASS but audit FAIL — expected and correct: that TTL is
  intentionally minimal, isolating reasoning behaviour without the full
  documentary infrastructure the audit layer requires. The 1(a) decoy
  (DecoySystem_001) carries its documentary scaffolding and passes the full
  audit since the L3.11 fix (its former sole audit FAIL was the union-sync
  guard false-alarming on the closure; the guard now runs on the asserted
  graph, where the decoy's inferred alias subclassing does not trip it).

ANCHOR-TABLE NOTE (OPEN_PROBLEMS L4.8 item 5):
  SCENARIOS below is the single source of expected classification polarity
  for the whole repo. hermit_cross_check.py imports it and asserts BOTH
  reasoners against these values per cell — do not create a second expected
  table anywhere. Every scenario carries a "latent_risk" key (the
  detect_latent_risk.sparql structural ASK, asserted RL-side in this test's
  own loop as a live co-witness). latent_risk is NOT derivable from
  HighRiskSystem: they coincide on current fixtures only contingently, and
  GhostSystem is the standing proof they can diverge across reasoners.
  WeirdCalcSystem_001 (the 5(b) equivalency decoy) is in the table so its
  polarity anchor no longer lives only in test_adversarial_mechanism.py.
"""

from __future__ import annotations

import sys
from pathlib import Path
from rdflib import Graph, Namespace, URIRef

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

REASONING_DIR = REPO_ROOT / "03_TECHNICAL_CORE" / "reasoning"
# Audit-layer absence checks (OPEN_PROBLEMS L3.8). Caller-bound ASKs; these
# audit the materialized closure and never classify (Invariant 2).
NEGATIVE_CASE_ABSENCE_QUERY = REASONING_DIR / "check_negative_case_no_annex_iii_in_closure.sparql"
CROSS_CATEGORY_ISOLATION_QUERY = REASONING_DIR / "check_cross_category_isolation_in_closure.sparql"
INTENT_WITHOUT_CAPABILITY_QUERY = REASONING_DIR / "flag_intent_without_capability.sparql"
UNION_SYNC_QUERY = REASONING_DIR / "check_union_subclass_sync.sparql"
# Structural latent-risk traversal; its expected value is the "latent_risk"
# anchor key in SCENARIOS (L4.8 item 5 — the cross-check's fourth query).
DETECT_LATENT_RISK_QUERY = REASONING_DIR / "detect_latent_risk.sparql"

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
            "latent_risk": True,
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
            "latent_risk": True,
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
            "latent_risk": False,
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
            "latent_risk": True,
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
            # RL-side value. GhostSystem is excluded from the HermiT cross-check:
            # the structural traversal returns False under HermiT for blank-node
            # dispositions (LIMITATIONS §7.4) — the standing proof latent_risk
            # must not be derived from HighRiskSystem.
            "latent_risk": True,
        },
    },
    {
        "name": "WeirdCalcSystem_001",
        "label": "ADVERSARIAL: 5(b) Equivalency Decoy (WeirdCalculator EQUIV CreditworthinessEvaluationCapability)",
        "instances": ONTOLOGY_DIR / "ARCO_instances_adversarial_decoy_5b.ttl",
        "system": ARCO["WeirdCalcSystem_001"],
        "expected": {
            "HighRiskSystem": True,           # equivalence must propagate
            "AnnexIII1aApplicableSystem": False,
            "AnnexIII5bApplicableSystem": True,  # all 3 gates satisfied via equivalence
            "latent_risk": True,
        },
        # Classification-core minimal fixture (see SCOPE NOTE above): every
        # check this test runs per scenario is a graph-level ASK and all are
        # satisfiable on it. The full pipeline's audit layer is expected to
        # FAIL on this fixture — that is the documented two-layer split, and
        # it is out of scope here. Previously this system's polarity anchor
        # lived only in test_adversarial_mechanism.py (a second home); this
        # entry makes SCENARIOS the single source (L4.8 item 5, gap B).
    },
    # Flag-detection scenarios — entailment plus exception-flag SPARQL ASKs.
    {
        "name": "FlagTest_BiometricSystem_WithDerogationClaim",
        "label": "FLAG: Biometric + Article 6(3) DerogationClaim",
        "instances": ONTOLOGY_DIR / "ARCO_instances_flag_tests.ttl",
        "system": ARCO["FlagTest_BiometricSystem_WithDerogationClaim"],
        "expected": {
            "HighRiskSystem": True,
            "AnnexIII1aApplicableSystem": True,
            "AnnexIII5bApplicableSystem": False,
            "latent_risk": True,
        },
        "expected_flags": {
            "DerogationClaim": True,
            "FraudDetectionProcess": False,
        },
    },
    {
        "name": "FlagTest_CreditSystem_WithFraudProcess",
        "label": "FLAG: Credit + 5(b) FraudDetectionProcess",
        "instances": ONTOLOGY_DIR / "ARCO_instances_flag_tests.ttl",
        "system": ARCO["FlagTest_CreditSystem_WithFraudProcess"],
        "expected": {
            "HighRiskSystem": True,
            "AnnexIII1aApplicableSystem": False,
            "AnnexIII5bApplicableSystem": True,
            "latent_risk": True,
        },
        "expected_flags": {
            "DerogationClaim": False,
            "FraudDetectionProcess": True,
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


def run_ask(g: Graph, query_path: Path, bindings: dict) -> bool:
    """Run a caller-bound ASK from reasoning/ against the reasoned graph."""
    result = g.query(query_path.read_text(encoding="utf-8"), initBindings=bindings)
    return bool(result.askAnswer)


IAO_IS_ABOUT = URIRef("http://purl.obolibrary.org/obo/IAO_0000136")
CCO_PRESCRIBES = URIRef("http://www.ontologyrepository.com/CommonCoreOntologies/prescribes")


def has_derogation_claim_for(g: Graph, system) -> bool:
    """A DerogationClaim individual is_about the given system."""
    for claim, _, _ in g.triples((None, RDF_NS["type"], ARCO["DerogationClaim"])):
        if (claim, IAO_IS_ABOUT, system) in g:
            return True
    return False


def has_fraud_process_for(g: Graph, system) -> bool:
    """An IntendedUseSpecification is_about the given system AND prescribes a FraudDetectionProcess."""
    for ius, _, _ in g.triples((None, IAO_IS_ABOUT, system)):
        if (ius, RDF_NS["type"], ARCO["IntendedUseSpecification"]) not in g:
            continue
        for _, _, process in g.triples((ius, CCO_PRESCRIBES, None)):
            if (process, RDF_NS["type"], ARCO["FraudDetectionProcess"]) in g:
                return True
    return False


FLAG_CHECKS = {
    "DerogationClaim": has_derogation_claim_for,
    "FraudDetectionProcess": has_fraud_process_for,
}


def main() -> None:
    print("=" * 72)
    print("ARCO MULTI-SCENARIO REGRESSION TEST")
    print("=" * 72)

    # Table-coherence guard (OPEN_PROBLEMS L3.8 gap 2, revised plan): the
    # Annex-applicability => HighRiskSystem subsumption is purely
    # OWL-RL-derived (the governance extension asserts no subClassOf between
    # the applicability classes and :HighRiskSystem), so a graph-side
    # NOT-EXISTS ASK would pass vacuously exactly when the reasoner
    # under-derives. The witness is positive instead: any scenario expecting
    # an Annex III applicability True must also expect HighRiskSystem True;
    # the per-class assertions below then verify both memberships actually
    # materialize in the same closure run.
    for scenario in SCENARIOS:
        exp = scenario["expected"]
        annex_true = exp.get("AnnexIII1aApplicableSystem") or exp.get("AnnexIII5bApplicableSystem")
        if annex_true and not exp.get("HighRiskSystem"):
            print(
                f"TABLE ERROR: {scenario['name']} expects an Annex III applicability "
                "without HighRiskSystem — violates the derived Article 6(2) pairing"
            )
            sys.exit(1)

    all_pass = True

    for scenario in SCENARIOS:
        print(f"\n--- {scenario['label'].upper()} ---")
        instance_file = scenario["instances"]
        system = scenario["system"]

        g, initial, final = load_and_reason(instance_file)
        print(f"  Triples: {initial} -> {final} (+{final - initial})")

        for cls_name, expected in scenario["expected"].items():
            if cls_name == "latent_risk":
                continue  # ASK anchor, not a class membership; handled below
            actual = check_type(g, system, cls_name)
            ok = actual == expected
            status = "OK" if ok else "FAIL"
            print(f"  {cls_name}: {actual} (expected {expected}) [{status}]")
            if not ok:
                all_pass = False

        # ── Latent-risk anchor co-witness (L4.8 item 5, gap A) ──
        # The "latent_risk" key anchors the cross-check's fourth query
        # (detect_latent_risk.sparql). Exercising it here RL-side on every
        # scenario run keeps the anchor value itself tested, not just copied.
        latent_expected = scenario["expected"]["latent_risk"]
        latent_actual = run_ask(g, DETECT_LATENT_RISK_QUERY, {"system": system})
        ok = latent_actual == latent_expected
        status = "OK" if ok else "FAIL"
        print(f"  latent_risk (ASK): {latent_actual} (expected {latent_expected}) [{status}]")
        if not ok:
            all_pass = False

        # ── Audit-layer absence checks (OPEN_PROBLEMS L3.8) ──
        # Expected values derive from the scenario's expected dict — one
        # source of truth, no second table. Positive fixtures must return
        # False, proving the query detects presence in the same test run
        # that reads the kiosk's True (live co-witness against the reasoner
        # silently under-deriving everywhere).
        annex_classes = ("AnnexIII1aApplicableSystem", "AnnexIII5bApplicableSystem")
        expect_absent = not any(scenario["expected"][c] for c in annex_classes)
        actual_absent = run_ask(g, NEGATIVE_CASE_ABSENCE_QUERY, {"system": system})
        ok = actual_absent == expect_absent
        status = "OK" if ok else "FAIL"
        print(f"  no_annex_iii_in_closure: {actual_absent} (expected {expect_absent}) [{status}]")
        if not ok:
            all_pass = False

        # Cross-category isolation: for each Annex class the table expects
        # False, the (system, excluded_class)-bound isolation ASK must return
        # True. Keyed off the expected dict so a future legitimate
        # dual-category fixture updates one table and nothing falsely blocks.
        for cls_name in annex_classes:
            if scenario["expected"][cls_name]:
                continue
            isolated = run_ask(
                g, CROSS_CATEGORY_ISOLATION_QUERY,
                {"system": system, "excluded_class": ARCO[cls_name]},
            )
            ok = isolated is True
            status = "OK" if ok else "FAIL"
            print(f"  isolation from {cls_name}: {isolated} (expected True) [{status}]")
            if not ok:
                all_pass = False

        # ── Intent-without-capability flag (OPEN_PROBLEMS L3.10; report-only
        # in the pipeline). Every current fixture carries the capability that
        # matches its documented category (or no regulated-subkind IUS at all),
        # so the expected answer is False across the table. The live co-witness
        # that the query CAN return True is the Gate-1-removal mutation check
        # after the scenario loop.
        iwc = run_ask(g, INTENT_WITHOUT_CAPABILITY_QUERY, {"system": system})
        ok = iwc is False
        status = "OK" if ok else "FAIL"
        print(f"  intent_without_capability: {iwc} (expected False) [{status}]")
        if not ok:
            all_pass = False

        expected_flags = scenario.get("expected_flags")
        if expected_flags is not None:
            for flag_cls, expected in expected_flags.items():
                checker = FLAG_CHECKS.get(flag_cls)
                if checker is None:
                    print(f"  {flag_cls}: no checker registered [FAIL]")
                    all_pass = False
                    continue
                actual = checker(g, system)
                ok = actual == expected
                status = "OK" if ok else "FAIL"
                print(f"  {flag_cls} for system: {actual} (expected {expected}) [{status}]")
                if not ok:
                    all_pass = False

    # ── Mutation witness for the intent-without-capability flag (L3.10):
    # Sentinel with every ro:0000091 disposition edge removed from the
    # asserted graph still carries its RBI-subkind IUS and role-designating
    # USS, so the flag must return True post-reasoning. Proves the ASK
    # detects the under-classification shape and is not vacuously False.
    print("\n--- MUTATION WITNESS: Sentinel minus Gate-1 disposition edges ---")
    RO_HAS_DISPOSITION = URIRef("http://purl.obolibrary.org/obo/RO_0000091")
    mg = Graph()
    for p in (BFO_2020, IAO_BOT, RO_BOT, CCO_BOT, CORE, GOV, ONTOLOGY_DIR / "ARCO_instances_sentinel.ttl"):
        mg.parse(p.as_posix(), format="xml" if p.suffix == ".owl" else "turtle")
    removed = 0
    for s, _, o in list(mg.triples((None, RO_HAS_DISPOSITION, None))):
        # strip only instance-level disposition edges on ARCO-namespace subjects;
        # TBox restrictions on ro:0000091 live in blank-node restrictions and stay
        if isinstance(s, URIRef) and str(s).startswith(str(ARCO)):
            mg.remove((s, RO_HAS_DISPOSITION, o))
            removed += 1
    owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(mg)
    mut_flag = run_ask(mg, INTENT_WITHOUT_CAPABILITY_QUERY, {"system": ARCO["Sentinel_ID_System"]})
    mut_not_entailed = (ARCO["Sentinel_ID_System"], RDF_NS["type"], ARCO["AnnexIII1aApplicableSystem"]) not in mg
    ok = removed > 0 and mut_flag is True and mut_not_entailed
    status = "OK" if ok else "FAIL"
    print(f"  removed {removed} disposition edge(s); flag={mut_flag} (expected True); "
          f"1(a) not entailed={mut_not_entailed} (expected True) [{status}]")
    if not ok:
        all_pass = False

    # ── Union-sync drift witness (OPEN_PROBLEMS L3.11): the pipeline runs this
    # guard against the ASSERTED graph. Three checks: baseline asserted graph
    # passes; removing the explicit per-member rdfs:subClassOf FAILS on the
    # asserted graph (the drift case the closure hides by re-materializing it);
    # the decoy fixture's asserted graph does NOT false-alarm (its alias
    # subclassing is inferred, not asserted).
    print("\n--- UNION-SYNC DRIFT WITNESS (asserted graph; L3.11) ---")
    RDFS_SUBCLASS = URIRef("http://www.w3.org/2000/01/rdf-schema#subClassOf")

    def load_source(instance_file: Path) -> Graph:
        sg = Graph()
        for fp in (BFO_2020, IAO_BOT, RO_BOT, CCO_BOT, CORE, GOV, instance_file):
            sg.parse(fp.as_posix(), format="xml" if fp.suffix == ".owl" else "turtle")
        return sg

    src = load_source(ONTOLOGY_DIR / "ARCO_instances_sentinel.ttl")
    base_ok = run_ask(src, UNION_SYNC_QUERY, {})
    src.remove((ARCO["BiometricIdentificationCapability"], RDFS_SUBCLASS,
                ARCO["AnnexIIITriggeringCapability"]))
    drift_caught = run_ask(src, UNION_SYNC_QUERY, {}) is False
    decoy_src = load_source(ONTOLOGY_DIR / "ARCO_instances_adversarial_decoy.ttl")
    decoy_no_false_alarm = run_ask(decoy_src, UNION_SYNC_QUERY, {})
    ok = bool(base_ok) and drift_caught and bool(decoy_no_false_alarm)
    status = "OK" if ok else "FAIL"
    print(f"  baseline={base_ok} (True); drift caught={drift_caught} (True); "
          f"decoy no-false-alarm={decoy_no_false_alarm} (True) [{status}]")
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
