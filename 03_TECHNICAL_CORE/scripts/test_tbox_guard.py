"""
test_tbox_guard.py — regression test for OPEN_PROBLEMS L3.12.

Instance data is ABox-only by contract. The decoy fixtures proved that an
owl:equivalentClass triple inside an instance file rewires classification
under both reasoners; guard_instances_tbox is the load-time enforcement.

Asserts:
  1. An injected instance file carrying ':Innocent owl:equivalentClass
     :BiometricIdentificationCapability' fails the guard with the named
     TBOX GUARD error.
  2. A subClassOf wedge into :AnnexIIITriggeringCapability fails the guard.
  3. Every shipped non-decoy fixture passes the guard (no false positives —
     TBox-looking text inside comments/string literals must not trip it).
  4. The two sanctioned adversarial decoy fixtures are allowlisted.

Run: python 03_TECHNICAL_CORE/scripts/test_tbox_guard.py
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "03_TECHNICAL_CORE" / "scripts"))

from run_pipeline import guard_instances_tbox, TBOX_GUARD_ALLOWLIST  # noqa: E402

ONTOLOGY_DIR = REPO_ROOT / "03_TECHNICAL_CORE" / "ontology"

PREFIXES = """@prefix : <https://arco.ai/ontology/core#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix ex: <http://example.org/attack#> .
@prefix cco: <http://www.ontologyrepository.com/CommonCoreOntologies/> .
"""

INJECTIONS = {
    "equivalentClass alias": PREFIXES
    + ":Innocent a owl:Class ; owl:equivalentClass :BiometricIdentificationCapability .\n",
    "subClassOf wedge": PREFIXES
    + ":SneakyCapability rdfs:subClassOf :AnnexIIITriggeringCapability .\n",
    # QA change 6: property-level attacks, foreign-namespace subjects — would
    # evade an ARCO-term-scoped check; the guard forbids these predicates in
    # instance files outright.
    "subPropertyOf onto cco:prescribes (fakes Gate 2 via prp-spo1)": PREFIXES
    + "ex:harmlessRef rdfs:subPropertyOf cco:prescribes .\n",
    "sameAs onto the role universal (fakes Gate 3 hasValue via eq-rep)": PREFIXES
    + "ex:Impostor owl:sameAs :NaturalPersonRole .\n",
}


def expect_guard_failure(label: str, ttl: str) -> bool:
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "ARCO_instances_injected.ttl"
        p.write_text(ttl, encoding="utf-8")
        try:
            guard_instances_tbox(p)
        except RuntimeError as e:
            ok = "TBOX GUARD" in str(e)
            print(f"  {label}: guard raised TBOX GUARD [{'OK' if ok else 'FAIL'}]")
            return ok
    print(f"  {label}: guard did NOT raise [FAIL]")
    return False


def main() -> None:
    print("=" * 72)
    print("TBOX/ABOX LOAD GUARD TEST (OPEN_PROBLEMS L3.12)")
    print("=" * 72)
    all_pass = True

    print("\nInjection cases (must fail the guard):")
    for label, ttl in INJECTIONS.items():
        all_pass &= expect_guard_failure(label, ttl)

    print("\nShipped fixtures (non-decoy must pass; decoys allowlisted):")
    for fixture in sorted(ONTOLOGY_DIR.glob("ARCO_instances_*.ttl")):
        try:
            guard_instances_tbox(fixture)
            allow = fixture.name in TBOX_GUARD_ALLOWLIST
            print(f"  {fixture.name}: {'allowlisted' if allow else 'clean'} [OK]")
        except RuntimeError as e:
            print(f"  {fixture.name}: unexpected guard failure [FAIL]\n    {e}")
            all_pass = False

    # The allowlist must be load-bearing: identical decoy content under a
    # non-allowlisted filename must fail the guard.
    print("\nAllowlist is load-bearing (renamed decoy content must fail):")
    decoy_ttl = (ONTOLOGY_DIR / "ARCO_instances_adversarial_decoy.ttl").read_text(encoding="utf-8")
    all_pass &= expect_guard_failure("renamed decoy content", decoy_ttl)

    print()
    print("=" * 72)
    print("ALL TBOX GUARD TESTS PASSED" if all_pass else "SOME TBOX GUARD TESTS FAILED")
    print("=" * 72)
    if not all_pass:
        sys.exit(1)


if __name__ == "__main__":
    main()
