"""
Adversarial-mechanism regression tests.

`test_scenarios.py` already asserts that DecoySystem_001 and GhostSystem_001
classify correctly under OWL-RL. This file verifies HOW the classification
fires, not just that it fires. Each assertion catches a failure mode that
would let a pattern-matching pipeline pass test_scenarios.py with the wrong
mechanism in place.

  Decoy fixture (ARCO_instances_adversarial_decoy.ttl) — Annex III 1(a):
    The disposition is typed only as :WeirdScanner. :WeirdScanner is declared
    owl:equivalentClass :BiometricIdentificationCapability in the same fixture.
    Pre-reasoning, no asserted triple types the disposition as
    :BiometricIdentificationCapability. Post-reasoning under OWL-RL,
    the equivalentClass propagation entails the typing and Gate 1 fires.

    If a pipeline did IRI-name pattern matching, it would see no
    :BiometricIdentificationCapability triple in the input and miss the
    classification. The OWL reasoner does not.

  Decoy 5(b) fixture (ARCO_instances_adversarial_decoy_5b.ttl) — Annex III 5(b):
    Same shape as the 1(a) decoy, branch-swapped. :WeirdCalculator is declared
    owl:equivalentClass :CreditworthinessEvaluationCapability. Disposition is
    typed only as :WeirdCalculator. Post-reasoning the disposition entails as
    :CreditworthinessEvaluationCapability and the three-gate intersection
    entails :AnnexIII5bApplicableSystem. Cross-category isolation is also
    under test: post-reasoning the system MUST NOT entail
    :AnnexIII1aApplicableSystem (no biometric capability bound). Closes
    OPEN_PROBLEMS L3.7.

  Ghost fixture (ARCO_instances_adversarial_blanknode.ttl):
    The disposition is an anonymous individual (blank node) typed as
    :BiometricIdentificationCapability. owl:someValuesFrom requires
    existence of an instance satisfying the restriction; it does not
    require a named individual.

    If a pipeline required named individuals for evidence walks, it would
    miss this case. The OWL reasoner does not require names; existential
    quantification is satisfied by any witness, including blank nodes.

Run from repo root:
    python 03_TECHNICAL_CORE/scripts/test_adversarial_mechanism.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from rdflib import Graph, Namespace, URIRef
from rdflib.term import BNode

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
RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
RO = Namespace("http://purl.obolibrary.org/obo/RO_")


def parse_fixture(instances_path: Path) -> Graph:
    """Parse the full ontology + fixture WITHOUT running the reasoner."""
    g = Graph()
    for p in (BFO_2020, IAO_BOT, RO_BOT, CCO_BOT, CORE, GOV, instances_path):
        if not p.exists():
            raise FileNotFoundError(f"Missing: {p}")
        fmt = "xml" if p.suffix == ".owl" else "turtle"
        g.parse(p.as_posix(), format=fmt)
    return g


def reason(g: Graph) -> Graph:
    owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(g)
    return g


def test_decoy_classifies_via_equivalent_class() -> bool:
    """
    Verify that DecoySystem_001's Gate 1 entailment fires via
    owl:equivalentClass propagation, not via direct IRI assertion.

    Pre-reasoning expectation:
      :Decoy_Disposition rdf:type :WeirdScanner            present
      :Decoy_Disposition rdf:type :BiometricIdentificationCapability  ABSENT

    Post-reasoning expectation:
      :Decoy_Disposition rdf:type :BiometricIdentificationCapability  present
      :DecoySystem_001   rdf:type :AnnexIII1aApplicableSystem         present
    """
    print("\n--- DECOY: classification via owl:equivalentClass ---")
    fixture = ONTOLOGY_DIR / "ARCO_instances_adversarial_decoy.ttl"
    g_pre = parse_fixture(fixture)

    decoy_disp = ARCO["Decoy_Disposition"]
    weird_scanner = ARCO["WeirdScanner"]
    bio_cap = ARCO["BiometricIdentificationCapability"]
    decoy_system = ARCO["DecoySystem_001"]
    annex_1a = ARCO["AnnexIII1aApplicableSystem"]

    # Precondition 1: disposition is typed as :WeirdScanner (the decoy class)
    has_weird_pre = (decoy_disp, RDF["type"], weird_scanner) in g_pre
    # Precondition 2: disposition is NOT directly typed as
    # :BiometricIdentificationCapability before reasoning
    has_bio_pre = (decoy_disp, RDF["type"], bio_cap) in g_pre
    # Precondition 3: System is NOT yet classified as 1(a) applicable
    is_annex_pre = (decoy_system, RDF["type"], annex_1a) in g_pre

    ok = True
    print(f"  pre-reasoning :Decoy_Disposition rdf:type :WeirdScanner: {has_weird_pre} (expected True)")
    if not has_weird_pre:
        ok = False
    print(f"  pre-reasoning :Decoy_Disposition rdf:type :BiometricIdentificationCapability: {has_bio_pre} (expected False)")
    if has_bio_pre:
        print("    FAIL: decoy disposition asserted directly as BiometricIdentificationCapability; "
              "test premise (equivalence-only routing) is invalid.")
        ok = False
    print(f"  pre-reasoning :DecoySystem_001 rdf:type :AnnexIII1aApplicableSystem: {is_annex_pre} (expected False)")
    if is_annex_pre:
        ok = False

    # Reason and re-check
    g_post = reason(g_pre)
    has_bio_post = (decoy_disp, RDF["type"], bio_cap) in g_post
    is_annex_post = (decoy_system, RDF["type"], annex_1a) in g_post

    print(f"  post-reasoning :Decoy_Disposition rdf:type :BiometricIdentificationCapability: {has_bio_post} (expected True)")
    if not has_bio_post:
        ok = False
    print(f"  post-reasoning :DecoySystem_001 rdf:type :AnnexIII1aApplicableSystem: {is_annex_post} (expected True)")
    if not is_annex_post:
        ok = False

    if ok:
        print("  RESULT: classification routed via owl:equivalentClass, not via direct IRI.")
    return ok


def test_credit_decoy_classifies_via_equivalent_class() -> bool:
    """
    Verify that WeirdCalcSystem_001's Gate 1 entailment fires via
    owl:equivalentClass propagation on the Annex III 5(b) branch, not via
    direct IRI assertion. Mirrors test_decoy_classifies_via_equivalent_class
    for the credit branch. Closes OPEN_PROBLEMS L3.7.

    Five assertions:
      1. Pre-reasoning: disposition rdf:type :WeirdCalculator (alias only).
      2. Pre-reasoning: disposition rdf:type :CreditworthinessEvaluationCapability
         is ABSENT (proves alias-only routing).
      3. Post-reasoning: disposition rdf:type :CreditworthinessEvaluationCapability
         is present (equivalentClass propagation fired).
      4. Post-reasoning: system rdf:type :AnnexIII5bApplicableSystem
         (three-gate intersection entails).
      5. Post-reasoning: system rdf:type :AnnexIII1aApplicableSystem
         is ABSENT (cross-category isolation; no biometric capability bound).
    """
    print("\n--- DECOY 5(b): classification via owl:equivalentClass (credit branch) ---")
    fixture = ONTOLOGY_DIR / "ARCO_instances_adversarial_decoy_5b.ttl"
    g_pre = parse_fixture(fixture)

    calc_disp = ARCO["WeirdCalc_Disposition"]
    weird_calculator = ARCO["WeirdCalculator"]
    credit_cap = ARCO["CreditworthinessEvaluationCapability"]
    calc_system = ARCO["WeirdCalcSystem_001"]
    annex_5b = ARCO["AnnexIII5bApplicableSystem"]
    annex_1a = ARCO["AnnexIII1aApplicableSystem"]

    # Precondition 1: disposition is typed as :WeirdCalculator (the decoy class)
    has_alias_pre = (calc_disp, RDF["type"], weird_calculator) in g_pre
    # Precondition 2: disposition is NOT directly typed as
    # :CreditworthinessEvaluationCapability before reasoning
    has_credit_pre = (calc_disp, RDF["type"], credit_cap) in g_pre
    # Precondition 3: System is NOT yet classified as 5(b) applicable
    is_5b_pre = (calc_system, RDF["type"], annex_5b) in g_pre

    ok = True
    print(f"  pre-reasoning :WeirdCalc_Disposition rdf:type :WeirdCalculator: {has_alias_pre} (expected True)")
    if not has_alias_pre:
        ok = False
    print(f"  pre-reasoning :WeirdCalc_Disposition rdf:type :CreditworthinessEvaluationCapability: {has_credit_pre} (expected False)")
    if has_credit_pre:
        print("    FAIL: decoy disposition asserted directly as CreditworthinessEvaluationCapability; "
              "test premise (equivalence-only routing) is invalid.")
        ok = False
    print(f"  pre-reasoning :WeirdCalcSystem_001 rdf:type :AnnexIII5bApplicableSystem: {is_5b_pre} (expected False)")
    if is_5b_pre:
        ok = False

    # Reason and re-check
    g_post = reason(g_pre)
    has_credit_post = (calc_disp, RDF["type"], credit_cap) in g_post
    is_5b_post = (calc_system, RDF["type"], annex_5b) in g_post
    is_1a_post = (calc_system, RDF["type"], annex_1a) in g_post

    print(f"  post-reasoning :WeirdCalc_Disposition rdf:type :CreditworthinessEvaluationCapability: {has_credit_post} (expected True)")
    if not has_credit_post:
        ok = False
    print(f"  post-reasoning :WeirdCalcSystem_001 rdf:type :AnnexIII5bApplicableSystem: {is_5b_post} (expected True)")
    if not is_5b_post:
        ok = False
    # Cross-category isolation check.
    print(f"  post-reasoning :WeirdCalcSystem_001 rdf:type :AnnexIII1aApplicableSystem: {is_1a_post} (expected False)")
    if is_1a_post:
        print("    FAIL: cross-category isolation broken; 5(b) decoy entailed into 1(a) class.")
        ok = False

    if ok:
        print("  RESULT: 5(b) classification routed via owl:equivalentClass, not via direct IRI.")
        print("          Cross-category isolation preserved (no 1(a) entailment).")
    return ok


def test_ghost_classifies_via_blank_node_disposition() -> bool:
    """
    Verify that GhostSystem_001's Gate 1 entailment fires via a blank-node
    disposition satisfying owl:someValuesFrom, not via a named individual.

    Pre-reasoning expectation:
      :Ghost_Module ro:0000091 _:b    where _:b is a blank node typed
                                      as :BiometricIdentificationCapability

    Post-reasoning expectation:
      :GhostSystem_001 rdf:type :AnnexIII1aApplicableSystem    present
    """
    print("\n--- GHOST: classification via blank-node owl:someValuesFrom ---")
    fixture = ONTOLOGY_DIR / "ARCO_instances_adversarial_blanknode.ttl"
    g_pre = parse_fixture(fixture)

    ghost_module = ARCO["Ghost_Module"]
    has_disposition = RO["0000091"]
    bio_cap = ARCO["BiometricIdentificationCapability"]
    ghost_system = ARCO["GhostSystem_001"]
    annex_1a = ARCO["AnnexIII1aApplicableSystem"]

    # Find disposition objects of :Ghost_Module via ro:0000091
    disposition_objs = list(g_pre.objects(ghost_module, has_disposition))

    ok = True
    print(f"  :Ghost_Module ro:0000091 ? -> {len(disposition_objs)} disposition object(s)")
    if not disposition_objs:
        print("    FAIL: no disposition object found")
        return False

    # The disposition must be a blank node, not a named IRI
    blank_node_dispositions = [d for d in disposition_objs if isinstance(d, BNode)]
    named_dispositions = [d for d in disposition_objs if not isinstance(d, BNode)]

    print(f"  blank-node dispositions: {len(blank_node_dispositions)} (expected >= 1)")
    print(f"  named dispositions:      {len(named_dispositions)} (expected 0 for this fixture's test target)")
    if not blank_node_dispositions:
        print("    FAIL: no blank-node disposition; test premise (anonymous individual) is invalid.")
        ok = False
    if named_dispositions:
        print("    FAIL: a named disposition is present; test premise (anonymous individual) is invalid.")
        ok = False

    # The blank-node disposition must be typed as :BiometricIdentificationCapability
    if blank_node_dispositions:
        bn = blank_node_dispositions[0]
        bn_typed = (bn, RDF["type"], bio_cap) in g_pre
        print(f"  blank-node typed as :BiometricIdentificationCapability: {bn_typed} (expected True)")
        if not bn_typed:
            ok = False

    # Pre-reasoning: system is not yet classified
    is_annex_pre = (ghost_system, RDF["type"], annex_1a) in g_pre
    print(f"  pre-reasoning :GhostSystem_001 rdf:type :AnnexIII1aApplicableSystem: {is_annex_pre} (expected False)")
    if is_annex_pre:
        ok = False

    # Reason and re-check
    g_post = reason(g_pre)
    is_annex_post = (ghost_system, RDF["type"], annex_1a) in g_post
    print(f"  post-reasoning :GhostSystem_001 rdf:type :AnnexIII1aApplicableSystem: {is_annex_post} (expected True)")
    if not is_annex_post:
        ok = False

    if ok:
        print("  RESULT: classification satisfied by blank-node owl:someValuesFrom witness.")
    return ok


def main() -> int:
    print("=" * 72)
    print("ARCO ADVERSARIAL-MECHANISM TEST")
    print("=" * 72)

    all_pass = True
    if not test_decoy_classifies_via_equivalent_class():
        all_pass = False
    if not test_credit_decoy_classifies_via_equivalent_class():
        all_pass = False
    if not test_ghost_classifies_via_blank_node_disposition():
        all_pass = False

    print()
    print("=" * 72)
    if all_pass:
        print("ALL ADVERSARIAL-MECHANISM TESTS PASSED")
        print("Decoy 1(a) classification routes via owl:equivalentClass.")
        print("Decoy 5(b) classification routes via owl:equivalentClass; cross-category isolated.")
        print("Ghost classification routes via blank-node owl:someValuesFrom witness.")
        print("Neither relies on a direct IRI assertion or a named individual.")
    else:
        print("SOME ADVERSARIAL-MECHANISM TESTS FAILED")
        print("=" * 72)
        return 1
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())
