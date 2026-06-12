"""
test_genus_elicitation.py — regression test for the L2.12 component-D output
carrier (walk-up remoteness elicitation, OPEN_PROBLEMS L2.12 / LIMITATIONS §3.7.d).

When the asserted prescribed process types as the bare 1:N genus
(:BiometricIdentificationProcess), the negative/counterfactual panel must ask
the Article 3(41) remoteness question (the single reviewed commitment that
would change the outcome) instead of presenting a stable-looking endpoint.

Asserts:
  1. A Sentinel-derived fixture whose process token is retyped to the bare
     genus produces an HTML view containing the elicitation question.
  2. The verification kiosk (verification-typed process, adjudicated negative)
     does NOT contain the elicitation question.

Run: python 03_TECHNICAL_CORE/scripts/test_genus_elicitation.py
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PIPELINE = REPO_ROOT / "03_TECHNICAL_CORE" / "scripts" / "run_pipeline.py"
ONTOLOGY_DIR = REPO_ROOT / "03_TECHNICAL_CORE" / "ontology"
HTML_OUTPUT = REPO_ROOT / "runs" / "demo" / "determination_view.html"

ELICITATION_MARKER = "Open elicitation question (Article 3(41))"


def run_pipeline(instances: Path, system: str) -> None:
    result = subprocess.run(
        [sys.executable, str(PIPELINE), "--instances", str(instances), "--system", system],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    # exit 0 expected: genus fixture is latent-flag-only (classification layer
    # passes; audit not applicable / passes) and kiosk is the honest negative
    if result.returncode != 0:
        print(result.stdout[-2000:])
        print(result.stderr[-2000:])
        raise RuntimeError(f"pipeline exited {result.returncode} on {instances.name}")


def main() -> None:
    print("=" * 72)
    print("GENUS ELICITATION PROMPT TEST (L2.12 component D)")
    print("=" * 72)
    all_pass = True

    sentinel = (ONTOLOGY_DIR / "ARCO_instances_sentinel.ttl").read_text(encoding="utf-8")
    genus_ttl = sentinel.replace(
        ":RemoteBiometricIdentificationProcess", ":BiometricIdentificationProcess"
    )
    with tempfile.TemporaryDirectory() as td:
        genus_fixture = Path(td) / "ARCO_instances_genus_walkup.ttl"
        genus_fixture.write_text(genus_ttl, encoding="utf-8")
        run_pipeline(genus_fixture, "Sentinel_ID_System")
        html = HTML_OUTPUT.read_text(encoding="utf-8")
        ok = ELICITATION_MARKER in html
        print(f"  genus-typed fixture: elicitation prompt present [{'OK' if ok else 'FAIL'}]")
        all_pass &= ok

    run_pipeline(ONTOLOGY_DIR / "ARCO_instances_verification.ttl", "VerificationKiosk_001")
    html = HTML_OUTPUT.read_text(encoding="utf-8")
    ok = ELICITATION_MARKER not in html
    print(f"  verification kiosk: elicitation prompt absent [{'OK' if ok else 'FAIL'}]")
    all_pass &= ok

    print("=" * 72)
    print("ALL ELICITATION TESTS PASSED" if all_pass else "SOME ELICITATION TESTS FAILED")
    print("=" * 72)
    if not all_pass:
        sys.exit(1)


if __name__ == "__main__":
    main()
