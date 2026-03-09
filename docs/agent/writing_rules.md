# Writing Rules — Outward-Facing Documents

Governs: `README.md`, `BRIEF.md`, `01_COMMERCIAL/*.md`, `02_SYSTEM_OVERVIEW/*.md`

## Tone Sequence

Technical precision first, business translation second. Always in this order:

1. State the mechanism accurately — what the system actually does, in formal terms
2. Translate to business implication — what that means for the reader's decision
3. Do not reverse this order. Business framing that obscures technical accuracy is worse than no framing.

The existing README and BRIEF.md demonstrate the target: they open with what the system produces formally, then move to economic/governance consequences.

## Invariants for All Outward-Facing Docs

- ARCO produces **determinations**, not scores, not confidence levels, not advisory opinions
- ARCO uses **formal logic** for classification. "AI" is appropriate only for systems being *classified by* ARCO, not for ARCO itself
- Classification is **OWL-RL entailment**. SPARQL queries are the audit/documentation layer. Do not describe SPARQL as "the system that classifies" in any document
- Gates check **content**, not existence — Gate 2 requires the specific process type to be prescribed (typed); Gate 3 requires the role category to be referenced. This distinction matters legally and must be accurate in any description of how classification works
- Numbers (entailed triples, asserted triples) must match current `run_pipeline.py` output — check before updating any certificate example in any document
- The two-layer architecture (classification vs. audit) must be represented accurately. Do not flatten them into a single list of "checks"

## Hard Stops

- No probabilistic language: ~~"confidence," "likely high-risk," "suggests classification"~~
- No describing SPARQL as the classification engine in client-facing or public documents
- No referring to ARCO itself as an AI system
- No certificate examples with stale triple counts — run pipeline, copy actual output
- No claims that gate presence alone (document existence) triggers classification

## Tone Consistency

The target register is: authoritative, precise, direct. Not academic, not sales-heavy. The voice of someone who built the thing and understands it well enough to explain it simply without losing accuracy.

- Prefer short declarative sentences over long subordinate clauses
- Prefer "ARCO produces a determination" over "ARCO can help you understand whether..."
- Prefer "If Gate 2 fails, the system is not classified" over "Without the right documentation, classification may not be possible"
- Technical terms are welcome — they carry precision. Always pair with a plain-language consequence when the audience includes non-technical readers

## Accuracy Before Publishing / Committing

Before finalizing any outward-facing edit:
1. Run `python 03_TECHNICAL_CORE/scripts/run_pipeline.py` if the edit includes certificate examples or triple counts
2. Verify any claim about how gates work against the current OWL axioms in `ARCO_governance_extension.ttl`
3. Verify any claim about pipeline structure against `run_pipeline.py`
4. Do not describe resolved issues as open or open issues as resolved — check `docs/agent/eu_ai_act_rules.md` for current state
