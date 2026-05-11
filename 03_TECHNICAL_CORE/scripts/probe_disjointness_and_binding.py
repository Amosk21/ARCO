"""
Verification script: owlrl disjointness-violation + subPropertyOf binding probes.

Purpose:
1. Probe whether owlrl==7.1.4 fires the cax-dw rule (pairwise owl:disjointWith)
   into closure.error_messages — confirms ARCO's pairwise disjointness
   declarations at ARCO_core.ttl:98-100 are load-bearing.
2. Probe whether owlrl fires the cax-adc rule (owl:AllDisjointClasses collective
   form) — determines whether a future swap from pairwise to collective form
   is safe.
3. Probe whether ARCO's subPropertyOf binding (ARCO_core.ttl section 5:
   ro:0000052 rdfs:subPropertyOf bfo:0000197) catches a category error where
   a role is asserted to be characteristic_of an ICE-typed bearer. The
   binding inherits BFO 2020's IC range on the inferred inherence triple via
   prp-spo1 + prp-rng + cax-dw.

This is a one-off verification probe, not a regression test. It builds minimal
in-memory ontologies and reports observable reasoner behavior.

No ARCO files are modified. No fixtures are added.
"""

import owlrl
import rdflib
from rdflib.namespace import OWL, RDF, RDFS

ARCO = rdflib.Namespace("https://arco.ai/ontology/core#")
BFO = rdflib.Namespace("http://purl.obolibrary.org/obo/BFO_")
RO = rdflib.Namespace("http://purl.obolibrary.org/obo/RO_")
IAO = rdflib.Namespace("http://purl.obolibrary.org/obo/IAO_")


def run_closure(graph):
    """Run owlrl materialization and return error messages from the closure."""
    closure = owlrl.OWLRL_Semantics(graph, axioms=False, daxioms=False, rdfs=False)
    closure.closure()
    closure.flush_stored_triples()
    errors = list(getattr(closure, "error_messages", []) or [])
    return errors


def probe_pairwise_disjoint():
    """Probe 1: pairwise owl:disjointWith fires cax-dw violation on overlap."""
    g = rdflib.Graph()
    g.add((ARCO.A, RDF.type, OWL.Class))
    g.add((ARCO.B, RDF.type, OWL.Class))
    g.add((ARCO.A, OWL.disjointWith, ARCO.B))
    # Adversarial: assert an individual as member of both A and B
    g.add((ARCO.x, RDF.type, ARCO.A))
    g.add((ARCO.x, RDF.type, ARCO.B))
    errors = run_closure(g)
    return len(errors) > 0, errors


def probe_alldisjoint_collective():
    """Probe 2: owl:AllDisjointClasses fires cax-adc violation on overlap."""
    g = rdflib.Graph()
    g.add((ARCO.A, RDF.type, OWL.Class))
    g.add((ARCO.B, RDF.type, OWL.Class))
    g.add((ARCO.C, RDF.type, OWL.Class))
    # AllDisjointClasses block
    adc = rdflib.BNode()
    g.add((adc, RDF.type, OWL.AllDisjointClasses))
    members_list = rdflib.collection.Collection(g, rdflib.BNode(), [ARCO.A, ARCO.B, ARCO.C])
    g.add((adc, OWL.members, members_list.uri))
    # Adversarial: assert an individual as member of two of the three
    g.add((ARCO.x, RDF.type, ARCO.A))
    g.add((ARCO.x, RDF.type, ARCO.B))
    errors = run_closure(g)
    return len(errors) > 0, errors


def probe_binding_catches_ice_bearer():
    """
    Probe 3: with ARCO's subPropertyOf binding (ro:0000052 rdfs:subPropertyOf
    bfo:0000197), does owlrl detect a category error when a role is asserted
    to be characteristic_of an ICE-typed bearer? The binding routes the
    asserted triple through BFO 2020's range constraint on inheres_in
    (range = IndependentContinuant ∩ NOT spatial-region) via prp-spo1 +
    prp-rng + cax-dw against ICE ⊑ GDC ⊥ IC.
    """
    g = rdflib.Graph()

    # BFO upper-level disjointness (the load-bearing fact)
    g.add((BFO["0000004"], RDF.type, OWL.Class))  # IndependentContinuant
    g.add((BFO["0000031"], RDF.type, OWL.Class))  # GenericallyDependentContinuant
    g.add((BFO["0000004"], OWL.disjointWith, BFO["0000031"]))

    # ICE chain: ICE → GenericallyDependentContinuant
    g.add((IAO["0000030"], RDFS.subClassOf, BFO["0000031"]))

    # BFO 2020 inheres_in with IC range (range = IC; spatial-region carve-out omitted here)
    g.add((BFO["0000197"], RDF.type, OWL.ObjectProperty))
    g.add((BFO["0000197"], RDFS.range, BFO["0000004"]))

    # ARCO's binding: ro:0000052 rdfs:subPropertyOf bfo:0000197
    g.add((RO["0000052"], RDF.type, OWL.ObjectProperty))
    g.add((RO["0000052"], RDFS.subPropertyOf, BFO["0000197"]))

    # Adversarial fixture: role characteristic_of an ICE-typed bearer
    g.add((ARCO.bad_role, RO["0000052"], ARCO.bad_ice_bearer))
    g.add((ARCO.bad_ice_bearer, RDF.type, IAO["0000030"]))

    errors = run_closure(g)
    return len(errors) > 0, errors


def probe_binding_baseline_no_binding():
    """
    Probe 3-baseline: same adversarial fixture WITHOUT the subPropertyOf
    binding. ro:0000052 has no range; the asserted triple does not project
    into bfo:0000197; no range entailment fires; bearer's ICE typing is
    permitted under OWA. Should produce no error.
    """
    g = rdflib.Graph()

    # Same BFO disjointness setup
    g.add((BFO["0000004"], RDF.type, OWL.Class))
    g.add((BFO["0000031"], RDF.type, OWL.Class))
    g.add((BFO["0000004"], OWL.disjointWith, BFO["0000031"]))
    g.add((IAO["0000030"], RDFS.subClassOf, BFO["0000031"]))
    g.add((BFO["0000197"], RDF.type, OWL.ObjectProperty))
    g.add((BFO["0000197"], RDFS.range, BFO["0000004"]))

    # ro:0000052 declared, but NO subPropertyOf binding to bfo:0000197
    g.add((RO["0000052"], RDF.type, OWL.ObjectProperty))

    # Same adversarial fixture
    g.add((ARCO.bad_role, RO["0000052"], ARCO.bad_ice_bearer))
    g.add((ARCO.bad_ice_bearer, RDF.type, IAO["0000030"]))

    errors = run_closure(g)
    return len(errors) > 0, errors


def main():
    print("=" * 72)
    print("owlrl disjointness-violation + bearer-restriction probes")
    print("=" * 72)

    print("\nProbe 1: pairwise owl:disjointWith (cax-dw rule)")
    print("  Expected: violation detected (errors > 0)")
    fired, errors = probe_pairwise_disjoint()
    print(f"  Result: violation_fired={fired}, error_count={len(errors)}")
    if errors:
        print(f"  Sample error: {errors[0][:200]}")

    print("\nProbe 2: owl:AllDisjointClasses collective form (cax-adc rule)")
    print("  Expected: violation detected (errors > 0)")
    print("  If NOT fired: owlrl 7.1.4 has no cax-adc support; collective form")
    print("  silently weaker than pairwise; PR A1 swap unsafe.")
    fired, errors = probe_alldisjoint_collective()
    print(f"  Result: violation_fired={fired}, error_count={len(errors)}")
    if errors:
        print(f"  Sample error: {errors[0][:200]}")

    print("\nProbe 3: ARCO's subPropertyOf binding catches ICE-typed bearer category error")
    print("  Expected (binding load-bearing): violation detected (errors > 0)")
    print("  Mechanism: ro:0000052 rdfs:subPropertyOf bfo:0000197 -> prp-spo1")
    print("  projects asserted triple, prp-rng enforces BFO IC range, cax-dw")
    print("  fires against ICE subClassOf GDC disjointWith IC.")
    fired, errors = probe_binding_catches_ice_bearer()
    print(f"  Result: violation_fired={fired}, error_count={len(errors)}")
    if errors:
        print(f"  Sample error: {errors[0][:200]}")

    print("\nProbe 3-baseline: same adversarial fixture WITHOUT the binding")
    print("  Expected: no violation (baseline confirms the binding is the")
    print("  catching mechanism, not some other axiom)")
    fired_baseline, errors_baseline = probe_binding_baseline_no_binding()
    print(f"  Result: violation_fired={fired_baseline}, error_count={len(errors_baseline)}")
    if errors_baseline:
        print(f"  Sample error: {errors_baseline[0][:200]}")

    print("\n" + "=" * 72)
    print("Summary")
    print("=" * 72)
    print(f"  Probe 1 (pairwise disjointWith fires):           check above")
    print(f"  Probe 2 (AllDisjointClasses fires):              check above")
    print(f"  Probe 3 (binding catches ICE-typed bearer):      check above")
    print(f"  Probe 3-baseline (no binding, no catch):         check above")
    print()
    print("Interpretation hints:")
    print("  - Probes 1 == True, 2 == True: collective AllDisjointClasses form")
    print("    safe; pairwise can be swapped (deferred, see queued follow-ups).")
    print("  - Probes 3 == True, 3-baseline == False: ARCO's subPropertyOf")
    print("    binding (ARCO_core.ttl section 5) is load-bearing for owlrl")
    print("    enforcement of BFO 2020's IC range on the inheres_in relation.")
    print("  - Probes 3 == False: binding does not enforce at owlrl layer;")
    print("    revisit assumption that prp-spo1 + prp-rng + cax-dw chain composes.")


if __name__ == "__main__":
    main()
