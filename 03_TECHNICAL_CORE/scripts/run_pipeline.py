"""
ARCO Compliance Verification Pipeline — BFO/RO Aligned (RO:0000091 has_disposition)

Stages:
1) Load ontology + instance data
2) OWL-RL reasoning (materialize entailments)
3) SHACL validation
4) SPARQL audit checks (ASK)
5) Verify HighRiskSystem latent-risk entailment + evidence path
6) Print formal Annex III condition assessment certificate

Modeling relation: RO_0000091 has_disposition (per OBO Foundry / RO best practice)
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from rdflib import Graph, URIRef
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
BFO_2020 = ONTOLOGY_DIR / "imports" / "bfo-2020.owl"
IAO_BOT = ONTOLOGY_DIR / "imports" / "iao_bot.owl"
RO_BOT = ONTOLOGY_DIR / "imports" / "ro_bot.owl"
CCO_BOT = ONTOLOGY_DIR / "imports" / "cco_bot.owl"

SHAPES = VALIDATION_DIR / "assessment_documentation_shape.ttl"

TRACEABILITY_QUERY = REASONING_DIR / "check_assessment_traceability.sparql"
LATENT_RISK_QUERY = REASONING_DIR / "detect_latent_risk.sparql"
HIGH_RISK_INFERENCE_QUERY = REASONING_DIR / "check_high_risk_inference.sparql"
INTENDED_USE_QUERY = REASONING_DIR / "check_intended_use.sparql"
ANNEX_III_1A_QUERY = REASONING_DIR / "check_annex_iii_1a_entailment.sparql"
ANNEX_III_5B_QUERY = REASONING_DIR / "check_annex_iii_5b_entailment.sparql"
OBLIGATION_QUERY = REASONING_DIR / "check_obligation_link.sparql"
REGULATORY_ALIGNMENT_QUERY = REASONING_DIR / "check_regulatory_alignment.sparql"
DEROGATION_FLAG_QUERY = REASONING_DIR / "flag_derogation_candidate.sparql"
FRAUD_FLAG_QUERY = REASONING_DIR / "flag_fraud_exclusion_candidate.sparql"
UNION_SYNC_QUERY = REASONING_DIR / "check_union_subclass_sync.sparql"
# Report-only absence audits (OPEN_PROBLEMS L3.8) — informational lines like
# the derogation/fraud flags; never audit_pass constituents, never emitted fields.
NEGATIVE_CASE_ABSENCE_QUERY = REASONING_DIR / "check_negative_case_no_annex_iii_in_closure.sparql"
CROSS_CATEGORY_ISOLATION_QUERY = REASONING_DIR / "check_cross_category_isolation_in_closure.sparql"
INTENT_WITHOUT_CAPABILITY_QUERY = REASONING_DIR / "flag_intent_without_capability.sparql"

# Emission-layer SELECT queries — graph-bound display values for certificate fields.
# These replace inline Python-embedded SPARQL strings (Gate 1/2/3) and Python
# literal composition (primary classification headline, determination IRI).
# Each query takes ?system as a caller-bound variable.
SELECT_PRIMARY_CLASSIFICATION_QUERY = REASONING_DIR / "select_primary_classification.sparql"
SELECT_GATE_1_CAPABILITY_QUERY = REASONING_DIR / "select_gate_1_capability.sparql"
SELECT_GATE_2_PRESCRIBED_PROCESS_QUERY = REASONING_DIR / "select_gate_2_prescribed_process.sparql"
SELECT_GATE_3_DESIGNATED_ROLE_QUERY = REASONING_DIR / "select_gate_3_designated_role.sparql"
SELECT_DETERMINATION_NODE_QUERY = REASONING_DIR / "select_determination_node.sparql"
# Negative-case companions: surface asserted commitments outside the regulated
# union, so the negative-case output renders what the system DOES assert
# rather than empty placeholders. Used only for emission-layer display in the
# Gate 1/2 negative branches and Determination Path graphic.
SELECT_ASSERTED_COMPONENT_DISPOSITION_QUERY = REASONING_DIR / "select_asserted_component_disposition.sparql"
SELECT_ASSERTED_PRESCRIBED_PROCESS_QUERY = REASONING_DIR / "select_asserted_prescribed_process.sparql"
SELECT_SYSTEM_COMMENT_QUERY = REASONING_DIR / "select_system_comment.sparql"

OUTPUT_DIR = REPO_ROOT / "runs" / "demo"

# --- System under evaluation ---
# SYSTEM_LOCAL and SYSTEM_IRI are set by main() either from the --system CLI
# argument or by deriving from the loaded instance graph (looking up
# ?s rdf:type :System). The previous module-level constant hardcoded
# "Sentinel_ID_System" which test_output_provenance.py Check 3 flagged as a
# cross-fixture-leak smell (closes OPEN_PROBLEMS SYSTEM_LOCAL row of A+ scope).
# Function defaults below reference SYSTEM_LOCAL but every call site in this
# file passes the resolved value explicitly, so the None default is unused.
SYSTEM_LOCAL: str | None = None
SYSTEM_IRI: str | None = None
ARCO_NS = "https://arco.ai/ontology/core#"


# ---------------------------
# helpers
# ---------------------------

def _repo_relative(p: Path) -> str:
    """Return path relative to REPO_ROOT, or the absolute path string as fallback."""
    try:
        return str(p.relative_to(REPO_ROOT))
    except ValueError:
        return str(p)


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
        fmt = "xml" if p.suffix == ".owl" else "turtle"
        g.parse(p.as_posix(), format=fmt)
    return g


# ── TBox/ABox load guard (OPEN_PROBLEMS L3.12) ─────────────────────────
# Instance data is ABox-only by contract: class semantics come from the
# reviewed ontology files, never from input. Without this guard a single
# owl:equivalentClass / rdfs:subClassOf triple smuggled into an instance
# file rewires classification, and both reasoners honor it identically
# (the adversarial decoy fixtures prove the mechanism). The decoys are the
# sanctioned exception — they exist to demonstrate classification rides on
# owl:equivalentClass semantics rather than IRI names — and are allowlisted
# by filename.
_OWL = "http://www.w3.org/2002/07/owl#"
_RDFS = "http://www.w3.org/2000/01/rdf-schema#"
_RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
# Class-level schema predicates: forbidden when the triple touches an
# ARCO-namespace term (subject or object).
SCHEMA_SHAPING_PREDICATES = (
    URIRef(_OWL + "equivalentClass"),
    URIRef(_RDFS + "subClassOf"),
    URIRef(_OWL + "disjointWith"),
    URIRef(_OWL + "unionOf"),
    URIRef(_OWL + "sameAs"),
)
# Property-level schema predicates: forbidden in instance files in ANY
# namespace — instance data has no business declaring property semantics.
# (QA-verified attack shapes: rdfs:subPropertyOf onto cco:prescribes fakes
# Gate 2 via prp-spo1; owl:sameAs onto the punned role universal fakes
# Gate 3's hasValue via eq-rep. A foreign-namespace subject would evade an
# ARCO-term-scoped check, hence the blanket rule for this set.)
PROPERTY_SHAPING_PREDICATES = (
    URIRef(_RDFS + "subPropertyOf"),
    URIRef(_OWL + "propertyChainAxiom"),
    URIRef(_OWL + "inverseOf"),
    URIRef(_OWL + "equivalentProperty"),
    URIRef(_RDFS + "domain"),
    URIRef(_RDFS + "range"),
)
TBOX_GUARD_ALLOWLIST = {
    "ARCO_instances_adversarial_decoy.ttl",
    "ARCO_instances_adversarial_decoy_5b.ttl",
}


def guard_instances_tbox(instances_path: Path) -> None:
    """Fail the run if the instances file asserts schema-shaping triples
    on ARCO-namespace terms, or property-semantics triples in any
    namespace (L3.12)."""
    if instances_path.name in TBOX_GUARD_ALLOWLIST:
        return
    ig = Graph()
    ig.parse(instances_path.as_posix(), format="turtle")
    owl_class = URIRef(_OWL + "Class")
    rdf_type = URIRef(_RDF + "type")
    violations = []
    for s, p, o in ig:
        arco_term = (isinstance(s, URIRef) and str(s).startswith(ARCO_NS)) or (
            isinstance(o, URIRef) and str(o).startswith(ARCO_NS)
        )
        if p in SCHEMA_SHAPING_PREDICATES and arco_term:
            violations.append((s, p, o))
        elif p in PROPERTY_SHAPING_PREDICATES:
            violations.append((s, p, o))
        elif p == rdf_type and o == owl_class and isinstance(s, URIRef) and str(s).startswith(ARCO_NS):
            violations.append((s, p, o))
    if violations:
        listing = "\n".join(f"  {s} {p} {o}" for s, p, o in violations[:10])
        raise RuntimeError(
            "TBOX GUARD: instance file asserts schema-shaping triples on "
            f"ARCO-namespace terms ({len(violations)} violation(s)); instance "
            "data is ABox-only — class semantics come from the reviewed "
            f"ontology (OPEN_PROBLEMS L3.12):\n{listing}"
        )

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
    """Run a SPARQL ASK file query with the system IRI bound to ?system via initBindings.

    The on-disk query file uses a ?system variable rather than a hardcoded IRI,
    so the same file is reusable by any caller (the ROBOT/HermiT cross-check
    workflow, external auditors) by binding ?system at query time. This avoids
    string substitution, which is fragile against substring collisions in
    future class IRIs.
    """
    if not query_path.exists():
        raise FileNotFoundError(f"Missing SPARQL query file: {query_path}")
    q = query_path.read_text(encoding="utf-8").strip()
    system_iri = URIRef(f"{ARCO_NS}{system_local}")
    try:
        result = data_graph.query(q, initBindings={"system": system_iri})
        if isinstance(result, bool):
            return result
        if hasattr(result, "askAnswer") and result.askAnswer is not None:
            return bool(result.askAnswer)
        rows = list(result)
        return bool(rows[0]) if rows else False
    except Exception as e:
        raise RuntimeError(f"SPARQL query failed: {query_path}\n{e}")


def run_sparql_ask_for_system_with_class(
    data_graph: Graph, query_path: Path, system_local: str, excluded_class_local: str
) -> bool:
    """Run a caller-bound ASK with both ?system and ?excluded_class bound.

    Companion to run_sparql_ask_for_system for the cross-category isolation
    audit (OPEN_PROBLEMS L3.8 gap 3), which is deliberately per-(system,
    foreign-class) rather than graph-level: the Annex III applicability
    classes are not asserted disjoint, and a graph-level variant would encode
    a disjointness the regulation does not assert.
    """
    if not query_path.exists():
        raise FileNotFoundError(f"Missing SPARQL query file: {query_path}")
    q = query_path.read_text(encoding="utf-8").strip()
    bindings = {
        "system": URIRef(f"{ARCO_NS}{system_local}"),
        "excluded_class": URIRef(f"{ARCO_NS}{excluded_class_local}"),
    }
    try:
        result = data_graph.query(q, initBindings=bindings)
        if isinstance(result, bool):
            return result
        if hasattr(result, "askAnswer") and result.askAnswer is not None:
            return bool(result.askAnswer)
        rows = list(result)
        return bool(rows[0]) if rows else False
    except Exception as e:
        raise RuntimeError(f"SPARQL query failed: {query_path}\n{e}")


def run_sparql_select_for_system(data_graph: Graph, query_path: Path, system_local: str) -> list[dict]:
    """Run a SPARQL SELECT file query with ?system bound via initBindings.

    Returns a list of result rows as dicts (variable name -> string value, or
    None if unbound). Empty list if zero rows; raises on query execution
    failure (broken query or graph), not on empty results.

    Counterpart to run_sparql_ask_for_system. Used by the emission layer to
    bind graph-derived values into certificate fields (Gate 1/2/3 evidence,
    primary classification, determination IRI) instead of composing them
    from Python literals.
    """
    if not query_path.exists():
        raise FileNotFoundError(f"Missing SPARQL query file: {query_path}")
    q = query_path.read_text(encoding="utf-8").strip()
    system_iri = URIRef(f"{ARCO_NS}{system_local}")
    try:
        result = data_graph.query(q, initBindings={"system": system_iri})
        rows: list[dict] = []
        for r in result:
            row: dict = {}
            for var in result.vars:
                val = r[var]
                row[str(var)] = str(val) if val is not None else None
            rows.append(row)
        return rows
    except Exception as e:
        raise RuntimeError(f"SPARQL query failed: {query_path}\n{e}")


def derive_system_local_from_graph(g: Graph) -> tuple[str | None, list[str]]:
    """Find the system local name from the loaded graph.

    Returns (local_name, all_candidates). local_name is set only if exactly
    one :System instance is asserted; otherwise the caller must require
    explicit --system to disambiguate (e.g. flag-tests fixture has two
    :System instances).
    """
    rdf_type = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
    system_cls = URIRef(f"{ARCO_NS}System")
    candidates = sorted({
        str(s).rsplit("#", 1)[-1]
        for s, _, _ in g.triples((None, rdf_type, system_cls))
    })
    if len(candidates) == 1:
        return candidates[0], candidates
    return None, candidates


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
    # Direct OWLRL_Semantics invocation instead of DeductiveClosure.expand()
    # because expand() creates an anonymous instance internally, making
    # closure.error_messages inaccessible. Both produce identical entailment
    # results (verified against the regression suite).
    closure = owlrl.OWLRL_Semantics(data_graph, False, False, False)
    closure.closure()
    closure.post_process()
    final = len(data_graph)
    added = final - initial
    print(f"Triples: {initial} -> {final}   (+{added} entailed)")

    # BFO disjointness enforcement via closure.error_messages.
    # owlrl handles owl:disjointWith via rule cax-dw by populating
    # error_messages (NOT by entailing owl:Nothing — empirically verified).
    # This is the correct and only mechanism for detecting violations.
    if closure.error_messages:
        print(f"\nBFO DISJOINTNESS VIOLATIONS DETECTED ({len(closure.error_messages)}):")
        for msg in closure.error_messages:
            print(f"  ERROR: {msg}")
        raise RuntimeError(
            f"OWL-RL reasoning found {len(closure.error_messages)} disjointness "
            f"violation(s). This indicates a BFO category error in the ontology."
        )
    print("BFO disjointness check: CLEAN (0 violations)")

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

def _short(iri: str) -> str:
    """Shorten an IRI to its local name for display.

    Blank-node identifiers (no '://' scheme) are rendered as a readable
    placeholder in user-facing output.  Raw IDs are preserved in the
    *_iri fields of machine-readable JSON artifacts.
    """
    if not iri:
        return iri
    if "://" not in iri:
        # Blank-node identifier — not a resolvable IRI
        return "Anonymous Entity (Blank Node)"
    return iri.rsplit("#", 1)[-1] if "#" in iri else iri.rsplit("/", 1)[-1]

def get_primary_arco_classes(g: Graph, system_local: str) -> list[str]:
    """Return local-names of Annex III applicability classes entailed for the
    system, from select_primary_classification.sparql on the reasoned graph.

    Previously: built from per-category ASK booleans (annex_iii_1a_ok /
    annex_iii_5b_ok). Now: bound directly from a SELECT, so the headline
    value is graph-bound rather than derived in Python from ASKs. The SELECT
    and the ASKs both run on the same reasoned graph against the same
    owl:equivalentClass axioms; they must agree.
    Closes OPEN_PROBLEMS L4.3 (headline classification list).
    """
    try:
        rows = run_sparql_select_for_system(g, SELECT_PRIMARY_CLASSIFICATION_QUERY, system_local)
    except Exception:
        return []
    return [_short(r["cls"]) for r in rows if r.get("cls")]

def format_primary_arco_classification(primary_classes: list[str]) -> str:
    """Headline classification string — pure class local-names, no Python qualifier.

    The class IRIs come from select_primary_classification.sparql against the
    reasoned graph; this function just formats them for display. The previous
    Python qualifier mentioning the three-gate provenance is dropped here in
    favour of the separate classification_mode (ENTAILED / NOT_ENTAILED)
    field already present in summary.json and determination_packet.json.
    Closes OPEN_PROBLEMS L4.3 headline composition.
    """
    if not primary_classes:
        return "No ARCO classification within currently modeled categories: Annex III 1(a) and 5(b)."
    return ", ".join(primary_classes)

def format_latent_risk_flag(classification_mode: str) -> str:
    """Latent risk flag string — pure status enum, no Python qualifier.

    The longer scope text ("Annex III Capability-Precondition Flag";
    "not the EU AI Act legal high-risk classification") lived as a Python
    literal in the previous version of this function and is dropped here.
    Per the manifest, that scope text is documentary commentary on
    :HighRiskSystem and belongs to documentary fields / LIMITATIONS, not
    embedded in the graph-backed value. Closes OPEN_PROBLEMS L4.3 latent-flag
    composition.
    """
    if classification_mode in ("INFERRED", "ASSERTED"):
        return "HighRiskSystem (PRESENT)"
    return "HighRiskSystem (NOT PRESENT)"

def get_primary_bindings(g: Graph, system_local: str) -> list[tuple[str, str]]:
    """Return [(component_iri, disposition_iri), ...] for the system.

    Uses select_gate_1_capability.sparql (which binds component, disposition,
    cap_class, cap_label); this function discards cap_class/cap_label and
    surfaces just the unique (component, disposition) tuples for the legacy
    bindings callsite. The SELECT query uses rdfs:subClassOf* so a single
    disposition typed under multiple parent capability classes (post-OWL-RL
    closure) yields one row per parent; dedupe by (component, disposition)
    to preserve the historical one-row-per-evidence-path display. Closes
    OPEN_PROBLEMS L4.3 (gate 1 inline SELECT relocated to standalone file).
    """
    try:
        rows = run_sparql_select_for_system(g, SELECT_GATE_1_CAPABILITY_QUERY, system_local)
    except Exception:
        return []
    seen: set[tuple[str, str]] = set()
    result: list[tuple[str, str]] = []
    for r in rows:
        key = (r.get("component") or "", r.get("disposition") or "")
        if key not in seen:
            seen.add(key)
            result.append(key)
    return result


def get_asserted_dispositions(g: Graph, system_local: str) -> list[dict]:
    """Return component/disposition rows asserted on the system regardless of
    triggering-union membership.

    Uses select_asserted_component_disposition.sparql. Used by the negative-
    case Gate 1 answer and Determination Path graphic to surface what the
    system DOES assert (e.g., the kiosk's :BiometricVerificationCapability)
    rather than rendering em-dashes when the regulated-union query returns
    zero rows. Picks the most specific named class per (component,
    disposition) pair, prefers the class with a label, and falls back to
    IRI local name. Returns [] on query failure.
    """
    try:
        rows = run_sparql_select_for_system(
            g, SELECT_ASSERTED_COMPONENT_DISPOSITION_QUERY, system_local
        )
    except Exception:
        return []
    # Dedupe per (component, disposition); prefer rows with a label and a
    # disposition_class that is not the most generic ARCO ancestor.
    seen: dict[tuple[str, str], dict] = {}
    for r in rows:
        comp = r.get("component") or ""
        disp = r.get("disposition") or ""
        key = (comp, disp)
        cls = r.get("disposition_class") or ""
        # Skip the most generic capability ancestor classes that OWL-RL closure
        # materializes for any disposition typed under :CapabilityDisposition;
        # they are uninformative for emission-layer display.
        if cls.endswith("#CapabilityDisposition"):
            if key in seen:
                continue
        seen[key] = {
            "component_iri": comp,
            "disposition_iri": disp,
            "class_iri": cls,
            "class_label": r.get("cls_label") or _short(cls),
        }
    return list(seen.values())


def get_system_comment(g: Graph, system_local: str) -> str:
    """Return rdfs:comment of the system instance, or empty string.

    Used by the negative-case Provider Obligations panel to surface fixture-
    authored regulatory reasoning (e.g., the kiosk fixture's note on
    Recital 15 + Recital 17 + Annex III 1(a) carve-out) as a documentary
    scope text rather than a Python literal in the emitter. Returns "" on
    query failure or empty result;
    emitter is responsible for skipping the panel when empty.
    """
    try:
        rows = run_sparql_select_for_system(g, SELECT_SYSTEM_COMMENT_QUERY, system_local)
    except Exception:
        return ""
    if not rows:
        return ""
    return rows[0].get("comment") or ""


def get_asserted_prescribed_processes(g: Graph, system_local: str) -> list[dict]:
    """Return IUS / process / process_class rows asserted on the system,
    regardless of regulated-category union membership.

    Uses select_asserted_prescribed_process.sparql. Used by the negative-
    case Gate 2 answer to surface what the system's IUS DOES prescribe
    (e.g., the kiosk's :BiometricVerificationProcess) rather than asserting
    flat absence. Returns [] on query failure.
    """
    try:
        rows = run_sparql_select_for_system(
            g, SELECT_ASSERTED_PRESCRIBED_PROCESS_QUERY, system_local
        )
    except Exception:
        return []
    seen: dict[tuple[str, str], dict] = {}
    for r in rows:
        ius = r.get("ius") or ""
        proc = r.get("process") or ""
        key = (ius, proc)
        if key in seen:
            continue
        seen[key] = {
            "ius_iri": ius,
            "process_iri": proc,
            "class_iri": r.get("process_class") or "",
            "class_label": r.get("process_label") or _short(r.get("process_class") or ""),
        }
    return list(seen.values())


# ---------------------------
# determination packet
# ---------------------------

def select_gate_evidence(g: Graph, system_local: str) -> dict:
    """Run SELECT queries over the reasoned graph to extract gate evidence labels.

    Returns a compact determination packet dict. All labels come from rdfs:label
    annotations in the graph; falls back to shortened IRI local names if absent.
    The three gate queries are standalone .sparql files in
    03_TECHNICAL_CORE/reasoning/ (select_gate_1_capability,
    select_gate_2_prescribed_process, select_gate_3_designated_role); the
    previous inline Python-embedded SPARQL strings were relocated to those
    files as part of A+ (Gate 2 also gained ORDER BY + category filter,
    closes OPEN_PROBLEMS L3.1).

    Empty evidence (zero rows) is a valid result for a system that does not
    satisfy a gate (verification kiosk yields zero Gate 1 rows). Query
    execution failure (broken query / graph) still raises.
    """
    packet: dict = {
        "gate1": {"cap_type_uri": "", "cap_type_label": ""},
        "gate2": {"ius_uri": "", "process_uri": "", "process_type_uri": "", "process_type_label": ""},
        "gate3": {"uss_uri": "", "role_uri": "", "role_label": ""},
    }

    # Gate 1 — capability class via select_gate_1_capability.sparql.
    # Returns rows of (component, disposition, cap_class, cap_label). For the
    # gate-1 evidence panel we surface cap_class + cap_label; component and
    # disposition IRIs are surfaced separately via get_primary_bindings.
    try:
        rows = run_sparql_select_for_system(g, SELECT_GATE_1_CAPABILITY_QUERY, system_local)
    except Exception as e:
        raise RuntimeError(f"select_gate_evidence: gate1 query failed: {e}")
    if rows:
        r = rows[0]
        cap_uri = r.get("cap_class") or ""
        packet["gate1"]["cap_type_uri"] = cap_uri
        packet["gate1"]["cap_type_label"] = r.get("cap_label") or _short(cap_uri)

    # Gate 2 — prescribed process via select_gate_2_prescribed_process.sparql.
    # Deterministic ORDER BY + category filter (closes L3.1; previously used
    # an undirected single-row limit at run_pipeline.py:322-340 with no
    # ordering, so the same fixture could yield different evidence rows
    # across runs).
    try:
        rows = run_sparql_select_for_system(g, SELECT_GATE_2_PRESCRIBED_PROCESS_QUERY, system_local)
    except Exception as e:
        raise RuntimeError(f"select_gate_evidence: gate2 query failed: {e}")
    if rows:
        r = rows[0]
        packet["gate2"]["ius_uri"] = r.get("ius") or ""
        packet["gate2"]["process_uri"] = r.get("process") or ""
        ptype_uri = r.get("process_class") or ""
        packet["gate2"]["process_type_uri"] = ptype_uri
        packet["gate2"]["process_type_label"] = r.get("process_label") or _short(ptype_uri)

    # Gate 3 — designated role via select_gate_3_designated_role.sparql.
    # The file no longer hardcodes FILTER(?role = :NaturalPersonRole) — the
    # category-specific role check lives in the OWL gate axiom
    # (owl:hasValue per equivalentClass), not at the emission layer.
    # OPEN_PROBLEMS L3.2 (audit-layer / SHACL role parameterization) remains
    # open as separate scope.
    try:
        rows = run_sparql_select_for_system(g, SELECT_GATE_3_DESIGNATED_ROLE_QUERY, system_local)
    except Exception as e:
        raise RuntimeError(f"select_gate_evidence: gate3 query failed: {e}")
    if rows:
        r = rows[0]
        packet["gate3"]["uss_uri"] = r.get("uss") or ""
        role_uri = r.get("role_iri") or ""
        packet["gate3"]["role_uri"] = role_uri
        packet["gate3"]["role_label"] = r.get("role_label") or _short(role_uri)

    return packet


def gate3_designates_expected_role(gate_evidence: dict) -> bool:
    """Return whether Gate 3 satisfies ARCO's current role-designation axiom.

    Current modeled Annex III branches both require the USS to designate the
    NaturalPersonRole universal. OPEN_PROBLEMS L3.2 tracks future
    category-parameterized role expectations.
    """
    return (
        bool(gate_evidence["gate3"]["uss_uri"])
        and gate_evidence["gate3"]["role_uri"] == f"{ARCO_NS}NaturalPersonRole"
    )


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

    # Evidence check (RO has_disposition path)
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
    print("  HighRiskSystem = System AND (has_part SOME (SystemComponent AND has_disposition SOME AnnexIIITriggeringCapability))")
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
        print("HighRiskSystem latent-risk flag is present AND justified by an explicit structural path.")
        return True, asserted_pre, entailed_post, bindings

    sub("FAIL")
    print("HighRiskSystem latent-risk flag was not inferred.")
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
    all_pass: bool | None,
    summary_raw: str,
    evidence_raw: str,
    primary_arco_classes: list[str],
    gate_evidence: dict | None = None,
    derogation_flagged: bool = False,
    fraud_flagged: bool = False,
    asserted_dispositions: list[dict] | None = None,
    asserted_prescribed_processes: list[dict] | None = None,
    system_comment: str = "",
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

    if asserted_dispositions is None:
        asserted_dispositions = []
    if asserted_prescribed_processes is None:
        asserted_prescribed_processes = []

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # ── strip node labels ──────────────────────────────────────────
    # When the regulated-union bindings (Gate 1) are empty but the system
    # DOES assert a component-borne disposition, surface the asserted
    # commitments rather than rendering em-dashes that look like missing
    # data. The disposition class label is added separately (disp_class_label)
    # so the determination path can show the asserted type and flag that it
    # is outside the regulated union (per
    # runs/audits/2026-05-14_output_audit_AGENT1_technical_trace.md C3).
    if bindings:
        comp_label = _short(bindings[0][0])
        disp_label = _short(bindings[0][1])
        comp_iri = bindings[0][0]
        disp_iri = bindings[0][1]
        disp_class_label = ""
        disp_outside_union = False
    elif asserted_dispositions:
        first = asserted_dispositions[0]
        comp_label = _short(first["component_iri"])
        disp_label = _short(first["disposition_iri"])
        comp_iri = first["component_iri"]
        disp_iri = first["disposition_iri"]
        disp_class_label = first["class_label"]
        disp_outside_union = True
    else:
        comp_label = "\u2014"
        disp_label = "\u2014"
        comp_iri = ""
        disp_iri = ""
        disp_class_label = ""
        disp_outside_union = False

    # ── classification labels ──────────────────────────────────────
    is_high_risk = classification_mode in ("INFERRED", "ASSERTED")
    result_label = (
        "HighRiskSystem latent-risk flag"
        if is_high_risk
        else "No ARCO classification within currently modeled categories: Annex III 1(a) and 5(b)."
    )

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
            # L3.3: read from graph-derived gate_evidence (same pattern as the
            # 1(a) branch above). The existing helpers _select_gate1_capability /
            # _select_gate2_process / _select_gate3_role are category-agnostic
            # and system-scoped, so they return creditworthiness-shaped values
            # for a 5(b) system. Hardcoding them as Python literals would emit
            # the same string regardless of what the graph actually contains.
            "capability": gate_evidence["gate1"]["cap_type_label"] or "Creditworthiness evaluation",
            "process": gate_evidence["gate2"]["process_type_label"] or "Creditworthiness evaluation",
            "role": gate_evidence["gate3"]["role_label"] or "Natural persons",
        })

    has_applicable_category = bool(triggered_categories)
    primary_result_label = ", ".join(primary_arco_classes) if primary_arco_classes else "No category-specific ARCO class"

    # ── human-readable system name ─────────────────────────────────
    sys_display = system_local.replace("_", " ")

    # ── build executive summary text ───────────────────────────────
    if has_applicable_category:
        cat_list = ", ".join(c["label"] for c in triggered_categories)
        cap_list = ", ".join(c["capability"] for c in triggered_categories)
        summary_text = (
            f"{sys_display} has a <strong>category-specific ARCO applicability "
            f"classification</strong> under ARCO's ontology encoding of EU AI Act "
            f"Annex III. The system possesses a {cap_list}, triggering {cat_list}. "
            f"All three regulatory gates are satisfied for each applicable category, "
            f"and the category class was entailed by OWL-RL formal reasoning over "
            f"{inferred_added:,} entailed triples."
        )
        cap_phrase = cap_list.lower().replace(" capability", "")
        plain_english_summary = (
            f"In plain language: this system contains a hardware component capable of "
            f"{cap_phrase}. The provider's intended-use specification names a regulated "
            f"process, and the use scenario designates natural persons as the affected "
            f"population. Together these three conditions match {cat_list} of "
            f"Regulation (EU) 2024/1689 (the EU AI Act). ARCO does not evaluate the "
            f"Article 6(3) derogation; that requires human legal review."
        )
    elif is_high_risk:
        summary_text = (
            f"{sys_display} has a <strong>latent-risk flag</strong>: "
            f"HighRiskSystem was {classification_mode.lower()} from the Gate 1 "
            f"capability precondition, but no category-specific Annex III "
            f"applicability class was entailed."
        )
        plain_english_summary = (
            f"In plain language: this system contains a component capable of an "
            f"Annex III triggering capability, but the provider's documentation does "
            f"not yet name a regulated process or affected role. The system is flagged "
            f"for follow-up review; it is not yet classified into a specific Annex III "
            f"item."
        )
    else:
        summary_text = (
            f"{sys_display}: <strong>No ARCO classification within currently modeled "
            f"categories: Annex III 1(a) and 5(b).</strong> No HighRiskSystem latent-risk "
            f"flag was inferred under ARCO's ontology encoding of EU AI Act Annex III "
            f"based on current assertions. ARCO does not currently model other Annex III "
            f"categories; absence here is not a determination about those other categories."
        )
        plain_english_summary = (
            f"In plain language: this system has been assessed against ARCO's encoding "
            f"of Annex III items 1(a) (biometric identification) and 5(b) "
            f"(creditworthiness). No triggering capability or matching intended use is "
            f"asserted in the loaded graph for this system. Under the Open World "
            f"Assumption, this is not a closed-world denial of what the system can do; "
            f"it is the absence of the commitments required to entail Annex III "
            f"applicability. Other Annex III items are not currently modeled, so "
            f"absence here is not a determination about them."
        )

    if all_pass is None:
        # Non-applicable run (no in-scope Annex III category triggered):
        # the audit constituents do not semantically apply, so aggregator
        # all_pass is null rather than True/False. Per-row state is
        # communicated by the ternary audit-table badges below; an exec-
        # summary aggregate sentence here would contradict the populated
        # rows it sits above (Wave 3 W3-4 / adversarial M-A6 / M-W2-4).
        # No suffix appended.
        pass
    elif all_pass:
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

    def _status_badge(val, present_label, absent_label, *, absence_is_normal=False):
        """Three-state badge helper for rows whose semantics are ternary
        (present / not_present / not_run) per output_manifest_v2.yaml.

        When absence_is_normal=True, the False case renders as gray (.bn)
        rather than red (.bf). Used for the HighRiskSystem latent-risk flag,
        Obligation linked, and Regulatory alignment rows on non-applicable
        runs, where False is a correct-and-expected outcome — not a defect.
        Closes the misleading red-FAIL polarity for negative-control fixtures
        (see runs/audits/2026-05-14_output_audit_AGENT1_technical_trace.md C1).
        """
        if val is None:
            return '<span class="badge bn">N/A</span>'
        if val:
            return f'<span class="badge bp">{present_label}</span>'
        cls = "bn" if absence_is_normal else "bf"
        return f'<span class="badge {cls}">{absent_label}</span>'

    def _annex(val):
        if val is None:
            return '<span class="badge bn">N/A</span>'
        if val:
            # Pure graph-backed entailment value. The Article 6(3) derogation
            # scope qualifier (when no DerogationClaim is asserted) is
            # surfaced as the separate `derogation_scope_badge` rendered
            # alongside the conclusion banner, per
            # output_manifest_v2.yaml field `derogation_evaluation_scope`
            # (forbidden_pattern: embedding the qualifier into a
            # graph_backed value).
            return '<span class="badge bp">VERIFIED (ENTAILED)</span>'
        return '<span class="badge bn">NOT APPLICABLE</span>'

    # ── mode badge ─────────────────────────────────────────────────
    if has_applicable_category:
        mode_badge = '<span class="badge bi">ENTAILED</span>'
    elif classification_mode == "INFERRED":
        mode_badge = '<span class="badge bi">LATENT INFERRED</span>'
    elif classification_mode == "ASSERTED":
        mode_badge = '<span class="badge ba">LATENT ASSERTED</span>'
    else:
        mode_badge = '<span class="badge bn">NOT PRESENT</span>'

    # ── derogation scope qualifier badge (HTML conclusion banner) ──
    # ARCO does not evaluate the Article 6(3) carve-out. When an Annex III
    # category is entailed and no provider :DerogationClaim is asserted,
    # disclose the unevaluated scope in the same banner as the conclusion.
    # When a DerogationClaim IS asserted, the existing FLAGGED banner / row
    # already signals the unevaluated derogation; do not double-disclose.
    if has_applicable_category and not derogation_flagged:
        derogation_scope_badge = (
            '<span class="badge bn" title="ARCO does not evaluate the Article '
            '6(3) carve-out conditions; provider must self-supply a '
            'DerogationClaim artifact.">ARTICLE 6(3) DEROGATION: NOT EVALUATED</span>'
        )
    else:
        derogation_scope_badge = ""

    headline_label = (
        "CATEGORY APPLICABLE" if has_applicable_category
        else ("LATENT RISK ONLY" if is_high_risk
              else "NO ARCO CATEGORY (1(a) OR 5(b))")
    )

    # Drop the aggregate audit badge on non-applicable runs. The badge said
    # "AUDIT N/A" while the audit table below it rendered with populated
    # rows, producing an internal contradiction (per
    # runs/audits/2026-05-14_output_audit_AGENT1_technical_trace.md C2 and
    # AGENT3 §4.4). The table itself is informational and now uses the
    # ternary _status_badge helper so each row honestly reports its own
    # state — no aggregate-level badge is needed on negative cases.
    if all_pass is None:
        overall_badge = ""
    elif all_pass:
        overall_badge = '<span class="badge bp">ALL PASS</span>'
    else:
        overall_badge = '<span class="badge bf">SOME FAIL</span>'

    # ── audit rows ─────────────────────────────────────────────────
    # Three rows have ternary semantics per output_manifest_v2.yaml:
    #   - HighRiskSystem latent-risk flag: present / not_present (always
    #     informational — absence is not a defect; matches the manifest enum
    #     [present, not_present]).
    #   - Obligation linked / Regulatory alignment: pass / fail / not_run.
    #     When the system has no applicable Annex III category, no obligation
    #     or alignment audit semantically applies, so absence renders neutral
    #     rather than red. When a category IS triggered, absence is a real
    #     defect and renders red. Matches the manifest enum [pass, fail, not_run].
    # Detection-style rows (Latent risk SPARQL traversal) preserve their
    # gray-on-not-detected behavior because not-detected is the correct,
    # expected outcome for a non-applicable system.
    audit_rows = [
        ("SHACL conformance",        "classification / structure", _b(shacl_ok)),
        ("HighRiskSystem latent-risk flag", "classification / OWL-RL",
         _status_badge(inference_ok, "PRESENT", "NOT PRESENT", absence_is_normal=True)),
        ("Annex III 1(a)",           "classification / OWL-RL",   _annex(annex_iii_1a_ok)),
        ("Annex III 5(b)",           "classification / OWL-RL",   _annex(annex_iii_5b_ok)),
        ("Traceability",             "audit / SPARQL",            _b(traceability_ok)),
        ("Latent risk",              "audit / SPARQL",
         _status_badge(latent_ok, "DETECTED", "NOT DETECTED", absence_is_normal=True)
         if latent_ok is not None
         else '<span class="badge bn">N/A</span>'),
        ("Intended use modelled",    "audit / SPARQL",            _b(intended_use_ok)),
        ("Obligation linked",        "audit / SPARQL",
         _status_badge(obligation_ok, "LINKED", "NOT LINKED",
                       absence_is_normal=not has_applicable_category)),
        ("Regulatory alignment",     "audit / SPARQL",
         _status_badge(reg_alignment_ok, "ALIGNED", "NOT ALIGNED",
                       absence_is_normal=not has_applicable_category)),
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

    result_node_cls = "nr-high" if has_applicable_category or is_high_risk else "nr-none"

    # Disposition node label: when surfacing an asserted-but-not-in-union
    # disposition (negative-control case), include the asserted class label
    # so a reader sees what the disposition IS typed as, not just the
    # individual IRI. The bridge edge to AnnexIIITriggeringCapability is
    # then labeled "outside regulated union" instead of em-dash, so the
    # entailment break is visible (per audit C3).
    if disp_outside_union and disp_class_label:
        disp_node_label = f"{disp_label} \u2014 typed {disp_class_label}"
        bridge_node_label = "outside regulated union"
    else:
        disp_node_label = disp_label
        bridge_node_label = "(bridge axiom) \u2021"

    strip_html = (
        node("ns", "System", system_local)
        + edge_el("has_part", "bfo:0000051")
        + node("nc", "SystemComponent", comp_label, comp_iri)
        + edge_el("has_disposition", "ro:0000091")
        + node("nd", "Disposition", disp_node_label, disp_iri)
        + edge_el("rdf:type \u2286")
        + node("nt", "AnnexIIITriggeringCapability", bridge_node_label)
        + edge_el("OWL-RL \u22a2")
        + node(result_node_cls, "Primary Result", primary_result_label if has_applicable_category else result_label)
    )

    # ── gate cards (for Layer 2) ───────────────────────────────────
    # Each gate_ok flag is bound to the typed evidence the emission queries
    # produce, NOT to the audit-layer documentary ASKs. This is the
    # output-discipline contract that prevents the HTML gate-card affirmative
    # branch from firing when the loaded TTL does not assert typed gate
    # evidence (OPEN_PROBLEMS L4.7).
    #
    # Gate 1: inference_ok mirrors :HighRiskSystem entailment via has_part /
    # has_disposition / AnnexIIITriggeringCapability; cap_type_uri is the
    # typed-evidence binding from select_gate_1_capability.sparql.
    gate1_ok = inference_ok
    # Gate 2: bound to typed-process-class evidence from
    # select_gate_2_prescribed_process.sparql (which FILTERs to the regulated
    # category classes). intended_use_ok (the check_intended_use.sparql ASK)
    # is a separate documentary-traceability audit and does NOT prove
    # typed-content satisfaction by itself — its own header at
    # reasoning/check_intended_use.sparql:5-12 declares it documentary.
    gate2_ok = bool(gate_evidence["gate2"]["process_type_uri"])
    # Gate 3: USS designation is asserted AND designates the expected role
    # universal. The OWL Gate 3 axiom uses
    # `cco:designates owl:hasValue :NaturalPersonRole`; a fixture asserting
    # a USS that designates a different role would otherwise display as
    # Gate 3 OK while OWL correctly does not entail Gate 3 satisfaction.
    # (L3.4 truth-surface fix; per-category role parameterization tracked
    # at L3.2.)
    gate3_ok = gate3_designates_expected_role(gate_evidence)

    # Pre-compute gate display labels from the determination packet.
    # These are used in axiom pattern text, gate answers, and counterfactuals.
    # Using the full rdfs:label so text tracks ontology changes automatically.
    # The fallback placeholders are non-concretizing — they do NOT name a
    # category-specific class IRI that may not be asserted in the loaded TTL
    # (OPEN_PROBLEMS L4.7 closure; output_manifest_v2.yaml forbidden patterns).
    _cap_label      = gate_evidence["gate1"]["cap_type_label"] or "(no Annex III triggering capability bound for this run)"
    _process_label  = gate_evidence["gate2"]["process_type_label"] or "(no in-scope regulated process bound for this run)"
    _role_label     = gate_evidence["gate3"]["role_label"] or "(no role designated for this run)"
    _role_local     = _short(gate_evidence["gate3"]["role_uri"]) if gate_evidence["gate3"]["role_uri"] else "(no role local)"

    # Negative-branch text for Gates 1 and 2: when the regulated-union queries
    # return zero rows but the system DOES assert a disposition / prescribed
    # process outside the regulated union, surface that asserted commitment
    # using OWA-bounded language. Prevents the pre-fix output from saying
    # "no triggering capability detected" when the kiosk fixture asserts
    # :BiometricVerificationCapability (per CLAUDE.md Forbidden prose patterns
    # and runs/audits/2026-05-14_output_audit_AGENT1_technical_trace.md H1).
    if asserted_dispositions:
        first_d = asserted_dispositions[0]
        _gate1_negative_html = (
            f"<strong>No <code>:AnnexIIITriggeringCapability</code>-typed disposition "
            f"is asserted on any component of this system in the loaded graph.</strong> "
            f"The asserted disposition <em>{_short(first_d['disposition_iri'])}</em> "
            f"on <em>{_short(first_d['component_iri'])}</em> is typed as "
            f"<em>{first_d['class_label']}</em>, which is not a member of the "
            f"<code>:AnnexIIITriggeringCapability</code> <code>owl:unionOf</code>. "
            f"Under the Open World Assumption, this is not a closed-world denial of "
            f"the underlying hardware's capabilities."
        )
    else:
        _gate1_negative_html = (
            "<strong>No <code>:AnnexIIITriggeringCapability</code>-typed disposition "
            "is asserted on any component of this system in the loaded graph.</strong> "
            "Under the Open World Assumption, absence in the graph is not a "
            "closed-world denial."
        )

    if asserted_prescribed_processes:
        first_p = asserted_prescribed_processes[0]
        _gate2_negative_html = (
            f"<strong>No process token prescribed by an Intended Use Specification of "
            f"this system is typed as a regulated process class in the loaded graph.</strong> "
            f"The asserted prescribed process <em>{_short(first_p['process_iri'])}</em> is "
            f"typed as <em>{first_p['class_label']}</em>, which is not a member of the "
            f"regulated process union "
            f"(<code>:RemoteBiometricIdentificationProcess</code> for Annex III 1(a); "
            f"<code>:CreditworthinessEvaluationProcess</code> for 5(b))."
        )
    else:
        _gate2_negative_html = (
            "<strong>No process token prescribed by an Intended Use Specification of "
            "this system is typed as a regulated process class in the loaded graph.</strong> "
            "Under the Open World Assumption, absence in the graph is not a "
            "closed-world denial."
        )

    # Gate 2 evidence-line prefix mirrors the Gate 1 conditional shape
    # (commit 82979a0 / adversarial M-A1). Three outcomes:
    #   - regulated-union bound (gate2_ok): "Matched" with the IUS and process token
    #   - asserted process outside regulated union: "Asserted (not matched in
    #     regulated union)" with the IUS and asserted process token
    #   - neither bound nor asserted: "No asserted process path"
    if gate2_ok:
        _gate2_evidence_prefix = "Matched"
        _g2_ius = _short(gate_evidence["gate2"]["ius_uri"]) or "(IntendedUseSpecification)"
        _g2_proc = _short(gate_evidence["gate2"]["process_uri"]) or "(process token)"
        _gate2_evidence_text = f"{_g2_ius} &rarr; {_g2_proc} (typed as {_process_label})"
    elif asserted_prescribed_processes:
        first_p_ev = asserted_prescribed_processes[0]
        _gate2_evidence_prefix = "Asserted (not matched in regulated union)"
        _g2_ius_a = _short(first_p_ev["ius_iri"]) or "(IntendedUseSpecification)"
        _g2_proc_a = _short(first_p_ev["process_iri"])
        _gate2_evidence_text = f"{_g2_ius_a} &rarr; {_g2_proc_a} (typed as {first_p_ev['class_label']})"
    else:
        _gate2_evidence_prefix = "No asserted process path"
        _gate2_evidence_text = "—"

    gate_cards_html = f"""
        <div class="gate-card {_gate_status_class(gate1_ok)}">
          <div class="gate-header">
            <span class="gate-num">Gate 1</span>
            <span class="gate-title">Triggering Capability</span>
            <span class="gate-badge {'gbp' if gate1_ok else 'gbf'}">{_gate_status_label(gate1_ok)}</span>
          </div>
          <div class="gate-question">Does the system contain a component with a regulated capability?</div>
          <div class="gate-answer">
            {"<strong>Yes.</strong> The system contains <em>" + comp_label + "</em>, which has a disposition typed as <em>" + _cap_label + "</em> (<em>" + disp_label + "</em>). This disposition falls within the regulated capability scope of Annex III." if gate1_ok and bindings else _gate1_negative_html}
          </div>
          <details class="gate-evidence">
            <summary>Technical evidence</summary>
            <div class="gate-tech">
              <p><strong>Axiom pattern:</strong> System <code>bfo:0000051</code> <span class="prop-label">(has part)</span> some (SystemComponent and <code>ro:0000091</code> <span class="prop-label">(has disposition)</span> some {_cap_label})</p>
              <p><strong>{"Matched" if bindings else ("Asserted (not matched in regulated union)" if disp_outside_union else "No asserted disposition path")}:</strong> {system_local} &rarr; {comp_label} &rarr; {disp_label}</p>
              <p><strong>Layer:</strong> OWL-RL entailment (classification-authoritative)</p>
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
            {"<strong>Yes.</strong> An Intended Use Specification prescribes the system for <em>" + _process_label + "</em>. This is not merely any use &mdash; the process token must be typed as the regulated process class for this gate to be satisfied." if gate2_ok else _gate2_negative_html}
          </div>
          <details class="gate-evidence">
            <summary>Technical evidence</summary>
            <div class="gate-tech">
              <p><strong>Axiom pattern:</strong> IntendedUseSpecification <code>iao:0000136</code> <span class="prop-label">(is about)</span> System and <code>cco:prescribes</code> <span class="prop-label">(prescribes)</span> some {_process_label}</p>
              <p><strong>{_gate2_evidence_prefix}:</strong> {_gate2_evidence_text}</p>
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
            {"<strong>Yes.</strong> A Use Scenario Specification designates <em>" + _role_label + "</em> as the affected role category, via the typed CCO designation property. The spec names the role universal directly; no role-bearer instance is asserted at this layer." if gate3_ok else "<strong>No designation of the regulated role category</strong> found in the use scenario documentation."}
          </div>
          <details class="gate-evidence">
            <summary>Technical evidence</summary>
            <div class="gate-tech">
              <p><strong>Axiom pattern:</strong> UseScenarioSpecification <code>iao:0000136</code> <span class="prop-label">(is about)</span> System and <code>cco:designates</code> <span class="prop-label">(designates)</span> {_role_label}</p>
              <p><strong>Gate mechanism:</strong> <code>cco:designates</code> is the CCO designation property whose specification supports inscription naming an entity, including a universal. The spec designates the role category at class level; this is documentary aboutness, not a role-token assertion.</p>
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
        # L2.12 component D output carrier (OPEN_PROBLEMS L2.12; LIMITATIONS §3.7.d):
        # when the asserted prescribed process types as the bare 1:N genus, the
        # single fact that would change the outcome is the Art 3(41) remoteness
        # question — deliberately a deployer elicitation, not a baked-in class.
        # Surface the question instead of presenting a stable-looking endpoint.
        _genus_iri = f"{ARCO_NS}BiometricIdentificationProcess"
        _genus_asserted = any(
            p.get("class_iri") == _genus_iri
            for p in (asserted_prescribed_processes or [])
        )
        _elicitation_html = ""
        if _genus_asserted:
            _elicitation_html = (
                '<p><strong>Open elicitation question (Article 3(41)):</strong> the asserted '
                'prescribed process is typed as the bare 1:N identification genus '
                '(<code>BiometricIdentificationProcess</code>). Whether this deployment is '
                '<em>remote</em> &mdash; identification without the subjects&rsquo; active '
                'involvement &mdash; is the single reviewed commitment that would change this '
                'outcome, and it is deliberately a deployer question, not a baked-in class '
                '(LIMITATIONS &sect;3.7.d). If the deployer confirms capture without active '
                'involvement, retype the process token as '
                '<code>RemoteBiometricIdentificationProcess</code> and re-run; Annex III 1(a) '
                'would then be evaluated against the remote subkind.</p>'
            )
        counterfactual_html = (
            '<div class="cf-item"><p>No Annex III categories are currently triggered. '
            'To trigger a category-specific ARCO classification, the system would '
            'need to satisfy all three gates (capability, prescribed process, '
            'affected role) for at least one Annex III category.</p>'
            + _elicitation_html + '</div>'
        )

    # ── obligations text (Layer 3) ─────────────────────────────────
    if has_applicable_category:
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
            <div class="obl-desc">The system must undergo conformity assessment procedures before being placed on the market or put into service (Article 43). For Annex III point 1 biometric systems: where harmonised standards or common specifications are applied, the provider opts for either internal control (Annex VI) or the notified-body procedure (Annex VII); where they are not applied, the notified-body procedure (Annex VII) is required (Article 43(1)). For the other Annex III categories, internal control per Annex VI applies (Article 43(2)).</div>
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
        # Negative-case Provider Obligations panel.
        # The previous version emitted a Python-literal scope qualifier
        # ("Standard transparency obligations under Title IV may still apply
        # ...") that did not trace to any modeling decision, SHACL shape,
        # SPARQL query, or LIMITATIONS disclosure (per
        # runs/audits/2026-05-14_output_audit_AGENT2_modeling_competency.md H2 —
        # ARCO does not model Title IV obligations; see LIMITATIONS §2). It
        # is dropped here.
        # When the loaded fixture provides a system-level rdfs:comment with
        # regulatory framing (e.g., the kiosk fixture's note on Recital 15 +
        # Recital 17 + Annex III 1(a) carve-out), surface it via the
        # documentary scope text path
        # declared in output_manifest_v2.yaml. Otherwise the panel reports
        # the OWA-bounded non-entailment note alone.
        if system_comment:
            _comment_safe = system_comment.replace("<", "&lt;").replace(">", "&gt;")
            obligations_html = f"""
        <div class="obl-note">
          <p>No category-specific Annex III applicability class is currently entailed under ARCO's encoding of Annex III 1(a) and 5(b). ARCO does not model other regulatory obligations; absence here is not a determination about other regulatory regimes.</p>
          <p style="margin-top:0.75rem;border-left:3px solid #888;padding-left:0.75rem;color:#444"><strong>Fixture note (rdfs:comment on the system):</strong> {_comment_safe}</p>
        </div>"""
        else:
            obligations_html = """
        <div class="obl-note">
          <p>No category-specific Annex III applicability class is currently entailed under ARCO's encoding of Annex III 1(a) and 5(b). ARCO does not model other regulatory obligations; absence here is not a determination about other regulatory regimes.</p>
        </div>"""

    # ── assemble full HTML ─────────────────────────────────────────
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ARCO \u2014 {system_local} \u2014 Condition Assessment</title>
<style>
/* ══════════════════════════════════════════════════════════════
   ARCO Condition Assessment View — Self-contained CSS
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
.prop-label {{ color: var(--mu); font-style: italic; font-size: 0.72rem; opacity: 0.8 }}

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
  .exec-banner .classification {{ color: {"#dc3545" if is_high_risk else "#155724"} }}
  .exec-text strong {{ color: {"#dc3545" if is_high_risk else "#155724"} }}
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
    <h1>Condition Assessment Report</h1>
  </div>
  <div class="header-meta">
    <span>System: <strong>{sys_display}</strong></span>
    <span>Regime: ARCO ontology encoding of EU AI Act Article 6 / Annex III</span>
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
      <span class="classification">{headline_label}</span>
      {mode_badge}
      {overall_badge}
      {derogation_scope_badge}
    </div>
    <p class="exec-text">{summary_text}</p>
    <p class="exec-text" style="background:#f5f9ff;border-left:3px solid #2563eb;padding:0.75rem 1rem;margin-top:0.75rem;color:#1e3a5f">{plain_english_summary}</p>
    {"<div class='exec-cats'>" + "".join(
      '<div class="exec-cat"><div class="cat-id">' + c["article_ref"].upper() + '</div>'
      '<div class="cat-title">' + c["title"] + '</div></div>'
      for c in triggered_categories
    ) + "</div>" if triggered_categories else ""}
    <p class="exec-text" style="font-size:0.85em;border-left:3px solid #888;padding-left:0.75rem;margin-top:1rem;color:#444">
      <strong>Scope:</strong> ARCO assesses structured RDF instance data supplied to the
      pipeline. It does not verify raw vendor documentation, the physical deployed system,
      or legal sufficiency. ARCO currently models Annex III 1(a) (biometric identification)
      and 5(b) (creditworthiness) only. The PRIMARY classification is the Annex III
      applicability ARCO entails under its encoding, not the final legal high-risk
      determination under the EU AI Act (which also depends on the Article 6(3) derogation,
      surfaced but not evaluated). Article 5 prohibited-practice routing is not evaluated.
    </p>
    {("<p class='exec-text' style='font-size:0.85em;border-left:3px solid #c97a00;padding-left:0.75rem;margin-top:0.75rem;color:#5a3a00;background:#fff7e6'><strong>Derogation note:</strong> Article 6(3) derogation, if legally valid, may supersede Annex III high-risk treatment. ARCO flags the claim but does not evaluate it; human legal review is required.</p>") if (derogation_flagged and is_high_risk) else ""}
  </div>
</section>

<!-- ═══════════════════════════════════════════════════════════
     LAYER 2: GATE-BY-GATE CLASSIFICATION STORY
     ═══════════════════════════════════════════════════════════ -->
<section id="gates">
  <h2>Classification Gates</h2>
  <p class="gate-intro">
    ARCO encodes the EU AI Act's high-risk classification as a three-gate test.
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
    <span class="gr-final">{headline_label}</span>
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
  <p style="margin:0.25rem 0 1rem 0; font-size:0.85em; color:#555;">Most are upper-ontology subclass and inverse-property closure across BFO/RO/IAO/CCO. The load-bearing classification entailments are the small subset shown above (system <code>rdf:type</code> assignments plus the supporting subclass and inverse-aboutness triples the gates depend on).</p>

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
     LAYER 6: EXCEPTION FLAGS
     ═══════════════════════════════════════════════════════════ -->
<section id="exception-flags">
  <h2>Exception Flags &mdash; Provider-Submitted Claims</h2>
  <p class="gate-intro" style="margin-bottom:1rem">
    These flags detect provider-submitted claim artifacts in the instance data.
    They are <strong>informational only</strong> and do not affect the OWL-RL
    classification or audit-layer pass/fail result. A flagged claim requires
    independent human legal review before any regulatory reliance.
  </p>
  <table class="audit-table">
    <thead><tr><th>Exception Type</th><th>Legal Basis</th><th>Status</th></tr></thead>
    <tbody>
      <tr>
        <td>Art. 6(3) derogation</td>
        <td class="layer">provider claim / DerogationClaim artifact</td>
        <td>{"<span class='badge ba'>FLAGGED &mdash; human review required</span>" if derogation_flagged else "<span class='badge bp'>NOT FLAGGED</span>"}</td>
      </tr>
      <tr>
        <td>5(b) fraud exclusion</td>
        <td class="layer">provider claim / FraudDetectionProcess artifact</td>
        <td>{"<span class='badge ba'>FLAGGED &mdash; human review required</span>" if fraud_flagged else "<span class='badge bp'>NOT FLAGGED</span>"}</td>
      </tr>
    </tbody>
  </table>
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


def _status_label(
    val,
    present_label: str,
    absent_label: str,
    *,
    not_applicable_label: str | None = None,
    not_run_label: str = "NOT_RUN",
) -> str:
    """Three-state label helper for JSON / certificate fields whose semantics
    are ternary per output_manifest_v2.yaml.

    Mirrors _status_badge() in write_html_view but emits ENUM LABELS rather
    than HTML classes:
      - val is None  -> not_run_label (the query did not run)
      - val is True  -> present_label (the query returned true on this run)
      - val is False AND not_applicable_label is not None -> not_applicable_label
        (used when False is the legitimate outcome of a query that doesn't
        logically apply to this run, e.g. obligation/regulatory ASKs on a
        non-applicable kiosk)
      - val is False AND not_applicable_label is None     -> absent_label
        (used when False is a real audit failure OR a domain-specific
        negative outcome, e.g. latent_risk_flag's NOT_PRESENT on a
        non-high-risk system)

    Closes the kiosk HTML/JSON same-document contradiction flagged by
    PR #68 adversarial audit H-A2 (visible audit table showed gray
    "NOT LINKED" / "NOT ALIGNED" while embedded summary.json showed
    "FAIL"). Manifest enums:
      - latent_risk_flag (line 124): [present, not_present, not_run]
      - obligation_check (line 201): [pass, fail, not_run]
      - regulatory_alignment_check (line 208): [pass, fail, not_run]
    On non_applicable runs, obligation/regulatory pass not_applicable_label
    so the False outcome reads as "field is not in scope for this run"
    rather than "field reports a real audit failure."
    """
    if val is None:
        return not_run_label
    if val:
        return present_label
    if not_applicable_label is not None:
        return not_applicable_label
    return absent_label


def main() -> None:
    parser = argparse.ArgumentParser(description="ARCO Compliance Verification Pipeline")
    parser.add_argument(
        "--system", default=None,
        help="Local name of the system under evaluation (auto-derived from the loaded graph if exactly one :System is asserted; required if multiple)."
    )
    parser.add_argument(
        "--instances", default=None,
        help="Path to instance TTL file (default: ARCO_instances_sentinel.ttl)"
    )
    args = parser.parse_args()

    global SYSTEM_LOCAL, SYSTEM_IRI, INSTANCES
    if args.instances is not None:
        candidate = Path(args.instances)
        resolved = candidate.resolve()
        if not resolved.exists():
            fallback = (ONTOLOGY_DIR / candidate.name).resolve()
            if fallback.exists():
                resolved = fallback
        INSTANCES = resolved

    hr("ARCO COMPLIANCE VERIFICATION PIPELINE (OPERATOR VIEW)")

    sub("LOAD")
    print("Loading: core ontology + governance extension + instance data")
    guard_instances_tbox(INSTANCES)
    g_source = load_union_graph(BFO_2020, IAO_BOT, RO_BOT, CCO_BOT, CORE, GOV, INSTANCES)
    print(f"Triples loaded (asserted): {len(g_source)}")

    # ── resolve SYSTEM_LOCAL from --system or auto-derive ──────────
    # Previously a module-level constant hardcoded "Sentinel_ID_System" which
    # test_output_provenance.py Check 3 flagged as a cross-fixture-leak smell.
    # Now: --system overrides; otherwise inspect the loaded graph for
    # ?s rdf:type :System and use the unique candidate. The flag-tests
    # fixture has multiple :System instances and still requires --system.
    if args.system is not None:
        SYSTEM_LOCAL = args.system
    else:
        derived, candidates = derive_system_local_from_graph(g_source)
        if derived is None:
            print()
            if not candidates:
                print(f"ERROR: No :System instance asserted in {INSTANCES.name}.")
                print("Pass --system <local_name> or load a fixture that declares a :System.")
            else:
                print(f"ERROR: Multiple :System instances in {INSTANCES.name}. Pass --system to disambiguate.")
                print("Available:")
                for c in candidates:
                    print(f"  - {c}")
            print()
            print("No new certificate was written.")
            raise SystemExit(2)
        SYSTEM_LOCAL = derived
        print(f"Auto-derived --system: {SYSTEM_LOCAL}")
    SYSTEM_IRI = f"{ARCO_NS}{SYSTEM_LOCAL}"

    # ── invalid --system fail-fast (before reasoning) ──────────────
    # If --system names a local that is not asserted as rdf:type :System in
    # the pre-reasoning graph, the pipeline produces nonsense gate evidence
    # and risks emitting a misleading "NOT TRIGGERED" certificate for a
    # system that was never actually loaded. Fail before OWL-RL runs.
    _RDF_TYPE = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
    _SYSTEM_CLS = URIRef(f"{ARCO_NS}System")
    _system_iri = URIRef(f"{ARCO_NS}{SYSTEM_LOCAL}")
    if (_system_iri, _RDF_TYPE, _SYSTEM_CLS) not in g_source:
        print()
        print(f"ERROR: --system '{SYSTEM_LOCAL}' is not asserted as :System in the loaded instance data.")
        print(f"Looked up IRI: {_system_iri}")
        try:
            _available = sorted({
                str(s).rsplit("#", 1)[-1] for s, _, _ in g_source.triples((None, _RDF_TYPE, _SYSTEM_CLS))
            })
        except Exception:
            _available = []
        if _available:
            print("Available asserted :System local names in this instance file:")
            for _name in _available:
                print(f"  - {_name}")
        print()
        print("No new certificate was written. Existing runs/demo artifacts (if any) reflect")
        print("a prior run and may be stale relative to the current invocation.")
        raise SystemExit(2)

    # clone -> reason over the copy so we can compare pre vs post
    g = clone_graph(g_source)

    g, initial_count, inferred_added = run_reasoning(g)

    # L4.8: serialize the reasoned graph so reviewers can re-derive the
    # classification with their own OWL-RL reasoner. The graph contains
    # the original RDF commitments plus all entailed triples.
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    reasoned_graph_path = OUTPUT_DIR / "reasoned_graph.ttl"
    g.serialize(destination=str(reasoned_graph_path), format="turtle")
    print(f"Reasoned graph written: {reasoned_graph_path.name} "
          f"({len(g)} triples; {inferred_added} inferred)")

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

    union_sync_ok = None
    if UNION_SYNC_QUERY.exists():
        print("\nUnion-subclass sync (AnnexIIITriggeringCapability membership consistency)...")
        # L3.11: run against the ASSERTED graph (g_source), not the closure.
        # On the closure the guard is half-dead (OWL-RL re-materializes the
        # missing subclass triple before the guard looks, so the drift it
        # exists to catch can never be caught) and half-false-alarm (the
        # decoys' inferred alias subclassing trips Direction 2). Empirically
        # verified twice in the 2026-06-10 audit.
        union_sync_ok = run_sparql_ask_from_file(g_source, UNION_SYNC_QUERY)
        print(f"Union sync: {union_sync_ok}")

    # ── Negative-case absence + cross-category isolation (report-only; OPEN_PROBLEMS L3.8) ──
    # Absence-in-closure audit lines, informational like the exception flags
    # below: NOT audit_pass constituents and NOT emitted fields (folding them
    # in would change the Sentinel smoke-test surface and the manifest's
    # fixed audit_layer_status constituent set). On positive fixtures the
    # absence check correctly prints False (membership present); on the
    # verification kiosk it prints True. Absence here is absence from the
    # materialized OWL-RL closure under current commitments (OWA), not DL
    # non-entailment — HermiT is the independent DL check. Expected-answer
    # enforcement lives in test_scenarios.py, keyed off each scenario's
    # expected dict.
    if NEGATIVE_CASE_ABSENCE_QUERY.exists():
        print("\nNegative-case absence check (Annex III membership in closure; report-only)...")
        _absence = run_sparql_ask_for_system(g, NEGATIVE_CASE_ABSENCE_QUERY, SYSTEM_LOCAL)
        print(f"Annex III membership absent from closure: {_absence}")

    if CROSS_CATEGORY_ISOLATION_QUERY.exists():
        print("\nCross-category isolation (per foreign Annex III class; report-only)...")
        for _foreign_local in ("AnnexIII1aApplicableSystem", "AnnexIII5bApplicableSystem"):
            _isolated = run_sparql_ask_for_system_with_class(
                g, CROSS_CATEGORY_ISOLATION_QUERY, SYSTEM_LOCAL, _foreign_local
            )
            print(f"Not a member of {_foreign_local} in closure: {_isolated}")

    # Intent-without-capability (report-only; OPEN_PROBLEMS L3.10). Surfaces the
    # under-classification direction disclosed at LIMITATIONS §3.9: Gate 2+3
    # documentary evidence present for a modeled category while that category's
    # Gate 1 capability is absent from the closure. Never folded into audit_pass;
    # never a gate condition (same discipline as the derogation/fraud flags).
    if INTENT_WITHOUT_CAPABILITY_QUERY.exists():
        print("\nIntent-without-capability check (Gates 2+3 documented, Gate 1 absent in closure; report-only)...")
        _iwc = run_sparql_ask_for_system(g, INTENT_WITHOUT_CAPABILITY_QUERY, SYSTEM_LOCAL)
        print(f"Documented regulated intent without asserted capability: {_iwc}")

    # ── Audit-layer exception flags (informational only — do not affect classification or audit_pass) ──
    # These detect provider-submitted claim artifacts that may affect legal interpretation.
    # A flag does not override OWL classification. It directs human review.
    derogation_flagged = False
    if DEROGATION_FLAG_QUERY.exists():
        print("\nArticle 6(3) derogation claim detection...")
        derogation_flagged = run_sparql_ask_for_system(g, DEROGATION_FLAG_QUERY, SYSTEM_LOCAL)
        print(f"Derogation claim present: {derogation_flagged}")

    fraud_flagged = False
    if FRAUD_FLAG_QUERY.exists():
        print("\n5(b) fraud exclusion candidate detection...")
        fraud_flagged = run_sparql_ask_for_system(g, FRAUD_FLAG_QUERY, SYSTEM_LOCAL)
        print(f"Fraud exclusion candidate: {fraud_flagged}")

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
    # Pure graph-backed entailment values. Article 6(3) derogation scope
    # is reported as a separate run-metadata line below, not embedded in
    # the graph_backed VERIFIED literal (per output_manifest_v2.yaml
    # field `derogation_evaluation_scope` forbidden_pattern).
    if annex_iii_1a_ok is not None:
        print(f"Annex III 1a:  {'VERIFIED (ENTAILED)' if annex_iii_1a_ok else 'NOT APPLICABLE'} (OWL-entailed)")
    if annex_iii_5b_ok is not None:
        print(f"Annex III 5b:  {'VERIFIED (ENTAILED)' if annex_iii_5b_ok else 'NOT APPLICABLE'} (OWL-entailed)")
    # Separate run-scope disclosure for derogation evaluation. Surfaces
    # only when a category is entailed and no DerogationClaim is asserted
    # (when a claim IS asserted, the existing FLAG row signals the
    # unevaluated derogation; do not double-disclose).
    if (annex_iii_1a_ok or annex_iii_5b_ok) and not derogation_flagged:
        print("  [run scope]    Article 6(3) derogation: NOT EVALUATED")
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
    if union_sync_ok is not None:
        print(f"Union sync:    {_pf(union_sync_ok)}")
    print(f"Entailed triples added: +{inferred_added}")

    print()
    print("  [exception flags — provider-submitted claims, human review required]")
    print(f"Art. 6(3) derogation:  {'FLAGGED — DerogationClaim detected; human review required' if derogation_flagged else 'NOT FLAGGED'}")
    print(f"5(b) fraud exclusion:  {'FLAGGED — FraudDetectionProcess detected; human review required' if fraud_flagged else 'NOT FLAGGED'}")

    # ── Two-layer pass computation ──────────────────────────────────
    # A system can be legitimately non-applicable to all modeled categories.
    # That is a correct classification outcome, not a pipeline failure: the
    # SHACL graph validated and the reasoner correctly determined no Annex III
    # category fires.
    no_category_triggered = (annex_iii_1a_ok is False) and (annex_iii_5b_ok is False)
    non_applicable_run = shacl_ok and no_category_triggered

    # Classification layer: OWL-RL entailment + SHACL structural validation.
    # PASS if either (a) HighRiskSystem entailment fired, or (b) the system is
    # legitimately non-applicable (no Annex III category, SHACL clean).
    classification_pass = (shacl_ok and inference_ok) or non_applicable_run

    # Audit layer: SPARQL ASK queries on the reasoned graph.
    # These inspect declared documentary content; they do not produce
    # and cannot affect the classification result. A non-applicable system has
    # no Annex III audit content to verify; treat audit as N/A in that case
    # by reporting None (not a forced True).
    #
    # Closes OPEN_PROBLEMS L4.1: the previous version force-set
    # audit_pass = True on non-applicable runs, which made all_checks_passed
    # report a misleading True even when individual audit constituents
    # returned False (e.g. VerificationKiosk: latent_risk=FAIL,
    # obligation=FAIL, but all_checks_passed=true under the lie). Now:
    # audit_pass is None on non-applicable runs; all_pass is None on
    # non-applicable runs; applicability_status names the case explicitly.
    if non_applicable_run:
        audit_pass = None
    else:
        audit_pass = traceability_ok
        if latent_ok is not None:
            audit_pass = audit_pass and latent_ok
        if intended_use_ok is not None:
            audit_pass = audit_pass and intended_use_ok
        if obligation_ok is not None:
            audit_pass = audit_pass and obligation_ok
        if reg_alignment_ok is not None:
            audit_pass = audit_pass and reg_alignment_ok
        if union_sync_ok is not None:
            audit_pass = audit_pass and union_sync_ok

    # Applicability status — separate from audit_pass so consumers can
    # disambiguate "no in-scope category triggered" (not_applicable) from
    # "category triggered AND audit passed/failed" (applicable + pass/fail).
    applicability_status = "not_applicable" if non_applicable_run else "applicable"

    # Overall aggregator. None when audit doesn't apply; otherwise the
    # boolean AND of the two layers. The previous version aggregated to a
    # forced True; now consumers reading all_checks_passed see null (or
    # JSON null) and must consult applicability_status to interpret.
    if audit_pass is None:
        all_pass = None
    else:
        all_pass = classification_pass and audit_pass

    print(f"\n  Classification layer: {'PASS' if classification_pass else 'FAIL'}")
    if audit_pass is None:
        print(f"  Audit layer:          NOT APPLICABLE")
    else:
        print(f"  Audit layer:          {'PASS' if audit_pass else 'FAIL'}")
    # CI smoke-test greps for the literal "ALL CHECKS PASSED" — preserve that
    # substring on non-applicable runs so the smoke-test default (Sentinel /
    # CreditScorer / Kiosk) keeps signalling pipeline health.
    if all_pass is None:
        print("\nALL CHECKS PASSED (audit not applicable)")
    elif all_pass:
        print("\nALL CHECKS PASSED")
    else:
        print("\nSOME CHECKS FAILED")

    # ---------------------------------------------------------------
    # ARCO CONDITION ASSESSMENT CERTIFICATE
    # ---------------------------------------------------------------
    if not asserted_pre and entailed_post:
        classification_mode = "INFERRED"
    elif asserted_pre and entailed_post:
        classification_mode = "ASSERTED"
    else:
        classification_mode = "NOT PRESENT"

    primary_arco_classes = get_primary_arco_classes(g, SYSTEM_LOCAL)
    primary_arco_classification = format_primary_arco_classification(primary_arco_classes)
    latent_risk_flag = format_latent_risk_flag(classification_mode)
    primary_classification_mode = "ENTAILED" if primary_arco_classes else "NOT_ENTAILED"

    # Negative-case companion reads — bound here so the certificate-text
    # block below can surface asserted-but-outside-regulated-union evidence
    # alongside the HTML view and evidence.json (Wave 3 W3-2; adversarial
    # M-W2-1). The same three values are passed to write_html_view further
    # down and re-used in evidence.json emission. All three come from named
    # SPARQL queries on the reasoned graph.
    asserted_dispositions = get_asserted_dispositions(g, SYSTEM_LOCAL)
    asserted_prescribed_processes = get_asserted_prescribed_processes(g, SYSTEM_LOCAL)
    system_comment = get_system_comment(g, SYSTEM_LOCAL)

    # Derive triggering capability class. Three outcomes:
    #   - regulated-union bound (bindings non-empty): name the matched class
    #   - asserted but outside regulated union: name the asserted class with
    #     an "(asserted, not in regulated union)" qualifier so the certificate
    #     does not silently drop the asserted commitment (matches HTML view's
    #     "Asserted (not matched in regulated union)" prefix, Wave 2 #8).
    #   - neither: keep "N/A"
    trigger_display = "N/A"
    if bindings:
        trigger_display = _short(bindings[0][1])
    elif asserted_dispositions:
        _ad0 = asserted_dispositions[0]
        trigger_display = f"{_ad0['class_label']} (asserted, not in regulated union)"

    # Build evidence path strings. Three outcomes mirror trigger_display:
    #   - regulated-union bound: emit one line per binding (system -> comp -> disp)
    #   - asserted but outside regulated union: emit the asserted path with the
    #     "asserted" qualifier so the consumer sees the OWA-bounded data
    #   - neither: leave empty (caller renders "(none detected)")
    evidence_lines = []
    if bindings:
        for comp, disp in bindings[:3]:
            evidence_lines.append(f"  {SYSTEM_LOCAL} -> {_short(comp)} -> {_short(disp)}")
    elif asserted_dispositions:
        for ad in asserted_dispositions[:3]:
            evidence_lines.append(
                f"  {SYSTEM_LOCAL} -> {_short(ad['component_iri'])} "
                f"-> {_short(ad['disposition_iri'])} "
                f"(asserted, typed {ad['class_label']}; not in regulated union)"
            )

    # EVIDENCE PATH header label distinguishes the three outcomes computed
    # above (Wave 3 W3-2): regulated-union match, asserted-but-not-in-union,
    # or neither. The "(none detected)" closed-world phrasing is preserved
    # only for the case where no asserted-disposition data exists at all,
    # so a reader sees the same line in the same situation as before.
    if bindings:
        _evidence_path_header = "EVIDENCE PATH:"
        _evidence_path_absent_text = ""
    elif asserted_dispositions:
        _evidence_path_header = "EVIDENCE PATH (asserted, not in regulated union):"
        _evidence_path_absent_text = ""
    else:
        _evidence_path_header = "EVIDENCE PATH:"
        _evidence_path_absent_text = "(no asserted disposition path)"

    hr("ARCO CONDITION ASSESSMENT CERTIFICATE")
    print(f"  SYSTEM:                  {SYSTEM_LOCAL}")
    print(f"  REGIME:                  ARCO ontology encoding of EU AI Act (Article 6 / Annex III)")
    print(f"  INPUT INSTANCE:          {INSTANCES.name}  ({_repo_relative(INSTANCES)})")
    print(f"  PRIMARY ARCO CLASSIFICATION:  {primary_arco_classification}")
    print(f"  LATENT-RISK FLAG:             {latent_risk_flag}")
    print(f"  TRIGGERING CAPABILITY:   {trigger_display}")
    if evidence_lines:
        print(f"  {_evidence_path_header}")
        for line in evidence_lines:
            print(line)
    else:
        print(f"  {_evidence_path_header:<25}{_evidence_path_absent_text}")
    # LATENT-RISK FLAG, OBLIGATION, and REGULATORY ALIGNMENT use ternary
    # _status_label() so the certificate matches the HTML view's neutral
    # rendering on non-applicable runs (closes PR #68 adversarial audit
    # H-A2). On non-applicable runs, obligation and regulatory alignment
    # pass not_applicable_label so the False outcome reads as "out of
    # scope for this run" rather than as a real audit failure (parallel
    # to the gray HTML badge). LATENT_RISK uses domain labels DETECTED /
    # NOT_DETECTED — NOT_DETECTED is a substantive answer for a non-
    # high-risk system, not a "not applicable" outcome.
    _cert_latent_risk_label = _status_label(
        latent_ok, "DETECTED", "NOT_DETECTED",
    )
    _cert_obligation_label = _status_label(
        obligation_ok, "PASS", "FAIL",
        not_applicable_label="NOT_APPLICABLE" if non_applicable_run else None,
    )
    _cert_reg_alignment_label = _status_label(
        reg_alignment_ok, "PASS", "FAIL",
        not_applicable_label="NOT_APPLICABLE" if non_applicable_run else None,
    )

    print(f"  SHACL:                   {_pf(shacl_ok)}")
    print(f"  TRACEABILITY:            {_pf(traceability_ok)}")
    # The standalone "LATENT RISK:" row (from detect_latent_risk.sparql) was
    # removed here because the "LATENT-RISK FLAG: HighRiskSystem (PRESENT |
    # NOT PRESENT)" head-block row above already names the same fact in the
    # same vocabulary the HTML view uses. Two semantically-overlapping rows
    # in certificate.txt were N-1 in the PR #68 counter-adversarial review.
    # The underlying SPARQL ASK result remains in summary.json under
    # "latent_risk" so consumers that need the audit-layer evidence still
    # see it; the certificate is the human-readable summary, not the full
    # audit record.
    if intended_use_ok is not None:
        print(f"  INTENDED USE:            {_pf(intended_use_ok)}")
    # Article 6(3) derogation scope: ARCO does not evaluate the
    # Article 6(3) carve-out conditions; it only detects whether a provider-
    # supplied :DerogationClaim artifact is asserted. The Annex III ENTAILED
    # conclusion below is a pure graph_backed value; the derogation scope
    # disclosure rides on its own line (see "ARTICLE 6(3) DEROGATION" below)
    # per output_manifest_v2.yaml field `derogation_evaluation_scope`
    # forbidden_pattern (Python concatenation that embeds the qualifier
    # into a graph_backed value).
    if annex_iii_1a_ok is not None:
        _line_1a = "VERIFIED (ENTAILED)" if annex_iii_1a_ok else "NOT APPLICABLE"
        print(f"  ANNEX III 1(a):          {_line_1a}")
    if annex_iii_5b_ok is not None:
        if annex_iii_5b_ok:
            _line_5b = "VERIFIED (ENTAILED)"
        else:
            _line_5b = "NOT APPLICABLE"
        print(f"  ANNEX III 5(b):          {_line_5b}")
    # Separate run-scope disclosure for derogation evaluation. Surfaces
    # only when a category is entailed and no DerogationClaim is asserted
    # (when a claim IS asserted, the existing FLAG line below already
    # signals the unevaluated derogation; do not double-disclose).
    if (annex_iii_1a_ok or annex_iii_5b_ok) and not derogation_flagged:
        print("  ARTICLE 6(3) DEROGATION: NOT EVALUATED (run scope)")
    if annex_iii_1a_ok:
        print("  ARTICLE 5 PROHIBITION:   NOT EVALUATED (run scope)")
    if obligation_ok is not None:
        print(f"  OBLIGATION:              {_cert_obligation_label}")
    if reg_alignment_ok is not None:
        print(f"  REGULATORY ALIGNMENT:    {_cert_reg_alignment_label}")
    print(f"  ENTAILED TRIPLES ADDED:  +{inferred_added}")
    print(f"                           Most are upper-ontology subclass and inverse-property")
    print(f"                           closure across BFO/RO/IAO/CCO. The load-bearing")
    print(f"                           classification entailments are the small subset above")
    print(f"                           (system rdf:type assignments plus the supporting subclass")
    print(f"                           and inverse-aboutness triples the gates depend on).")
    print()
    print("  SCOPE: ARCO assesses structured RDF instance data supplied to the pipeline.")
    print("         It does not verify raw vendor documentation, the physical deployed")
    print("         system, or legal sufficiency. ARCO currently models Annex III 1(a)")
    print("         (biometric identification) and 5(b) (creditworthiness) only.")
    print("         The PRIMARY classification is the Annex III applicability ARCO")
    print("         entails under its encoding, not the final legal high-risk")
    print("         determination under the EU AI Act, which also depends on the")
    print("         Article 6(3) derogation (surfaced but not evaluated here).")
    print("=" * 72)

    # ---------------------------------------------------------------
    # WRITE OUTPUT FILES (runs/demo/)
    # ---------------------------------------------------------------
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # certificate.txt
    cert_lines = []
    cert_lines.append("=" * 72)
    cert_lines.append("ARCO CONDITION ASSESSMENT CERTIFICATE")
    cert_lines.append("=" * 72)
    cert_lines.append(f"  SYSTEM:                  {SYSTEM_LOCAL}")
    cert_lines.append(f"  REGIME:                  ARCO ontology encoding of EU AI Act (Article 6 / Annex III)")
    cert_lines.append(f"  INPUT INSTANCE:          {INSTANCES.name}  ({_repo_relative(INSTANCES)})")
    cert_lines.append(f"  PRIMARY ARCO CLASSIFICATION:  {primary_arco_classification}")
    cert_lines.append(f"  LATENT-RISK FLAG:             {latent_risk_flag}")
    cert_lines.append(f"  TRIGGERING CAPABILITY:   {trigger_display}")
    if evidence_lines:
        cert_lines.append(f"  {_evidence_path_header}")
        for line in evidence_lines:
            cert_lines.append(line)
    else:
        cert_lines.append(f"  {_evidence_path_header:<25}{_evidence_path_absent_text}")
    cert_lines.append(f"  SHACL:                   {_pf(shacl_ok)}")
    cert_lines.append(f"  TRACEABILITY:            {_pf(traceability_ok)}")
    # See operator-view comment above: the "LATENT RISK:" row is dropped
    # from certificate.txt to remove the semantic duplication with
    # "LATENT-RISK FLAG:". The underlying SPARQL ASK result stays in
    # summary.json["latent_risk"] for audit consumers.
    if intended_use_ok is not None:
        cert_lines.append(f"  INTENDED USE:            {_pf(intended_use_ok)}")
    # Pure graph-backed entailment values. The Article 6(3) derogation
    # scope rides on the separate "ARTICLE 6(3) DEROGATION" line below
    # (per output_manifest_v2.yaml field `derogation_evaluation_scope`
    # forbidden_pattern).
    if annex_iii_1a_ok is not None:
        _cert_line_1a = "VERIFIED (ENTAILED)" if annex_iii_1a_ok else "NOT APPLICABLE"
        cert_lines.append(f"  ANNEX III 1(a):          {_cert_line_1a}")
    if annex_iii_5b_ok is not None:
        _cert_line_5b = "VERIFIED (ENTAILED)" if annex_iii_5b_ok else "NOT APPLICABLE"
        cert_lines.append(f"  ANNEX III 5(b):          {_cert_line_5b}")
    # Separate run-scope disclosure for derogation evaluation. Surfaces
    # only when a category is entailed and no DerogationClaim is asserted.
    if (annex_iii_1a_ok or annex_iii_5b_ok) and not derogation_flagged:
        cert_lines.append("  ARTICLE 6(3) DEROGATION: NOT EVALUATED (run scope)")
    if annex_iii_1a_ok:
        cert_lines.append("  ARTICLE 5 PROHIBITION:   NOT EVALUATED (run scope)")
    if obligation_ok is not None:
        cert_lines.append(f"  OBLIGATION:              {_cert_obligation_label}")
    if reg_alignment_ok is not None:
        cert_lines.append(f"  REGULATORY ALIGNMENT:    {_cert_reg_alignment_label}")
    cert_lines.append(f"  ENTAILED TRIPLES ADDED:  +{inferred_added}")
    cert_lines.append(f"                           Most are upper-ontology subclass and inverse-property")
    cert_lines.append(f"                           closure across BFO/RO/IAO/CCO. The load-bearing")
    cert_lines.append(f"                           classification entailments are the small subset above")
    cert_lines.append(f"                           (system rdf:type assignments plus the supporting subclass")
    cert_lines.append(f"                           and inverse-aboutness triples the gates depend on).")
    cert_lines.append("")
    cert_lines.append("  [exception flags — provider-submitted claims, human review required]")
    cert_lines.append(f"  ART. 6(3) DEROGATION:    {'FLAGGED — DerogationClaim artifact detected; human legal review required before treating this as a final determination' if derogation_flagged else 'NOT FLAGGED'}")
    _cert_is_high_risk = classification_mode in ("INFERRED", "ASSERTED")
    if derogation_flagged and _cert_is_high_risk:
        cert_lines.append("                           NOTE: Article 6(3) derogation, if legally valid, may supersede Annex III high-risk treatment. ARCO flags the claim but does not evaluate it; human legal review is required.")
    cert_lines.append(f"  5(b) FRAUD EXCLUSION:    {'FLAGGED — FraudDetectionProcess artifact detected; human legal review required' if fraud_flagged else 'NOT FLAGGED'}")
    cert_lines.append("")
    cert_lines.append("  SCOPE: ARCO assesses structured RDF instance data supplied to the pipeline.")
    cert_lines.append("         It does not verify raw vendor documentation, the physical deployed")
    cert_lines.append("         system, or legal sufficiency. ARCO currently models Annex III 1(a)")
    cert_lines.append("         (biometric identification) and 5(b) (creditworthiness) only.")
    cert_lines.append("         The PRIMARY classification is the Annex III applicability ARCO")
    cert_lines.append("         entails under its encoding, not the final legal high-risk")
    cert_lines.append("         determination under the EU AI Act, which also depends on the")
    cert_lines.append("         Article 6(3) derogation (surfaced but not evaluated here).")
    cert_lines.append("=" * 72)
    (OUTPUT_DIR / "certificate.txt").write_text("\n".join(cert_lines) + "\n", encoding="utf-8")

    # Determination IRI from graph — closes OPEN_PROBLEMS L4.2. Returns the
    # IRI of any :HighRiskDetermination asserted in the loaded fixture;
    # null for fixtures without one. Previously the emitter hardcoded a
    # Sentinel-shaped determination IRI for every fixture, producing a
    # cross-fixture leak (CreditScorer / Verification / Decoy / FlagTests
    # all carried Sentinel's IRI in their determination_packet.json output
    # despite that node not existing in their graphs).
    try:
        determination_rows = run_sparql_select_for_system(g, SELECT_DETERMINATION_NODE_QUERY, SYSTEM_LOCAL)
    except Exception:
        determination_rows = []
    determination_node_uri: str | None = determination_rows[0].get("det") if determination_rows else None

    # summary.json — schema 1.4 applies ternary semantics to latent_risk_flag
    # (entailment), obligation, and regulatory_alignment so the JSON contract
    # matches the HTML view's ternary rendering on non-applicable runs.
    # Closes the same-document HTML/JSON contradiction flagged by the PR #68
    # adversarial audit (HIGH H-A2): the kiosk HTML embeds summary.json in a
    # <details> block, and a reader expanding it previously saw "FAIL" for
    # the same fields the visible audit table now renders as gray neutral.
    #
    # Manifest enum mapping (output_manifest_v2.yaml):
    #   - latent_risk_flag (manifest line 124) emits [present, not_present, not_run]
    #   - obligation_check (line 201) emits [pass, fail, not_run]
    #   - regulatory_alignment_check (line 208) emits [pass, fail, not_run]
    # Schema 1.4 adds the regulatory_alignment field (was computed but not
    # emitted at schema 1.3) and replaces binary _pf() with the ternary
    # _status_label() for the three negative-control-relevant fields.
    summary = {
        "schema_version": "1.4",
        "system": SYSTEM_LOCAL,
        "regime": "ARCO ontology encoding of EU AI Act (Article 6 / Annex III)",
        "instance_file_name": INSTANCES.name,
        "instance_file_path": str(_repo_relative(INSTANCES)),
        "classification": primary_arco_classification,
        "classification_mode": primary_classification_mode,
        "primary_arco_classes": primary_arco_classes,
        "latent_risk_flag": latent_risk_flag,
        "latent_risk_class": "HighRiskSystem",
        "latent_risk_mode": classification_mode,
        "shacl": _pf(shacl_ok),
        "traceability": _pf(traceability_ok),
        "latent_risk": _status_label(
            latent_ok, "DETECTED", "NOT_DETECTED",
        ),
        "intended_use": (_pf(intended_use_ok) if intended_use_ok is not None else "NOT_RUN"),
        # Pure graph-backed entailment values. Article 6(3) derogation
        # scope rides on the separate `derogation_evaluation_scope`
        # field below, not embedded in these graph_backed literals
        # (per output_manifest_v2.yaml field `derogation_evaluation_scope`
        # forbidden_pattern).
        "annex_iii_1a": ("VERIFIED (ENTAILED)" if annex_iii_1a_ok else ("NOT APPLICABLE" if annex_iii_1a_ok is not None else "N/A")),
        "annex_iii_5b": ("VERIFIED (ENTAILED)" if annex_iii_5b_ok else ("NOT APPLICABLE" if annex_iii_5b_ok is not None else "N/A")),
        "derogation_evaluation_scope": {
            "evaluated": False,
            "reason": "Article 6(3) derogation evaluation not modeled in current ARCO release; see LIMITATIONS.md §2",
        },
        "obligation": _status_label(
            obligation_ok, "PASS", "FAIL",
            not_applicable_label="NOT_APPLICABLE" if non_applicable_run else None,
        ),
        "regulatory_alignment": _status_label(
            reg_alignment_ok, "PASS", "FAIL",
            not_applicable_label="NOT_APPLICABLE" if non_applicable_run else None,
        ),
        "entailment": _status_label(
            inference_ok, "PRESENT", "NOT_PRESENT",
        ),
        "entailed_triples_added": inferred_added,
        "applicability_status": applicability_status,
        "all_checks_passed": all_pass,
        "determination_node_uri": determination_node_uri,
        "flag_derogation_candidate": derogation_flagged,
        "flag_fraud_exclusion_candidate": fraud_flagged,
    }
    (OUTPUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    # asserted_dispositions / asserted_prescribed_processes / system_comment
    # were read in the certificate section above (Wave 3 W3-2) so the same
    # bindings back the certificate-text EVIDENCE PATH, the evidence.json
    # asserted-disposition fields, and the HTML view's negative-case panels
    # from one set of SPARQL reads.

    # evidence.json — schema-versioned object so negative-control runs
    # carry the asserted-but-not-in-regulated-union evidence rather than
    # an empty list. On positive runs the regulated-union bindings list
    # carries the matched evidence; on negative runs the asserted-but-
    # outside-union list carries the asserted commitments instead.
    # Schema 1.4 (paired with summary.json 1.4) wraps the prior bare list
    # in an object so future evidence kinds can be added without breaking
    # consumers.
    evidence = {
        "schema_version": "1.4",
        "system": SYSTEM_LOCAL,
        "regulated_capability_bindings": [
            {
                "component": _short(comp),
                "disposition": _short(disp),
                "component_iri": comp,
                "disposition_iri": disp,
            }
            for comp, disp in bindings
        ],
        "asserted_dispositions_outside_regulated_union": [
            {
                "component": _short(d["component_iri"]),
                "component_iri": d["component_iri"],
                "disposition": _short(d["disposition_iri"]),
                "disposition_iri": d["disposition_iri"],
                "asserted_class_iri": d["class_iri"],
                "asserted_class_label": d["class_label"],
            }
            for d in (asserted_dispositions if not bindings else [])
        ],
        "asserted_prescribed_processes_outside_regulated_union": [
            {
                "ius_iri": p["ius_iri"],
                "process": _short(p["process_iri"]),
                "process_iri": p["process_iri"],
                "asserted_class_iri": p["class_iri"],
                "asserted_class_label": p["class_label"],
            }
            for p in (asserted_prescribed_processes if not gate_evidence["gate2"]["process_type_uri"] else [])
        ],
    }
    (OUTPUT_DIR / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")

    # determination_packet.json — compact intermediate representation;
    # the HTML view is rendered from this, not from scattered Python logic.
    # Schema 1.3 adds applicability_status (closes L4.1) and binds the
    # determination_node_uri from a SPARQL SELECT instead of a hardcoded IRI
    # (closes L4.2). Schema 1.4 mirrors the asserted-but-outside-regulated-
    # union bindings from evidence.json and certificate.txt EVIDENCE PATH so
    # the packet, certificate, evidence ledger, and HTML view communicate the
    # same epistemic state for negative-case runs (same-document consistency).
    determination_packet = {
        "schema_version": "1.4",
        "applicability_status": applicability_status,
        "system_uri": SYSTEM_IRI,
        "system_label": SYSTEM_LOCAL.replace("_", " "),
        "run_id": datetime.now(timezone.utc).isoformat(),
        "instance_file_name": INSTANCES.name,
        "instance_file_path": str(_repo_relative(INSTANCES)),
        "classification": "CATEGORY_APPLICABLE" if primary_arco_classes else "NO_CATEGORY_APPLICABILITY",
        "classification_mode": primary_classification_mode,
        "primary_arco_classification": primary_arco_classification,
        "primary_arco_classes": primary_arco_classes,
        "latent_risk_flag": "PRESENT" if classification_mode in ("INFERRED", "ASSERTED") else "NOT_PRESENT",
        "latent_risk_class": "HighRiskSystem",
        "latent_risk_mode": classification_mode,
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
                # Packet-side gate_2 status mirrors HTML-side `gate2_ok` rebind
                # (run_pipeline.py:806): typed-evidence presence, not the
                # documentary ASK `intended_use_ok`. Closes the schema-incoherent
                # SATISFIED-with-empty-evidence state on non-applicable runs.
                "status": "SATISFIED" if bool(gate_evidence["gate2"]["process_type_uri"]) else "NOT_SATISFIED",
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
                # Packet-side Gate 3 status mirrors HTML-side `gate3_ok`:
                # USS existence is not enough; the designated role must match
                # the current OWL Gate 3 target.
                "status": "SATISFIED" if gate3_designates_expected_role(gate_evidence) else "NOT_SATISFIED",
                "evidence": {
                    "uss_uri": gate_evidence["gate3"]["uss_uri"],
                    "role_uri": gate_evidence["gate3"]["role_uri"],
                    "role_label": gate_evidence["gate3"]["role_label"],
                },
            },
        ],
        "determination_node_uri": determination_node_uri,
        "inferred_triples_added": inferred_added,
        "flag_derogation_candidate": derogation_flagged,
        "flag_fraud_exclusion_candidate": fraud_flagged,
        # Mirror the asserted-but-outside-the-regulated-union bindings already
        # emitted into evidence.json and the certificate-text EVIDENCE PATH.
        # On positive runs (gate-1 / gate-2 match the regulated union) these
        # lists are empty; on the kiosk negative the lists carry the asserted
        # commitments the regulated-union bindings did not. Same-document
        # consistency with certificate.txt and evidence.json.
        "asserted_dispositions_outside_regulated_union": [
            {
                "component": _short(d["component_iri"]),
                "component_iri": d["component_iri"],
                "disposition": _short(d["disposition_iri"]),
                "disposition_iri": d["disposition_iri"],
                "asserted_class_iri": d["class_iri"],
                "asserted_class_label": d["class_label"],
            }
            for d in (asserted_dispositions if not bindings else [])
        ],
        "asserted_prescribed_processes_outside_regulated_union": [
            {
                "ius_iri": p["ius_iri"],
                "process": _short(p["process_iri"]),
                "process_iri": p["process_iri"],
                "asserted_class_iri": p["class_iri"],
                "asserted_class_label": p["class_label"],
            }
            for p in (asserted_prescribed_processes if not gate_evidence["gate2"]["process_type_uri"] else [])
        ],
    }
    (OUTPUT_DIR / "determination_packet.json").write_text(
        json.dumps(determination_packet, indent=2) + "\n", encoding="utf-8"
    )

    # determination_view.html
    # Negative-case companion bindings (asserted_dispositions /
    # asserted_prescribed_processes / system_comment) were read above so
    # the same data backs both evidence.json and the HTML view.
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
        primary_arco_classes=primary_arco_classes,
        gate_evidence=gate_evidence,
        derogation_flagged=derogation_flagged,
        fraud_flagged=fraud_flagged,
        asserted_dispositions=asserted_dispositions,
        asserted_prescribed_processes=asserted_prescribed_processes,
        system_comment=system_comment,
    )

    # shacl_report.txt
    shacl_out = f"conforms: {shacl_ok}\n"
    if shacl_report_text:
        shacl_out += "\n" + shacl_report_text
    (OUTPUT_DIR / "shacl_report.txt").write_text(shacl_out, encoding="utf-8")

    sub("OUTPUT FILES")
    for f in sorted(OUTPUT_DIR.iterdir()):
        print(f"  {f.relative_to(REPO_ROOT)}")

    # Exit semantics: pipeline-ran-cleanly is what the exit code reflects.
    # A non-applicable system has classification_pass True and audit checks
    # (designed for triggered systems) may legitimately fail. That is expected
    # behaviour, not a pipeline failure. Exit 1 only on classification-layer
    # failures (SHACL validation, reasoner error, missing triples).
    if not classification_pass:
        sys.exit(1)


if __name__ == "__main__":
    main()
