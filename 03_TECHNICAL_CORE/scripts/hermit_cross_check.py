"""
HermiT vs OWL-RL cross-reasoner agreement check across certificate-grade fixtures.

Replaces the Sentinel-only Phase 3 logic in .github/workflows/robot-validate.yml.
For every certificate-grade fixture, merges ontology + imports + core + governance
+ fixture, runs HermiT via ROBOT, runs OWL-RL via owlrl, and diffs SPARQL ASK
results bound to each fixture's system IRI(s).

Exits 0 iff both reasoners agree on every (fixture, system, query) triple in the
certificate-grade set. Exits 1 otherwise.

Excluded fixtures:

  GhostSystem (ARCO_instances_adversarial_blanknode.ttl) — its disposition is an
  anonymous individual (blank node). HermiT does not emit ClassAssertion axioms
  for anonymous individuals (DL profile behavior, not a defect), so the audit-side
  detect_latent_risk traversal returns False under HermiT and True under OWL-RL.
  GhostSystem is a reasoner-property probe, not production modeling guidance. The
  decision to require named evidence-bearing particulars is queued for human
  modeling session — see:
    runs/loop/2026-05-09_beverley-research/design_memo_named-evidence-bearing-particulars.md
    runs/loop/2026-05-09_beverley-research/modeling_decisions_queue.md (Q1)

ROBOT JAR is located at:
  $ROBOT_JAR if set
  $HOME/.local/share/robot/robot.jar otherwise

Run from repo root or any subdirectory:
  python 03_TECHNICAL_CORE/scripts/hermit_cross_check.py
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Iterable

from rdflib import Graph, Namespace, URIRef

try:
    import owlrl
except ImportError:
    print("FATAL: owlrl not installed. pip install owlrl==7.1.4", file=sys.stderr)
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parents[2]
ONTOLOGY_DIR = REPO_ROOT / "03_TECHNICAL_CORE" / "ontology"
REASONING_DIR = REPO_ROOT / "03_TECHNICAL_CORE" / "reasoning"

ROBOT_JAR = Path(os.environ.get("ROBOT_JAR", str(Path.home() / ".local" / "share" / "robot" / "robot.jar")))

BFO_2020 = ONTOLOGY_DIR / "imports" / "bfo-2020.owl"
IAO_BOT = ONTOLOGY_DIR / "imports" / "iao_bot.owl"
RO_BOT = ONTOLOGY_DIR / "imports" / "ro_bot.owl"
CCO_BOT = ONTOLOGY_DIR / "imports" / "cco_bot.owl"
CORE = ONTOLOGY_DIR / "ARCO_core.ttl"
GOV = ONTOLOGY_DIR / "ARCO_governance_extension.ttl"

ARCO = Namespace("https://arco.ai/ontology/core#")

# Certificate-grade scenarios. Each entry: (fixture_basename, [system_local_names])
# GhostSystem is intentionally absent. See module docstring.
CERTIFICATE_GRADE_SCENARIOS: list[tuple[str, list[str]]] = [
    ("ARCO_instances_sentinel.ttl",              ["Sentinel_ID_System"]),
    ("ARCO_instances_creditscoring.ttl",         ["CreditScorer_001"]),
    ("ARCO_instances_verification.ttl",          ["VerificationKiosk_001"]),
    ("ARCO_instances_adversarial_decoy.ttl",     ["DecoySystem_001"]),
    ("ARCO_instances_adversarial_decoy_5b.ttl",  ["WeirdCalcSystem_001"]),
    ("ARCO_instances_flag_tests.ttl",            ["FlagTest_BiometricSystem_WithDerogationClaim",
                                                  "FlagTest_CreditSystem_WithFraudProcess"]),
]

QUERIES: dict[str, Path] = {
    "high_risk": REASONING_DIR / "check_high_risk_inference.sparql",
    "annex_1a":  REASONING_DIR / "check_annex_iii_1a_entailment.sparql",
    "annex_5b":  REASONING_DIR / "check_annex_iii_5b_entailment.sparql",
    "latent":    REASONING_DIR / "detect_latent_risk.sparql",
}

ONTOLOGY_INPUTS = (BFO_2020, IAO_BOT, RO_BOT, CCO_BOT, CORE, GOV)


def reason_owlrl(instance_file: Path) -> Graph:
    g = Graph()
    for p in (*ONTOLOGY_INPUTS, instance_file):
        fmt = "xml" if p.suffix == ".owl" else "turtle"
        g.parse(p.as_posix(), format=fmt)
    owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(g)
    return g


def reason_hermit(instance_file: Path, workdir: Path) -> Graph:
    merged = workdir / "merged.owl"
    reasoned = workdir / "reasoned.owl"
    merge_cmd = ["java", "-jar", str(ROBOT_JAR), "merge"]
    for p in (*ONTOLOGY_INPUTS, instance_file):
        merge_cmd += ["--input", str(p)]
    merge_cmd += ["--output", str(merged)]
    r = subprocess.run(merge_cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"ROBOT merge failed for {instance_file.name}:\n{r.stderr}")

    reason_cmd = [
        "java", "-jar", str(ROBOT_JAR), "reason",
        "--reasoner", "hermit",
        "--axiom-generators", "ClassAssertion SubClass",
        "--include-indirect", "true",
        "--input", str(merged),
        "--output", str(reasoned),
    ]
    r = subprocess.run(reason_cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"ROBOT/HermiT reason failed for {instance_file.name}:\n{r.stderr}")

    g = Graph()
    g.parse(str(reasoned), format="xml")
    return g


def ask_all(g: Graph, system_iri: URIRef) -> dict[str, bool]:
    return {
        name: bool(g.query(qpath.read_text(), initBindings={"system": system_iri}))
        for name, qpath in QUERIES.items()
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="HermiT vs OWL-RL cross-reasoner agreement check across certificate-grade fixtures.",
    )
    parser.add_argument(
        "--fixture",
        default=None,
        help="Run only the named fixture file (e.g. ARCO_instances_sentinel.ttl). "
             "If omitted, runs all certificate-grade fixtures sequentially. "
             "Used by the matrix-strategy CI workflow to fan out per-fixture jobs.",
    )
    args = parser.parse_args()

    if args.fixture:
        scenarios = [(f, s) for f, s in CERTIFICATE_GRADE_SCENARIOS if f == args.fixture]
        if not scenarios:
            valid = [f for f, _ in CERTIFICATE_GRADE_SCENARIOS]
            print(f"FATAL: --fixture '{args.fixture}' not in certificate-grade set.", file=sys.stderr)
            print(f"Valid fixtures: {valid}", file=sys.stderr)
            return 2
    else:
        scenarios = list(CERTIFICATE_GRADE_SCENARIOS)

    if not ROBOT_JAR.exists():
        print(f"FATAL: ROBOT JAR not found at {ROBOT_JAR}.", file=sys.stderr)
        print("Set ROBOT_JAR env var or place jar at $HOME/.local/share/robot/robot.jar.", file=sys.stderr)
        return 2

    print("=" * 92)
    if args.fixture:
        print(f"HermiT vs OWL-RL cross-reasoner agreement check (single fixture: {args.fixture})")
    else:
        print("HermiT vs OWL-RL cross-reasoner agreement check (certificate-grade fixtures)")
    print("=" * 92)
    print(f"ROBOT JAR: {ROBOT_JAR}")
    print(f"Excluded fixtures: GhostSystem (anonymous-individual probe, queued for modeling session).")
    print()
    print(f"{'System':<48} {'Query':<11} {'OWL-RL':>7} {'HermiT':>7} Status")
    print("-" * 92)

    all_agree = True
    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        for fixture_name, system_names in scenarios:
            instance_file = ONTOLOGY_DIR / fixture_name

            try:
                g_rl = reason_owlrl(instance_file)
            except Exception as e:
                print(f"ERROR: OWL-RL failed for {fixture_name}: {e}", file=sys.stderr)
                return 2

            try:
                g_dl = reason_hermit(instance_file, workdir)
            except Exception as e:
                print(f"ERROR: HermiT failed for {fixture_name}: {e}", file=sys.stderr)
                return 2

            for sys_name in system_names:
                system_iri = ARCO[sys_name]
                rl = ask_all(g_rl, system_iri)
                dl = ask_all(g_dl, system_iri)
                for qname in QUERIES:
                    agree = rl[qname] == dl[qname]
                    if not agree:
                        all_agree = False
                    status = "OK" if agree else "DISAGREE"
                    print(f"{sys_name:<48} {qname:<11} {str(rl[qname]):>7} {str(dl[qname]):>7} {status}")

    print()
    print("=" * 92)
    if all_agree:
        print("RESULT: HermiT and OWL-RL agree on every (fixture, system, query) in the certificate-grade set.")
        return 0
    else:
        print("RESULT: HermiT and OWL-RL disagree on at least one query.")
        print("        Diagnose: RL incompleteness, unexpected DL entailment, or new reasoner-profile divergence.")
        print("        If a new fixture introduces blank-node SDCs, see:")
        print("          runs/loop/2026-05-09_beverley-research/modeling_decisions_queue.md (Q1)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
