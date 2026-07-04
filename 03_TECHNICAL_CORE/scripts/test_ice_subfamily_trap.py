"""
ICE-subfamily disjointness trap guard (fail-closed regression).

A single Information Content Entity individual asserting BOTH cco:designates
and cco:prescribes is entailed into two pairwise-disjoint CCO classes under
the pinned CCO v1.7 slim (cco:designates has rdfs:domain
DesignativeInformationContentEntity, cco:prescribes has rdfs:domain
DirectiveInformationContentEntity, and the two domain classes are
owl:disjointWith each other). Both detection rules — prp-dom and cax-dw —
sit inside OWL 2 RL, so the production pipeline must halt fail-closed during
REASONING: nonzero exit, the disjoint pair and the trap individual named in
the diagnostics, and no certificate emitted. The CI HermiT leg independently
reports the same merge inconsistent.

This test pins three behaviors on the committed trap fixture
(03_TECHNICAL_CORE/ontology/probes/probe_ice_subfamily_trap.ttl):

  1. run_pipeline.py exits nonzero on the trap (fail-closed; a regression
     that silently swallowed the reasoner's error messages would pass the
     trap through to SHACL/audits/certificate and exit 0 — caught here);
  2. the diagnostics name the violated disjoint pair
     (DesignativeInformationContentEntity / DirectiveInformationContentEntity)
     and the trap individual, so a trapped fixture author sees WHICH
     assertion pair to fix;
  3. the failure happens before certificate emission (no "ALL CHECKS PASSED"
     and no certificate banner in the output).

The trap is a fixture-authoring landmine, not a modeling pattern: the
fixture's own header carries the authoring warning (never put designates and
prescribes on one ICE individual; split into two ICEs).

Run from repo root or any subdirectory:
  python 03_TECHNICAL_CORE/scripts/test_ice_subfamily_trap.py
Exit 0 = all three pins hold. Exit 1 = regression (printed).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "03_TECHNICAL_CORE" / "scripts"
ONTOLOGY_DIR = REPO_ROOT / "03_TECHNICAL_CORE" / "ontology"

PIPELINE = SCRIPTS_DIR / "run_pipeline.py"
TRAP_FIXTURE = ONTOLOGY_DIR / "probes" / "probe_ice_subfamily_trap.ttl"

DISJOINT_PAIR = (
    "DesignativeInformationContentEntity",
    "DirectiveInformationContentEntity",
)
TRAP_INDIVIDUAL = "ICETrap_ICE"


def main() -> None:
    print("=" * 72)
    print("ICE-SUBFAMILY DISJOINTNESS TRAP GUARD (fail-closed regression)")
    print("=" * 72)

    for required in (PIPELINE, TRAP_FIXTURE):
        if not required.exists():
            print(f"ERROR: missing required file: {required}")
            sys.exit(1)

    print(f"\nRunning pipeline on trap fixture: {TRAP_FIXTURE.name}")
    result = subprocess.run(
        [sys.executable, str(PIPELINE),
         "--instances", str(TRAP_FIXTURE),
         "--system", "ICETrap_Carrier_System"],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    output = (result.stdout or "") + (result.stderr or "")

    all_pass = True

    def check(label: str, ok: bool) -> None:
        nonlocal all_pass
        print(f"  {label}: {'OK' if ok else 'FAIL'}")
        if not ok:
            all_pass = False

    # 1. Fail-closed: nonzero exit during REASONING.
    check(f"pipeline exit code nonzero (got {result.returncode})",
          result.returncode != 0)
    check("output reports a disjointness violation",
          "disjointness violation" in output.lower()
          or "disjointness violations detected" in output.lower())

    # 2. Diagnostics name the disjoint pair and the trap individual.
    for cls in DISJOINT_PAIR:
        check(f"output names disjoint class {cls}", cls in output)
    check(f"output names trap individual {TRAP_INDIVIDUAL}",
          TRAP_INDIVIDUAL in output)

    # 3. Halt precedes SHACL, audits, and certificate emission: the failure
    # is raised inside REASONING, so the SHACL stage header and the pass
    # banner must both be absent from the output.
    check("halt precedes SHACL stage (no SHACL section in output)",
          "SHACL" not in output)
    check("no 'ALL CHECKS PASSED' in output", "ALL CHECKS PASSED" not in output)

    print()
    print("=" * 72)
    if all_pass:
        print("ICE-SUBFAMILY TRAP GUARD PASSED")
        print("Trap fails closed; disjoint pair and individual named; no certificate.")
    else:
        print("ICE-SUBFAMILY TRAP GUARD FAILED")
        print("--- pipeline output (last 40 lines) ---")
        for line in output.splitlines()[-40:]:
            print(f"  {line}")
    print("=" * 72)

    if not all_pass:
        sys.exit(1)


if __name__ == "__main__":
    main()
