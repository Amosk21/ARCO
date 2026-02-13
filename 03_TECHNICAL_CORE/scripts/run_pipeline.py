"""
ARCO Compliance Verification Pipeline — BFO/RO Aligned (RO:0000091 has_disposition)

Stages:
1) Load ontology + instance data
2) OWL-RL reasoning (materialize entailments)
3) SHACL validation
4) SPARQL audit checks (ASK)
5) Verify HighRiskSystem entailment + evidence path
6) Print regulatory determination certificate

Modeling relation: RO_0000091 has_disposition (per OBO Foundry / RO best practice)
"""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from rdflib import Graph, URIRef
from rdflib.namespace import RDF
from pyshacl import validate

try:
    import owlrl
    HAS_OWLRL = True
except ImportError:
    HAS_OWLRL = False

REPO_ROOT = Path(__file__).resolve().parents[2]

ONTOLOGY_DIR = REPO_ROOT / "03_TECHNICAL_CORE" / "ontology"
VALIDATION_DIR = REPO_ROOT / "03_TECHNICAL_CORE" / "validation"
REASONING_DIR = REPO_ROOT / "03_TECHNICAL_CORE" / "reasoning"

CORE = ONTOLOGY_DIR / "ARCO_core.ttl"
GOV = ONTOLOGY_DIR / "ARCO_governance_extension.ttl"
INSTANCES = ONTOLOGY_DIR / "ARCO_instances_sentinel.ttl"

SHAPES = VALIDATION_DIR / "assessment_documentation_shape.ttl"

TRACEABILITY_QUERY = REASONING_DIR / "check_assessment_traceability.sparql"
LATENT_RISK_QUERY = REASONING_DIR / "detect_latent_risk.sparql"
HIGH_RISK_INFERENCE_QUERY = REASONING_DIR / "check_high_risk_inference.sparql"

# --- System under evaluation (change this one line for a different system) ---
SYSTEM_LOCAL = "Sentinel_ID_System"
SYSTEM_IRI = f"https://arco.ai/ontology/core#{SYSTEM_LOCAL}"
ARCO_NS = "https://arco.ai/ontology/core#"


# ---------------------------
# helpers
# ---------------------------

def hr(title: str, width: int = 72) -> None:
    print("\n" + "=" * width)
    print(title)
    print("=" * width)

def sub(title: str, width: int = 72) -> None:
    print("\n" + "-" * width)
    print(title)
    print("-" * width)

def load_union_graph(*paths: Path) -> Graph:
    g = Graph()
    for p in paths:
        if not p.exists():
            raise FileNotFoundError(f"Missing file: {p}")
        g.parse(p.as_posix(), format="turtle")
    return g

def clone_graph(g: Graph) -> Graph:
    h = Graph()
    for t in g:
        h.add(t)
    return h

def run_sparql_ask_inline(data_graph: Graph, query: str) -> bool:
    result = data_graph.query(query)
    if isinstance(result, bool):
        return result
    rows = list(result)
    return bool(rows[0]) if rows else False

def run_sparql_ask_from_file(data_graph: Graph, query_path: Path) -> bool:
    if not query_path.exists():
        raise FileNotFoundError(f"Missing SPARQL query file: {query_path}")
    q = query_path.read_text(encoding="utf-8").strip()

    try:
        result = data_graph.query(q)
        if isinstance(result, bool):
            return result
        rows = list(result)
        return bool(rows[0]) if rows else False
    except Exception as e:
        raise RuntimeError(f"SPARQL query failed: {query_path}\n{e}")


# ---------------------------
# reasoning / validation
# ---------------------------

def run_reasoning(data_graph: Graph) -> tuple[Graph, int, int]:
    if not HAS_OWLRL:
        sub("REASONING")
        print("owlrl not installed -> skipping reasoning")
        print("Install: pip install owlrl")
        return data_graph, len(data_graph), 0

    sub("REASONING")
    initial = len(data_graph)
    print("Running OWL-RL closure (materializing entailments)...")
    owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(data_graph)
    final = len(data_graph)
    added = final - initial
    print(f"Triples: {initial} -> {final}   (+{added} entailed)")
    return data_graph, initial, added

def run_shacl(data_graph: Graph) -> tuple[bool, int]:
    sub("SHACL")
    if not SHAPES.exists():
        raise FileNotFoundError(f"Missing SHACL shapes file: {SHAPES}")

    print("Validating SHACL shapes against the reasoned graph...")
    shapes_graph = Graph().parse(SHAPES.as_posix(), format="turtle")

    conforms, report_graph, report_text = validate(
        data_graph=data_graph,
        shacl_graph=shapes_graph,
        inference="none",
        abort_on_first=False,
        allow_infos=True,
        allow_warnings=True,
        meta_shacl=False,
        advanced=True,
    )

    print(f"Conforms: {conforms}")
    if not conforms:
        print("\nSHACL report:\n")
        print(report_text)

    sh_validation_result = URIRef("http://www.w3.org/ns/shacl#ValidationResult")
    violation_count = len(list(report_graph.subjects(RDF.type, sh_validation_result)))

    print(f"Validation results: {violation_count}")

    return conforms, violation_count


# ---------------------------
# proof / evidence extraction
# ---------------------------

def _ask_highrisk(sys: str = SYSTEM_LOCAL) -> str:
    return f"""
PREFIX : <{ARCO_NS}>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
ASK WHERE {{ :{sys} rdf:type :HighRiskSystem . }}
"""


def _ask_annex_iii_1a(sys: str = SYSTEM_LOCAL) -> str:
    return f"""
PREFIX : <{ARCO_NS}>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
ASK WHERE {{ :{sys} rdf:type :AnnexIII1aApplicableSystem . }}
"""

def _ask_primary_path(sys: str = SYSTEM_LOCAL) -> str:
    return f"""
PREFIX : <{ARCO_NS}>
PREFIX bfo: <http://purl.obolibrary.org/obo/BFO_>
PREFIX ro:  <http://purl.obolibrary.org/obo/RO_>
ASK WHERE {{
  :{sys} bfo:0000051 ?component .
  ?component ro:0000091 ?d .
  ?d a :AnnexIIITriggeringCapability .
}}
"""


def _ask_gate1_biometric_capability(sys: str = SYSTEM_LOCAL) -> str:
        return f"""
PREFIX : <{ARCO_NS}>
PREFIX bfo: <http://purl.obolibrary.org/obo/BFO_>
PREFIX ro:  <http://purl.obolibrary.org/obo/RO_>
ASK WHERE {{
    :{sys} bfo:0000051 ?component .
    ?component ro:0000091 ?d .
    ?d a :BiometricIdentificationCapability .
}}
"""


def _ask_gate2_intended_use(sys: str = SYSTEM_LOCAL) -> str:
        return f"""
PREFIX : <{ARCO_NS}>
PREFIX iao: <http://purl.obolibrary.org/obo/IAO_>
ASK WHERE {{
    ?intended a :IntendedUseSpecification .
    ?intended iao:0000136 :{sys} .
}}
"""


def _ask_gate3_use_scenario(sys: str = SYSTEM_LOCAL) -> str:
        return f"""
PREFIX : <{ARCO_NS}>
PREFIX iao: <http://purl.obolibrary.org/obo/IAO_>
ASK WHERE {{
    ?scenario a :UseScenarioSpecification .
    ?scenario iao:0000136 :{sys} .
}}
"""


def _ask_assessment_doc_about_system(sys: str = SYSTEM_LOCAL) -> str:
        return f"""
PREFIX : <{ARCO_NS}>
PREFIX iao: <http://purl.obolibrary.org/obo/IAO_>
ASK WHERE {{
    ?doc a :AssessmentDocumentation .
    ?doc iao:0000136 :{sys} .
}}
"""


def _ask_any_capability_path(sys: str = SYSTEM_LOCAL) -> str:
        return f"""
PREFIX : <{ARCO_NS}>
PREFIX bfo: <http://purl.obolibrary.org/obo/BFO_>
PREFIX ro:  <http://purl.obolibrary.org/obo/RO_>
ASK WHERE {{
    :{sys} bfo:0000051 ?component .
    ?component ro:0000091 ?d .
    ?d a :CapabilityDisposition .
}}
"""

def _select_primary_bindings(sys: str = SYSTEM_LOCAL) -> str:
    return f"""
PREFIX : <{ARCO_NS}>
PREFIX bfo: <http://purl.obolibrary.org/obo/BFO_>
PREFIX ro:  <http://purl.obolibrary.org/obo/RO_>
SELECT ?component ?d WHERE {{
  :{sys} bfo:0000051 ?component .
  ?component ro:0000091 ?d .
  ?d a :AnnexIIITriggeringCapability .
}}
LIMIT 5
"""

def _short(iri: str) -> str:
    """Shorten an IRI to its local name for display."""
    return iri.rsplit("#", 1)[-1] if "#" in iri else iri.rsplit("/", 1)[-1]

def get_primary_bindings(g: Graph) -> list[tuple[str, str]]:
    rows = []
    try:
        qres = g.query(_select_primary_bindings())
        for r in qres:
            rows.append((str(r.component), str(r.d)))
    except Exception:
        return []
    return rows

def verify_high_risk_inference(reasoned: Graph, source: Graph) -> tuple[bool, bool, bool, list[tuple[str, str]]]:
    """Returns (inference_ok, asserted_pre, entailed_post, bindings)."""
    hr("ARCO RESULT (ENTAILMENT + PROOF SKETCH)")

    # Before/after: was HighRiskSystem asserted in raw input?
    asserted_pre = run_sparql_ask_inline(source, _ask_highrisk())

    # After reasoning: is HighRiskSystem present now?
    if HIGH_RISK_INFERENCE_QUERY.exists():
        entailed_post = run_sparql_ask_from_file(reasoned, HIGH_RISK_INFERENCE_QUERY)
    else:
        entailed_post = run_sparql_ask_inline(reasoned, _ask_highrisk())

    print(f"HighRiskSystem in source data (pre-reasoning):   {asserted_pre}")
    print(f"HighRiskSystem in reasoned graph (post-reason):  {entailed_post}")

    # Evidence check (primary path only — legacy bearer_of removed)
    primary_path = run_sparql_ask_inline(reasoned, _ask_primary_path())

    sub("EVIDENCE PATH CHECK")
    print(f"has_disposition path (RO:0000091): {primary_path}")

    # Concrete bindings
    bindings = get_primary_bindings(reasoned)
    if bindings:
        sub("CONCRETE BINDINGS")
        for i, (comp, disp) in enumerate(bindings, 1):
            print(f"{i}) component = {_short(comp)}")
            print(f"   disposition/capability = {_short(disp)}")

    sub("WHY THIS ENTAILS HighRiskSystem")
    print("Bridge axiom (ARCO_core.ttl):")
    print("  HighRiskSystem = System AND (has_part SOME (has_disposition SOME AnnexIIITriggeringCapability))")
    if not asserted_pre and entailed_post:
        print(f"  => {SYSTEM_LOCAL} rdf:type HighRiskSystem  (INFERRED, not asserted)")
    elif entailed_post:
        print(f"  => {SYSTEM_LOCAL} rdf:type HighRiskSystem  (ASSERTED)")

    # Hard enforcement: entailment must have at least one evidence path
    if entailed_post and not primary_path:
        sub("FAIL")
        print("Entailment is True, but no supporting evidence path was detected.")
        print("Likely cause: predicate mismatch or missing component facts.")
        return False, asserted_pre, entailed_post, bindings

    if entailed_post:
        sub("SUCCESS")
        print("HighRiskSystem classification is present AND justified by an explicit structural path.")
        return True, asserted_pre, entailed_post, bindings

    sub("NOT ENTAILED")
    print("HighRiskSystem was not inferred for the current asserted commitments.")
    if not HAS_OWLRL:
        print("Reasoning engine unavailable: install owlrl to enable OWL-RL materialization.")
    else:
        print("This can be a valid outcome when AnnexIII-triggering capability commitments are absent.")
        print("If unexpected, verify has_part/component facts and AnnexIIITriggeringCapability typing.")
    return False, asserted_pre, entailed_post, bindings


def determine_commitment_state(reasoned: Graph, system_local: str) -> tuple[str, list[str], dict[str, bool]]:
    annex_entailed = run_sparql_ask_inline(reasoned, _ask_annex_iii_1a(system_local))
    high_risk_entailed = run_sparql_ask_inline(reasoned, _ask_highrisk(system_local))

    gate1 = run_sparql_ask_inline(reasoned, _ask_gate1_biometric_capability(system_local))
    gate2 = run_sparql_ask_inline(reasoned, _ask_gate2_intended_use(system_local))
    gate3 = run_sparql_ask_inline(reasoned, _ask_gate3_use_scenario(system_local))

    has_doc_signal = run_sparql_ask_inline(reasoned, _ask_assessment_doc_about_system(system_local))
    has_any_capability_signal = run_sparql_ask_inline(reasoned, _ask_any_capability_path(system_local))

    diagnostics = {
        "high_risk_entailed": high_risk_entailed,
        "annex_iii_1a_entailed": annex_entailed,
        "gate1_biometric_capability": gate1,
        "gate2_intended_use": gate2,
        "gate3_use_scenario": gate3,
        "has_assessment_documentation": has_doc_signal,
        "has_any_capability_signal": has_any_capability_signal,
    }

    missing = []
    if not gate1:
        missing.append("Gate 1 missing: biometric identification capability commitment")
    if not gate2:
        missing.append("Gate 2 missing: intended-use specification for the system")
    if not gate3:
        missing.append("Gate 3 missing: use-scenario specification for affected role")

    if annex_entailed or high_risk_entailed:
        return "ENTAILED", missing, diagnostics

    if gate1 or gate2 or gate3 or has_doc_signal or has_any_capability_signal:
        return "UNDERDETERMINED", missing, diagnostics

    return "NOT ENTAILED", missing, diagnostics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run ARCO pipeline with explicit commitment-state reporting.",
    )
    parser.add_argument(
        "--profile",
        choices=["sentinel", "claude"],
        default="sentinel",
        help="Preconfigured system+instance pair.",
    )
    parser.add_argument(
        "--instances",
        type=str,
        default=None,
        help="Path to an instances TTL file (overrides profile default).",
    )
    parser.add_argument(
        "--system-local",
        type=str,
        default=None,
        help="Local name of the system individual (overrides profile default).",
    )
    parser.add_argument(
        "--json-out",
        type=str,
        default=None,
        help="Write machine-readable pipeline result JSON to this path.",
    )
    parser.add_argument(
        "--determination-ttl-out",
        type=str,
        default=None,
        help="Write ontology-native determination TTL with human-readable comments.",
    )
    parser.add_argument(
        "--report-out",
        type=str,
        default=None,
        help="Write deterministic markdown report projected from the JSON result payload.",
    )
    return parser.parse_args()


def resolve_runtime_selection(args: argparse.Namespace) -> tuple[Path, str]:
    defaults = {
        "sentinel": (ONTOLOGY_DIR / "ARCO_instances_sentinel.ttl", "Sentinel_ID_System"),
        "claude": (ONTOLOGY_DIR / "ARCO_instances_claude3.ttl", "Claude3_System"),
    }
    default_instances, default_system = defaults[args.profile]
    instances_path = Path(args.instances).resolve() if args.instances else default_instances
    system_local = args.system_local if args.system_local else default_system
    return instances_path, system_local


# ---------------------------
# main
# ---------------------------

def _pf(ok: bool) -> str:
    return "PASS" if ok else "FAIL"


def _status_text(ok: bool) -> str:
    return "present" if ok else "absent"


def _human_state_explanation(
    *,
    commitment_state: str,
    classification: str,
    gate1: bool,
    gate2: bool,
    gate3: bool,
    missing_commitments: list[str],
) -> str:
    if commitment_state == "ENTAILED":
        return (
            "Regulatory applicability is derivable from asserted commitments. "
            "The required gate chain is structurally present in the reasoned graph."
        )
    if commitment_state == "UNDERDETERMINED":
        missing = "; ".join(missing_commitments) if missing_commitments else "no explicit gate list"
        return (
            "Regulatory applicability is not derivable because required commitments are missing or incomplete. "
            f"Current missing commitments: {missing}."
        )
    return (
        "No regulated commitment path was detected in the current graph. "
        f"Classification remains {classification} with gates set to "
        f"G1={_status_text(gate1)}, G2={_status_text(gate2)}, G3={_status_text(gate3)}."
    )


def _escape_ttl_literal(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def get_git_commit_hash() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        commit = result.stdout.strip()
        return commit if commit else None
    except Exception:
        return None


def build_result_payload(
    *,
    profile: str,
    instances_path: Path,
    system_local: str,
    asserted_triples: int,
    reasoned_triples: int,
    entailed_triples_added: int,
    shacl_ok: bool,
    traceability_ok: bool,
    latent_ok: bool | None,
    inference_ok: bool,
    asserted_pre: bool,
    entailed_post: bool,
    commitment_state: str,
    missing_commitments: list[str],
    diagnostics: dict[str, bool],
    bindings: list[tuple[str, str]],
    shacl_violation_count: int,
    run_timestamp_utc: str,
    git_commit_hash: str | None,
) -> dict:
    if not asserted_pre and entailed_post:
        classification_mode = "INFERRED"
    elif asserted_pre and entailed_post:
        classification_mode = "ASSERTED"
    else:
        classification_mode = "NOT PRESENT"

    classification = "HighRiskSystem" if classification_mode in {"INFERRED", "ASSERTED"} else "NOT PRESENT"
    classification_iri = f"{ARCO_NS}HighRiskSystem" if classification == "HighRiskSystem" else None
    gate1 = diagnostics.get("gate1_biometric_capability", False)
    gate2 = diagnostics.get("gate2_intended_use", False)
    gate3 = diagnostics.get("gate3_use_scenario", False)

    evidence_paths = [
        {
            "system": system_local,
            "component": _short(comp),
            "disposition": _short(disp),
        }
        for comp, disp in bindings[:3]
    ]

    checks = {
        "shacl": shacl_ok,
        "shacl_violation_count": shacl_violation_count,
        "traceability": traceability_ok,
        "entailment": inference_ok,
    }
    if latent_ok is not None:
        checks["latent_risk"] = latent_ok

    all_pass = checks["shacl"] and checks["traceability"] and checks["entailment"]
    if latent_ok is not None:
        all_pass = all_pass and latent_ok

    human_explanation = {
        "overview": (
            "This artifact records a deterministic ARCO determination over the provided ontology and instance graph."
        ),
        "determination": _human_state_explanation(
            commitment_state=commitment_state,
            classification=classification,
            gate1=gate1,
            gate2=gate2,
            gate3=gate3,
            missing_commitments=missing_commitments,
        ),
        "gates": [
            f"Gate 1 (biometric capability commitment): {'satisfied' if gate1 else 'not satisfied'}.",
            f"Gate 2 (intended-use specification): {'satisfied' if gate2 else 'not satisfied'}.",
            f"Gate 3 (use-scenario specification): {'satisfied' if gate3 else 'not satisfied'}.",
        ],
        "checks": (
            "SHACL validates structural documentation constraints; traceability verifies required audit links; "
            "entailment verifies whether HighRiskSystem is derivable from asserted structure."
        ),
    }

    return {
        "schema_version": "arco.pipeline.result.v1",
        "run": {
            "timestamp_utc": run_timestamp_utc,
            "git_commit_hash": git_commit_hash,
        },
        "profile": profile,
        "system": {
            "local_name": system_local,
            "iri": f"https://arco.ai/ontology/core#{system_local}",
            "instances_file": str(instances_path),
        },
        "regime": "EU AI Act (Article 6 / Annex III)",
        "counts": {
            "asserted_triples": asserted_triples,
            "reasoned_triples": reasoned_triples,
            "entailed_triples_added": entailed_triples_added,
        },
        "classification": {
            "label": classification,
            "class_iri": classification_iri,
            "mode": classification_mode,
            "state": commitment_state,
        },
        "gates": {
            "gate1_biometric_capability": gate1,
            "gate2_intended_use": gate2,
            "gate3_use_scenario": gate3,
            "missing_commitments": missing_commitments,
        },
        "signals": {
            "high_risk_entailed": diagnostics.get("high_risk_entailed", False),
            "annex_iii_1a_entailed": diagnostics.get("annex_iii_1a_entailed", False),
            "has_assessment_documentation": diagnostics.get("has_assessment_documentation", False),
            "has_any_capability_signal": diagnostics.get("has_any_capability_signal", False),
        },
        "checks": checks,
        "all_checks_passed": all_pass,
        "evidence_paths": evidence_paths,
        "evidence_path_predicates": {
            "has_part": "http://purl.obolibrary.org/obo/BFO_0000051",
            "has_disposition": "http://purl.obolibrary.org/obo/RO_0000091",
        },
        "human_explanation": human_explanation,
    }


def write_result_json(payload: dict, out_path: str) -> Path:
    target = Path(out_path)
    if not target.is_absolute():
        target = REPO_ROOT / target
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return target


def build_determination_ttl(payload: dict) -> str:
    system_local = payload["system"]["local_name"]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    determination_local = f"ARCO_Determination_{system_local}_{stamp}"

    classification_label = payload["classification"]["label"]
    classification_mode = payload["classification"]["mode"]
    determination_state = payload["classification"]["state"]

    checks = payload["checks"]
    gates = payload["gates"]
    missing = payload["gates"]["missing_commitments"]
    human = payload["human_explanation"]

    comments = [
        human["overview"],
        human["determination"],
        *human["gates"],
        human["checks"],
        f"Classification label: {classification_label} ({classification_mode}).",
        f"Determination state: {determination_state}.",
        f"Check results: SHACL={checks.get('shacl')}, Traceability={checks.get('traceability')}, Entailment={checks.get('entailment')}, LatentRisk={checks.get('latent_risk')}.",
    ]

    if missing:
        comments.append("Missing commitments: " + "; ".join(missing) + ".")
    else:
        comments.append("Missing commitments: none.")

    classification_type = ":HighRiskDetermination" if classification_label == "HighRiskSystem" else ":ComplianceDetermination"
    comment_lines = "\n".join(
        f'  rdfs:comment "{_escape_ttl_literal(line)}" ;' for line in comments
    )

    return (
        "@prefix : <https://arco.ai/ontology/core#> .\n"
        "@prefix run: <https://arco.ai/ontology/runs#> .\n"
        "@prefix iao: <http://purl.obolibrary.org/obo/IAO_> .\n"
        "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n"
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
        "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n\n"
        f"run:{determination_local} rdf:type {classification_type} ;\n"
        f"  rdfs:label \"ARCO Determination for {system_local} ({stamp})\" ;\n"
        f"  iao:0000136 :{system_local} ;\n"
        f"  rdfs:comment \"Generated by run_pipeline.py with schema {payload['schema_version']}.\" ;\n"
        f"{comment_lines}\n"
        "  rdfs:comment \"This determination artifact models epistemic state from available evidence and does not invent unsupported reality-side commitments.\" .\n"
    )


def write_result_ttl(payload: dict, out_path: str) -> Path:
    target = Path(out_path)
    if not target.is_absolute():
        target = REPO_ROOT / target
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(build_determination_ttl(payload), encoding="utf-8")
    return target


def build_markdown_report(payload: dict) -> str:
    run_meta = payload.get("run", {})
    system = payload["system"]
    classification = payload["classification"]
    gates = payload["gates"]
    checks = payload["checks"]
    evidence_paths = payload.get("evidence_paths", [])
    predicates = payload.get("evidence_path_predicates", {})

    gate_rows = [
        ("Gate 1 (capability commitment)", gates.get("gate1_biometric_capability", False)),
        ("Gate 2 (intended use)", gates.get("gate2_intended_use", False)),
        ("Gate 3 (use scenario / affected role)", gates.get("gate3_use_scenario", False)),
    ]

    check_rows: list[tuple[str, str]] = [
        (
            "SHACL",
            f"{'PASS' if checks.get('shacl') else 'FAIL'} (violations: {checks.get('shacl_violation_count', 0)})",
        ),
        ("Traceability", "PASS" if checks.get("traceability") else "FAIL"),
        ("Entailment", "PASS" if checks.get("entailment") else "FAIL"),
    ]
    if "latent_risk" in checks:
        check_rows.append(("Latent risk", "PASS" if checks.get("latent_risk") else "FAIL"))

    lines = [
        "# ARCO Determination Report",
        "",
        f"- **System**: {system['local_name']}",
        f"- **System IRI**: {system['iri']}",
        f"- **Instances file**: {system['instances_file']}",
        f"- **Run timestamp (UTC)**: {run_meta.get('timestamp_utc', 'N/A')}",
        f"- **Git commit hash**: {run_meta.get('git_commit_hash') or 'N/A'}",
        "",
        f"- **Regime**: {payload['regime']}",
        f"- **Classification state**: {classification['state']}",
        f"- **Classification label**: {classification['label']}",
    ]

    if classification.get("class_iri"):
        lines.append(f"- **Entailed class IRI**: {classification['class_iri']}")

    lines.extend([
        "",
        "## Gate Results",
        "",
        "| Gate | Result |",
        "|---|---|",
    ])
    for gate_name, ok in gate_rows:
        lines.append(f"| {gate_name} | {'PASS' if ok else 'FAIL'} |")

    lines.extend([
        "",
        "## Check Results",
        "",
        "| Check | Result |",
        "|---|---|",
    ])
    for check_name, result in check_rows:
        lines.append(f"| {check_name} | {result} |")

    lines.extend([
        "",
        "## Evidence Paths",
        "",
    ])

    if evidence_paths:
        has_part = predicates.get("has_part", "http://purl.obolibrary.org/obo/BFO_0000051")
        has_disposition = predicates.get("has_disposition", "http://purl.obolibrary.org/obo/RO_0000091")
        lines.append(f"- Predicates used: `{has_part}` and `{has_disposition}`")
        for path in evidence_paths:
            lines.append(
                f"- {path['system']} --{has_part}--> {path['component']} --{has_disposition}--> {path['disposition']}"
            )
    else:
        lines.append("No evidence path entailed under current axioms.")

    lines.extend([
        "",
        "## Missing Commitments",
        "",
    ])
    missing_commitments = gates.get("missing_commitments", [])
    if missing_commitments:
        for item in missing_commitments:
            lines.append(f"- {item}")
    else:
        lines.append("- (none)")
    lines.append(
        "These are missing ICE commitments required by the Annex III gate pattern; absence is not evidence of absence."
    )

    return "\n".join(lines) + "\n"


def write_report_markdown(payload: dict, out_path: str) -> Path:
    target = Path(out_path)
    if not target.is_absolute():
        target = REPO_ROOT / target
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(build_markdown_report(payload), encoding="utf-8")
    return target

def main() -> None:
    global INSTANCES
    global SYSTEM_LOCAL
    global SYSTEM_IRI

    args = parse_args()
    INSTANCES, SYSTEM_LOCAL = resolve_runtime_selection(args)
    SYSTEM_IRI = f"https://arco.ai/ontology/core#{SYSTEM_LOCAL}"

    hr("ARCO COMPLIANCE VERIFICATION PIPELINE (OPERATOR VIEW)")

    sub("LOAD")
    print("Loading: core ontology + governance extension + instance data")
    print(f"System: {SYSTEM_LOCAL}")
    print(f"Instances file: {INSTANCES}")
    g_source = load_union_graph(CORE, GOV, INSTANCES)
    print(f"Triples loaded (asserted): {len(g_source)}")

    # clone -> reason over the copy so we can compare pre vs post
    g = clone_graph(g_source)

    g, initial_count, inferred_added = run_reasoning(g)

    shacl_ok, shacl_violation_count = run_shacl(g)

    sub("AUDIT QUERIES (SPARQL ASK)")
    print("Traceability check...")
    traceability_ok = run_sparql_ask_from_file(g, TRACEABILITY_QUERY)
    print(f"Traceability: {traceability_ok}")

    latent_ok = None
    if LATENT_RISK_QUERY.exists():
        print("\nLatent risk detection (hardware path)...")
        latent_ok = run_sparql_ask_from_file(g, LATENT_RISK_QUERY)
        print(f"Latent risk detected: {latent_ok}")

    inference_ok, asserted_pre, entailed_post, bindings = verify_high_risk_inference(g, g_source)
    commitment_state, missing_commitments, diagnostics = determine_commitment_state(g, SYSTEM_LOCAL)

    sub("COMMITMENT STATE")
    print(f"State: {commitment_state}")
    print("Evidence gates:")
    print(f"  Gate 1 (biometric capability): {diagnostics['gate1_biometric_capability']}")
    print(f"  Gate 2 (intended use):         {diagnostics['gate2_intended_use']}")
    print(f"  Gate 3 (use scenario):         {diagnostics['gate3_use_scenario']}")
    if missing_commitments:
        print("Missing commitments:")
        for item in missing_commitments:
            print(f"  - {item}")
    else:
        print("Missing commitments: (none)")

    # ---------------------------------------------------------------
    # SUMMARY (existing)
    # ---------------------------------------------------------------
    hr("SUMMARY")
    print(f"SHACL:         {_pf(shacl_ok)}")
    print(f"Traceability:  {_pf(traceability_ok)}")
    if latent_ok is not None:
        print(f"Latent risk:   {_pf(latent_ok)}")
    print(f"Entailment:    {_pf(inference_ok)}")
    print(f"State:         {commitment_state}")
    print(f"Entailed triples added: +{inferred_added}")

    all_pass = shacl_ok and traceability_ok and inference_ok
    if latent_ok is not None:
        all_pass = all_pass and latent_ok

    print("\nALL CHECKS PASSED" if all_pass else "\nSOME CHECKS FAILED")

    # ---------------------------------------------------------------
    # REGULATORY DETERMINATION CERTIFICATE
    # ---------------------------------------------------------------
    if not asserted_pre and entailed_post:
        classification_mode = "INFERRED"
    elif asserted_pre and entailed_post:
        classification_mode = "ASSERTED"
    else:
        classification_mode = "NOT PRESENT"

    # Derive triggering capability class from bindings
    trigger_display = "N/A"
    if bindings:
        trigger_display = _short(bindings[0][1])

    # Build evidence path strings (up to 3)
    evidence_lines = []
    for comp, disp in bindings[:3]:
        evidence_lines.append(f"  {SYSTEM_LOCAL} -> {_short(comp)} -> {_short(disp)}")

    hr("REGULATORY DETERMINATION CERTIFICATE")
    print(f"  SYSTEM:                  {SYSTEM_LOCAL}")
    print(f"  REGIME:                  EU AI Act (Article 6 / Annex III)")
    print(f"  DETERMINATION STATE:     {commitment_state}")
    if classification_mode in ("INFERRED", "ASSERTED"):
        print(f"  CLASSIFICATION:          HighRiskSystem ({classification_mode})")
    else:
        print(f"  CLASSIFICATION:          {classification_mode}")
    print(f"  TRIGGERING CAPABILITY:   {trigger_display}")
    if evidence_lines:
        print(f"  EVIDENCE PATH:")
        for line in evidence_lines:
            print(line)
    else:
        print(f"  EVIDENCE PATH:           (none detected)")
    print(f"  SHACL:                   {_pf(shacl_ok)}")
    print(f"  TRACEABILITY:            {_pf(traceability_ok)}")
    if latent_ok is not None:
        print(f"  LATENT RISK:             {'DETECTED' if latent_ok else 'NOT DETECTED'}")
    print(f"  ENTAILED TRIPLES ADDED:  +{inferred_added}")
    if missing_commitments:
        print(f"  MISSING COMMITMENTS:")
        for item in missing_commitments:
            print(f"    - {item}")
    print("=" * 72)

    payload = build_result_payload(
        profile=args.profile,
        instances_path=INSTANCES,
        system_local=SYSTEM_LOCAL,
        asserted_triples=initial_count,
        reasoned_triples=len(g),
        entailed_triples_added=inferred_added,
        shacl_ok=shacl_ok,
        traceability_ok=traceability_ok,
        latent_ok=latent_ok,
        inference_ok=inference_ok,
        asserted_pre=asserted_pre,
        entailed_post=entailed_post,
        commitment_state=commitment_state,
        missing_commitments=missing_commitments,
        diagnostics=diagnostics,
        bindings=bindings,
        shacl_violation_count=shacl_violation_count,
        run_timestamp_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        git_commit_hash=get_git_commit_hash(),
    )

    if args.json_out:
        written = write_result_json(payload, args.json_out)
        print(f"JSON result written: {written}")

    if args.determination_ttl_out:
        written_ttl = write_result_ttl(payload, args.determination_ttl_out)
        print(f"Determination TTL written: {written_ttl}")

    if args.report_out:
        written_report = write_report_markdown(payload, args.report_out)
        print(f"Markdown report written: {written_report}")


if __name__ == "__main__":
    main()
