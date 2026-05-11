"""
test_kiosk_html_no_false_concretization.py — regression test for OPEN_PROBLEMS L4.7.

Runs the pipeline against `ARCO_instances_verification.ttl` (VerificationKiosk_001)
and asserts the rendered HTML view does not emit the Gate 2 affirmative sentence
"...prescribes the system for...". The kiosk's IUS prescribes a
`:BiometricVerificationProcess` token, NOT the regulated
`:RemoteBiometricIdentificationProcess` that Annex III 1(a) Gate 2 keys on.

Pre-fix (run_pipeline.py:806 binding `gate2_ok = intended_use_ok`):
the documentary ASK `check_intended_use.sparql` returns TRUE on the kiosk
(an IUS exists, prescribing some process, with a USS designating
NaturalPersonRole), so the HTML Gate 2 affirmative branch fires AND the
Python literal fallback `or "RemoteBiometricIdentificationProcess"` at line 816
emits the regulated class name into a sentence about the kiosk — false against
the loaded TTL.

Post-fix (gate2_ok bound to typed-evidence presence): the kiosk emits the
negative branch ("No matching prescribed process type found...") and the
sentence "prescribes the system for ..." does not appear.

Run from repo root:
    python 03_TECHNICAL_CORE/scripts/test_kiosk_html_no_false_concretization.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PIPELINE = REPO_ROOT / "03_TECHNICAL_CORE" / "scripts" / "run_pipeline.py"
KIOSK_TTL = REPO_ROOT / "03_TECHNICAL_CORE" / "ontology" / "ARCO_instances_verification.ttl"
HTML_OUTPUT = REPO_ROOT / "runs" / "demo" / "determination_view.html"

GATE_2_AFFIRMATIVE_PHRASE = "prescribes the system for"


def main() -> int:
    result = subprocess.run(
        [
            sys.executable,
            str(PIPELINE),
            "--instances",
            str(KIOSK_TTL),
            "--system",
            "VerificationKiosk_001",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"FAIL: pipeline exit {result.returncode}")
        print(result.stdout[-500:])
        print(result.stderr[-500:])
        return 1

    if not HTML_OUTPUT.exists():
        print(f"FAIL: HTML view not generated at {HTML_OUTPUT}")
        return 1

    # Precondition: verify kiosk TTL really does not prescribe the regulated process class
    kiosk_ttl = KIOSK_TTL.read_text(encoding="utf-8")
    if ":RemoteBiometricIdentificationProcess" in kiosk_ttl:
        print(
            "PRECONDITION FAIL: kiosk TTL asserts :RemoteBiometricIdentificationProcess; "
            "test premise (kiosk does not prescribe the regulated class) is invalid."
        )
        return 1

    html = HTML_OUTPUT.read_text(encoding="utf-8")

    # Regression assertion: the Gate 2 affirmative phrase ("prescribes the system for")
    # must NOT appear in the kiosk's rendered HTML. The phrase is generated only by
    # the Gate 2 affirmative branch at run_pipeline.py:849; its presence on a kiosk
    # run means gate2_ok was True on a system whose IUS does not prescribe a
    # regulated process class.
    if GATE_2_AFFIRMATIVE_PHRASE in html:
        idx = html.find(GATE_2_AFFIRMATIVE_PHRASE)
        context = html[max(0, idx - 80) : idx + len(GATE_2_AFFIRMATIVE_PHRASE) + 200]
        context_clean = " ".join(context.split())
        print(
            "FAIL: kiosk HTML emits Gate 2 affirmative sentence on a system whose IUS "
            "does not prescribe a regulated process class. OPEN_PROBLEMS L4.7."
        )
        print(f"  Context: ...{context_clean}...")
        return 1

    print(
        "PASS: kiosk HTML does not emit the Gate 2 affirmative sentence. "
        "L4.7 regression gate green."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
