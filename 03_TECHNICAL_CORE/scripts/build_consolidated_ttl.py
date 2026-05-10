"""
Build a single consolidated TTL by merging ARCO's modular sources.

Default merge set (ontology only):
  imports/bfo-2020.owl
  imports/ro_bot.owl
  imports/iao_bot.owl
  imports/cco_bot.owl
  ARCO_core.ttl
  ARCO_governance_extension.ttl

Optional includes:
  --shacl                   include 03_TECHNICAL_CORE/validation/*.ttl
  --instances <file|name>   include an instance fixture (relative or bare name)
  --output <path>           override default output path

Output is a build artifact, not a source file. Default destination is under
runs/build/ which is gitignored. The output is suitable for upload to external
linters (GRL Workshop linter, ROBOT report, OOPS!) or for one-file review.

SPARQL queries are NOT bundled into the output. SPARQL is a separate query
layer, not an ontology serialization. Two paths if you want SPARQL alongside:
  (1) wrap the queries as sh:SPARQLConstraint nodes in a SHACL shape file and
      include that file via --shacl,
  (2) run the audit queries against the loaded graph at pipeline runtime.

Usage:
  python 03_TECHNICAL_CORE/scripts/build_consolidated_ttl.py
  python 03_TECHNICAL_CORE/scripts/build_consolidated_ttl.py --shacl
  python 03_TECHNICAL_CORE/scripts/build_consolidated_ttl.py \\
      --instances ARCO_instances_sentinel.ttl --shacl
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rdflib import Graph

REPO_ROOT = Path(__file__).resolve().parents[2]
ONTOLOGY_DIR = REPO_ROOT / "03_TECHNICAL_CORE" / "ontology"
VALIDATION_DIR = REPO_ROOT / "03_TECHNICAL_CORE" / "validation"

ONTOLOGY_INPUTS = [
    ONTOLOGY_DIR / "imports" / "bfo-2020.owl",
    ONTOLOGY_DIR / "imports" / "ro_bot.owl",
    ONTOLOGY_DIR / "imports" / "iao_bot.owl",
    ONTOLOGY_DIR / "imports" / "cco_bot.owl",
    ONTOLOGY_DIR / "ARCO_core.ttl",
    ONTOLOGY_DIR / "ARCO_governance_extension.ttl",
]


def _shacl_inputs() -> list[Path]:
    return sorted(VALIDATION_DIR.glob("*.ttl"))


def _resolve_instances(arg: str) -> Path:
    p = Path(arg)
    if p.is_absolute() and p.exists():
        return p
    candidate_repo = REPO_ROOT / arg
    if candidate_repo.exists():
        return candidate_repo
    candidate_ontology = ONTOLOGY_DIR / p.name
    if candidate_ontology.exists():
        return candidate_ontology
    return candidate_repo  # nonexistent; caller surfaces the error


def parse_into(g: Graph, path: Path) -> int:
    """Parse a file into the graph; return triples added."""
    if not path.exists():
        raise FileNotFoundError(f"Missing input: {path}")
    fmt = "xml" if path.suffix == ".owl" else "turtle"
    before = len(g)
    g.parse(path.as_posix(), format=fmt)
    return len(g) - before


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--shacl", action="store_true",
                    help="Include SHACL shapes from 03_TECHNICAL_CORE/validation/.")
    ap.add_argument("--instances", default=None,
                    help="Optional instance fixture filename or path.")
    ap.add_argument("--output", default=None,
                    help="Output path. Default: runs/build/arco_full[suffix].ttl")
    args = ap.parse_args()

    g = Graph()

    print("=" * 72)
    print("ARCO consolidated TTL build")
    print("=" * 72)

    print("\nOntology inputs:")
    for path in ONTOLOGY_INPUTS:
        added = parse_into(g, path)
        print(f"  {path.relative_to(REPO_ROOT)}: +{added} triples")

    suffix_parts: list[str] = []

    if args.shacl:
        print("\nSHACL inputs:")
        for path in _shacl_inputs():
            added = parse_into(g, path)
            print(f"  {path.relative_to(REPO_ROOT)}: +{added} triples")
        suffix_parts.append("with_shapes")

    if args.instances:
        path = _resolve_instances(args.instances)
        added = parse_into(g, path)
        print(f"\nInstance fixture: {path.relative_to(REPO_ROOT)}: +{added} triples")
        suffix_parts.append(path.stem.replace("ARCO_instances_", ""))

    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = REPO_ROOT / args.output
    else:
        suffix = "_" + "_".join(suffix_parts) if suffix_parts else ""
        output_path = REPO_ROOT / "runs" / "build" / f"arco_full{suffix}.ttl"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    g.serialize(destination=str(output_path), format="turtle")

    print(f"\nMerged graph: {len(g)} triples")
    print(f"Output: {output_path.relative_to(REPO_ROOT)}")
    print(f"Size: {output_path.stat().st_size / 1024:.1f} KB")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())
