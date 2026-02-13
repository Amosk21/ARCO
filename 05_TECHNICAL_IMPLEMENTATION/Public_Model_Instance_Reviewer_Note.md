# ARCO Reviewer Note: Public-Model Instance Pattern (Option B)

**Scope:** Claude-style public system instance modeling  
**Status:** Implemented and validated in current branch  
**Date:** February 12, 2026

---

## Why this note exists

The goal was to pressure-test ARCO on something real, not just a clean engineered demo.  
Claude provides that test: high visibility, strong documentation footprint, and imperfect evidence boundaries.

This note captures the pattern used to stay practical and strict at the same time.

---

## Working position for this pattern

1. **Reality-side commitments stay minimal and evidence-bounded.**  
   Capability dispositions are asserted on material infrastructure only when documentation supports them.

2. **Representation-side artifacts do not force classification.**  
   Model cards, addenda, refusal reports, and policy text remain ICE/documentation artifacts.

3. **No capability-by-assumption.**  
   Generic vision, benchmark wins, or refusal language do not become biometric identification capability.

4. **Regulatory class remains entailment-first.**  
   Annex III 1(a) applies only when all three gates are present (capability + intended use + scenario).

---

## What was asserted for Claude

### Asserted (evidence-bounded)
- Text generation capability disposition
- Static image understanding capability disposition
- Computer-use capability disposition (screenshot-mediated)

### Explicitly not asserted
- Biometric identification capability
- Annex III 1(a) applicability
- Any critical-infrastructure-specific control capability

### Refusal handling
- "Refusal to identify people in images" is modeled as documentation/control evidence, not as proof of biometric capability.

---

## Why this stays BFO-aligned

- Dispositions inhere in material bearers, not in software artifacts.
- Software artifacts remain ICEs linked through aboutness/documentation.
- Institutional/regulatory determinations are outputs of governed reasoning, not ontology shortcuts.

---

## Verification outcome (current run)

- Sentinel high-risk: **True**
- Sentinel Annex III 1(a): **True**
- Claude high-risk: **False**
- Claude Annex III 1(a): **False**
- Claude refusal documentation present: **True**

This is the expected separation: engineered positive case remains positive; evidence-constrained public-model case remains honest and non-overclaimed.

---

## Reviewer takeaway

ARCO can model a real public system without inflating claims.  
That is a meaningful assurance signal: the framework is useful when evidence is messy, not only when examples are idealized.
