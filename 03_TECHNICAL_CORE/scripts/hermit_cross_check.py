"""
HermiT vs OWL-RL expected-polarity cross-check across certificate-grade fixtures.

Replaces the Sentinel-only Phase 3 logic in .github/workflows/robot-validate.yml.
For every certificate-grade fixture, merges ontology + imports + core + governance
+ fixture, runs HermiT via ROBOT, runs OWL-RL via owlrl, and asserts BOTH
reasoners' SPARQL ASK results against the expected polarity anchored in
test_scenarios.py SCENARIOS (the single source table — no expected values are
kept here).

Exits 0 iff both reasoners return the SCENARIOS-anchored expected value on
every (fixture, system, query) cell in the certificate-grade set. Exits 1 on
any wrong-polarity cell — including a correlated flip, where BOTH reasoners
return the same wrong answer (status BOTH-WRONG(AGREE); with boolean cells,
two answers that both differ from the expected value necessarily agree, so
RL-WRONG / DL-WRONG / BOTH-WRONG(AGREE) are the only failure shapes).
Exits 2 on configuration errors, kept distinct from polarity failures:
missing anchor entry or key (a fixture in the cross-check set but not in
SCENARIOS), an empty system list, or a cell count that does not match
len(systems) x len(queries) (a never-reasoned slot).

Register anchor: OPEN_PROBLEMS L4.8 item 5. Before this version the script
asserted agreement only (rl == dl per cell), so a both-reasoners-wrong flip,
an all-False mistyped-IRI run, and an empty matrix slot all exited 0.

Excluded fixtures:

  GhostSystem (ARCO_instances_adversarial_blanknode.ttl) — its disposition is an
  anonymous individual (blank node). HermiT does not emit ClassAssertion axioms
  for anonymous individuals (DL profile behavior, not a defect), so the audit-side
  detect_latent_risk traversal returns False under HermiT and True under OWL-RL.
  GhostSystem is a reasoner-property probe, not production modeling guidance. The
  decision to require named evidence-bearing particulars is queued for human
  modeling session — see:
    the local design memos and modeling-decisions queue (runs/loop, untracked; Q1)

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

# Expected-polarity anchor: SCENARIOS in test_scenarios.py is the single
# source (L4.8 item 5). Import, never copy — a second table here is exactly
# the drift this fix removes.
from test_scenarios import SCENARIOS  # noqa: E402  (same directory)

QUERY_TO_EXPECTED_KEY: dict[str, str] = {
    "high_risk": "HighRiskSystem",
    "annex_1a":  "AnnexIII1aApplicableSystem",
    "annex_5b":  "AnnexIII5bApplicableSystem",
    "latent":    "latent_risk",
}
EXPECTED: dict[str, dict] = {s["name"]: s["expected"] for s in SCENARIOS}

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

    # ── Anchor-completeness guard (configuration, not polarity) ──────────
    # Every (fixture, system) in the selected set must have a SCENARIOS entry
    # carrying all four mapped keys, and no slot may have an empty system
    # list. This is what keeps the anchor gaps from silently re-opening when
    # a fixture is added to the cross-check but not to SCENARIOS.
    config_errors: list[str] = []
    for fixture_name, system_names in scenarios:
        if not system_names:
            config_errors.append(f"{fixture_name}: empty system list (never-reasoned slot)")
        for sys_name in system_names:
            anchor = EXPECTED.get(sys_name)
            if anchor is None:
                config_errors.append(
                    f"{sys_name} ({fixture_name}): no SCENARIOS entry in test_scenarios.py")
                continue
            for qname, key in QUERY_TO_EXPECTED_KEY.items():
                if key not in anchor:
                    config_errors.append(
                        f"{sys_name} ({fixture_name}): SCENARIOS expected dict lacks "
                        f"'{key}' (anchors query '{qname}')")
    if config_errors:
        print("FATAL: expected-polarity anchor incomplete:", file=sys.stderr)
        for err in config_errors:
            print(f"  - {err}", file=sys.stderr)
        return 2

    print("=" * 104)
    if args.fixture:
        print(f"HermiT vs OWL-RL expected-polarity cross-check (single fixture: {args.fixture})")
    else:
        print("HermiT vs OWL-RL expected-polarity cross-check (certificate-grade fixtures)")
    print("=" * 104)
    print(f"ROBOT JAR: {ROBOT_JAR}")
    print("Expected values: SCENARIOS in test_scenarios.py (single anchor table).")
    print(f"Excluded fixtures: GhostSystem (anonymous-individual probe, queued for modeling session).")
    print()
    print(f"{'System':<48} {'Query':<11} {'Expected':>8} {'OWL-RL':>7} {'HermiT':>7} Status")
    print("-" * 104)

    cell_results: list[bool] = []
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
                    exp = EXPECTED[sys_name][QUERY_TO_EXPECTED_KEY[qname]]
                    rl_ok = rl[qname] == exp
                    dl_ok = dl[qname] == exp
                    agree = rl[qname] == dl[qname]  # implied by rl_ok and dl_ok; kept visible
                    cell_pass = rl_ok and dl_ok
                    if cell_pass:
                        status = "OK"
                    elif not rl_ok and not dl_ok:
                        status = "BOTH-WRONG(AGREE)" if agree else "BOTH-WRONG"
                    elif not rl_ok:
                        status = "RL-WRONG"
                    else:
                        status = "DL-WRONG"
                    cell_results.append(cell_pass)
                    print(f"{sys_name:<48} {qname:<11} {str(exp):>8} "
                          f"{str(rl[qname]):>7} {str(dl[qname]):>7} {status}")

    # ── Cell-count guard (never-reasoned slot) ────────────────────────────
    expected_cells = sum(len(names) for _, names in scenarios) * len(QUERIES)
    if len(cell_results) != expected_cells or not cell_results:
        print(f"FATAL: cell count {len(cell_results)} != expected {expected_cells} "
              f"(a slot was skipped or never reasoned).", file=sys.stderr)
        return 2

    print()
    print("=" * 104)
    if all(cell_results):
        print(f"RESULT: both reasoners match the SCENARIOS-anchored expected polarity on all "
              f"{len(cell_results)} (fixture, system, query) cells.")
        return 0
    else:
        n_bad = sum(1 for ok in cell_results if not ok)
        print(f"RESULT: {n_bad} of {len(cell_results)} cells FAIL expected polarity.")
        print("        RL-WRONG / DL-WRONG: one reasoner diverges — RL incompleteness,")
        print("        unexpected DL entailment, or new reasoner-profile divergence.")
        print("        BOTH-WRONG(AGREE): correlated flip — an ontology/fixture regression")
        print("        both reasoners follow; check the axioms and the SCENARIOS anchor.")
        print("        If a new fixture introduces blank-node SDCs, see:")
        print("          the local modeling-decisions queue (runs/loop, untracked; Q1)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
