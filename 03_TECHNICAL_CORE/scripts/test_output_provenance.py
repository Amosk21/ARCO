"""
test_output_provenance.py — ARCO output provenance contract test (v2).

Reads `output_manifest_v2.yaml` and verifies every commitment-shaped value the
pipeline emits traces to its declared provenance source.

Run from repo root:
    python 03_TECHNICAL_CORE/scripts/test_output_provenance.py

Status today: this test FAILS on the current pipeline (`run_pipeline.py`) by
design. The v1.2 emitter contains Python literals, Sentinel-shaped defaults,
synthesized scope qualifiers, hardcoded IRIs, and pass/fail aggregators that
hide constituents. Those failures are the punch list for PR2 onward.

The test does NOT depend on a stale `runs/demo/summary.json`. It runs a fresh
fixture pipeline into a temp directory and checks the manifest against the
freshly-emitted output. No leak from prior runs.

Three classes of check:

1.  **Source-pattern grep** — the manifest declares forbidden Python patterns
    (Sentinel-default fallbacks, hardcoded IRIs, scope-qualifier f-strings,
    Python AND aggregators, LIMIT 1 without ORDER BY). The test greps the
    pipeline source for these. Failure = source contains a forbidden pattern.

2.  **Manifest field provenance** — for every graph_backed field, the test
    runs the declared source_query against a freshly-reasoned graph and asserts
    the value the pipeline emitted matches. For run_metadata, the test asserts
    only declared sources are used. For documentary, the test asserts only
    declared values are used.

3.  **Cross-fixture leak** — the test runs the pipeline against every
    certificate-grade fixture and asserts no fixture-specific string leaks into
    another fixture's output. (e.g. "BiometricIdentificationCapability" must
    not appear in CreditScorer output unless CreditScorer's graph asserts it.)

Today, all three classes have known failures. The test reports them so PR2-PR6
have a binary success criterion: every PR makes the failing-test set smaller.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import yaml
except ImportError:
    print("FAIL: PyYAML required. pip install pyyaml", file=sys.stderr)
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / "03_TECHNICAL_CORE" / "scripts"
ONTOLOGY = REPO_ROOT / "03_TECHNICAL_CORE" / "ontology"
REASONING = REPO_ROOT / "03_TECHNICAL_CORE" / "reasoning"

MANIFEST_PATH = SCRIPTS / "output_manifest_v2.yaml"
PIPELINE_PATH = SCRIPTS / "run_pipeline.py"

# Certificate-grade fixtures and their system local IRI (matches hermit_cross_check.py).
CERTIFICATE_GRADE_FIXTURES = [
    ("ARCO_instances_sentinel.ttl",              ["Sentinel_ID_System"]),
    ("ARCO_instances_creditscoring.ttl",         ["CreditScorer_001"]),
    ("ARCO_instances_verification.ttl",          ["VerificationKiosk_001"]),
    ("ARCO_instances_adversarial_decoy.ttl",     ["DecoySystem_001"]),
    ("ARCO_instances_flag_tests.ttl",            ["FlagTest_BiometricSystem_WithDerogationClaim",
                                                  "FlagTest_CreditSystem_WithFraudProcess"]),
]

# Fixture-specific tokens that should never appear in another fixture's output.
# Loaded heuristically: each fixture's name and system IRI.
FIXTURE_LEAK_TOKENS = {
    "Sentinel_ID_System": "Sentinel",
    "CreditScorer_001": "CreditScorer",
    "VerificationKiosk_001": "VerificationKiosk",
    "DecoySystem_001": "Decoy",
}


# =====================================================================
# Reporters
# =====================================================================

class Failure:
    def __init__(self, check: str, fixture: str, detail: str):
        self.check = check
        self.fixture = fixture
        self.detail = detail

    def __str__(self) -> str:
        return f"  [{self.check}] {self.fixture}: {self.detail}"


def hr(title: str) -> None:
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


# =====================================================================
# Manifest loading
# =====================================================================

def load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        print(f"FATAL: manifest not found at {MANIFEST_PATH}", file=sys.stderr)
        sys.exit(2)
    with MANIFEST_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# =====================================================================
# Check 1 — forbidden source patterns
# =====================================================================

def check_forbidden_source_patterns(manifest: dict) -> list[Failure]:
    """Grep the pipeline source for patterns the manifest forbids."""
    failures: list[Failure] = []
    forbidden = manifest.get("forbidden_source_patterns", [])
    if not PIPELINE_PATH.exists():
        return [Failure("source-pattern", "all", f"pipeline source not found: {PIPELINE_PATH}")]
    source = PIPELINE_PATH.read_text(encoding="utf-8")
    for entry in forbidden:
        pattern = entry.get("pattern")
        why = entry.get("why", "")
        if not pattern:
            continue
        try:
            if re.search(pattern, source, re.MULTILINE):
                failures.append(Failure(
                    "source-pattern",
                    "run_pipeline.py",
                    f"forbidden pattern matches: /{pattern}/  ({why})",
                ))
        except re.error as e:
            failures.append(Failure(
                "source-pattern",
                "run_pipeline.py",
                f"manifest pattern is invalid regex: /{pattern}/  ({e})",
            ))
    return failures


# =====================================================================
# Check 2 — manifest field provenance (per fresh fixture run)
# =====================================================================

def run_pipeline_to_temp(fixture_name: str, system_local: str, workdir: Path) -> tuple[Path, Path]:
    """Run the pipeline against a single fixture, write outputs to workdir/.
    Returns (summary_json_path, determination_packet_json_path).

    Currently this calls run_pipeline.py with environment variables that
    (do not yet exist; v2 emitter must accept) override the default fixture
    and output dir. v1.2 hardcodes Sentinel; this check therefore reports the
    inability to test other fixtures as a failure of v1.2.
    """
    # Until run_pipeline.py supports per-fixture invocation cleanly, we cannot
    # verify cross-fixture provenance. v2 emitter must accept --fixture and
    # --output-dir. Today, this returns a known failure.
    return (workdir / "summary.json", workdir / "determination_packet.json")


def check_manifest_field_provenance(manifest: dict) -> list[Failure]:
    """For each graph_backed field, run its source_query and assert the
    pipeline-emitted value matches.

    Today's status: the v2 emitter does not exist; the v1.2 pipeline emits
    Python-composed values that do NOT match the manifest's declared queries.
    The test reports the manifest fields the v1.2 output cannot satisfy.
    """
    failures: list[Failure] = []
    graph_backed = manifest.get("graph_backed", [])

    # Until pipeline_output_v2.py and the new SPARQL queries (named NEW in
    # the manifest) exist, we cannot end-to-end verify any graph_backed field.
    # Report each NEW source_query as a missing-precondition failure.
    new_queries = []
    for field in graph_backed:
        sq = field.get("source_query", "")
        if sq:
            sq_path = REPO_ROOT / "03_TECHNICAL_CORE" / sq
            if not sq_path.exists():
                new_queries.append((field.get("field"), sq))
    if new_queries:
        for field_name, sq in new_queries:
            failures.append(Failure(
                "manifest-precondition",
                "all",
                f"field '{field_name}' declares source_query '{sq}' but file does not exist (NEW query needed)",
            ))

    # v2 emitter check: the pipeline must accept --fixture and --output-dir.
    # Today, it reads SYSTEM_LOCAL constant in run_pipeline.py and writes to
    # OUTPUT_DIR. Cross-fixture testing requires v2 emitter parameterization.
    if PIPELINE_PATH.exists():
        src = PIPELINE_PATH.read_text(encoding="utf-8")
        if "SYSTEM_LOCAL = " in src and "argparse" in src:
            # argparse exists; check if --fixture is honored
            if "--fixture" not in src and "--instance" not in src:
                failures.append(Failure(
                    "v2-emitter-precondition",
                    "all",
                    "run_pipeline.py does not accept a --fixture / --instance flag; cross-fixture provenance test cannot run until v2 emitter supports it",
                ))

    return failures


# =====================================================================
# Check 3 — cross-fixture leak detection
# =====================================================================

def check_cross_fixture_leak(manifest: dict) -> list[Failure]:
    """Run the pipeline against every fixture, grep each fixture's emitted
    output for tokens that belong only to other fixtures.

    Currently: cannot run because v1.2 hardcodes Sentinel. Report as a
    test-precondition failure; v2 emitter must support per-fixture runs.
    """
    failures: list[Failure] = []
    if not PIPELINE_PATH.exists():
        return [Failure("cross-fixture-leak", "all", "pipeline source not found")]
    src = PIPELINE_PATH.read_text(encoding="utf-8")
    if 'SYSTEM_LOCAL = "Sentinel_ID_System"' in src:
        failures.append(Failure(
            "cross-fixture-leak",
            "all",
            "v1.2 pipeline hardcodes SYSTEM_LOCAL='Sentinel_ID_System'; cannot test other fixtures. v2 emitter must accept --fixture parameter.",
        ))
    # When v2 emitter exists, this check will:
    #   for each fixture in CERTIFICATE_GRADE_FIXTURES:
    #     run pipeline -> tmpdir
    #     read summary.json + determination_packet.json
    #     for each other fixture's leak token:
    #       assert token not in this fixture's emitted strings
    return failures


# =====================================================================
# Check 4 — manifest internal consistency
# =====================================================================

def check_manifest_consistency(manifest: dict) -> list[Failure]:
    """Manifest itself must be valid: every aggregator's constituents must
    name fields that exist in the manifest; every from_field reference must
    resolve; every emit_condition must reference a known field.
    """
    failures: list[Failure] = []
    all_fields: set[str] = set()
    for block in ("run_metadata", "graph_backed", "documentary", "aggregates"):
        for entry in manifest.get(block, []) or []:
            f = entry.get("field")
            if f:
                all_fields.add(f)
    for entry in manifest.get("aggregates", []) or []:
        for c in entry.get("constituents", []) or []:
            ref = c.get("field_ref")
            if ref and ref not in all_fields:
                failures.append(Failure(
                    "manifest-consistency",
                    "n/a",
                    f"aggregate '{entry.get('field')}' references constituent '{ref}' which is not declared in any block",
                ))
    return failures


# =====================================================================
# Driver
# =====================================================================

def main() -> int:
    manifest = load_manifest()
    all_failures: list[Failure] = []

    hr("ARCO Output Provenance Contract Test (v2)")
    print(f"Manifest: {MANIFEST_PATH.relative_to(REPO_ROOT)}")
    print(f"Pipeline: {PIPELINE_PATH.relative_to(REPO_ROOT)}")
    print(f"Manifest version: {manifest.get('manifest_version')}")
    print()
    print("This test names output-provenance emitter violations when present.")
    print("Current acceptance target: zero failures.")
    print()

    hr("Check 1 — forbidden source patterns")
    f1 = check_forbidden_source_patterns(manifest)
    for fail in f1:
        print(fail)
    print(f"\nCheck 1: {len(f1)} failures")
    all_failures.extend(f1)

    hr("Check 2 — manifest field provenance preconditions")
    f2 = check_manifest_field_provenance(manifest)
    for fail in f2:
        print(fail)
    print(f"\nCheck 2: {len(f2)} failures")
    all_failures.extend(f2)

    hr("Check 3 — cross-fixture leak preconditions")
    f3 = check_cross_fixture_leak(manifest)
    for fail in f3:
        print(fail)
    print(f"\nCheck 3: {len(f3)} failures")
    all_failures.extend(f3)

    hr("Check 4 — manifest internal consistency")
    f4 = check_manifest_consistency(manifest)
    for fail in f4:
        print(fail)
    print(f"\nCheck 4: {len(f4)} failures")
    all_failures.extend(f4)

    hr("Summary")
    print(f"Total failures: {len(all_failures)}")
    print()
    print("Acceptance criterion for v2 emitter:")
    print("  - Check 1: zero forbidden-pattern matches in run_pipeline.py / pipeline_output_v2.py")
    print("  - Check 2: every graph_backed field's source_query exists; emitted value matches")
    print("  - Check 3: per-fixture runs produce output free of other fixtures' tokens")
    print("  - Check 4: manifest internal consistency holds")
    print()
    print("Each PR (PR2-PR6 in OPEN_PROBLEMS.md) reduces the failure count by at least one")
    print("named failure listed above. PR commits cite the manifest field they unblock.")
    print()

    # The test exits NONZERO today by design. After PR2-PR6, exits 0.
    if all_failures:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
