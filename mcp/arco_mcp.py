"""ARCO MCP server.

Exposes ARCO's deterministic EU AI Act Annex III classification pipeline as
three typed tools an MCP client (e.g. Claude Code) can call over stdio:

  1. arco_run_pipeline           Run run_pipeline.py and return parsed result.
  2. arco_run_hermit_crosscheck  Run ROBOT/HermiT and diff against OWL-RL.
  3. arco_competency_check       Run a single CQ (CQ1..CQ12) against a system.

The server is read-only: it dispatches to the existing pipeline scripts and
on-disk SPARQL queries / SHACL shapes. It does not modify ARCO source files.

All paths resolve from the repo root, computed from this script's location
(repo_root = parent_of_this_file.parent), so the server runs from any cwd.
"""

from __future__ import annotations

import json
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP
from rdflib import Graph, URIRef
from pyshacl import validate

try:
    import owlrl
    HAS_OWLRL = True
except ImportError:
    HAS_OWLRL = False


# ---------------------------------------------------------------------------
# Repo layout (single source of truth — mirrors run_pipeline.py)
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
ONTOLOGY_DIR = REPO_ROOT / "03_TECHNICAL_CORE" / "ontology"
VALIDATION_DIR = REPO_ROOT / "03_TECHNICAL_CORE" / "validation"
REASONING_DIR = REPO_ROOT / "03_TECHNICAL_CORE" / "reasoning"
SCRIPTS_DIR = REPO_ROOT / "03_TECHNICAL_CORE" / "scripts"
RUNS_DIR = REPO_ROOT / "runs" / "demo"

DEFAULT_INSTANCES_REL = "03_TECHNICAL_CORE/ontology/ARCO_instances_sentinel.ttl"
ARCO_NS = "https://arco.ai/ontology/core#"

ROBOT_JAR_DEFAULT = Path.home() / ".local" / "share" / "robot" / "robot.jar"


mcp_server = FastMCP("arco")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _err(message: str, **extra: Any) -> dict[str, Any]:
    """Return a structured error payload (never raise across the tool boundary)."""
    out: dict[str, Any] = {"error": True, "message": message}
    out.update(extra)
    return out


def _resolve_instances(instances: str | None) -> Path:
    """Resolve an instances arg (None | abs path | repo-relative path | bare filename)."""
    if instances is None or instances == "":
        return REPO_ROOT / DEFAULT_INSTANCES_REL
    p = Path(instances)
    if p.is_absolute() and p.exists():
        return p
    candidate = (REPO_ROOT / p).resolve()
    if candidate.exists():
        return candidate
    fallback = (ONTOLOGY_DIR / p.name).resolve()
    if fallback.exists():
        return fallback
    return candidate  # may not exist; caller surfaces the error


def _system_iri(system_local: str) -> URIRef:
    return URIRef(f"{ARCO_NS}{system_local}")


def _load_reasoned_graph(instances_path: Path) -> Graph:
    """Load core + governance + instances and run OWL-RL closure.

    Reuses the same files run_pipeline.py loads, so the in-process reasoned
    graph is identical to what the pipeline would produce. Used by the
    competency-check tool, which runs a single SPARQL/SHACL check against
    the reasoned graph without invoking the full pipeline subprocess.
    """
    if not HAS_OWLRL:
        raise RuntimeError("owlrl is not installed; run pip install owlrl")
    g = Graph()
    files = [
        ONTOLOGY_DIR / "imports" / "bfo-2020.owl",
        ONTOLOGY_DIR / "imports" / "iao_bot.owl",
        ONTOLOGY_DIR / "imports" / "ro_bot.owl",
        ONTOLOGY_DIR / "imports" / "cco_bot.owl",
        ONTOLOGY_DIR / "ARCO_core.ttl",
        ONTOLOGY_DIR / "ARCO_governance_extension.ttl",
        instances_path,
    ]
    for p in files:
        if not p.exists():
            raise FileNotFoundError(f"Missing file: {p}")
        fmt = "xml" if p.suffix == ".owl" else "turtle"
        g.parse(p.as_posix(), format=fmt)
    closure = owlrl.OWLRL_Semantics(g, False, False, False)
    closure.closure()
    closure.post_process()
    return g


def _ask_with_system(graph: Graph, query_path: Path, system_local: str) -> bool:
    """Run an ASK query from disk with ?system bound to the given local name."""
    if not query_path.exists():
        raise FileNotFoundError(f"Missing SPARQL file: {query_path}")
    q = query_path.read_text(encoding="utf-8").strip()
    result = graph.query(q, initBindings={"system": _system_iri(system_local)})
    if isinstance(result, bool):
        return result
    if hasattr(result, "askAnswer") and result.askAnswer is not None:
        return bool(result.askAnswer)
    rows = list(result)
    return bool(rows[0]) if rows else False


def _ask_inline(graph: Graph, sparql: str) -> bool:
    result = graph.query(sparql)
    if isinstance(result, bool):
        return result
    if hasattr(result, "askAnswer") and result.askAnswer is not None:
        return bool(result.askAnswer)
    rows = list(result)
    return bool(rows[0]) if rows else False


# ---------------------------------------------------------------------------
# Tool 1: arco_run_pipeline
# ---------------------------------------------------------------------------

@mcp_server.tool()
def arco_run_pipeline(
    system: str = "Sentinel_ID_System",
    instances: str | None = None,
) -> dict[str, Any]:
    """Run the ARCO pipeline against an AI system instance file and return the structured classification result.

    Args:
        system: Local IRI fragment of the system to classify (e.g. "Sentinel_ID_System").
        instances: Path to instances TTL file relative to repo root (default: ARCO_instances_sentinel.ttl).
    """
    instances_path = _resolve_instances(instances)
    if not instances_path.exists():
        return _err(
            f"Instances file not found: {instances_path}",
            resolved_path=str(instances_path),
        )

    cmd = [
        sys.executable,
        str(SCRIPTS_DIR / "run_pipeline.py"),
        "--system", system,
        "--instances", str(instances_path),
    ]
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=300,
        )
    except subprocess.TimeoutExpired:
        return _err("run_pipeline.py timed out after 300s", cmd=cmd)
    except Exception as e:
        return _err(f"Failed to invoke run_pipeline.py: {e}", cmd=cmd)

    summary_path = RUNS_DIR / "summary.json"
    cert_path = RUNS_DIR / "certificate.txt"
    if proc.returncode != 0 or not summary_path.exists():
        return _err(
            "Pipeline exited non-zero or did not produce summary.json",
            returncode=proc.returncode,
            stdout_tail=proc.stdout[-2000:] if proc.stdout else "",
            stderr_tail=proc.stderr[-2000:] if proc.stderr else "",
        )

    try:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    except Exception as e:
        return _err(f"Failed to parse summary.json: {e}")

    cert_text = cert_path.read_text(encoding="utf-8") if cert_path.exists() else ""

    # Two-layer pass derivation (mirrors run_pipeline.py main()):
    # the layers are not in summary.json directly, so we rebuild them from the
    # field-value strings the pipeline writes. This stays consistent because
    # summary.json is the contract; rebuilding here matches the pipeline's
    # internal computation exactly for non-applicable, applicable, and failed
    # runs.
    # summary.json entailment field uses the ternary enum {"PRESENT",
    # "NOT_PRESENT", "NOT_RUN"} per output_manifest_v2.yaml line 124. Strict
    # manifest conformance: read the declared enum, no legacy bridge.
    shacl_pass = summary.get("shacl") == "PASS"
    entail_pass = summary.get("entailment") == "PRESENT"
    annex_1a = summary.get("annex_iii_1a", "N/A")
    annex_5b = summary.get("annex_iii_5b", "N/A")
    no_category = annex_1a == "NOT ENTAILED" and annex_5b == "NOT ENTAILED"
    non_applicable_run = shacl_pass and no_category
    classification_layer = "PASS" if (shacl_pass and entail_pass) or non_applicable_run else "FAIL"
    audit_layer = "PASS" if summary.get("all_checks_passed") and classification_layer == "PASS" else (
        "PASS" if non_applicable_run else "FAIL"
    )

    primary_classes = summary.get("primary_arco_classes", [])
    classification = primary_classes[0] if primary_classes else "NotEntailed"
    latent_mode = summary.get("latent_risk_mode", "NOT PRESENT")

    return {
        "classification": classification,
        "primary_arco_classes": primary_classes,
        "latent_risk_flag": latent_mode in ("INFERRED", "ASSERTED"),
        "latent_risk_mode": latent_mode,
        "annex_iii_1a": annex_1a,
        "annex_iii_5b": annex_5b,
        "derogation_flagged": bool(summary.get("flag_derogation_candidate", False)),
        "fraud_flagged": bool(summary.get("flag_fraud_exclusion_candidate", False)),
        "entailed_triples_added": int(summary.get("entailed_triples_added", 0)),
        "classification_layer": classification_layer,
        "audit_layer": audit_layer,
        "all_checks_passed": bool(summary.get("all_checks_passed", False)),
        "certificate_text": cert_text,
        "system": summary.get("system", system),
        "instance_file": summary.get("instance_file_name", instances_path.name),
    }


# ---------------------------------------------------------------------------
# Tool 2: arco_run_hermit_crosscheck
# ---------------------------------------------------------------------------

HERMIT_SCENARIOS: dict[str, tuple[str, str]] = {
    "sentinel": ("ARCO_instances_sentinel.ttl", "Sentinel_ID_System"),
    "credit_scorer": ("ARCO_instances_creditscoring.ttl", "CreditScorer_001"),
    "verification_kiosk": ("ARCO_instances_verification.ttl", "VerificationKiosk_001"),
    "decoy": ("ARCO_instances_adversarial_decoy.ttl", "DecoySystem_001"),
    "flag_biometric": ("ARCO_instances_flag_tests.ttl", "FlagTest_BiometricSystem_WithDerogationClaim"),
    "flag_credit": ("ARCO_instances_flag_tests.ttl", "FlagTest_CreditSystem_WithFraudProcess"),
}

HERMIT_SCENARIO_ALIASES: dict[str, str] = {
    "sentinel": "sentinel",
    "sentinel_id": "sentinel",
    "sentinel_id_system": "sentinel",
    "credit": "credit_scorer",
    "creditscorer": "credit_scorer",
    "credit_scorer": "credit_scorer",
    "creditscoring": "credit_scorer",
    "verification": "verification_kiosk",
    "kiosk": "verification_kiosk",
    "verification_kiosk": "verification_kiosk",
    "verificationkiosk": "verification_kiosk",
    "decoy": "decoy",
    "decoysystem": "decoy",
    "decoy_system": "decoy",
    "flag_biometric": "flag_biometric",
    "flagtest_biometric": "flag_biometric",
    "flagtest_biometricsystem_withderogationclaim": "flag_biometric",
    "flag_credit": "flag_credit",
    "flagtest_credit": "flag_credit",
    "flagtest_creditsystem_withfraudprocess": "flag_credit",
}

# Mirrors the query set in hermit_cross_check.py. The MCP tool runs one named
# scenario at a time; CI runs the full fixture sweep through the standalone script.
HERMIT_QUERIES: dict[str, str] = {
    "high_risk": "check_high_risk_inference.sparql",
    "annex_1a": "check_annex_iii_1a_entailment.sparql",
    "annex_5b": "check_annex_iii_5b_entailment.sparql",
    "latent": "detect_latent_risk.sparql",
}


def _find_robot_jar() -> Path | None:
    """Locate the ROBOT JAR. First check the workflow default, then $ROBOT_JAR."""
    import os
    if ROBOT_JAR_DEFAULT.exists():
        return ROBOT_JAR_DEFAULT
    env = os.environ.get("ROBOT_JAR")
    if env and Path(env).exists():
        return Path(env)
    return None


def _normalize_hermit_scenario(fixture: str | None) -> tuple[str, Path, str] | dict[str, Any]:
    """Resolve a user-facing fixture name to the scenario checked by HermiT."""
    requested = (fixture or "sentinel").strip().lower().replace("-", "_").replace(" ", "_")
    scenario_key = HERMIT_SCENARIO_ALIASES.get(requested)
    if scenario_key is None:
        return _err(
            f"Unknown HermiT fixture: {fixture!r}",
            valid_fixtures=sorted(HERMIT_SCENARIOS.keys()),
        )
    fixture_name, system_local = HERMIT_SCENARIOS[scenario_key]
    instance_file = ONTOLOGY_DIR / fixture_name
    if not instance_file.exists():
        return _err(
            f"Fixture file not found: {instance_file}",
            fixture=scenario_key,
            system=system_local,
        )
    return scenario_key, instance_file, system_local


@mcp_server.tool()
def arco_run_hermit_crosscheck(fixture: str | None = "sentinel") -> dict[str, Any]:
    """Run a single-fixture OWL 2 DL HermiT cross-check and compare it with OWL-RL.

    Materializes the HermiT-reasoned graph via ROBOT, computes the OWL-RL
    baseline for the same fixture, then compares the classification query set
    used by hermit_cross_check.py. ROBOT must be installed (jar at
    ~/.local/share/robot/robot.jar or $ROBOT_JAR).

    Args:
        fixture: One named certificate-grade scenario: sentinel, credit_scorer,
            verification_kiosk, decoy, flag_biometric, or flag_credit.
    """
    scenario = _normalize_hermit_scenario(fixture)
    if isinstance(scenario, dict):
        return scenario
    fixture_key, instance_file, system_local = scenario

    robot_jar = _find_robot_jar()
    if robot_jar is None:
        return _err(
            "ROBOT JAR not found. Install ROBOT v1.9.10 to "
            "~/.local/share/robot/robot.jar or set ROBOT_JAR. "
            "Download: https://github.com/ontodev/robot/releases",
            hermit_status="UNAVAILABLE",
            fixture=fixture_key,
            system=system_local,
        )

    # Step 1: compute the OWL-RL baseline for the same fixture.
    try:
        g_rl = _load_reasoned_graph(instance_file)
    except Exception as e:
        return _err(
            f"OWL-RL baseline failed for {instance_file.name}: {e}",
            hermit_status="FAIL",
            fixture=fixture_key,
            system=system_local,
        )

    # Step 2: merge ARCO ontology files (matches the standalone cross-check).
    import shutil
    # ROBOT/HermiT can leave Windows file handles open briefly after exit. Use
    # manual temp cleanup so a locked temp dir cannot replace the tool result
    # with a post-success cleanup exception.
    scratch_root = REPO_ROOT / ".tmp-hermit"
    scratch_root.mkdir(exist_ok=True)
    tmp = scratch_root / f"arco-mcp-{uuid.uuid4().hex}"
    tmp.mkdir()
    try:
        merged = tmp / "arco_merged.owl"
        reasoned = tmp / "arco_reasoned.owl"
        merge_cmd = [
            "java", "-jar", str(robot_jar), "merge",
            "--input", str(ONTOLOGY_DIR / "imports" / "bfo-2020.owl"),
            "--input", str(ONTOLOGY_DIR / "imports" / "iao_bot.owl"),
            "--input", str(ONTOLOGY_DIR / "imports" / "ro_bot.owl"),
            "--input", str(ONTOLOGY_DIR / "imports" / "cco_bot.owl"),
            "--input", str(ONTOLOGY_DIR / "ARCO_core.ttl"),
            "--input", str(ONTOLOGY_DIR / "ARCO_governance_extension.ttl"),
            "--input", str(instance_file),
            "--output", merged.name,
        ]
        try:
            proc = subprocess.run(
                merge_cmd,
                cwd=str(tmp),
                capture_output=True,
                text=True,
                timeout=600,
            )
        except subprocess.TimeoutExpired:
            return _err(
                "ROBOT merge timed out",
                hermit_status="FAIL",
                fixture=fixture_key,
                system=system_local,
            )
        if proc.returncode != 0:
            return _err(
                "ROBOT merge failed",
                hermit_status="FAIL",
                fixture=fixture_key,
                system=system_local,
                returncode=proc.returncode,
                stdout_tail=proc.stdout[-2000:] if proc.stdout else "",
                stderr_tail=proc.stderr[-2000:] if proc.stderr else "",
            )

        # Step 3: HermiT reason with ClassAssertion + SubClass, indirect on.
        # Same flags as the standalone cross-check so behavior matches CI.
        reason_cmd = [
            "java", "-jar", str(robot_jar), "reason",
            "--reasoner", "hermit",
            "--axiom-generators", "ClassAssertion SubClass",
            "--include-indirect", "true",
            "--input", merged.name,
            "--output", reasoned.name,
        ]
        try:
            proc = subprocess.run(
                reason_cmd,
                cwd=str(tmp),
                capture_output=True,
                text=True,
                timeout=600,
            )
        except subprocess.TimeoutExpired:
            return _err(
                "HermiT reasoning timed out",
                hermit_status="FAIL",
                fixture=fixture_key,
                system=system_local,
            )
        if proc.returncode != 0 or not reasoned.exists():
            return _err(
                "HermiT reasoning failed",
                hermit_status="FAIL",
                fixture=fixture_key,
                system=system_local,
                returncode=proc.returncode,
                stdout_tail=proc.stdout[-2000:] if proc.stdout else "",
                stderr_tail=proc.stderr[-2000:] if proc.stderr else "",
            )

        # Step 4: run the SPARQL ASK queries against both graphs and diff.
        try:
            g_dl = Graph()
            g_dl.parse(str(reasoned), format="xml")
        except Exception as e:
            return _err(
                f"Failed to parse HermiT-reasoned graph: {e}",
                hermit_status="FAIL",
                fixture=fixture_key,
                system=system_local,
            )

        system_iri = _system_iri(system_local)
        query_results = []
        mismatches = []
        for name, qfile in HERMIT_QUERIES.items():
            qpath = REASONING_DIR / qfile
            try:
                q = qpath.read_text(encoding="utf-8")
                owlrl_result = bool(g_rl.query(q, initBindings={"system": system_iri}))
                hermit_result = bool(g_dl.query(q, initBindings={"system": system_iri}))
            except Exception as e:
                return _err(
                    f"SPARQL query {name} failed: {e}",
                    hermit_status="FAIL",
                    fixture=fixture_key,
                    system=system_local,
                )
            match = hermit_result == owlrl_result
            query_results.append({
                "name": name,
                "hermit_result": hermit_result,
                "owlrl_result": owlrl_result,
                "match": match,
            })
            if not match:
                mismatches.append({
                    "name": name,
                    "hermit": hermit_result,
                    "owlrl": owlrl_result,
                })

        agreement = len(mismatches) == 0
        return {
            "hermit_status": "PASS" if agreement else "FAIL",
            "fixture": fixture_key,
            "fixture_file": instance_file.name,
            "system": system_local,
            "query_results": query_results,
            "mismatches": mismatches,
            "agreement": agreement,
            "queries_total": len(query_results),
            "queries_matching": sum(1 for r in query_results if r["match"]),
        }
    finally:
        try:
            shutil.rmtree(tmp, ignore_errors=True)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Tool 3: arco_competency_check
# ---------------------------------------------------------------------------

# CQ-to-implementation mapping. Mirrors docs/_archive/COMPETENCY_QUESTIONS.md exactly.
# Each CQ identifies (a) the regulator-paraphrase question, (b) the regulatory
# anchor, (c) the layer that answers it, (d) the file that implements it, and
# (e) a dispatch tag the tool uses to route to the right runner.
CQ_MAP: dict[str, dict[str, Any]] = {
    "CQ1": {
        "question": "Does this system have a component bearing an Annex III triggering capability?",
        "regulatory_anchor": "Article 6(2) and Annex III generally",
        "layer": "OWL-RL",
        "answered_by": "03_TECHNICAL_CORE/reasoning/detect_latent_risk.sparql",
        "dispatch": "sparql_ask",
        "query_file": "detect_latent_risk.sparql",
    },
    "CQ2": {
        "question": "Does this system meet all three gates for Annex III item 1(a)?",
        "regulatory_anchor": "Annex III item 1(a) (biometric identification)",
        "layer": "OWL-RL",
        "answered_by": "03_TECHNICAL_CORE/reasoning/check_annex_iii_1a_entailment.sparql",
        "dispatch": "sparql_ask",
        "query_file": "check_annex_iii_1a_entailment.sparql",
    },
    "CQ3": {
        "question": "Does this system meet all three gates for Annex III item 5(b)?",
        "regulatory_anchor": "Annex III item 5(b) (creditworthiness)",
        "layer": "OWL-RL",
        "answered_by": "03_TECHNICAL_CORE/reasoning/check_annex_iii_5b_entailment.sparql",
        "dispatch": "sparql_ask",
        "query_file": "check_annex_iii_5b_entailment.sparql",
    },
    "CQ4": {
        "question": "Is the system's intended use documented?",
        "regulatory_anchor": "Article 3(12) (intended purpose)",
        "layer": "SHACL",
        "answered_by": "03_TECHNICAL_CORE/validation/assessment_documentation_shape.ttl (IntendedUseSpecificationShape) + 03_TECHNICAL_CORE/reasoning/check_intended_use.sparql",
        "dispatch": "shacl_plus_ask",
        "query_file": "check_intended_use.sparql",
    },
    "CQ5": {
        "question": "Does the use scenario designate the regulated affected role universal?",
        "regulatory_anchor": "Annex III items 1(a) and 5(b), affected-role scoping",
        "layer": "SHACL",
        "answered_by": "03_TECHNICAL_CORE/validation/assessment_documentation_shape.ttl (UseScenarioSpecificationShape, PS_UseScenario_DesignatesRole) + 03_TECHNICAL_CORE/reasoning/check_intended_use.sparql",
        "dispatch": "shacl_plus_ask",
        "query_file": "check_intended_use.sparql",
    },
    "CQ6": {
        "question": "Is the prescribed process aligned with the regulation-named regulated process?",
        "regulatory_anchor": "Annex III general (per-item process alignment)",
        "layer": "SPARQL_ASK",
        "answered_by": "03_TECHNICAL_CORE/reasoning/check_regulatory_alignment.sparql",
        "dispatch": "sparql_ask",
        "query_file": "check_regulatory_alignment.sparql",
    },
    "CQ7": {
        "question": "Is there assessment documentation linking the system to applicable regulatory content?",
        "regulatory_anchor": "Article 6(2), supporting traceability",
        "layer": "SHACL",
        "answered_by": "03_TECHNICAL_CORE/validation/assessment_documentation_shape.ttl (AssessmentDocumentationShape) + 03_TECHNICAL_CORE/reasoning/check_assessment_traceability.sparql",
        "dispatch": "shacl_plus_ask",
        "query_file": "check_assessment_traceability.sparql",
    },
    "CQ8": {
        "question": "Is there a compliance obligation specifying the provider's responsibilities?",
        "regulatory_anchor": "Article 6(2) and Articles 16 onward (provider obligations)",
        "layer": "SHACL",
        "answered_by": "03_TECHNICAL_CORE/validation/assessment_documentation_shape.ttl (ComplianceObligationSpecificationShape) + 03_TECHNICAL_CORE/reasoning/check_obligation_link.sparql",
        "dispatch": "shacl_plus_ask",
        "query_file": "check_obligation_link.sparql",
    },
    "CQ9": {
        "question": "Has the provider asserted an Article 6(3) derogation claim for this system?",
        "regulatory_anchor": "Article 6(3) (derogation)",
        "layer": "SPARQL_ASK",
        "answered_by": "03_TECHNICAL_CORE/reasoning/flag_derogation_candidate.sparql",
        "dispatch": "sparql_ask",
        "query_file": "flag_derogation_candidate.sparql",
    },
    "CQ10": {
        "question": "Does the system have a fraud-detection process in scope (Annex III 5(b) exclusion candidate)?",
        "regulatory_anchor": "Annex III item 5(b), fraud-detection exclusion clause",
        "layer": "SPARQL_ASK",
        "answered_by": "03_TECHNICAL_CORE/reasoning/flag_fraud_exclusion_candidate.sparql",
        "dispatch": "sparql_ask",
        "query_file": "flag_fraud_exclusion_candidate.sparql",
    },
    "CQ11": {
        "question": "Does each ProviderRole instance correctly inhere in a single bearer?",
        "regulatory_anchor": "Indirect; supports Article 16 obligation attribution",
        "layer": "SHACL",
        "answered_by": "03_TECHNICAL_CORE/validation/assessment_documentation_shape.ttl (ProviderRoleShape, PS_ProviderRole_InheresIn) + 03_TECHNICAL_CORE/reasoning/ask_provider_role_inheres_in_org.sparql",
        "dispatch": "shacl_plus_ask_no_system",
        "query_file": "ask_provider_role_inheres_in_org.sparql",
    },
    "CQ12": {
        "question": "Did the latent-risk OWL-RL entailment fire correctly?",
        "regulatory_anchor": "Article 6(2); cross-check on classification soundness",
        "layer": "SPARQL_ASK",
        "answered_by": "03_TECHNICAL_CORE/reasoning/check_high_risk_inference.sparql",
        "dispatch": "sparql_ask",
        "query_file": "check_high_risk_inference.sparql",
    },
}


def _interpret(cq_id: str, system: str, result: Any) -> str:
    """One-sentence plain-English summary of the result for the given CQ."""
    if isinstance(result, dict) and "shacl_conforms" in result:
        s = "conforms" if result["shacl_conforms"] else "does NOT conform"
        a = "true" if result["sparql_ask"] else "false"
        return f"SHACL {s} for the documentary shape; the audit query returns {a} for {system}."
    truthy = bool(result)
    if cq_id == "CQ1":
        return ("System has a component bearing an Annex III triggering capability "
                "(latent-risk path detected)." if truthy
                else "No latent-risk path detected on this system.")
    if cq_id == "CQ2":
        return (f"{system} is in the AnnexIII1aApplicableSystem extension." if truthy
                else f"{system} is NOT in the AnnexIII1aApplicableSystem extension.")
    if cq_id == "CQ3":
        return (f"{system} is in the AnnexIII5bApplicableSystem extension." if truthy
                else f"{system} is NOT in the AnnexIII5bApplicableSystem extension.")
    if cq_id == "CQ6":
        return ("Prescribed process is aligned with the regulator-named regulated process." if truthy
                else "Prescribed process is NOT aligned (or no alignment can be verified).")
    if cq_id == "CQ9":
        return ("Article 6(3) derogation claim asserted; human legal review required." if truthy
                else "No Article 6(3) derogation claim asserted.")
    if cq_id == "CQ10":
        return ("Fraud-detection process in scope; 5(b) exclusion candidate, human review required." if truthy
                else "No fraud-detection process in scope.")
    if cq_id == "CQ12":
        return ("HighRiskSystem entailment fired correctly on the reasoned graph." if truthy
                else "HighRiskSystem entailment did NOT fire (regression candidate).")
    return f"Result: {result}"


@mcp_server.tool()
def arco_competency_check(
    cq_id: str,
    system: str = "Sentinel_ID_System",
    instances: str | None = None,
) -> dict[str, Any]:
    """Run a specific competency question (CQ1-CQ12 from docs/_archive/COMPETENCY_QUESTIONS.md) against a system.

    Args:
        cq_id: One of "CQ1".."CQ12".
        system: Local IRI fragment (e.g. "Sentinel_ID_System").
        instances: Path to instances TTL (default: ARCO_instances_sentinel.ttl).
    """
    cq_id = cq_id.upper().strip()
    if cq_id not in CQ_MAP:
        return _err(
            f"Unknown CQ: {cq_id}. Must be one of CQ1..CQ12.",
            valid=list(CQ_MAP.keys()),
        )
    spec = CQ_MAP[cq_id]
    instances_path = _resolve_instances(instances)
    if not instances_path.exists():
        return _err(
            f"Instances file not found: {instances_path}",
            resolved_path=str(instances_path),
        )

    try:
        reasoned = _load_reasoned_graph(instances_path)
    except Exception as e:
        return _err(f"Failed to load + reason graph: {e}")

    dispatch = spec["dispatch"]
    qpath = REASONING_DIR / spec["query_file"]

    try:
        if dispatch == "sparql_ask":
            ask_result = _ask_with_system(reasoned, qpath, system)
            result: Any = ask_result
        elif dispatch == "shacl_plus_ask":
            shapes = Graph().parse(
                (VALIDATION_DIR / "assessment_documentation_shape.ttl").as_posix(),
                format="turtle",
            )
            conforms, _, _ = validate(
                data_graph=reasoned,
                shacl_graph=shapes,
                inference="none",
                abort_on_first=False,
                allow_infos=True,
                allow_warnings=True,
                meta_shacl=False,
                advanced=True,
            )
            ask_result = _ask_with_system(reasoned, qpath, system)
            result = {"shacl_conforms": bool(conforms), "sparql_ask": bool(ask_result)}
        elif dispatch == "shacl_plus_ask_no_system":
            # CQ11 — sentinel smoke test, not parameterized by ?system.
            shapes = Graph().parse(
                (VALIDATION_DIR / "assessment_documentation_shape.ttl").as_posix(),
                format="turtle",
            )
            conforms, _, _ = validate(
                data_graph=reasoned,
                shacl_graph=shapes,
                inference="none",
                abort_on_first=False,
                allow_infos=True,
                allow_warnings=True,
                meta_shacl=False,
                advanced=True,
            )
            q = qpath.read_text(encoding="utf-8")
            ask_result = _ask_inline(reasoned, q)
            result = {"shacl_conforms": bool(conforms), "sparql_ask": bool(ask_result)}
        else:
            return _err(f"Unknown dispatch type for {cq_id}: {dispatch}")
    except Exception as e:
        return _err(f"CQ runner failed for {cq_id}: {e}")

    return {
        "cq_id": cq_id,
        "cq_question": spec["question"],
        "regulatory_anchor": spec["regulatory_anchor"],
        "layer": spec["layer"],
        "answered_by": spec["answered_by"],
        "result": result,
        "interpretation": _interpret(cq_id, system, result),
        "system": system,
    }


# ---------------------------------------------------------------------------
# Entry point — STDIO transport (the standard MCP local-server pattern).
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp_server.run(transport="stdio")
