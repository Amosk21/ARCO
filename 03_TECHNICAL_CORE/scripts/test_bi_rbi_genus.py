"""
Named acceptance test for the BI/RBI genus change.

The ontology-change harness requires a fail-first acceptance test for the
:BiometricIdentificationProcess genus change. On UNMODIFIED core (before the change) case C
could not be expressed (the genus class did not exist); after the change it can, and this test
pins the intended entailment behaviour:

  A. remote   : a process typed :RemoteBiometricIdentificationProcess  => Annex III 1(a) entailed (unchanged).
  C. genus    : the SAME system, process typed only the bare :BiometricIdentificationProcess => NOT entailed
                (the honest "identification not asserted to be remote" answer). The at-the-door /
                premises-access case is biometric verification (1:1), carved out per Recitals 15 & 17 and
                handled by :BiometricVerificationProcess; no separate non-remote class is minted.
  D. regression : the real Sentinel fixture still entails :AnnexIII1aApplicableSystem.
  E. disjointness : the verification / identification-genus disjointness axiom is present for the HermiT layer.

Loads the real core ontology read-only; runs the production reasoner (OWL-RL). No fixture files.
Run: python 03_TECHNICAL_CORE/scripts/test_bi_rbi_genus.py   (exit 0 = pass)
"""
from __future__ import annotations
from pathlib import Path
from rdflib import Graph, Namespace, RDF, OWL
import owlrl

ROOT = Path(__file__).resolve().parents[2]
OD = ROOT / "03_TECHNICAL_CORE" / "ontology"
IMP = OD / "imports"
CORE = [
    IMP / "bfo-2020.owl", IMP / "iao_bot.owl", IMP / "ro_bot.owl", IMP / "cco_bot.owl",
    OD / "ARCO_core.ttl", OD / "ARCO_governance_extension.ttl",
]
A = Namespace("https://arco.ai/ontology/core#")
BFO = Namespace("http://purl.obolibrary.org/obo/BFO_")
RO = Namespace("http://purl.obolibrary.org/obo/RO_")
IAO = Namespace("http://purl.obolibrary.org/obo/IAO_")
CCO = Namespace("http://www.ontologyrepository.com/CommonCoreOntologies/")
ANNEX_1A = A["AnnexIII1aApplicableSystem"]

_base = Graph()
for p in CORE:
    _base.parse(str(p), format="xml" if str(p).endswith(".owl") else "turtle")

def _reason(extra):
    g = Graph()
    for t in _base:
        g.add(t)
    for t in extra:
        g.add(t)
    owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(g)
    return g

def _idface(process_type):
    S, TERM, DISP = A["t_System"], A["t_Terminal"], A["t_Disposition"]
    PROC, IUS, USS = A["t_Proc"], A["t_IntendedUse"], A["t_UseScenario"]
    return [
        (S, RDF.type, A["System"]),
        (S, BFO["0000051"], TERM),
        (TERM, RDF.type, A["HardwareComponent"]),
        (TERM, RO["0000091"], DISP),
        (DISP, RDF.type, A["BiometricIdentificationCapability"]),
        (PROC, RDF.type, process_type),
        (IUS, RDF.type, A["IntendedUseSpecification"]),
        (IUS, CCO["prescribes"], PROC),
        (IUS, IAO["0000136"], S),
        (USS, RDF.type, A["UseScenarioSpecification"]),
        (USS, IAO["0000136"], S),
        (USS, CCO["designates"], A["NaturalPersonRole"]),
    ], S

def _is_1a(process_type):
    triples, S = _idface(process_type)
    return (S, RDF.type, ANNEX_1A) in _reason(triples)

def main():
    assert _is_1a(A["RemoteBiometricIdentificationProcess"]) is True, \
        "A: remote-typed process must still entail Annex III 1(a)"
    assert _is_1a(A["BiometricIdentificationProcess"]) is False, \
        "C: bare genus (identification not asserted remote) must NOT entail Annex III 1(a)"

    sent = Graph(); sent.parse(str(OD / "ARCO_instances_sentinel.ttl"), format="turtle")
    g = _reason(list(sent))
    assert len(set(g.subjects(RDF.type, ANNEX_1A))) >= 1, \
        "D: real Sentinel fixture must still entail at least one AnnexIII1aApplicableSystem"

    # E (two-layer boundary): OWL-RL classifies; HermiT checks DL consistency. Assert the
    # verification/identification-genus disjointness axiom is present for the HermiT layer to
    # enforce (owlrl does not enforce disjointness as a classification effect; see LIMITATIONS 3.7.d).
    gE = _reason([])
    assert (A["BiometricVerificationProcess"], OWL.disjointWith,
            A["BiometricIdentificationProcess"]) in gE, \
        "E: verification/identification-genus disjointness axiom must be present for the HermiT layer"

    print("PASS: BI/RBI genus acceptance test (A remote=1a, C genus!=1a, "
          "D Sentinel regression, E verification/genus disjointness present for HermiT layer).")

if __name__ == "__main__":
    main()
