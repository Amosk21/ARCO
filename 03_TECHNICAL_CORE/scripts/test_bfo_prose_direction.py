#!/usr/bin/env python3
"""Catch BFO relation IRIs cited in prose with the wrong direction word.

WHY THIS EXISTS
---------------
On 2026-07-27 an audit found `README.md` and `ARCO_core.ttl` both saying "the
hardware concretizes the software" while citing `bfo:0000058`. Two errors in one
clause. `BFO_0000058` is "is concretized by" (domain: generically dependent
continuant), and its inverse `BFO_0000059` "concretizes" has domain process or
specifically dependent continuant, so a material entity can never be the subject
of "concretizes" under BFO 2020's own axioms.

No reasoner could catch it. ARCO asserts ZERO concretization triples, so there
was nothing to reason over. The defect lived entirely in an rdfs:comment and in
prose describing the model, which is exactly the class Neuhaus (arXiv:1810.09171
section 4.2) names as undetectable by a reasoner: documentation and axioms each
internally consistent and jointly contradictory.

So this is a prose-versus-axiom check, and it is the only kind that could have
caught it. It reads the PINNED BFO file for ground truth rather than hardcoding
labels, so it cannot drift from the ontology it validates.

WHAT IT CHECKS
--------------
For every BFO object-property IRI mentioned in a scanned file, if the surrounding
sentence uses the label of a DIFFERENT BFO property whose IRI is not also cited,
that is a direction mismatch and it fails.

Exit 0 clean, 1 on findings. Run: python 03_TECHNICAL_CORE/scripts/test_bfo_prose_direction.py
"""
import os, re, sys, glob

import rdflib
from rdflib.namespace import OWL, RDFS

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BFO = os.path.join(ROOT, "03_TECHNICAL_CORE", "ontology", "imports", "bfo-2020.owl")
OBO = "http://purl.obolibrary.org/obo/"

SCAN = [
    "README.md",
    "LIMITATIONS.md",
    "docs/**/*.md",
    "03_TECHNICAL_CORE/ontology/*.ttl",
]
# Generated output and vendored upstreams are not authored prose.
SKIP = ("runs/", "imports/", "node_modules", ".venv", "_archive")

def bfo_facts():
    """(labels, inverse pairs) parsed from the pinned BFO file. Ground truth.

    PARSED, not regexed. An earlier version matched `<owl:ObjectProperty>` blocks
    with a regex and hardcoded the inverse map as a two-entry literal, under a
    comment claiming it was "populated from the pinned file at runtime." It was
    not. BFO 2020 declares SEVENTEEN owl:inverseOf pairs, so fifteen of them,
    including `realizes`/`has realization` and `inheres in`/`bearer of` which are
    ARCO's load-bearing relations, had no direction protection whatsoever.
    A comment asserting a mechanism that does not exist is worse than no comment.
    """
    g = rdflib.Graph()
    g.parse(BFO)
    labels = {
        str(s).replace(OBO, ""): str(o).strip().lower()
        for s, o in g.subject_objects(RDFS.label)
        if isinstance(s, rdflib.URIRef) and str(s).startswith(OBO + "BFO_")
    }
    inverse = {}
    for a, b in g.subject_objects(OWL.inverseOf):
        if isinstance(a, rdflib.URIRef) and isinstance(b, rdflib.URIRef):
            ka, kb = str(a).replace(OBO, ""), str(b).replace(OBO, "")
            inverse[ka], inverse[kb] = kb, ka
    return labels, inverse


def verb_forms(label):
    """Surface forms a writer would actually type for a BFO label."""
    l = label.lower()
    forms = {l, l.replace(" ", "_"), l.replace(" ", "-")}
    # "is concretized by" -> also match "concretized by"
    if l.startswith("is "):
        forms.add(l[3:])
        forms.add(l[3:].replace(" ", "_"))
    return {f for f in forms if len(f) > 5}


def scan_file(path, labels, inverse, exempt):
    rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
    if any(s in rel for s in SKIP):
        return []
    try:
        text = open(path, encoding="utf-8", errors="ignore").read()
    except OSError:
        return []
    hits = []
    for i, line in enumerate(text.splitlines(), 1):
        # Case-insensitive: prose writes `bfo:0000058`, the OWL file writes BFO_0000058.
        # The first version of this check was case-sensitive and therefore matched nothing
        # in the very documents it exists to police. Caught by its own backtest.
        cited = set(re.findall(r"BFO[_:]?(\d{7})", line, re.I))
        cited = {f"BFO_{c}" for c in cited}
        if not cited:
            continue
        # Drop glosses attached to NON-BFO IRIs before matching. RO, IAO and CCO
        # carry properties whose labels collide with BFO's, so the documentation
        # pattern `ro:0000053` (bearer_of) is a CORRECT citation of RO's own
        # property, not a BFO direction error. Without this the check fires on
        # value_chain.md:144, which is right, and calls it a mismatch.
        low = re.sub(
            r"`?\b(?:ro|iao|cco|skos|rdfs|owl|obo)[:_]\S*?`?\s*\([^)]*\)",
            " ", line, flags=re.I,
        ).lower()
        for iri in cited:
            other = inverse.get(iri)
            if not other:
                continue
            if other in cited:
                # Both cited: the sentence may legitimately contrast the pair, and
                # no regex distinguishes a real contrast from a wrong verb sitting
                # next to the wrong IRI. This is a REAL BLIND SPOT, so it is counted
                # and reported rather than passed over in silence. ARCO_core.ttl:208,
                # the line this check was written for, now lives inside it.
                exempt.append((rel, i, iri, other))
                continue
            other_label = labels.get(other)
            this_label = labels.get(iri)
            if not other_label or not this_label:
                continue
            for form in verb_forms(other_label):
                # The other property's verb appears while its IRI does not.
                # NOTE: an earlier version also exempted lines where THIS
                # property's own label appeared, on the theory that the sentence
                # was contrasting the pair deliberately. That exemption made the
                # check useless: the 2026-07-27 defect wrote "the hardware
                # concretizes the software (`bfo:0000058 is_concretized_by`)",
                # so the cited label sat in the code span while the wrong verb
                # sat in the prose, and the check skipped it. Only a second IRI
                # citation counts as a deliberate contrast, handled above.
                if re.search(rf"\b{re.escape(form)}\b", low):
                    hits.append((rel, i, iri, this_label, other, other_label, line.strip()[:150]))
                    break
    return hits


def main():
    # The scanned files are UTF-8 prose (arrows, dashes, curly quotes) while the
    # default Windows console codec is cp1252. Without this, the check CRASHES
    # mid-report on the first such character and prints nothing further, which
    # loses findings it already made. Reconfigure before any output.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass
    if not os.path.exists(BFO):
        # FAIL CLOSED. An earlier version returned 0 here, so a missing or renamed
        # pin turned the whole check into a silent pass, which is the failure mode
        # this file exists to prevent.
        print(f"FAIL: pinned BFO file not found at {BFO}; cannot verify directions.")
        return 1
    labels, inverse = bfo_facts()
    if not labels or not inverse:
        print("FAIL: could not read BFO labels or inverse pairs from the pinned file")
        return 1

    files = []
    for pat in SCAN:
        files.extend(glob.glob(os.path.join(ROOT, pat), recursive=True))

    findings, exempt = [], []
    for f in sorted(set(files)):
        findings.extend(scan_file(f, labels, inverse, exempt))

    print(f"BFO prose-direction check: {len(labels)} labels and "
          f"{len(inverse) // 2} inverse pairs from the pinned file, "
          f"{len(set(files))} files scanned.")
    if not findings:
        print("PASS: no BFO relation cited with a conflicting direction word.")
        print(f"  BLIND SPOT, reported not hidden: {len(exempt)} line(s) cite both halves")
        print("  of an inverse pair and are exempt, because no regex separates a deliberate")
        print("  contrast from a wrong verb beside the wrong IRI. Those lines are checked")
        print("  by a human or not at all:")
        for rel, ln, a, b in exempt:
            print(f"    {rel}:{ln}  ({a} + {b})")
        print("  ALSO NOT checked: relations named in prose with no IRI cited, domain and")
        print("  range violations where no IRI appears, and claims outside the BFO namespace.")
        return 0

    print(f"\nFAIL: {len(findings)} direction mismatch(es).\n")
    for rel, ln, iri, this_lab, other, other_lab, excerpt in findings:
        print(f"  {rel}:{ln}")
        print(f"    cites {iri} ('{this_lab}') but the sentence uses '{other_lab}', which is {other}")
        print(f"    ...{excerpt}...")
        print(f"    FIX: use the label matching the IRI you cited, or cite {other} instead.\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
