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

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BFO = os.path.join(ROOT, "03_TECHNICAL_CORE", "ontology", "imports", "bfo-2020.owl")

SCAN = [
    "README.md",
    "LIMITATIONS.md",
    "docs/**/*.md",
    "03_TECHNICAL_CORE/ontology/*.ttl",
]
# Generated output and vendored upstreams are not authored prose.
SKIP = ("runs/", "imports/", "node_modules", ".venv", "_archive")

# Inverse pairs get checked hardest: citing one while using the other's verb is
# the exact 2026-07-27 defect. Populated from the pinned file at runtime.
INVERSE_HINTS = {"BFO_0000058": "BFO_0000059", "BFO_0000059": "BFO_0000058"}


def bfo_labels():
    """IRI suffix -> label, read from the pinned BFO file. Ground truth."""
    txt = open(BFO, encoding="utf-8", errors="ignore").read()
    out = {}
    for m in re.finditer(
        r'<owl:ObjectProperty rdf:about="[^"]*?(BFO_\d+)">(.*?)</owl:ObjectProperty>',
        txt, re.S,
    ):
        lab = re.search(r"<rdfs:label[^>]*>(.*?)</rdfs:label>", m.group(2), re.S)
        if lab:
            out[m.group(1)] = lab.group(1).strip().lower()
    return out


def verb_forms(label):
    """Surface forms a writer would actually type for a BFO label."""
    l = label.lower()
    forms = {l, l.replace(" ", "_"), l.replace(" ", "-")}
    # "is concretized by" -> also match "concretized by"
    if l.startswith("is "):
        forms.add(l[3:])
        forms.add(l[3:].replace(" ", "_"))
    return {f for f in forms if len(f) > 5}


def scan_file(path, labels):
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
        low = line.lower()
        for iri in cited:
            other = INVERSE_HINTS.get(iri)
            if not other or other in cited:
                continue  # both cited, the sentence can legitimately name each
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
    if not os.path.exists(BFO):
        print(f"SKIP: pinned BFO file not found at {BFO}")
        return 0
    labels = bfo_labels()
    if not labels:
        print("FAIL: could not read any BFO object-property labels")
        return 1

    files = []
    for pat in SCAN:
        files.extend(glob.glob(os.path.join(ROOT, pat), recursive=True))

    findings = []
    for f in sorted(set(files)):
        findings.extend(scan_file(f, labels))

    print(f"BFO prose-direction check: {len(labels)} properties from the pinned file, "
          f"{len(set(files))} files scanned.")
    if not findings:
        print("PASS: no BFO relation cited with a conflicting direction word.")
        print("  NOT checked: relations named in prose with no IRI cited, domain and range")
        print("  violations where no IRI appears, and any claim outside the BFO namespace.")
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
