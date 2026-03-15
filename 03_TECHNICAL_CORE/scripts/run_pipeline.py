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
from datetime import datetime, timezone
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
INSTANCES = ONTOLOGY_DIR / "ARCO_instances_sentinel.ttl"

SHAPES = VALIDATION_DIR / "assessment_documentation_shape.ttl"

TRACEABILITY_QUERY = REASONING_DIR / "check_assessment_traceability.sparql"
LATENT_RISK_QUERY = REASONING_DIR / "detect_latent_risk.sparql"
HIGH_RISK_INFERENCE_QUERY = REASONING_DIR / "check_high_risk_inference.sparql"
INTENDED_USE_QUERY = REASONING_DIR / "check_intended_use.sparql"
ANNEX_III_1A_QUERY = REASONING_DIR / "check_annex_iii_1a_entailment.sparql"
ANNEX_III_5B_QUERY = REASONING_DIR / "check_annex_iii_5b_entailment.sparql"
OBLIGATION_QUERY = REASONING_DIR / "check_obligation_link.sparql"
REGULATORY_ALIGNMENT_QUERY = REASONING_DIR / "check_regulatory_alignment.sparql"

OUTPUT_DIR = REPO_ROOT / "runs" / "demo"

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

def run_sparql_ask_for_system(data_graph: Graph, query_path: Path, system_local: str) -> bool:
    """Run a SPARQL ASK file query, substituting the sentinel placeholder with the actual system IRI."""
    if not query_path.exists():
        raise FileNotFoundError(f"Missing SPARQL query file: {query_path}")
    q = query_path.read_text(encoding="utf-8").strip()
    if system_local != "Sentinel_ID_System":
        q = q.replace(":Sentinel_ID_System", f":{system_local}")
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
    sub("REASONING")
    if not HAS_OWLRL:
        raise RuntimeError(
            "owlrl is not installed, but this pipeline requires reasoning.\n"
            "Install: pip install owlrl"
        )

    initial = len(data_graph)
    print("Running OWL-RL closure (materializing entailments)...")
    owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(data_graph)
    final = len(data_graph)
    added = final - initial
    print(f"Triples: {initial} -> {final}   (+{added} entailed)")
    return data_graph, initial, added

def run_shacl(data_graph: Graph) -> tuple[bool, str]:
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

    return conforms, str(report_text) if report_text else ""


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
LIMIT 5
"""

def _short(iri: str) -> str:
    """Shorten an IRI to its local name for display."""
    return iri.rsplit("#", 1)[-1] if "#" in iri else iri.rsplit("/", 1)[-1]

def get_primary_bindings(g: Graph, system_local: str = "Sentinel_ID_System") -> list[tuple[str, str]]:
    rows = []
    try:
        qres = g.query(_select_primary_bindings(system_local))
        for r in qres:
            rows.append((str(r.component), str(r.d)))
    except Exception:
        return []
    return rows


# ---------------------------
# determination packet
# ---------------------------

def _select_cap_type_label(sys: str = SYSTEM_LOCAL) -> str:
    """SELECT the most specific ARCO capability class (direct subclass of AnnexIIITriggeringCapability)
    that the disposition is typed as, plus its rdfs:label."""
    return f"""
PREFIX : <{ARCO_NS}>
PREFIX bfo: <http://purl.obolibrary.org/obo/BFO_>
PREFIX ro:  <http://purl.obolibrary.org/obo/RO_>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?capType ?capLabel WHERE {{
  :{sys} bfo:0000051 ?comp .
  ?comp ro:0000091 ?disp .
  ?disp rdf:type ?capType .
  ?capType rdfs:subClassOf :AnnexIIITriggeringCapability .
  OPTIONAL {{ ?capType rdfs:label ?capLabel }}
}}
LIMIT 1
"""

def _select_gate2_process(sys: str = SYSTEM_LOCAL) -> str:
    """SELECT the prescribed process instance and its type + rdfs:label from the IntendedUseSpecification."""
    return f"""
PREFIX : <{ARCO_NS}>
PREFIX cco: <http://www.ontologyrepository.com/CommonCoreOntologies/>
PREFIX iao: <http://purl.obolibrary.org/obo/IAO_>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?ius ?process ?processType ?processLabel WHERE {{
  ?ius a :IntendedUseSpecification ;
    cco:prescribes ?process ;
    iao:0000136 :{sys} .
  ?process rdf:type ?processType .
  OPTIONAL {{ ?processType rdfs:label ?processLabel }}
  FILTER(STRSTARTS(STR(?processType), "{ARCO_NS}"))
  FILTER(!isBlank(?processType))
}}
LIMIT 1
"""

def _select_gate3_role(sys: str = SYSTEM_LOCAL) -> str:
    """SELECT the UseScenarioSpecification linked to the system via NaturalPersonRole,
    plus the rdfs:label of NaturalPersonRole."""
    return f"""
PREFIX : <{ARCO_NS}>
PREFIX iao: <http://purl.obolibrary.org/obo/IAO_>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?uss ?roleLabel WHERE {{
  ?uss a :UseScenarioSpecification ;
    iao:0000136 :{sys} ;
    iao:0000136 :NaturalPersonRole .
  OPTIONAL {{ :NaturalPersonRole rdfs:label ?roleLabel }}
}}
LIMIT 1
"""

def select_gate_evidence(g: Graph, system_local: str = SYSTEM_LOCAL) -> dict:
    """Run SELECT queries over the reasoned graph to extract gate evidence labels.

    Returns a compact determination packet dict.  All labels come from rdfs:label
    annotations in the graph; falls back to shortened IRI local names if absent.
    This is the intermediate representation the HTML view renders from — it must
    not invent content not present in the post-reasoning graph.
    """
    packet: dict = {
        "gate1": {"cap_type_uri": "", "cap_type_label": ""},
        "gate2": {"ius_uri": "", "process_uri": "", "process_type_uri": "", "process_type_label": ""},
        "gate3": {"uss_uri": "", "role_uri": f"{ARCO_NS}NaturalPersonRole", "role_label": ""},
    }

    try:
        rows = list(g.query(_select_cap_type_label(system_local)))
        if rows:
            r = rows[0]
            cap_uri = str(r[0]) if r[0] else ""
            packet["gate1"]["cap_type_uri"] = cap_uri
            packet["gate1"]["cap_type_label"] = str(r[1]) if r[1] else _short(cap_uri)
    except Exception:
        pass

    try:
        rows = list(g.query(_select_gate2_process(system_local)))
        if rows:
            r = rows[0]
            packet["gate2"]["ius_uri"] = str(r[0]) if r[0] else ""
            packet["gate2"]["process_uri"] = str(r[1]) if r[1] else ""
            ptype_uri = str(r[2]) if r[2] else ""
            packet["gate2"]["process_type_uri"] = ptype_uri
            packet["gate2"]["process_type_label"] = str(r[3]) if r[3] else _short(ptype_uri)
    except Exception:
        pass

    try:
        rows = list(g.query(_select_gate3_role(system_local)))
        if rows:
            r = rows[0]
            packet["gate3"]["uss_uri"] = str(r[0]) if r[0] else ""
            packet["gate3"]["role_label"] = str(r[1]) if r[1] else "Natural Person Role"
    except Exception:
        pass

    return packet

def verify_high_risk_inference(reasoned: Graph, source: Graph) -> tuple[bool, bool, bool, list[tuple[str, str]]]:
    """Returns (inference_ok, asserted_pre, entailed_post, bindings)."""
    hr("ARCO RESULT (ENTAILMENT + PROOF SKETCH)")

    # Before/after: was HighRiskSystem asserted in raw input?
    asserted_pre = run_sparql_ask_inline(source, _ask_highrisk(SYSTEM_LOCAL))

    # After reasoning: is HighRiskSystem present now?
    if HIGH_RISK_INFERENCE_QUERY.exists():
        entailed_post = run_sparql_ask_for_system(reasoned, HIGH_RISK_INFERENCE_QUERY, SYSTEM_LOCAL)
    else:
        entailed_post = run_sparql_ask_inline(reasoned, _ask_highrisk(SYSTEM_LOCAL))

    print(f"HighRiskSystem in source data (pre-reasoning):   {asserted_pre}")
    print(f"HighRiskSystem in reasoned graph (post-reason):  {entailed_post}")

    # Evidence check (primary path only — legacy bearer_of removed)
    primary_path = run_sparql_ask_inline(reasoned, _ask_primary_path(SYSTEM_LOCAL))

    sub("EVIDENCE PATH CHECK")
    print(f"has_disposition path (RO:0000091): {primary_path}")

    # Concrete bindings
    bindings = get_primary_bindings(reasoned, SYSTEM_LOCAL)
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

    sub("FAIL")
    print("HighRiskSystem was not inferred.")
    print("Common causes:")
    print("  - owlrl not installed (no reasoning step)")
    print("  - bridge axiom uses a different predicate than the instances")
    print("  - missing has_part/component facts or missing AnnexIIITriggeringCapability typing")
    return False, asserted_pre, entailed_post, bindings


# ---------------------------
# HTML view
# ---------------------------

def write_html_view(
    output_dir: Path,
    system_local: str,
    classification_mode: str,
    bindings: list,
    shacl_ok: bool,
    traceability_ok: bool,
    inference_ok: bool,
    latent_ok,
    intended_use_ok,
    annex_iii_1a_ok,
    annex_iii_5b_ok,
    obligation_ok,
    reg_alignment_ok,
    inferred_added: int,
    all_pass: bool,
    summary_raw: str,
    evidence_raw: str,
    gate_evidence: dict | None = None,
) -> None:
    """Write a self-contained static HTML determination view to output_dir.

    Viewer invariant:
    This HTML artifact is an explanatory surface over pipeline outputs, not a
    reasoning engine. Any visual compression is acceptable only if it:
      1. preserves the direction of reasoning,
      2. does not reverse asserted vs entailed status,
      3. does not invent evidence not present in pipeline outputs,
      4. explicitly discloses any collapsed inferential step where that collapse
         matters (e.g. subclass-mediated type propagation shown as a bridge edge).
    """

    if gate_evidence is None:
        gate_evidence = {"gate1": {"cap_type_uri": "", "cap_type_label": ""},
                         "gate2": {"ius_uri": "", "process_uri": "", "process_type_uri": "", "process_type_label": ""},
                         "gate3": {"uss_uri": "", "role_uri": "", "role_label": ""}}

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # ── strip node labels ──────────────────────────────────────────
    comp_label = _short(bindings[0][0]) if bindings else "\u2014"
    disp_label = _short(bindings[0][1]) if bindings else "\u2014"
    comp_iri   = bindings[0][0] if bindings else ""
    disp_iri   = bindings[0][1] if bindings else ""

    # ── classification labels ──────────────────────────────────────
    is_high_risk = classification_mode in ("INFERRED", "ASSERTED")
    result_label = "HighRiskSystem" if is_high_risk else "NOT CLASSIFIED AS HIGH RISK"

    # ── derive triggered Annex III categories from pipeline results ─
    triggered_categories = []
    if annex_iii_1a_ok:
        triggered_categories.append({
            "id": "1a",
            "label": "Annex III, Category 1(a)",
            "title": "Biometric identification of natural persons",
            "article_ref": "Article 6(2), Annex III point 1(a)",
            "capability": gate_evidence["gate1"]["cap_type_label"] or "Biometric identification",
            "process": gate_evidence["gate2"]["process_type_label"] or "Remote biometric identification",
            "role": gate_evidence["gate3"]["role_label"] or "Natural persons",
        })
    if annex_iii_5b_ok:
        triggered_categories.append({
            "id": "5b",
            "label": "Annex III, Category 5(b)",
            "title": "Creditworthiness evaluation of natural persons",
            "article_ref": "Article 6(2), Annex III point 5(b)",
            "capability": "Creditworthiness evaluation",
            "process": "Creditworthiness evaluation",
            "role": "Natural persons",
        })

    # ── human-readable system name ─────────────────────────────────
    sys_display = system_local.replace("_", " ")

    # ── build executive summary text ───────────────────────────────
    if is_high_risk and triggered_categories:
        cat_list = ", ".join(c["label"] for c in triggered_categories)
        cap_list = ", ".join(c["capability"] for c in triggered_categories)
        summary_text = (
            f"{sys_display} is classified as <strong>High Risk</strong> under the "
            f"EU AI Act. The system possesses a {cap_list}, triggering "
            f"{cat_list}. All three regulatory gates are satisfied for each applicable "
            f"category, and the classification was {classification_mode.lower()} by "
            f"OWL-RL formal reasoning over {inferred_added:,} entailed triples."
        )
    elif is_high_risk:
        summary_text = (
            f"{sys_display} is classified as <strong>High Risk</strong> under the "
            f"EU AI Act. Classification was {classification_mode.lower()} by OWL-RL "
            f"formal reasoning."
        )
    else:
        summary_text = (
            f"{sys_display} was <strong>not classified as High Risk</strong> under "
            f"the EU AI Act based on current assertions. The OWL-RL reasoner did not "
            f"entail HighRiskSystem membership."
        )

    if all_pass:
        summary_text += (
            " All structural validation (SHACL) and audit checks (SPARQL) pass."
        )
    else:
        summary_text += (
            " <strong>Some checks did not pass</strong> \u2014 see the audit results below."
        )

    # ── gate narrative builder ─────────────────────────────────────
    def _gate_status_class(ok):
        if ok is None: return "gate-na"
        return "gate-pass" if ok else "gate-fail"

    def _gate_status_label(ok):
        if ok is None: return "N/A"
        return "SATISFIED" if ok else "NOT SATISFIED"

    # ── badge helpers ──────────────────────────────────────────────
    def _b(val, t="PASS", f="FAIL"):
        if val is None:
            return '<span class="badge bn">N/A</span>'
        return f'<span class="badge {"bp" if val else "bf"}">{t if val else f}</span>'

    def _annex(val):
        if val is None:
            return '<span class="badge bn">N/A</span>'
        if val:
            return '<span class="badge bp">VERIFIED (ENTAILED)</span>'
        return '<span class="badge bn">NOT APPLICABLE</span>'

    # ── mode badge ─────────────────────────────────────────────────
    if classification_mode == "INFERRED":
        mode_badge = '<span class="badge bi">INFERRED</span>'
    elif classification_mode == "ASSERTED":
        mode_badge = '<span class="badge ba">ASSERTED</span>'
    else:
        mode_badge = '<span class="badge bn">NOT PRESENT</span>'

    overall_badge = ('<span class="badge bp">ALL PASS</span>' if all_pass
                     else '<span class="badge bf">SOME FAIL</span>')

    # ── audit rows ─────────────────────────────────────────────────
    audit_rows = [
        ("SHACL conformance",        "classification / structure", _b(shacl_ok)),
        ("HighRiskSystem entailment", "classification / OWL-RL",   _b(inference_ok)),
        ("Annex III 1(a)",           "classification / OWL-RL",   _annex(annex_iii_1a_ok)),
        ("Annex III 5(b)",           "classification / OWL-RL",   _annex(annex_iii_5b_ok)),
        ("Traceability",             "audit / SPARQL",            _b(traceability_ok)),
        ("Latent risk",              "audit / SPARQL",
         _b(latent_ok, "DETECTED", "NOT DETECTED") if latent_ok is not None
         else '<span class="badge bn">N/A</span>'),
        ("Intended use modelled",    "audit / SPARQL",            _b(intended_use_ok)),
        ("Obligation linked",        "audit / SPARQL",            _b(obligation_ok)),
        ("Regulatory alignment",     "audit / SPARQL",            _b(reg_alignment_ok)),
    ]
    audit_html = "\n".join(
        f'          <tr><td>{chk}</td><td class="layer">{layer}</td><td>{badge}</td></tr>'
        for chk, layer, badge in audit_rows
    )

    # ── determination path nodes ───────────────────────────────────
    def node(cls, type_label, label, iri=""):
        iri_attr = f' title="{iri}"' if iri else ""
        return (f'<div class="node {cls}"{iri_attr}>'
                f'<span class="ntype">{type_label}</span>'
                f'<span class="nlabel">{label}</span></div>')

    def edge_el(rel, iri_label=""):
        sub = f'<span class="eiri">{iri_label}</span>' if iri_label else ""
        return (f'<div class="edge"><span class="earrow">\u2192</span>'
                f'<span class="erel">{rel}</span>{sub}</div>')

    result_node_cls = "nr-high" if is_high_risk else "nr-none"

    strip_html = (
        node("ns", "System", system_local)
        + edge_el("has_part", "bfo:0000051")
        + node("nc", "SystemComponent", comp_label, comp_iri)
        + edge_el("has_disposition", "ro:0000091")
        + node("nd", "Disposition", disp_label, disp_iri)
        + edge_el("rdf:type \u2286")
        + node("nt", "AnnexIIITriggeringCapability", "(bridge axiom) \u2021")
        + edge_el("OWL-RL \u22a2")
        + node(result_node_cls, "Classification", result_label)
    )

    # ── gate cards (for Layer 2) ───────────────────────────────────
    # Gate 1 is satisfied if inference_ok (HighRiskSystem entailed
    # requires has_part some (SystemComponent and has_disposition some
    # AnnexIIITriggeringCapability))
    gate1_ok = inference_ok
    # Gate 2 satisfied if intended_use is modelled with correct process type
    gate2_ok = intended_use_ok
    # Gate 3 satisfied if use scenario references NaturalPersonRole
    gate3_ok = reg_alignment_ok

    # Pre-compute gate display labels from the determination packet.
    # These are used in axiom pattern text, gate answers, and counterfactuals.
    # Using the full rdfs:label so text tracks ontology changes automatically.
    _cap_label      = gate_evidence["gate1"]["cap_type_label"] or "BiometricIdentificationCapability"
    _process_label  = gate_evidence["gate2"]["process_type_label"] or "RemoteBiometricIdentificationProcess"
    _role_label     = gate_evidence["gate3"]["role_label"] or "Natural Person Role"
    _role_local     = _short(gate_evidence["gate3"]["role_uri"]) if gate_evidence["gate3"]["role_uri"] else "NaturalPersonRole"

    gate_cards_html = f"""
        <div class="gate-card {_gate_status_class(gate1_ok)}">
          <div class="gate-header">
            <span class="gate-num">Gate 1</span>
            <span class="gate-title">Triggering Capability</span>
            <span class="gate-badge {'gbp' if gate1_ok else 'gbf'}">{_gate_status_label(gate1_ok)}</span>
          </div>
          <div class="gate-question">Does the system contain a component with a regulated capability?</div>
          <div class="gate-answer">
            {"<strong>Yes.</strong> The system contains <em>" + comp_label + "</em>, which has a disposition typed as <em>" + _cap_label + "</em> (<em>" + disp_label + "</em>). This disposition falls within the regulated capability scope of Annex III." if gate1_ok and bindings else "<strong>No triggering capability detected</strong> in the current system assertions."}
          </div>
          <details class="gate-evidence">
            <summary>Technical evidence</summary>
            <div class="gate-tech">
              <p><strong>Axiom pattern:</strong> System <code>bfo:0000051</code> some (SystemComponent and <code>ro:0000091</code> some {_cap_label})</p>
              <p><strong>Matched:</strong> {system_local} &rarr; {comp_label} &rarr; {disp_label}</p>
              <p><strong>Layer:</strong> OWL-RL entailment (classification-authoritative)</p>
              <p><strong>Relations:</strong> <code>bfo:0000051</code> (has_part), <code>ro:0000091</code> (has_disposition)</p>
            </div>
          </details>
        </div>

        <div class="gate-card {_gate_status_class(gate2_ok)}">
          <div class="gate-header">
            <span class="gate-num">Gate 2</span>
            <span class="gate-title">Prescribed Process Type</span>
            <span class="gate-badge {'gbp' if gate2_ok else 'gbf'}">{_gate_status_label(gate2_ok)}</span>
          </div>
          <div class="gate-question">Is the system prescribed for a regulated process type?</div>
          <div class="gate-answer">
            {"<strong>Yes.</strong> An Intended Use Specification prescribes the system for <em>" + _process_label + "</em>. This is not merely any use &mdash; the process token must be typed as the regulated process class for this gate to be satisfied." if gate2_ok else "<strong>No matching prescribed process type</strong> found in the intended use documentation."}
          </div>
          <details class="gate-evidence">
            <summary>Technical evidence</summary>
            <div class="gate-tech">
              <p><strong>Axiom pattern:</strong> IntendedUseSpecification <code>iao:0000136</code> System and <code>cco:prescribes</code> some {_process_label}</p>
              <p><strong>Gate mechanism:</strong> <code>owl:someValuesFrom</code> performs genuine type-checking &mdash; the prescribed process token must be an instance of the regulated process class, not a bare IRI reference</p>
              <p><strong>Layer:</strong> OWL-RL entailment (classification-authoritative)</p>
            </div>
          </details>
        </div>

        <div class="gate-card {_gate_status_class(gate3_ok)}">
          <div class="gate-header">
            <span class="gate-num">Gate 3</span>
            <span class="gate-title">Affected Role Category</span>
            <span class="gate-badge {'gbp' if gate3_ok else 'gbf'}">{_gate_status_label(gate3_ok)}</span>
          </div>
          <div class="gate-question">Does the use scenario reference the regulated role category?</div>
          <div class="gate-answer">
            {"<strong>Yes.</strong> A Use Scenario Specification references <em>" + _role_label + "</em> as a role category &mdash; the universal, not any specific individual. This satisfies the <code>owl:hasValue</code> restriction in the gate axiom, which checks for the role category itself rather than any particular role-bearer." if gate3_ok else "<strong>No matching role category</strong> found in the use scenario documentation."}
          </div>
          <details class="gate-evidence">
            <summary>Technical evidence</summary>
            <div class="gate-tech">
              <p><strong>Axiom pattern:</strong> UseScenarioSpecification <code>iao:0000136</code> System and <code>iao:0000136</code> :{_role_local}</p>
              <p><strong>Gate mechanism:</strong> <code>owl:hasValue</code> is intentional &mdash; the specification must reference the role <em>category</em> ({_role_label} as universal), not a role-bearer instance. This is a check on the role type, not on any particular person.</p>
              <p><strong>Layer:</strong> OWL-RL entailment (classification-authoritative)</p>
            </div>
          </details>
        </div>"""

    # ── counterfactual text (Layer 4) ──────────────────────────────
    if is_high_risk and triggered_categories:
        counterfactual_items = []
        for cat in triggered_categories:
            counterfactual_items.append(
                f'<div class="cf-item">'
                f'<div class="cf-label">{cat["label"]}</div>'
                f'<ul>'
                f'<li>If the system did not possess a <strong>{cat["capability"]}</strong>, Gate 1 would not be satisfied and this category would not apply.</li>'
                f'<li>If the intended use did not prescribe a <strong>{cat["process"]}</strong>, Gate 2 would not be satisfied. A system with the capability but prescribed for a different process type would not trigger this category.</li>'
                f'<li>If the use scenario did not reference the <strong>{cat["role"]}</strong> category, Gate 3 would not be satisfied.</li>'
                f'<li>Each gate is independently necessary. Removing any single condition changes the classification.</li>'
                f'</ul></div>'
            )
        counterfactual_html = "\n".join(counterfactual_items)
    else:
        counterfactual_html = (
            '<div class="cf-item"><p>No Annex III categories are currently triggered. '
            'To trigger a high-risk classification, the system would need to satisfy '
            'all three gates (capability, prescribed process, affected role) for at '
            'least one Annex III category.</p></div>'
        )

    # ── obligations text (Layer 3) ─────────────────────────────────
    if is_high_risk:
        obligations_html = """
        <p class="fn" style="margin-bottom:0.9rem">
          <strong>Static regulatory reference</strong> &mdash; the obligation categories
          below are fixed text drawn from EU AI Act Articles&nbsp;9&ndash;15, 43, Annex&nbsp;IV.
          They are <em>not</em> derived from this run&rsquo;s reasoning and will not
          automatically update if the regulation changes.
          For the authoritative determination see the Classification Gates above.
        </p>
        <div class="obl-grid">
          <div class="obl-card">
            <div class="obl-icon">1</div>
            <div class="obl-title">Conformity Assessment</div>
            <div class="obl-desc">The system must undergo conformity assessment procedures before being placed on the market or put into service (Article 43). For biometric identification systems, this requires involvement of a notified body.</div>
            <div class="obl-ref">Articles 16, 43</div>
          </div>
          <div class="obl-card">
            <div class="obl-icon">2</div>
            <div class="obl-title">Risk Management System</div>
            <div class="obl-desc">Establish, implement, document, and maintain a risk management system throughout the entire lifecycle of the AI system. This must be a continuous, iterative process.</div>
            <div class="obl-ref">Article 9</div>
          </div>
          <div class="obl-card">
            <div class="obl-icon">3</div>
            <div class="obl-title">Data Governance</div>
            <div class="obl-desc">Training, validation, and testing data sets must be subject to appropriate data governance and management practices, including examination for possible biases.</div>
            <div class="obl-ref">Article 10</div>
          </div>
          <div class="obl-card">
            <div class="obl-icon">4</div>
            <div class="obl-title">Technical Documentation</div>
            <div class="obl-desc">Draw up technical documentation demonstrating compliance before the system is placed on the market. Documentation must be kept up to date.</div>
            <div class="obl-ref">Article 11, Annex IV</div>
          </div>
          <div class="obl-card">
            <div class="obl-icon">5</div>
            <div class="obl-title">Record-Keeping &amp; Logging</div>
            <div class="obl-desc">The system must be designed to automatically record events (logs) throughout its lifetime. Logging capabilities must enable traceability of the system's functioning.</div>
            <div class="obl-ref">Article 12</div>
          </div>
          <div class="obl-card">
            <div class="obl-icon">6</div>
            <div class="obl-title">Transparency &amp; Information</div>
            <div class="obl-desc">Provide deployers with instructions for use that include concise, complete, correct, and clear information that is relevant, accessible, and comprehensible.</div>
            <div class="obl-ref">Article 13</div>
          </div>
          <div class="obl-card">
            <div class="obl-icon">7</div>
            <div class="obl-title">Human Oversight</div>
            <div class="obl-desc">Design the system so it can be effectively overseen by natural persons during use, including appropriate human-machine interface tools.</div>
            <div class="obl-ref">Article 14</div>
          </div>
          <div class="obl-card">
            <div class="obl-icon">8</div>
            <div class="obl-title">Accuracy, Robustness &amp; Cybersecurity</div>
            <div class="obl-desc">Achieve appropriate levels of accuracy, robustness, and cybersecurity, and perform consistently throughout the lifecycle.</div>
            <div class="obl-ref">Article 15</div>
          </div>
        </div>"""
    else:
        obligations_html = """
        <div class="obl-note">
          <p>The system is not currently classified as high-risk. Standard transparency obligations under Title IV may still apply depending on the system's interaction with natural persons.</p>
        </div>"""

    # ── assemble full HTML ─────────────────────────────────────────
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ARCO \u2014 {system_local} \u2014 Regulatory Determination</title>
<style>
/* ══════════════════════════════════════════════════════════════
   ARCO Regulatory Determination View — Self-contained CSS
   ══════════════════════════════════════════════════════════════ */
:root {{
  --bg: #0d1017; --sf: #151922; --sf2: #1a1f2e; --bd: #252a3a;
  --tx: #e2e6f0; --tx2: #c0c5d4; --mu: #6b7280; --mu2: #4b5563;
  --pass: #22c55e; --pass-bg: #0a2e1a; --pass-bd: #166534;
  --fail: #ef4444; --fail-bg: #2a0a0a; --fail-bd: #991b1b;
  --inf: #818cf8; --inf-bg: #1e1b4b; --inf-bd: #4338ca;
  --warn: #f59e0b; --warn-bg: #451a03; --warn-bd: #b45309;
  --accent: #38bdf8; --accent2: #818cf8;
}}
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0 }}
html {{ scroll-behavior: smooth }}
body {{
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
  background: var(--bg); color: var(--tx); line-height: 1.6;
  max-width: 960px; margin: 0 auto; padding: 2.5rem 2rem;
}}
code, pre, .mono {{ font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'Courier New', monospace }}

/* ── Typography ───────────────────────────────────────────── */
h1 {{ font-size: 1.1rem; font-weight: 700; letter-spacing: -0.01em; color: var(--tx) }}
h2 {{
  font-size: 0.7rem; font-weight: 600; color: var(--mu);
  text-transform: uppercase; letter-spacing: 0.1em;
  margin: 2.5rem 0 1rem; padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--bd);
}}
h3 {{ font-size: 0.85rem; font-weight: 600; color: var(--tx2); margin: 0.5rem 0 }}
p {{ color: var(--tx2); font-size: 0.85rem }}

/* ── Header ───────────────────────────────────────────────── */
.header {{ margin-bottom: 2rem }}
.header-brand {{
  display: flex; align-items: center; gap: 0.6rem;
  margin-bottom: 0.4rem;
}}
.header-brand .logo {{
  font-size: 0.65rem; font-weight: 800; letter-spacing: 0.15em;
  color: var(--accent); background: rgba(56, 189, 248, 0.1);
  padding: 0.25rem 0.6rem; border-radius: 4px; border: 1px solid rgba(56, 189, 248, 0.2);
}}
.header-meta {{
  color: var(--mu); font-size: 0.75rem; display: flex;
  flex-wrap: wrap; gap: 0.3rem 1.2rem;
}}

/* ── Badges ───────────────────────────────────────────────── */
.badge {{
  font-size: 0.6rem; padding: 0.2rem 0.5rem; border-radius: 3px;
  font-weight: 700; letter-spacing: 0.04em; white-space: nowrap;
  display: inline-block;
}}
.bi {{ background: var(--inf-bg); color: var(--inf); border: 1px solid var(--inf-bd) }}
.ba {{ background: var(--warn-bg); color: var(--warn); border: 1px solid var(--warn-bd) }}
.bn {{ background: #1f2937; color: var(--mu); border: 1px solid #374151 }}
.bp {{ background: var(--pass-bg); color: var(--pass); border: 1px solid var(--pass-bd) }}
.bf {{ background: var(--fail-bg); color: var(--fail); border: 1px solid var(--fail-bd) }}

/* ── Layer 1: Executive Summary ───────────────────────────── */
.exec-summary {{
  background: var(--sf); border: 1px solid var(--bd); border-radius: 8px;
  padding: 1.5rem; margin-bottom: 0.5rem;
}}
.exec-banner {{
  display: flex; align-items: center; flex-wrap: wrap; gap: 0.6rem;
  margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid var(--bd);
}}
.exec-banner .classification {{
  font-size: 1.1rem; font-weight: 700;
  color: {"var(--fail)" if is_high_risk else "var(--pass)"};
}}
.exec-text {{ font-size: 0.88rem; color: var(--tx2); line-height: 1.7 }}
.exec-text strong {{ color: {"var(--fail)" if is_high_risk else "var(--pass)"} }}
.exec-cats {{
  display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 1rem;
}}
.exec-cat {{
  background: var(--sf2); border: 1px solid var(--bd); border-radius: 6px;
  padding: 0.6rem 1rem; font-size: 0.78rem;
}}
.exec-cat .cat-id {{ color: var(--accent); font-weight: 700; font-size: 0.7rem; letter-spacing: 0.05em }}
.exec-cat .cat-title {{ color: var(--tx2); margin-top: 0.15rem }}

/* ── Layer 2: Gate Story ──────────────────────────────────── */
.gate-intro {{
  font-size: 0.82rem; color: var(--mu); margin-bottom: 1.2rem; line-height: 1.6;
}}
.gate-card {{
  background: var(--sf); border: 1px solid var(--bd); border-radius: 8px;
  padding: 1.2rem 1.4rem; margin-bottom: 0.8rem;
  border-left: 3px solid var(--bd);
  transition: border-color 0.2s;
}}
.gate-card.gate-pass {{ border-left-color: var(--pass) }}
.gate-card.gate-fail {{ border-left-color: var(--fail) }}
.gate-card.gate-na {{ border-left-color: var(--mu) }}
.gate-header {{
  display: flex; align-items: center; gap: 0.7rem;
  margin-bottom: 0.7rem; flex-wrap: wrap;
}}
.gate-num {{
  font-size: 0.65rem; font-weight: 800; color: var(--accent);
  letter-spacing: 0.08em; text-transform: uppercase;
  background: rgba(56, 189, 248, 0.08); padding: 0.2rem 0.5rem;
  border-radius: 3px;
}}
.gate-title {{ font-size: 0.88rem; font-weight: 600; color: var(--tx) }}
.gate-badge {{
  font-size: 0.6rem; padding: 0.18rem 0.45rem; border-radius: 3px;
  font-weight: 700; letter-spacing: 0.04em; margin-left: auto;
}}
.gbp {{ background: var(--pass-bg); color: var(--pass); border: 1px solid var(--pass-bd) }}
.gbf {{ background: var(--fail-bg); color: var(--fail); border: 1px solid var(--fail-bd) }}
.gate-question {{
  font-size: 0.82rem; color: var(--mu); font-style: italic;
  margin-bottom: 0.6rem;
}}
.gate-answer {{ font-size: 0.85rem; color: var(--tx2); line-height: 1.65 }}
.gate-answer strong {{ color: var(--tx) }}
.gate-answer em {{ color: var(--accent); font-style: normal; font-weight: 500 }}
.gate-evidence {{ margin-top: 0.8rem }}
.gate-evidence summary {{
  cursor: pointer; color: var(--mu); font-size: 0.75rem;
  padding: 0.3rem 0; user-select: none;
}}
.gate-evidence summary:hover {{ color: var(--tx2) }}
.gate-tech {{
  background: var(--bg); border: 1px solid var(--bd); border-radius: 6px;
  padding: 0.8rem 1rem; margin-top: 0.5rem; font-size: 0.78rem;
  color: var(--mu); line-height: 1.7;
}}
.gate-tech code {{
  background: rgba(129, 140, 248, 0.1); color: var(--inf);
  padding: 0.1rem 0.35rem; border-radius: 3px; font-size: 0.73rem;
}}
.gate-tech strong {{ color: var(--tx2); font-weight: 600 }}
.gate-tech p {{ margin-bottom: 0.3rem; color: var(--mu) }}

/* ── Gate result strip ────────────────────────────────────── */
.gate-result {{
  background: var(--sf); border: 1px solid var(--bd); border-radius: 8px;
  padding: 1rem 1.4rem; margin-top: 1rem;
  display: flex; align-items: center; gap: 0.8rem; flex-wrap: wrap;
}}
.gate-result .gr-arrow {{ color: var(--mu2); font-size: 1.2rem }}
.gate-result .gr-label {{ font-size: 0.82rem; color: var(--tx2) }}
.gate-result .gr-final {{
  font-size: 0.9rem; font-weight: 700;
  color: {"var(--fail)" if is_high_risk else "var(--pass)"};
}}

/* ── Layer 3: Obligations ─────────────────────────────────── */
.obl-grid {{
  display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 0.8rem;
}}
.obl-card {{
  background: var(--sf); border: 1px solid var(--bd); border-radius: 8px;
  padding: 1rem 1.2rem;
}}
.obl-icon {{
  display: inline-flex; align-items: center; justify-content: center;
  width: 1.5rem; height: 1.5rem; border-radius: 50%;
  background: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.2);
  color: var(--accent); font-size: 0.7rem; font-weight: 700;
  margin-bottom: 0.5rem;
}}
.obl-title {{ font-size: 0.82rem; font-weight: 600; color: var(--tx); margin-bottom: 0.4rem }}
.obl-desc {{ font-size: 0.78rem; color: var(--mu); line-height: 1.6 }}
.obl-ref {{
  font-size: 0.68rem; color: var(--accent); margin-top: 0.6rem;
  font-weight: 600; letter-spacing: 0.03em;
}}
.obl-note {{
  background: var(--sf); border: 1px solid var(--bd); border-radius: 8px;
  padding: 1.2rem;
}}
.obl-note p {{ color: var(--mu) }}

/* ── Layer 4: Counterfactuals ─────────────────────────────── */
.cf-item {{
  background: var(--sf); border: 1px solid var(--bd); border-radius: 8px;
  padding: 1.2rem 1.4rem; margin-bottom: 0.8rem;
}}
.cf-label {{
  font-size: 0.78rem; font-weight: 700; color: var(--accent);
  letter-spacing: 0.04em; margin-bottom: 0.6rem;
}}
.cf-item ul {{
  list-style: none; padding: 0;
}}
.cf-item li {{
  font-size: 0.82rem; color: var(--tx2); line-height: 1.65;
  padding: 0.3rem 0 0.3rem 1.2rem; position: relative;
}}
.cf-item li::before {{
  content: "\u2192"; position: absolute; left: 0; color: var(--mu);
}}
.cf-item li strong {{ color: var(--accent); font-weight: 600 }}

/* ── Layer 5: Technical Deep Dive ─────────────────────────── */
.strip {{
  display: flex; align-items: center; flex-wrap: wrap; gap: 0;
  background: var(--sf); border: 1px solid var(--bd);
  padding: 1.2rem 1rem; border-radius: 8px; overflow-x: auto;
}}
.node {{
  display: flex; flex-direction: column; align-items: center;
  padding: 0.6rem 0.85rem; border-radius: 6px; min-width: 110px;
  text-align: center; gap: 0.25rem;
}}
.ntype {{
  color: var(--mu); font-size: 0.58rem; text-transform: uppercase;
  letter-spacing: 0.05em; font-family: 'JetBrains Mono', monospace;
}}
.nlabel {{
  font-weight: 600; font-size: 0.72rem; word-break: break-word;
  font-family: 'JetBrains Mono', monospace;
}}
.ns {{ background: #1e3a5f; border: 1px solid #2563eb }}
.nc {{ background: #134e4a; border: 1px solid #0d9488 }}
.nd {{ background: #431407; border: 1px solid #b45309 }}
.nt {{ background: #2e1065; border: 1px solid #7c3aed }}
.nr-high {{ background: #450a0a; border: 1px solid #dc2626 }}
.nr-none {{ background: #1f2937; border: 1px solid #374151 }}
.edge {{
  display: flex; flex-direction: column; align-items: center;
  padding: 0 0.4rem; min-width: 68px; text-align: center; gap: 0.15rem;
}}
.earrow {{ font-size: 1.1rem; color: var(--mu2) }}
.erel {{ font-size: 0.58rem; color: var(--mu); font-family: 'JetBrains Mono', monospace }}
.eiri {{ font-size: 0.52rem; color: #374151; font-family: 'JetBrains Mono', monospace }}

/* ── Audit table ──────────────────────────────────────────── */
.audit-table {{ width: 100%; border-collapse: collapse; font-size: 0.82rem }}
.audit-table th {{
  text-align: left; padding: 0.5rem 0.7rem;
  border-bottom: 1px solid var(--bd); color: var(--mu);
  font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.06em;
}}
.audit-table td {{ padding: 0.5rem 0.7rem; border-bottom: 1px solid var(--bd) }}
.audit-table tr:last-child td {{ border-bottom: none }}
.layer {{ color: var(--mu); font-size: 0.75rem; font-family: 'JetBrains Mono', monospace }}
.triples {{
  display: inline-block; background: var(--sf); border: 1px solid var(--bd);
  padding: 0.5rem 1rem; border-radius: 6px; font-size: 0.82rem;
  margin-top: 0.8rem;
}}
.triples span {{ color: var(--inf); font-weight: 700 }}

/* ── Expandable sections ──────────────────────────────────── */
details {{ margin-top: 0.8rem }}
details > summary {{
  cursor: pointer; color: var(--mu); font-size: 0.78rem;
  padding: 0.4rem 0; user-select: none; list-style: none;
}}
details > summary::-webkit-details-marker {{ display: none }}
details > summary::before {{
  content: "\u25b6"; display: inline-block; margin-right: 0.5rem;
  font-size: 0.6rem; transition: transform 0.15s;
}}
details[open] > summary::before {{ transform: rotate(90deg) }}
details > summary:hover {{ color: var(--tx2) }}
pre {{
  background: var(--bg); border: 1px solid var(--bd); padding: 0.9rem;
  border-radius: 6px; font-size: 0.72rem; overflow-x: auto;
  margin-top: 0.5rem; white-space: pre-wrap; word-break: break-all;
  line-height: 1.5; color: var(--tx2);
}}

/* ── Footnotes ────────────────────────────────────────────── */
.fn {{ font-size: 0.7rem; color: var(--mu); margin-top: 0.5rem }}

/* ── Footer ───────────────────────────────────────────────── */
footer {{
  margin-top: 3rem; padding-top: 1.5rem;
  border-top: 1px solid var(--bd); color: var(--mu); font-size: 0.7rem;
  line-height: 1.6;
}}
footer .disclaimer {{
  background: var(--sf); border: 1px solid var(--bd); border-radius: 6px;
  padding: 0.8rem 1rem; margin-top: 0.8rem; font-size: 0.7rem;
  color: var(--mu); line-height: 1.5;
}}

/* ── Nav tabs ─────────────────────────────────────────────── */
.nav {{
  display: flex; gap: 0; border-bottom: 1px solid var(--bd);
  margin-bottom: 1.5rem; overflow-x: auto;
}}
.nav a {{
  color: var(--mu); text-decoration: none; font-size: 0.72rem;
  font-weight: 600; padding: 0.6rem 1rem; letter-spacing: 0.03em;
  border-bottom: 2px solid transparent; white-space: nowrap;
  transition: color 0.15s, border-color 0.15s;
}}
.nav a:hover {{ color: var(--tx2) }}
.nav a.active {{ color: var(--accent); border-bottom-color: var(--accent) }}

/* ── Print / PDF ──────────────────────────────────────────── */
.print-btn {{
  background: var(--sf); border: 1px solid var(--bd); border-radius: 6px;
  color: var(--tx2); font-size: 0.75rem; font-weight: 600;
  padding: 0.5rem 1rem; cursor: pointer; letter-spacing: 0.03em;
  transition: background 0.15s, border-color 0.15s;
}}
.print-btn:hover {{ background: var(--sf2); border-color: var(--accent) }}

@media print {{
  body {{ background: #fff; color: #111; padding: 1rem; max-width: none }}
  .nav, .print-btn {{ display: none }}
  .exec-summary, .gate-card, .obl-card, .cf-item, .audit-table,
  .strip, pre, .gate-tech, footer .disclaimer {{
    background: #f8f9fa; border-color: #dee2e6; color: #111;
  }}
  .badge {{ border: 1px solid #999 }}
  .bp {{ background: #d4edda; color: #155724; border-color: #c3e6cb }}
  .bf {{ background: #f8d7da; color: #721c24; border-color: #f5c6cb }}
  .bi {{ background: #d1ecf1; color: #0c5460; border-color: #bee5eb }}
  .bn {{ background: #e2e3e5; color: #383d41; border-color: #d6d8db }}
  h2 {{ color: #495057; border-color: #dee2e6 }}
  .gate-card {{ border-left-width: 3px }}
  .gate-card.gate-pass {{ border-left-color: #28a745 }}
  .gate-card.gate-fail {{ border-left-color: #dc3545 }}
  .gate-tech code {{ background: #e9ecef; color: #495057 }}
  .exec-banner .classification {{ color: #dc3545 }}
  .exec-text strong {{ color: #dc3545 }}
  .gate-answer em {{ color: #0056b3 }}
  .cf-item li strong {{ color: #0056b3 }}
  .obl-ref {{ color: #0056b3 }}
  p, .exec-text, .gate-answer, .gate-question, .obl-desc,
  .cf-item li, .fn, footer, footer .disclaimer, .layer,
  .gate-tech, .gate-tech p, pre {{ color: #333 }}
  details {{ break-inside: avoid }}
  details[open] {{ break-inside: auto }}
  .gate-evidence[open] .gate-tech {{ break-inside: avoid }}
}}

/* ── Section anchors ──────────────────────────────────────── */
section {{ scroll-margin-top: 1rem }}
</style>
</head>
<body>

<!-- ═══════════════════════════════════════════════════════════
     HEADER
     ═══════════════════════════════════════════════════════════ -->
<header class="header">
  <div class="header-brand">
    <span class="logo">ARCO</span>
    <h1>Regulatory Determination Report</h1>
  </div>
  <div class="header-meta">
    <span>System: <strong>{sys_display}</strong></span>
    <span>Regime: EU AI Act Article 6 / Annex III</span>
    <span>Generated: {ts}</span>
  </div>
</header>

<!-- ═══════════════════════════════════════════════════════════
     NAVIGATION
     ═══════════════════════════════════════════════════════════ -->
<nav class="nav">
  <a href="#summary" class="active">Summary</a>
  <a href="#gates">Classification Gates</a>
  <a href="#obligations">Obligations</a>
  <a href="#counterfactuals">What Would Change</a>
  <a href="#technical">Technical Evidence</a>
</nav>

<div style="display:flex;justify-content:flex-end;margin-bottom:1.5rem">
  <button class="print-btn" onclick="window.print()">Export PDF</button>
</div>

<!-- ═══════════════════════════════════════════════════════════
     LAYER 1: EXECUTIVE SUMMARY
     ═══════════════════════════════════════════════════════════ -->
<section id="summary">
  <h2>Executive Summary</h2>
  <div class="exec-summary">
    <div class="exec-banner">
      <span class="classification">{"HIGH RISK" if is_high_risk else "NOT HIGH RISK"}</span>
      {mode_badge}
      {overall_badge}
    </div>
    <p class="exec-text">{summary_text}</p>
    {"<div class='exec-cats'>" + "".join(
      '<div class="exec-cat"><div class="cat-id">' + c["article_ref"].upper() + '</div>'
      '<div class="cat-title">' + c["title"] + '</div></div>'
      for c in triggered_categories
    ) + "</div>" if triggered_categories else ""}
  </div>
</section>

<!-- ═══════════════════════════════════════════════════════════
     LAYER 2: GATE-BY-GATE CLASSIFICATION STORY
     ═══════════════════════════════════════════════════════════ -->
<section id="gates">
  <h2>Classification Gates</h2>
  <p class="gate-intro">
    The EU AI Act classifies AI systems as high-risk through a three-gate test.
    Each gate is independently necessary &mdash; all three must be satisfied for
    a given Annex III category to apply. The classification is determined by
    OWL-RL formal reasoning, not by pattern matching or heuristics.
  </p>

  {gate_cards_html}

  <div class="gate-result">
    <span class="gr-label">Gate 1 {_gate_status_label(gate1_ok)}</span>
    <span class="gr-arrow">&amp;</span>
    <span class="gr-label">Gate 2 {_gate_status_label(gate2_ok)}</span>
    <span class="gr-arrow">&amp;</span>
    <span class="gr-label">Gate 3 {_gate_status_label(gate3_ok)}</span>
    <span class="gr-arrow">\u2192</span>
    <span class="gr-final">{"HIGH RISK (Annex III)" if is_high_risk else "NOT TRIGGERED"}</span>
  </div>
</section>

<!-- ═══════════════════════════════════════════════════════════
     LAYER 3: WHAT THIS MEANS — OBLIGATIONS
     ═══════════════════════════════════════════════════════════ -->
<section id="obligations">
  <h2>What This Means &mdash; Provider Obligations</h2>
  {obligations_html}
</section>

<!-- ═══════════════════════════════════════════════════════════
     LAYER 4: COUNTERFACTUAL REASONING
     ═══════════════════════════════════════════════════════════ -->
<section id="counterfactuals">
  <h2>What Would Change This Classification</h2>
  <p class="gate-intro" style="margin-bottom:1rem">
    Understanding the boundary conditions of a regulatory classification is as
    important as the classification itself. Below is what would need to change
    for each triggered category to no longer apply.
  </p>
  {counterfactual_html}
</section>

<!-- ═══════════════════════════════════════════════════════════
     LAYER 5: TECHNICAL DEEP DIVE
     ═══════════════════════════════════════════════════════════ -->
<section id="technical">
  <h2>Technical Evidence</h2>

  <h3 style="margin-top:1rem">Determination Path</h3>
  <div class="strip">
    {strip_html}
  </div>
  <p class="fn">\u2021 AnnexIIITriggeringCapability is a structural presentation assumption derived from the bridge axiom in ARCO_core.ttl. It is the type the disposition must satisfy for HighRiskSystem entailment to fire.</p>

  <h3 style="margin-top:1.5rem">Audit &amp; Classification Results</h3>
  <table class="audit-table">
    <thead><tr><th>Check</th><th>Layer</th><th>Result</th></tr></thead>
    <tbody>
      {audit_html}
    </tbody>
  </table>

  <div class="triples">OWL-RL entailed triples added: <span>+{inferred_added}</span></div>

  <h3 style="margin-top:1.5rem">Raw Pipeline Outputs</h3>
  <details>
    <summary>summary.json</summary>
    <pre>{summary_raw}</pre>
  </details>
  <details>
    <summary>evidence.json</summary>
    <pre>{evidence_raw}</pre>
  </details>
</section>

<!-- ═══════════════════════════════════════════════════════════
     FOOTER
     ═══════════════════════════════════════════════════════════ -->
<footer>
  <div>ARCO Compliance Verification Pipeline &nbsp;|&nbsp; OWL-RL + SHACL + SPARQL &nbsp;|&nbsp; {ts}</div>
  <div class="disclaimer">
    <strong>Methodology:</strong> Classification is authoritative from OWL-RL entailment only.
    SHACL validates documentary structure. SPARQL queries provide audit/documentation inspection
    of the reasoned graph. No machine learning, scoring, or heuristics are used in the
    determination pipeline. This artifact is an explanatory surface over deterministic
    formal reasoning outputs.<br><br>
    <strong>Scope:</strong> This determination covers the system as modelled in the ontology
    assertions at the time of generation. Changes to system composition, intended use,
    or deployment scenario may alter the classification. Re-run the pipeline after any
    change to system assertions.
  </div>
</footer>

<script>
// Minimal nav highlight on scroll
(function() {{
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav a');
  function onScroll() {{
    let current = '';
    sections.forEach(s => {{
      if (window.scrollY >= s.offsetTop - 80) current = s.id;
    }});
    navLinks.forEach(a => {{
      a.classList.toggle('active', a.getAttribute('href') === '#' + current);
    }});
  }}
  window.addEventListener('scroll', onScroll, {{ passive: true }});
}})();
</script>

</body>
</html>
"""
    (output_dir / "determination_view.html").write_text(html, encoding="utf-8")


# ---------------------------
# main
# ---------------------------

def _pf(ok: bool) -> str:
    return "PASS" if ok else "FAIL"

def main() -> None:
    parser = argparse.ArgumentParser(description="ARCO Compliance Verification Pipeline")
    parser.add_argument(
        "--system", default="Sentinel_ID_System",
        help="Local name of the system under evaluation (default: Sentinel_ID_System)"
    )
    parser.add_argument(
        "--instances", default=None,
        help="Path to instance TTL file (default: ARCO_instances_sentinel.ttl)"
    )
    args = parser.parse_args()

    global SYSTEM_LOCAL, SYSTEM_IRI, INSTANCES
    SYSTEM_LOCAL = args.system
    SYSTEM_IRI = f"{ARCO_NS}{SYSTEM_LOCAL}"
    if args.instances is not None:
        INSTANCES = Path(args.instances)

    hr("ARCO COMPLIANCE VERIFICATION PIPELINE (OPERATOR VIEW)")

    sub("LOAD")
    print("Loading: core ontology + governance extension + instance data")
    g_source = load_union_graph(CORE, GOV, INSTANCES)
    print(f"Triples loaded (asserted): {len(g_source)}")

    # clone -> reason over the copy so we can compare pre vs post
    g = clone_graph(g_source)

    g, initial_count, inferred_added = run_reasoning(g)

    shacl_ok, shacl_report_text = run_shacl(g)

    sub("AUDIT QUERIES (SPARQL ASK)")
    print("Traceability check...")
    traceability_ok = run_sparql_ask_for_system(g, TRACEABILITY_QUERY, SYSTEM_LOCAL)
    print(f"Traceability: {traceability_ok}")

    latent_ok = None
    if LATENT_RISK_QUERY.exists():
        print("\nLatent risk detection (hardware path)...")
        latent_ok = run_sparql_ask_for_system(g, LATENT_RISK_QUERY, SYSTEM_LOCAL)
        print(f"Latent risk detected: {latent_ok}")

    intended_use_ok = None
    if INTENDED_USE_QUERY.exists():
        print("\nIntended use + use scenario (three-gate check)...")
        intended_use_ok = run_sparql_ask_for_system(g, INTENDED_USE_QUERY, SYSTEM_LOCAL)
        print(f"Intended use modeled: {intended_use_ok}")

    annex_iii_1a_ok = None
    if ANNEX_III_1A_QUERY.exists():
        print("\nAnnex III 1(a) entailment (OWL-inferred, audit only)...")
        annex_iii_1a_ok = run_sparql_ask_for_system(g, ANNEX_III_1A_QUERY, SYSTEM_LOCAL)
        print(f"Annex III 1(a) applicable: {annex_iii_1a_ok}")

    annex_iii_5b_ok = None
    if ANNEX_III_5B_QUERY.exists():
        print("\nAnnex III 5(b) entailment (OWL-inferred, audit only)...")
        annex_iii_5b_ok = run_sparql_ask_for_system(g, ANNEX_III_5B_QUERY, SYSTEM_LOCAL)
        print(f"Annex III 5(b) applicable: {annex_iii_5b_ok}")

    obligation_ok = None
    if OBLIGATION_QUERY.exists():
        print("\nObligation link (provider/deployer responsibility)...")
        obligation_ok = run_sparql_ask_for_system(g, OBLIGATION_QUERY, SYSTEM_LOCAL)
        print(f"Obligation linked: {obligation_ok}")

    reg_alignment_ok = None
    if REGULATORY_ALIGNMENT_QUERY.exists():
        print("\nRegulatory alignment (law prescribes == intended use prescribes)...")
        reg_alignment_ok = run_sparql_ask_for_system(g, REGULATORY_ALIGNMENT_QUERY, SYSTEM_LOCAL)
        print(f"Regulatory aligned: {reg_alignment_ok}")

    inference_ok, asserted_pre, entailed_post, bindings = verify_high_risk_inference(g, g_source)

    sub("DETERMINATION PACKET (gate evidence extraction)")
    gate_evidence = select_gate_evidence(g, SYSTEM_LOCAL)
    print(f"Gate 1 capability type:  {gate_evidence['gate1']['cap_type_label'] or '(none)'}")
    print(f"Gate 2 process type:     {gate_evidence['gate2']['process_type_label'] or '(none)'}")
    print(f"Gate 3 role:             {gate_evidence['gate3']['role_label'] or '(none)'}")

    # ---------------------------------------------------------------
    # SUMMARY
    # Two-layer architecture: classification (OWL-RL) vs. audit (SPARQL).
    # Classification rows are OWL-entailed — gate-removal tests verify them.
    # Audit rows inspect declared documentary content on the reasoned graph;
    # they do not produce and cannot affect the classification result.
    # ---------------------------------------------------------------
    hr("SUMMARY")
    print("  [classification layer — OWL-RL entailment]")
    print(f"SHACL:         {_pf(shacl_ok)}")
    print(f"Entailment:    {_pf(inference_ok)}")
    if annex_iii_1a_ok is not None:
        print(f"Annex III 1a:  {'VERIFIED (ENTAILED)' if annex_iii_1a_ok else 'NOT APPLICABLE'} (OWL-entailed)")
    if annex_iii_5b_ok is not None:
        print(f"Annex III 5b:  {'VERIFIED (ENTAILED)' if annex_iii_5b_ok else 'NOT APPLICABLE'} (OWL-entailed)")
    print()
    print("  [audit documentation layer — SPARQL ASK on reasoned graph]")
    print(f"Traceability:  {_pf(traceability_ok)}")
    if latent_ok is not None:
        print(f"Latent risk:   {_pf(latent_ok)}")
    if intended_use_ok is not None:
        print(f"Intended use:  {_pf(intended_use_ok)}")
    if obligation_ok is not None:
        print(f"Obligation:    {_pf(obligation_ok)}")
    if reg_alignment_ok is not None:
        print(f"Reg. aligned:  {_pf(reg_alignment_ok)}")
    print(f"Entailed triples added: +{inferred_added}")

    # Annex III category checks (1a, 5b) are informational cross-category audit lines.
    # HighRiskSystem entailment (inference_ok) already covers the classification result.
    # Neither category check is included in all_pass: a system entailed as 5(b) but not
    # 1(a) (or vice versa) is not a failure — it reflects correct cross-category isolation.
    all_pass = shacl_ok and traceability_ok and inference_ok
    if latent_ok is not None:
        all_pass = all_pass and latent_ok
    if intended_use_ok is not None:
        all_pass = all_pass and intended_use_ok
    if obligation_ok is not None:
        all_pass = all_pass and obligation_ok
    if reg_alignment_ok is not None:
        all_pass = all_pass and reg_alignment_ok

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
    if intended_use_ok is not None:
        print(f"  INTENDED USE:            {_pf(intended_use_ok)}")
    if annex_iii_1a_ok is not None:
        print(f"  ANNEX III 1(a):          {'VERIFIED (ENTAILED)' if annex_iii_1a_ok else 'NOT APPLICABLE'}")
    if annex_iii_5b_ok is not None:
        print(f"  ANNEX III 5(b):          {'VERIFIED (ENTAILED)' if annex_iii_5b_ok else 'NOT APPLICABLE'}")
    if obligation_ok is not None:
        print(f"  OBLIGATION:              {_pf(obligation_ok)}")
    print(f"  ENTAILED TRIPLES ADDED:  +{inferred_added}")
    print("=" * 72)

    # ---------------------------------------------------------------
    # WRITE OUTPUT FILES (runs/demo/)
    # ---------------------------------------------------------------
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # certificate.txt
    cert_lines = []
    cert_lines.append("=" * 72)
    cert_lines.append("REGULATORY DETERMINATION CERTIFICATE")
    cert_lines.append("=" * 72)
    cert_lines.append(f"  SYSTEM:                  {SYSTEM_LOCAL}")
    cert_lines.append(f"  REGIME:                  EU AI Act (Article 6 / Annex III)")
    if classification_mode in ("INFERRED", "ASSERTED"):
        cert_lines.append(f"  CLASSIFICATION:          HighRiskSystem ({classification_mode})")
    else:
        cert_lines.append(f"  CLASSIFICATION:          {classification_mode}")
    cert_lines.append(f"  TRIGGERING CAPABILITY:   {trigger_display}")
    if evidence_lines:
        cert_lines.append(f"  EVIDENCE PATH:")
        for line in evidence_lines:
            cert_lines.append(line)
    else:
        cert_lines.append(f"  EVIDENCE PATH:           (none detected)")
    cert_lines.append(f"  SHACL:                   {_pf(shacl_ok)}")
    cert_lines.append(f"  TRACEABILITY:            {_pf(traceability_ok)}")
    if latent_ok is not None:
        cert_lines.append(f"  LATENT RISK:             {'DETECTED' if latent_ok else 'NOT DETECTED'}")
    if intended_use_ok is not None:
        cert_lines.append(f"  INTENDED USE:            {_pf(intended_use_ok)}")
    if annex_iii_1a_ok is not None:
        cert_lines.append(f"  ANNEX III 1(a):          {'VERIFIED (ENTAILED)' if annex_iii_1a_ok else 'NOT APPLICABLE'}")
    if annex_iii_5b_ok is not None:
        cert_lines.append(f"  ANNEX III 5(b):          {'VERIFIED (ENTAILED)' if annex_iii_5b_ok else 'NOT APPLICABLE'}")
    if obligation_ok is not None:
        cert_lines.append(f"  OBLIGATION:              {_pf(obligation_ok)}")
    cert_lines.append(f"  ENTAILED TRIPLES ADDED:  +{inferred_added}")
    cert_lines.append("=" * 72)
    (OUTPUT_DIR / "certificate.txt").write_text("\n".join(cert_lines) + "\n", encoding="utf-8")

    # summary.json
    summary = {
        "system": SYSTEM_LOCAL,
        "regime": "EU AI Act (Article 6 / Annex III)",
        "classification": f"HighRiskSystem ({classification_mode})" if classification_mode in ("INFERRED", "ASSERTED") else classification_mode,
        "shacl": _pf(shacl_ok),
        "traceability": _pf(traceability_ok),
        "latent_risk": (_pf(latent_ok) if latent_ok is not None else "N/A"),
        "intended_use": (_pf(intended_use_ok) if intended_use_ok is not None else "N/A"),
        "annex_iii_1a": ("VERIFIED (ENTAILED)" if annex_iii_1a_ok else ("NOT APPLICABLE" if annex_iii_1a_ok is not None else "N/A")),
        "annex_iii_5b": ("VERIFIED (ENTAILED)" if annex_iii_5b_ok else ("NOT APPLICABLE" if annex_iii_5b_ok is not None else "N/A")),
        "obligation": (_pf(obligation_ok) if obligation_ok is not None else "N/A"),
        "entailment": _pf(inference_ok),
        "entailed_triples_added": inferred_added,
        "all_checks_passed": all_pass,
    }
    (OUTPUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    # evidence.json
    evidence = [
        {"component": _short(comp), "disposition": _short(disp), "component_iri": comp, "disposition_iri": disp}
        for comp, disp in bindings
    ]
    (OUTPUT_DIR / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")

    # determination_packet.json — compact intermediate representation;
    # the HTML view is rendered from this, not from scattered Python logic.
    determination_packet = {
        "schema_version": "1.0",
        "system_uri": SYSTEM_IRI,
        "system_label": SYSTEM_LOCAL.replace("_", " "),
        "run_id": datetime.now(timezone.utc).isoformat(),
        "classification": "HIGH_RISK" if classification_mode in ("INFERRED", "ASSERTED") else "NOT_HIGH_RISK",
        "classification_mode": classification_mode,
        "annex_categories": [
            c for c in (
                "AnnexIII_1a" if annex_iii_1a_ok else None,
                "AnnexIII_5b" if annex_iii_5b_ok else None,
            ) if c is not None
        ],
        "gates": [
            {
                "id": "gate_1",
                "label": "Capability",
                "status": "SATISFIED" if inference_ok else "NOT_SATISFIED",
                "evidence": {
                    "cap_type_uri": gate_evidence["gate1"]["cap_type_uri"],
                    "cap_type_label": gate_evidence["gate1"]["cap_type_label"],
                    "component_uri": bindings[0][0] if bindings else "",
                    "disposition_uri": bindings[0][1] if bindings else "",
                },
            },
            {
                "id": "gate_2",
                "label": "Prescribed Process Type",
                "status": "SATISFIED" if intended_use_ok else "NOT_SATISFIED",
                "evidence": {
                    "ius_uri": gate_evidence["gate2"]["ius_uri"],
                    "process_uri": gate_evidence["gate2"]["process_uri"],
                    "process_type_uri": gate_evidence["gate2"]["process_type_uri"],
                    "process_type_label": gate_evidence["gate2"]["process_type_label"],
                },
            },
            {
                "id": "gate_3",
                "label": "Affected Role Category",
                "status": "SATISFIED" if reg_alignment_ok else "NOT_SATISFIED",
                "evidence": {
                    "uss_uri": gate_evidence["gate3"]["uss_uri"],
                    "role_uri": gate_evidence["gate3"]["role_uri"],
                    "role_label": gate_evidence["gate3"]["role_label"],
                },
            },
        ],
        "determination_node_uri": f"{ARCO_NS}HighRisk_Determination_001",
        "inferred_triples_added": inferred_added,
    }
    (OUTPUT_DIR / "determination_packet.json").write_text(
        json.dumps(determination_packet, indent=2) + "\n", encoding="utf-8"
    )

    # determination_view.html
    write_html_view(
        output_dir=OUTPUT_DIR,
        system_local=SYSTEM_LOCAL,
        classification_mode=classification_mode,
        bindings=bindings,
        shacl_ok=shacl_ok,
        traceability_ok=traceability_ok,
        inference_ok=inference_ok,
        latent_ok=latent_ok,
        intended_use_ok=intended_use_ok,
        annex_iii_1a_ok=annex_iii_1a_ok,
        annex_iii_5b_ok=annex_iii_5b_ok,
        obligation_ok=obligation_ok,
        reg_alignment_ok=reg_alignment_ok,
        inferred_added=inferred_added,
        all_pass=all_pass,
        summary_raw=json.dumps(summary, indent=2),
        evidence_raw=json.dumps(evidence, indent=2),
        gate_evidence=gate_evidence,
    )

    # shacl_report.txt
    shacl_out = f"conforms: {shacl_ok}\n"
    if shacl_report_text:
        shacl_out += "\n" + shacl_report_text
    (OUTPUT_DIR / "shacl_report.txt").write_text(shacl_out, encoding="utf-8")

    sub("OUTPUT FILES")
    for f in sorted(OUTPUT_DIR.iterdir()):
        print(f"  {f.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
