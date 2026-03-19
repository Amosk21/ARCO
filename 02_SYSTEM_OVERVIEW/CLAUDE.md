# Writing Rules — `02_SYSTEM_OVERVIEW/`

Governs: `arco_positioning.md`, `TechnicalDeck.md`, `Glass_Box_Compliance_White_Paper.md`, `Command_Center.md`

Full writing rules: `docs/agent/writing_rules.md` — read before substantive edits.

## This Directory's Purpose

System-level narrative, positioning, and technical overview content. Bridges technical architecture and business consequences. Audiences range from technical evaluators to governance leads.

## Key Invariants

- The two-layer pipeline architecture (OWL-RL classification + SPARQL audit) must be described accurately — do not flatten to "a set of checks"
- SPARQL queries are the audit/documentation layer; they are not the classification engine. Any description of "how classification works" must reflect the OWL-RL entailment as the source of the determination
- Gate content-checking (Gate 2 requires specific process type, Gate 3 requires role category) must be represented accurately — these are meaningful distinctions from existence-only checking and are part of what makes ARCO's determinations defensible
- ARCO sits upstream of deployment — do not describe it as a monitoring tool, a behavioral analysis tool, or a post-hoc audit artifact
- Do not overstate current scope: Annex III 1(a) (remote biometric identification) and Annex III 5(b) (creditworthiness evaluation) are the covered categories. Do not claim coverage of other Annex III categories.

## Tone

More narrative than `01_COMMERCIAL/`, still precise. These documents can carry more technical depth and system explanation. The positioning documents should read as authoritative technical overview, not marketing copy.
