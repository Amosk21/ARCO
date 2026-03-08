# Writing Rules — `01_COMMERCIAL/`

Governs: `EXEC_PITCH.md`, `ARCO_Assurance_Engine.md`, `ARCO_Pilot_Engagement_Scope.md`, `ARCO_Regulatory_Determination_Case.md`

Full writing rules: `docs/agent/writing_rules.md` — read before substantive edits.

## This Directory's Purpose

Client-facing, decision-maker-facing, business-case content. Primary audiences: executives, compliance officers, legal counsel, potential partners.

These files are NOT technical specifications. Do not apply ontology rules here. Do not apply SHACL or SPARQL constraints here. Technical accuracy still applies — do not misrepresent what the system does — but the framing is economic and governance-oriented, not formal-logic-oriented.

## Key Invariants for This Directory

- ARCO produces determinations, not scores or opinions — this must be accurate in all commercial materials
- Do not describe ARCO as an AI system — it classifies AI systems using formal logic
- Do not use probabilistic or hedged language for classification results
- Triple counts, entailed triples, pipeline examples — if present, must match actual pipeline output. Run `python 03_TECHNICAL_CORE/scripts/run_pipeline.py` and copy the real output.
- Economic claims (cost of remediation, fine exposure) — should be directionally accurate and conservative. Do not invent figures. Existing materials use "up to 6% of global revenue" (verbatim from the EU AI Act); retain the exact statutory framing.

## Tone

Direct, confident, non-academic. The register of a chief compliance officer presenting to a board, not a researcher presenting to a conference. Translate technical precision into governance and economic clarity.
