"""
Canonical-IRI conformance test (version-pin enforcement).

Enforces the exact-IRI discipline standard in OBO Foundry / ODK practice:
every external (BFO / RO / IAO / CCO) IRI used in ARCO's *authored* TTL
must be a pinned-canonical IRI present in the imported slim / ontology modules,
in the version-correct namespace.

Catches two drift modes the CLAUDE.md "IRI / version-pin verification" rule
warns about:
  1. CCO v2.0 numbered IRIs (commoncoreontologies.org/ont...) when ARCO is
     pinned to CCO v1.7 readable IRIs.
  2. Any external IRI that does not resolve to the pinned import modules
     (a typo, a wrong-version IRI, or a term referenced before it was added to
     the seed and the slim module regenerated).

This is the version-pinning invariant made into a CI gate. It does not touch
classification logic, OWL/SHACL/SPARQL semantics, or any axiom; it only reads.

COVERAGE, widened 2026-07-27
----------------------------
This test previously named its inputs by hand: two files plus an
`ARCO_instances_*.ttl` glob. On 2026-07-27 a probe fixture under
`ontology/probes/` asserted `bfo:0000052`, which expands to `BFO_0000052` and
appears nowhere in the pinned imports (BFO 2020's inheres-in is `BFO_0000197`;
`0000052` is RO's number). This test passed, because the probe directory was not
in the list. The bad IRI reached a published disclosure as quoted evidence.

An undeclared property is legal RDF with no domain, so no reasoner objects and
every domain rule that should have fired simply does not. A hand-maintained
input list is therefore the worst possible shape for this check: it fails silent
and it stops covering the repo the moment anyone adds a file.

So inputs are now enumerated BY PATTERN with exclusions stated explicitly, and
SPARQL is covered too, because a wrong IRI in a query matches nothing and returns
a clean negative that is indistinguishable from a real one.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from rdflib import Graph, URIRef
from rdflib.util import guess_format

REPO_ROOT = Path(__file__).resolve().parents[2]
TECH = REPO_ROOT / "03_TECHNICAL_CORE"
ONT = TECH / "ontology"
IMPORTS = ONT / "imports"
SEEDS = IMPORTS / "seeds"


def authored_files() -> list[Path]:
    """Every ARCO-authored artifact that can carry an external IRI.

    Enumerated by pattern so a new file is covered the day it is added. The only
    exclusion is `imports/`, which holds the upstream slim modules that define
    the canonical IRIs and are trusted as-is. See COVERAGE in the module
    docstring for why the previous hand-maintained list was unsafe.

    Python and YAML are included because IRIs live there too: a census on
    2026-07-27 found 47 across nine scripts and 10 in the output manifest, all
    unchecked. A typo there fails the same silent way, and in Python it is worse,
    since an IRI used to build a query or a comparison simply never matches and
    the run reports a clean negative.
    """
    files = [p for p in sorted(ONT.rglob("*.ttl")) if IMPORTS not in p.parents]
    files += sorted((TECH / "validation").rglob("*.ttl"))
    files += sorted((TECH / "reasoning").rglob("*.sparql"))
    files += sorted((TECH / "scripts").rglob("*.py"))
    files += sorted((TECH / "scripts").rglob("*.yaml"))
    files += sorted((TECH / "scripts").rglob("*.yml"))
    return files


def python_external_iris(path: Path) -> set[str]:
    """External IRIs in Python STRING LITERALS, excluding docstrings.

    Docstrings are excluded deliberately: this repo's checks document the exact
    bad IRIs they exist to catch (`bfo:0000052`, the 2026-07-27 chimera), and
    flagging a file for explaining a defect would make the check unusable and
    push people to delete the explanation. Only literals that could actually
    reach a query, a comparison or a graph are checked.
    """
    import ast

    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except SyntaxError:
        return set()
    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", None)
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
                if isinstance(body[0].value.value, str):
                    docstrings.add(id(body[0].value))
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docstrings:
            out |= iris_in_text(node.value)
    return {u for u in out if _is_external(u)}


def iris_in_text(txt: str) -> set[str]:
    """Full IRIs plus prefixed names expanded through ARCO's standard bindings.

    Namespace BASES are excluded. A string like "http://purl.obolibrary.org/obo/BFO_"
    is a prefix binding used to build IRIs, not an IRI, and flagging it produced 26
    false positives on the first run of this widened check.
    """
    out = set()
    for m in re.finditer(r"<?(https?://[^\s\"'<>)\],]+)>?", txt):
        u = m.group(1)
        if u.endswith("_") or u.endswith("/") or u.endswith("#"):
            continue  # namespace base, not a term
        out.add(u)
    for m in re.finditer(r"\b(bfo|ro|iao|cco):([A-Za-z0-9_]+)\b", txt):
        out.add(PREFIXES[m.group(1)] + m.group(2))
    return out




def yaml_external_iris(path: Path) -> set[str]:
    txt = path.read_text(encoding="utf-8", errors="ignore")
    txt = re.sub(r"#[^\n]*", "", txt)  # comments cannot affect the contract
    return {u for u in iris_in_text(txt) if _is_external(u)}

# Pinned import modules = source of truth for which external IRIs exist.
IMPORT_MODULES = [
    IMPORTS / "bfo-2020.owl",
    IMPORTS / "ro_bot.owl",
    IMPORTS / "iao_bot.owl",
    IMPORTS / "cco_bot.owl",
]

CCO_V17 = "http://www.ontologyrepository.com/CommonCoreOntologies/"
CCO_V2_MARK = "commoncoreontologies.org"   # the v2.0 numbered namespace
OBO = "http://purl.obolibrary.org/obo/"     # BFO_/RO_/IAO_ and other obo terms

# Prefix bindings ARCO uses, for expanding prefixed names in files that carry no
# @prefix header of their own (Python, YAML). Defined after the namespace
# constants because this dict is evaluated at import time, unlike function bodies.
PREFIXES = {
    "bfo": OBO + "BFO_",
    "ro": OBO + "RO_",
    "iao": OBO + "IAO_",
    "cco": CCO_V17,
}

# OBO term locals are seven digits at every version ARCO pins. A prefixed name
# like `bfo:has_part` LOOKS usable and expands to a term that exists nowhere, so
# a reader who copies it into a query gets a clean empty result. Reported with
# its own reason rather than lumped in with unseeded terms.
MALFORMED_OBO = re.compile(r"^" + re.escape(OBO) + r"(?:BFO|RO|IAO)_(?!\d{7}$)")


def _is_external(u: str) -> bool:
    return u.startswith(CCO_V17) or u.startswith(OBO) or (CCO_V2_MARK in u)


def load_known() -> set[str]:
    """All external IRIs that exist in the pinned imports, plus the seed lists."""
    known: set[str] = set()
    for m in IMPORT_MODULES:
        if not m.exists():
            print(f"[iri] WARN: import module missing: {m}")
            continue
        g = Graph()
        try:
            g.parse(str(m), format=guess_format(str(m)) or "xml")
        except Exception as exc:  # noqa: BLE001 - report and fall back to seeds
            print(f"[iri] WARN: could not parse {m.name} ({exc}); relying on seeds for its namespace")
            continue
        for s, p, o in g:
            for t in (s, p, o):
                if isinstance(t, URIRef):
                    known.add(str(t))
    # Seeds widen the trusted set, so an unresolvable seed entry AUTHORIZES ITSELF
    # and every use of it. Validate the whitelist against the modules before
    # trusting it. Clean at 19/19 on 2026-07-27; the gate is that it stays clean.
    from_modules = set(known)
    bad_seeds: list[tuple[str, str]] = []
    for sf in sorted(SEEDS.glob("*.txt")):
        for line in sf.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                if line not in from_modules:
                    bad_seeds.append((sf.name, line))
                known.add(line)
    if bad_seeds:
        print(f"\nFAIL: {len(bad_seeds)} seed entr(ies) resolve to no pinned module:")
        for fn, u in bad_seeds:
            print(f"  [seeds/{fn}] {u}\n      -> a seed that does not exist upstream whitelists a non-existent IRI")
        sys.exit(1)
    return known


def external_iris(path: Path) -> set[str]:
    g = Graph()
    g.parse(str(path), format="turtle")
    out: set[str] = set()
    for s, p, o in g:
        for t in (s, p, o):
            if isinstance(t, URIRef) and _is_external(str(t)):
                out.add(str(t))
    return out


def sparql_external_iris(path: Path) -> set[str]:
    """External IRIs in a query, expanded through the query's own PREFIX lines.

    Comments are stripped first: they cannot affect query semantics, and prose
    inside one is the other checks' business, not this one's.
    """
    txt = path.read_text(encoding="utf-8", errors="ignore")
    prefixes = dict(re.findall(r"(?im)^\s*PREFIX\s+(\S*):\s*<([^>]+)>", txt))
    body = re.sub(r"#[^\n]*", "", re.sub(r"(?im)^\s*PREFIX\s+.*$", "", txt))
    out = {m.group(1) for m in re.finditer(r"<(https?://[^>]+)>", body)}
    for m in re.finditer(r"\b([A-Za-z][\w.-]*)?:([A-Za-z0-9_][\w.-]*)", body):
        base = prefixes.get(m.group(1) or "")
        if base:
            out.add(base + m.group(2))
    return {u for u in out if _is_external(u)}


def main() -> None:
    known = load_known()
    print(f"[iri] pinned external IRIs known from imports + seeds: {len(known)}")

    files = authored_files()
    violations: list[tuple[str, str, str]] = []
    for path in files:
        if not path.exists():
            continue
        reader = {
            ".sparql": sparql_external_iris,
            ".py": python_external_iris,
            ".yaml": yaml_external_iris,
            ".yml": yaml_external_iris,
        }.get(path.suffix, external_iris)
        rel = path.relative_to(REPO_ROOT).as_posix()
        for u in sorted(reader(path)):
            if MALFORMED_OBO.match(u):
                violations.append((rel, u,
                    "malformed OBO reference: locals are seven digits at ARCO's pinned versions, "
                    "so this expands to a term that exists nowhere and any query using it returns empty"))
            elif CCO_V2_MARK in u:
                violations.append((rel, u, "CCO v2.0 numbered IRI (ARCO is pinned to CCO v1.7 readable IRIs)"))
            elif u not in known:
                violations.append((rel, u, "not present in any pinned import module or seed (drift / typo / unseeded term)"))

    if violations:
        print(f"\nFAIL: {len(violations)} non-canonical external IRI(s):")
        for fn, u, why in violations:
            print(f"  [{fn}] {u}\n      -> {why}")
        print(
            "\nFix: use the exact pinned IRI from the slim module, or add the term to the "
            "matching seed (imports/seeds/*.txt) and regenerate the slim module via ROBOT BOT "
            "before referencing it. (CLAUDE.md: IRI / version-pin verification.)"
        )
        sys.exit(1)

    # The file count is printed on success on purpose: a coverage regression
    # (a directory that stops being enumerated) shows up as a falling number
    # rather than as a silent PASS.
    print(
        f"PASS: every external IRI in {len(files)} authored file(s) "
        f"(ontology, probes, validation, reasoning) is a pinned-canonical IRI."
    )


if __name__ == "__main__":
    main()
