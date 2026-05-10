"""Smoke test for the ARCO MCP server.

Verifies:
  1. The server module imports cleanly.
  2. All three tool functions are registered with the FastMCP instance.
  3. The underlying tool callables exist as importable symbols and accept
     the documented arguments without raising at function-definition time.
  4. arco_competency_check (the lightweight in-process tool) runs end-to-end
     on the sentinel fixture and returns the expected schema.
  5. The pipeline-invoking tool (arco_run_pipeline) and the ROBOT-invoking
     tool (arco_run_hermit_crosscheck) are validated via mocked subprocess
     so the smoke test stays fast and works in environments without ROBOT.

Run: python mcp/test_arco_mcp.py
Expected: "ALL SMOKE TESTS PASSED" and exit 0.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest import mock

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))

import arco_mcp  # noqa: E402


REPO_ROOT = arco_mcp.REPO_ROOT


class TestServerStructure(unittest.TestCase):
    def test_server_instance_exists(self):
        self.assertIsNotNone(arco_mcp.mcp_server)
        self.assertEqual(arco_mcp.mcp_server.name, "arco")

    def test_three_tools_registered(self):
        # FastMCP exposes registered tools via list_tools(); call it through
        # the underlying tool manager which is the supported sync surface.
        tool_manager = arco_mcp.mcp_server._tool_manager
        names = sorted(tool_manager._tools.keys())
        self.assertEqual(
            names,
            ["arco_competency_check", "arco_run_hermit_crosscheck", "arco_run_pipeline"],
        )

    def test_tool_callables_exist(self):
        for fn_name in ("arco_run_pipeline", "arco_run_hermit_crosscheck", "arco_competency_check"):
            self.assertTrue(hasattr(arco_mcp, fn_name), f"missing {fn_name}")
            self.assertTrue(callable(getattr(arco_mcp, fn_name)))

    def test_repo_root_resolves_correctly(self):
        # Running from inside mcp/ should find REPO_ROOT one level up.
        self.assertTrue((REPO_ROOT / "03_TECHNICAL_CORE" / "scripts" / "run_pipeline.py").exists())


class TestCompetencyCheck(unittest.TestCase):
    """In-process CQ runner. Loads the ontology + sentinel instances + reasons
    once per call. Slow-ish (10-30s) but exercises real paths end-to-end."""

    def test_cq2_sentinel_passes(self):
        result = arco_mcp.arco_competency_check(cq_id="CQ2", system="Sentinel_ID_System")
        self.assertEqual(result["cq_id"], "CQ2")
        self.assertEqual(result["layer"], "OWL-RL")
        self.assertTrue(result["result"], "CQ2 should be True for Sentinel_ID_System")
        self.assertIn("AnnexIII1aApplicableSystem", result["interpretation"])

    def test_cq3_sentinel_fails(self):
        # Sentinel is 1(a), not 5(b)
        result = arco_mcp.arco_competency_check(cq_id="CQ3", system="Sentinel_ID_System")
        self.assertFalse(result["result"], "CQ3 should be False for Sentinel_ID_System")

    def test_unknown_cq_returns_error(self):
        result = arco_mcp.arco_competency_check(cq_id="CQ99", system="Sentinel_ID_System")
        self.assertTrue(result.get("error"))
        self.assertIn("valid", result)

    def test_missing_instances_returns_error(self):
        result = arco_mcp.arco_competency_check(
            cq_id="CQ2",
            system="Sentinel_ID_System",
            instances="nonexistent/path.ttl",
        )
        self.assertTrue(result.get("error"))


class TestRunPipelineMocked(unittest.TestCase):
    """Mock subprocess so the test stays fast. We assume run_pipeline.py works
    (it's covered by ARCO's own regression suite). What we test here is that
    the MCP wrapper parses summary.json + certificate.txt correctly."""

    def test_pipeline_parses_summary_correctly(self):
        # The summary.json on disk after a real run is the ground truth.
        summary_path = REPO_ROOT / "runs" / "demo" / "summary.json"
        cert_path = REPO_ROOT / "runs" / "demo" / "certificate.txt"
        self.assertTrue(summary_path.exists(), "summary.json should exist from a prior pipeline run")
        self.assertTrue(cert_path.exists(), "certificate.txt should exist from a prior pipeline run")

        # Mock subprocess.run to be a no-op success; the on-disk summary.json
        # is what the wrapper actually reads.
        fake = mock.Mock()
        fake.returncode = 0
        fake.stdout = "OK"
        fake.stderr = ""
        with mock.patch("arco_mcp.subprocess.run", return_value=fake):
            result = arco_mcp.arco_run_pipeline(
                system="Sentinel_ID_System",
                instances=None,
            )

        # Must not be an error envelope.
        self.assertNotIn("error", result, f"unexpected error: {result.get('message')}")
        # Required fields per the tool contract.
        for field in (
            "classification", "latent_risk_flag", "annex_iii_1a", "annex_iii_5b",
            "derogation_flagged", "fraud_flagged", "entailed_triples_added",
            "classification_layer", "audit_layer", "all_checks_passed", "certificate_text",
        ):
            self.assertIn(field, result, f"missing field {field}")

        self.assertIsInstance(result["latent_risk_flag"], bool)
        self.assertIsInstance(result["entailed_triples_added"], int)
        self.assertIsInstance(result["certificate_text"], str)
        self.assertGreater(len(result["certificate_text"]), 100)

    def test_pipeline_handles_subprocess_failure(self):
        fake = mock.Mock()
        fake.returncode = 2
        fake.stdout = ""
        fake.stderr = "boom"
        with mock.patch("arco_mcp.subprocess.run", return_value=fake):
            # Force the wrapper to think summary.json doesn't exist by pointing
            # to a file that won't exist.
            with mock.patch("arco_mcp.RUNS_DIR", REPO_ROOT / "nonexistent_runs_dir"):
                result = arco_mcp.arco_run_pipeline(system="Sentinel_ID_System")
        self.assertTrue(result.get("error"))
        self.assertIn("returncode", result)


class TestHermitCrosscheckMocked(unittest.TestCase):
    """Cross-check requires ROBOT. Mock _find_robot_jar to None so we exercise
    the structured 'not installed' path without needing ROBOT in CI."""

    def test_no_robot_returns_structured_error(self):
        with mock.patch("arco_mcp._find_robot_jar", return_value=None):
            result = arco_mcp.arco_run_hermit_crosscheck()
        self.assertTrue(result.get("error"))
        self.assertEqual(result.get("hermit_status"), "UNAVAILABLE")
        self.assertIn("ROBOT", result["message"])
        self.assertEqual(result.get("fixture"), "sentinel")
        self.assertEqual(result.get("system"), "Sentinel_ID_System")

    def test_unknown_fixture_returns_structured_error(self):
        result = arco_mcp.arco_run_hermit_crosscheck(fixture="not_a_fixture")
        self.assertTrue(result.get("error"))
        self.assertIn("valid_fixtures", result)
        self.assertIn("verification_kiosk", result["valid_fixtures"])


def main() -> int:
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if result.wasSuccessful():
        print("\nALL SMOKE TESTS PASSED")
        return 0
    print("\nSMOKE TESTS FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())
