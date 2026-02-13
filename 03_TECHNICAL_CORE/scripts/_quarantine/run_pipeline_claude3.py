"""QUARANTINED: not operational pipeline (stale high-risk assumptions).

ARCO Compliance Verification Pipeline — Claude 3 Model Family

Evaluates Anthropic's Claude 3 system against EU AI Act obligations.
Demonstrates ARCO operating on a REAL frontier AI system, not a synthetic example.

Stages:
1) Load ontology + Claude 3 instance data
2) OWL-RL reasoning (materialize entailments)
3) SHACL validation
4) SPARQL audit checks (ASK + SELECT)
5) Verify HighRiskSystem entailment + evidence paths
6) Print regulatory determination certificate

Expected result: Claude 3 is classified as HighRiskSystem via TWO
independent inference paths:
  Path 1: VisionCapability -> BiometricIdentificationCapability (Annex III 1a)
  Path 2: ComputerUseCapability -> AutonomousAgentCapability (Annex III 2)
"""

from __future__ import annotations

import sys
from pathlib import Path
from rdflib import Graph

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
INSTANCES = ONTOLOGY_DIR / "ARCO_instances_claude3.ttl"

SHAPES = VALIDATION_DIR / "assessment_documentation_shape.ttl"

# Claude 3-specific SPARQL queries
TRACEABILITY_QUERY = REASONING_DIR / "claude3_check_assessment_traceability.sparql"
LATENT_RISK_QUERY = REASONING_DIR / "claude3_detect_latent_risk.sparql"
HIGH_RISK_INFERENCE_QUERY = REASONING_DIR / "claude3_check_high_risk_inference.sparql"
ENUMERATE_RISKS_QUERY = REASONING_DIR / "claude3_enumerate_risk_paths.sparql"

# --- System under evaluation ---
SYSTEM_LOCAL = "Claude3_System"
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

def run_sparql_select_from_file(data_graph: Graph, query_path: Path) -> list:
    if not query_path.exists():
        return []
    q = query_path.read_text(encoding="utf-8").strip()
    try:
        return list(data_graph.query(q))
    except Exception:
        return []


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

def run_shacl(data_graph: Graph) -> bool:
    sub("SHACL")
    if not SHAPES.exists():
        raise FileNotFoundError(f"Missing SHACL shapes file: {SHAPES}")

    print("Validating SHACL shapes against the reasoned graph...")
    shapes_graph = Graph().parse(SHAPES.as_posix(), format="turtle")

    conforms, _, report_text = validate(
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

    return conforms


# ---------------------------
# proof / evidence extraction
# ---------------------------

def _ask_highrisk(sys: str = SYSTEM_LOCAL) -> str:
    return f"""
PREFIX : <{ARCO_NS}>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
ASK WHERE {{ :{sys} rdf:type :HighRiskSystem . }}
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
LIMIT 20
"""

def _short(iri: str) -> str:
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

    asserted_pre = run_sparql_ask_inline(source, _ask_highrisk())

    if HIGH_RISK_INFERENCE_QUERY.exists():
        entailed_post = run_sparql_ask_from_file(reasoned, HIGH_RISK_INFERENCE_QUERY)
    else:
        entailed_post = run_sparql_ask_inline(reasoned, _ask_highrisk())

    print(f"HighRiskSystem in source data (pre-reasoning):   {asserted_pre}")
    print(f"HighRiskSystem in reasoned graph (post-reason):  {entailed_post}")

    primary_path = run_sparql_ask_inline(reasoned, _ask_primary_path())

    sub("EVIDENCE PATH CHECK")
    print(f"has_disposition path (RO:0000091): {primary_path}")

    bindings = get_primary_bindings(reasoned)
    if bindings:
        sub("CONCRETE BINDINGS (all triggering paths)")
        for i, (comp, disp) in enumerate(bindings, 1):
            print(f"{i}) component = {_short(comp)}")
            print(f"   disposition/capability = {_short(disp)}")

    sub("WHY THIS ENTAILS HighRiskSystem")
    print("Bridge axiom (ARCO_core.ttl):")
    print("  HighRiskSystem = System AND (has_part SOME (has_disposition SOME AnnexIIITriggeringCapability))")
    print()
    print("AnnexIIITriggeringCapability = BiometricIdentificationCapability OR AutonomousAgentCapability")
    print()
    if not asserted_pre and entailed_post:
        print(f"  => {SYSTEM_LOCAL} rdf:type HighRiskSystem  (INFERRED, not asserted)")
        print()
        print("  Claude 3 was NEVER explicitly tagged as high-risk.")
        print("  The reasoner DERIVED it from the system's structure and capabilities.")
    elif entailed_post:
        print(f"  => {SYSTEM_LOCAL} rdf:type HighRiskSystem  (ASSERTED)")

    if entailed_post and not primary_path:
        sub("FAIL")
        print("Entailment is True, but no supporting evidence path was detected.")
        return False, asserted_pre, entailed_post, bindings

    if entailed_post:
        sub("SUCCESS")
        print("HighRiskSystem classification is present AND justified by explicit structural paths.")
        return True, asserted_pre, entailed_post, bindings

    sub("FAIL")
    print("HighRiskSystem was not inferred.")
    print("Common causes:")
    print("  - owlrl not installed (no reasoning step)")
    print("  - bridge axiom uses a different predicate than the instances")
    print("  - missing has_part/component facts or missing AnnexIIITriggeringCapability typing")
    return False, asserted_pre, entailed_post, bindings


# ---------------------------
# main
# ---------------------------

def _pf(ok: bool) -> str:
    return "PASS" if ok else "FAIL"

def main() -> None:
    hr("ARCO COMPLIANCE VERIFICATION PIPELINE — CLAUDE 3 MODEL FAMILY")
    print("System under evaluation: Anthropic Claude 3 (Opus/Sonnet/Haiku + 3.5 Sonnet)")
    print("Source: Claude 3 Model Card (March 2024) + Claude 3.5 Addendum")

    sub("LOAD")
    print("Loading: core ontology + governance extension + Claude 3 instances")
    g_source = load_union_graph(CORE, GOV, INSTANCES)
    print(f"Triples loaded (asserted): {len(g_source)}")

    g = clone_graph(g_source)

    g, initial_count, inferred_added = run_reasoning(g)

    shacl_ok = run_shacl(g)

    sub("AUDIT QUERIES (SPARQL ASK)")
    print("Traceability check...")
    traceability_ok = run_sparql_ask_from_file(g, TRACEABILITY_QUERY)
    print(f"Traceability: {traceability_ok}")

    latent_ok = None
    if LATENT_RISK_QUERY.exists():
        print("\nLatent risk detection (model component path)...")
        latent_ok = run_sparql_ask_from_file(g, LATENT_RISK_QUERY)
        print(f"Latent risk detected: {latent_ok}")

    # Enumerate all risk paths (SELECT query — shows every triggering binding)
    if ENUMERATE_RISKS_QUERY.exists():
        sub("RISK PATH ENUMERATION")
        risk_rows = run_sparql_select_from_file(g, ENUMERATE_RISKS_QUERY)
        if risk_rows:
            print(f"Found {len(risk_rows)} triggering risk path(s):")
            for i, row in enumerate(risk_rows, 1):
                print(f"  {i}) {_short(str(row.component))} -> {_short(str(row.disposition))} [{_short(str(row.capabilityType))}]")
        else:
            print("No risk paths found via SELECT query.")

    inference_ok, asserted_pre, entailed_post, bindings = verify_high_risk_inference(g, g_source)

    # ---------------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------------
    hr("SUMMARY")
    print(f"SHACL:         {_pf(shacl_ok)}")
    print(f"Traceability:  {_pf(traceability_ok)}")
    if latent_ok is not None:
        print(f"Latent risk:   {_pf(latent_ok)}")
    print(f"Entailment:    {_pf(inference_ok)}")
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

    # Collect unique triggering capabilities from bindings
    triggers = list(dict.fromkeys([_short(d) for _, d in bindings]))
    trigger_display = ", ".join(triggers[:5]) if triggers else "N/A"

    evidence_lines = []
    for comp, disp in bindings[:8]:
        evidence_lines.append(f"    {SYSTEM_LOCAL} -> {_short(comp)} -> {_short(disp)}")

    hr("REGULATORY DETERMINATION CERTIFICATE")
    print(f"  SYSTEM:                  {SYSTEM_LOCAL}")
    print(f"  SYSTEM LABEL:            Anthropic Claude 3 Model Family")
    print(f"  PROVIDER:                Anthropic")
    print(f"  REGIME:                  EU AI Act (Article 6 / Annex III / Chapter V)")
    if classification_mode in ("INFERRED", "ASSERTED"):
        print(f"  CLASSIFICATION:          HighRiskSystem ({classification_mode})")
    else:
        print(f"  CLASSIFICATION:          {classification_mode}")
    print(f"  TRIGGERING DISPOSITIONS: {trigger_display}")
    print(f"  ANNEX III CATEGORIES:")
    print(f"    1(a) Remote Biometric Identification — VisionCapability")
    print(f"    2    Critical Infrastructure — ComputerUseCapability/AutonomousAgentCapability")
    print(f"  GPAI OBLIGATIONS:        Chapter V (general-purpose AI model)")
    print(f"  ARTICLE 50:              Transparency (content generation)")
    print(f"  SAFETY FRAMEWORK:        Anthropic RSP — ASL-2")
    if evidence_lines:
        print(f"  EVIDENCE PATHS:")
        for line in evidence_lines:
            print(line)
    else:
        print(f"  EVIDENCE PATHS:          (none detected)")
    print(f"  SHACL:                   {_pf(shacl_ok)}")
    print(f"  TRACEABILITY:            {_pf(traceability_ok)}")
    if latent_ok is not None:
        print(f"  LATENT RISK:             {'DETECTED' if latent_ok else 'NOT DETECTED'}")
    print(f"  ENTAILED TRIPLES ADDED:  +{inferred_added}")
    print()
    print("  NOTE: Claude 3's HighRiskSystem classification is INFERRED by the")
    print("  reasoner from structural facts. Vision capability subsumes biometric")
    print("  identification. Computer use capability subsumes autonomous agent")
    print("  capability. Neither capability needs to be actively deployed —")
    print("  the latent disposition in the model weights is sufficient.")
    print("=" * 72)

    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
