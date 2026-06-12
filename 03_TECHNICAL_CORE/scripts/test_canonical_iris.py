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
"""

from __future__ import annotations

import sys
from pathlib import Path

from rdflib import Graph, URIRef
from rdflib.util import guess_format

REPO_ROOT = Path(__file__).resolve().parents[2]
ONT = REPO_ROOT / "03_TECHNICAL_CORE" / "ontology"
IMPORTS = ONT / "imports"
SEEDS = IMPORTS / "seeds"

# ARCO-authored TTL (NOT the upstream slim modules, which are trusted as-is).
AUTHORED = [
    ONT / "ARCO_core.ttl",
    ONT / "ARCO_governance_extension.ttl",
] + sorted(ONT.glob("ARCO_instances_*.ttl"))

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
    for sf in sorted(SEEDS.glob("*.txt")):
        for line in sf.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                known.add(line)
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


def main() -> None:
    known = load_known()
    print(f"[iri] pinned external IRIs known from imports + seeds: {len(known)}")

    violations: list[tuple[str, str, str]] = []
    for path in AUTHORED:
        if not path.exists():
            continue
        for u in sorted(external_iris(path)):
            if CCO_V2_MARK in u:
                violations.append((path.name, u, "CCO v2.0 numbered IRI (ARCO is pinned to CCO v1.7 readable IRIs)"))
            elif u not in known:
                violations.append((path.name, u, "not present in any pinned import module or seed (drift / typo / unseeded term)"))

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

    print("PASS: every external IRI in ARCO authored TTL is a pinned-canonical IRI.")


if __name__ == "__main__":
    main()
