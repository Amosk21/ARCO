# ARCO Extension Protocol

Every new Annex III category added to ARCO must pass through this protocol in order.
No step may be skipped. No TTL is written until Steps 1–4 are complete on paper.

---

## Step 0 — ROI Gate (human decision, before protocol starts)

Answer all three before invoking the protocol. If any answer is weak, do not proceed.

1. What criticism does this extension remove?
2. What architectural capability does it prove that Sentinel alone does not?
3. What future path does it open?

This is a project management gate, not an engineering step. It belongs to the human, not the AI.

---

## Step 1 — Legal Decomposition (Document A)

Rewrite the target Annex III clause into explicit logical parts. Do not begin modeling until this is written.

| Field | Content |
|-------|---------|
| Clause reference | e.g., Annex III §1(a) |
| Exact legal trigger text | verbatim from the regulation |
| Capability involved | what the system must be able to do |
| Process involved | what type of process must be prescribed |
| Subject/role involved | who the system acts on or in relation to |
| Deployment/use context | sector, setting, or condition required |
| Exclusions and derogations | what explicitly does not trigger this clause |
| What is positive-path for v1 | the minimal case that must classify correctly |
| What is explicitly deferred | edge cases, exclusions, or conditions not modeled yet |

Deferred items must be listed. "None deferred" is a claim that requires justification.

---

## Step 2 — Ontology Mapping (Document B)

Only after Document A is complete. Map each logical part to ARCO's existing architecture.

For each element from Document A:

| Legal element | BFO/CCO class family | Relation (RO/IAO/CCO IRI) | Existing ARCO class (or NEW) | Gate type if applicable |
|--------------|---------------------|--------------------------|------------------------------|------------------------|
| capability | Disposition | ro:0000091 has_disposition | existing or new subclass | Gate 1 (existential) |
| process | Process | cco:prescribes | existing or new subclass | Gate 2 (someValuesFrom) |
| subject/role | Role | ro:0000087 has_role | existing or new | Gate 3 (hasValue universal) |

Gate type must be stated explicitly:
- **Existential** — `owl:someValuesFrom` on a class
- **Value** — `owl:hasValue` on a named individual (universal)
- **Class** — subclass relationship only

---

## Step 3 — Reuse-First Audit

Before declaring any new class, answer each question in writing:

1. Does this already exist in BFO, CCO, IAO, or RO?
2. Does ARCO already have a reusable class for this?
3. Can this be represented by subclassing rather than a new pattern?
4. Is this a genuine domain universal (mind-independent natural kind) or only a regulatory grouping?

If the answer to (4) is "regulatory grouping," the class belongs in `ARCO_governance_extension.ttl`, not `ARCO_core.ttl`.

No new class is added until this audit is written down.

---

## Step 4 — Design Memo

One page. Exactly these sections. If you cannot write it clearly, the extension is not ready.

```
Category: [Annex III clause reference and name]
Legal target: [one sentence statement of what the clause covers]

Positive-path claim:
  [A system with X capability, prescribed for Y process, acting on Z role, must be entailed as AnnexIII[N]ApplicableSystem.]

Deferred edge cases:
  [List every exclusion or condition not modeled in this version. "None" requires justification.]

New classes:
  [IRI, BFO parent, rationale for new class vs reuse]

Reused classes:
  [IRI, existing file]

New individuals/examples:
  [IRI, type, purpose]

Expected entailments:
  [What the reasoner must derive for the positive case]

Expected non-entailments:
  [What the reasoner must NOT derive — the designed negative cases]

Regression risk to Sentinel:
  [Explicit statement of whether this touches Sentinel's inference chain and how]

Debt annotations:
  [Any compromise made in this version — collapsed disjunction, hasValue punning, hardcoded IRI, deferred exclusion — logged here with rationale]

Public claim allowed after merge:
  [Exact scoped statement that may be made about this category after merge. No stronger claim is permitted.]
```

---

## Step 5 — Negative-Case Design

Before writing a single triple, specify all four:

1. **Positive case** — a system that must be entailed as applicable
2. **Missing-capability case** — a system without the triggering capability that must not be entailed
3. **Wrong-process-type case** — a system with the right capability but a prescribed process of the wrong type
4. **Wrong-role-type case** — a system with the right capability and process but the wrong subject/role
5. **Broken-documentation case** — a system missing a required documentary artifact (for SHACL, not OWL)

Cases 1–4 are OWL entailment tests. Case 5 is a SHACL validation test. They are different checks; do not conflate them.

---

## Step 6 — Two-Phase Implementation

Never mix architecture work and category addition in one commit batch.

**Phase A — Architecture/prep only**
- Move classes between files if needed
- Clean bridge axioms and comments
- No new category content

Run after Phase A:
- `python 03_TECHNICAL_CORE/scripts/run_pipeline.py` — must print ALL CHECKS PASSED
- Confirm Sentinel inference is unchanged

**Phase B — Category addition only**
- New capability subclass
- New process subclass (if needed)
- New applicable system equivalentClass
- New instance file with positive and negative examples
- New entailment query

Run after Phase B:
- `python 03_TECHNICAL_CORE/scripts/run_pipeline.py` — must print ALL CHECKS PASSED
- Positive case is entailed
- All four designed negative cases are not entailed
- Sentinel inference is unchanged

Phase A and Phase B are separate commits.

---

## Step 7 — Acceptance Checklist

A category merges only when all of these are true. No exceptions.

- [ ] Sentinel still passes unchanged
- [ ] Positive case is entailed by OWL-RL
- [ ] All four designed negative cases are not entailed
- [ ] No SPARQL audit query is doing work that belongs to OWL classification
- [ ] No new custom object properties (BFO/RO/IAO/CCO relations only)
- [ ] All new classes have `rdfs:comment` with BFO/CCO rationale
- [ ] New classes in core (`ARCO_core.ttl`) are genuine domain universals; regulatory groupings are in governance extension
- [ ] Deferred exclusions are explicitly listed in the Design Memo
- [ ] Debt annotations are written inline on the affected triples (see below)
- [ ] Public claim is written in the Design Memo and is scoped correctly
- [ ] Pipeline exits 0 from clean state

---

## Debt Annotation Format

Do not maintain a separate ledger file. Annotate debt inline on the affected triple or class using `rdfs:comment`.

Format:
```turtle
:SomeClass rdfs:comment """DEBT(v1): [description of compromise]. Rationale: [why accepted].
Deferred: [what a future version must resolve].""" .
```

Examples of debt that must be annotated:
- `owl:hasValue` on a named individual used as a universal (punning)
- Collapsed disjunction (two legally distinct things merged into one class for v1)
- Deferred exclusion not yet modeled
- Hardcoded system IRI that should be parameterized
- Single-system pipeline artifact naming

Debt that is not annotated is treated as a hidden inconsistency, not an accepted compromise.

---

## What This Protocol Is Not

- It is not a prompt to paste into a chat window. It is a permanent engineering standard that lives in this repo and is read by any AI assistant working on ARCO.
- It does not replace the Global Invariants in CLAUDE.md. Those are hard constraints. This protocol is the procedure for controlled expansion within those constraints.
- It does not apply to bug fixes, pipeline changes, or documentation edits. It applies only to new Annex III category additions.
