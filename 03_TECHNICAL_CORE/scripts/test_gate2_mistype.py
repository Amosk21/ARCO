"""
Gate-2 mistype regression test (content-sensitivity, Global Invariant 3).

A different mutation class from test_gate_removal.py: that suite DELETES gate
evidence; this suite MISTYPES it. Each case is a PROGRAMMATIC single-triple
mutation of the committed sentinel fixture, applied in memory at test time
(no copied fixture files, so the mutants can never drift from the sentinel):
the Gate-2 prescribed process token's rdf:type is swapped to

  - :BiometricVerificationProcess (the WRONG regulated kind for 1(a)), or
  - :OperationalProcess (NEITHER regulated kind — a prescribed token exists,
    so an existence-sensitive gate would fire; only a content-sensitive one
    blocks).

Gate 2 goes through the IUS subkind
:RemoteBiometricIdentificationIntendedUseSpec, defined by owl:someValuesFrom
:RemoteBiometricIdentificationProcess — a type-check on the prescribed token,
not an existence check on the IUS. Both mutants keep Gates 1 and 3 fully
satisfied AND keep the iao:0000136 aboutness references to
:RemoteBiometricIdentificationProcess on the IUS and USS, proving that mere
aboutness-of-the-regulated-class does not satisfy the gate.

Expected on both mutants:
  - AnnexIII1aApplicableSystem NOT entailed (the content check blocks);
  - AnnexIII5bApplicableSystem NOT entailed;
  - HighRiskSystem entailed (the capability-only bridge deliberately fires on
    Gate 1 alone — latent-disposition flag present, no category classification);
  - the latent-risk audit ASK (detect_latent_risk.sparql) returns True.

Integrity pre-checks on the asserted sentinel graph (before mutation) guard
the test against becoming vacuous if the sentinel is later edited (e.g. the
aboutness references removed, or the token renamed).

Run from repo root or any subdirectory:
  python 03_TECHNICAL_CORE/scripts/test_gate2_mistype.py
Exit 0 = all expectations hold on both mutants. Exit 1 = failure (printed).
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
REASONING_DIR = REPO_ROOT / "03_TECHNICAL_CORE" / "reasoning"

BFO_2020 = ONTOLOGY_DIR / "imports" / "bfo-2020.owl"
IAO_BOT = ONTOLOGY_DIR / "imports" / "iao_bot.owl"
RO_BOT = ONTOLOGY_DIR / "imports" / "ro_bot.owl"
CCO_BOT = ONTOLOGY_DIR / "imports" / "cco_bot.owl"
CORE = ONTOLOGY_DIR / "ARCO_core.ttl"
GOV = ONTOLOGY_DIR / "ARCO_governance_extension.ttl"

LATENT_RISK_QUERY = REASONING_DIR / "detect_latent_risk.sparql"

ARCO = Namespace("https://arco.ai/ontology/core#")
RDF_NS = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
IAO_IS_ABOUT = URIRef("http://purl.obolibrary.org/obo/IAO_0000136")
RO_HAS_DISPOSITION = URIRef("http://purl.obolibrary.org/obo/RO_0000091")
CCO = Namespace("http://www.ontologyrepository.com/CommonCoreOntologies/")

SYSTEM = ARCO["Sentinel_ID_System"]
TOKEN = ARCO["Sentinel_RBIP_Process"]

SENTINEL = ONTOLOGY_DIR / "ARCO_instances_sentinel.ttl"
REGULATED_KIND = ARCO["RemoteBiometricIdentificationProcess"]

MUTATIONS = [
    {
        "label": "MISTYPED KIND (token retyped :BiometricVerificationProcess)",
        "token_type": ARCO["BiometricVerificationProcess"],
    },
    {
        "label": "NEITHER KIND (token retyped :OperationalProcess)",
        "token_type": ARCO["OperationalProcess"],
    },
]

# Identical expectations for both mutants: no category classification,
# latent-disposition flag present.
EXPECTED = {
    "AnnexIII1aApplicableSystem": False,
    "AnnexIII5bApplicableSystem": False,
    "HighRiskSystem": True,
}


def load_asserted(instance_file: Path) -> Graph:
    g = Graph()
    for p in (BFO_2020, IAO_BOT, RO_BOT, CCO_BOT, CORE, GOV, instance_file):
        if not p.exists():
            raise FileNotFoundError(f"Missing: {p}")
        g.parse(p.as_posix(), format="xml" if p.suffix == ".owl" else "turtle")
    return g


def run_ask(g: Graph, query_path: Path, bindings: dict) -> bool:
    result = g.query(query_path.read_text(encoding="utf-8"), initBindings=bindings)
    return bool(result.askAnswer)


def main() -> None:
    print("=" * 72)
    print("GATE-2 MISTYPE REGRESSION TEST (content-sensitivity)")
    print("=" * 72)

    all_pass = True

    def check(label: str, ok: bool) -> None:
        nonlocal all_pass
        print(f"  {label}: {'OK' if ok else 'FAIL'}")
        if not ok:
            all_pass = False

    for mutation in MUTATIONS:
        print(f"\n--- {mutation['label']} ---")
        g = load_asserted(SENTINEL)

        # Sentinel-integrity pre-check (before mutation): the committed
        # fixture must carry the regulated token type we are about to swap,
        # or the mutation (and the negative expectations) would be vacuous.
        check("sentinel asserts the regulated token type (pre-mutation)",
              (TOKEN, RDF_NS["type"], REGULATED_KIND) in g)

        # THE MUTATION: swap exactly one rdf:type triple, in memory.
        g.remove((TOKEN, RDF_NS["type"], REGULATED_KIND))
        g.add((TOKEN, RDF_NS["type"], mutation["token_type"]))

        # Post-mutation integrity checks: every gate satisfier EXCEPT the
        # regulated token type must still be present, or the negative
        # expectations become vacuous.
        check("gate-1 disposition edge asserted",
              (ARCO["Sentinel_FaceID_Module"], RO_HAS_DISPOSITION,
               ARCO["Sentinel_FaceID_Disposition"]) in g)
        check("gate-2 prescribes edge asserted",
              (ARCO["Sentinel_IntendedUse_001"], CCO["prescribes"], TOKEN) in g)
        check("gate-3 designates edge asserted",
              (ARCO["Sentinel_UseScenario_001"], CCO["designates"],
               ARCO["NaturalPersonRole"]) in g)
        check("IUS aboutness reference to the regulated process class asserted",
              (ARCO["Sentinel_IntendedUse_001"], IAO_IS_ABOUT,
               ARCO["RemoteBiometricIdentificationProcess"]) in g)
        check("token asserted as the mutant type",
              (TOKEN, RDF_NS["type"], mutation["token_type"]) in g)
        check("token NOT asserted as the regulated kind",
              (TOKEN, RDF_NS["type"],
               ARCO["RemoteBiometricIdentificationProcess"]) not in g)

        # Reason and test the expected classification outcomes.
        initial = len(g)
        owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(g)
        print(f"  Triples: {initial} -> {len(g)} (+{len(g) - initial})")

        for cls_name, expected in EXPECTED.items():
            actual = (SYSTEM, RDF_NS["type"], ARCO[cls_name]) in g
            check(f"{cls_name}: {actual} (expected {expected})",
                  actual == expected)

        latent = run_ask(g, LATENT_RISK_QUERY, {"system": SYSTEM})
        check(f"latent-risk audit ASK: {latent} (expected True)", latent is True)

    print()
    print("=" * 72)
    if all_pass:
        print("ALL GATE-2 MISTYPE TESTS PASSED")
        print("Gates are content-sensitive: a mistyped prescribed token blocks")
        print("category entailment while the latent-disposition flag stays on.")
    else:
        print("SOME GATE-2 MISTYPE TESTS FAILED")
    print("=" * 72)

    if not all_pass:
        sys.exit(1)


if __name__ == "__main__":
    main()
