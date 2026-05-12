# Kiosk Demo v1 — Modeling Decision Packet

**Purpose.** Before authoring source packet text, evidence-ledger rows, or runner code for the kiosk demo (`OPEN_PROBLEMS L1.1`), answer these questions in order. Hold any decision where the answer is "I don't know yet."

**Discipline.** Smallest scale that has a real CDO value point. Anchor each decision to (a) EU AI Act text and (b) the existing `ARCO_instances_verification.ttl` fixture. The packet is structured to either justify or disqualify each modeling step, so a wrong source packet cannot quietly slip through.

**Reference docs (do not duplicate; cite):**
- `docs/_archive/COMPETENCY_QUESTIONS.md` — session-level CDO-question script (CQ0-CQ17)
- `docs/_archive/MODELING_QUESTION_MAP.md` — per-commitment workbench
- `docs/_archive/EVIDENCE_TO_COMMITMENT_POLICY.md` — source-to-RDF discipline
- `03_TECHNICAL_CORE/ontology/ARCO_instances_verification.ttl` — the existing fixture (already aligned with what the demo proves)

---

## A. CDO question and regulatory anchor

| # | Question | Default answer (accept or override) |
|---|---|---|
| A1 | What single CDO question does the demo answer? | "Is this verification kiosk in scope of EU AI Act Annex III 1(a) (high-risk remote biometric identification)?" |
| A2 | Regulatory anchor (specific articles)? | Article 3(36) defines biometric verification (1:1). Article 3(41) defines remote biometric identification system (1:N). Annex III 1(a) covers RBI per 3(41); Recital 15 broadens the verification carve-out to access-to-service, unlock, and premises-access purposes. The regulation classifies by **intended use**, not by hardware capability. ARCO Gate 2 anchors to intended use via `:IntendedUseSpecification` and `cco:prescribes`. |
| A3 | Which CQ from `docs/_archive/COMPETENCY_QUESTIONS.md` covers it? | Most likely a "negative-case" CQ (the system does NOT entail Annex III 1(a)). User to fill once CQ backtest finishes. |
| A4 | CDO value point in one sentence? | "Confirm with formal evidence that a 1:1 verification system is not subject to Annex III high-risk obligations, before deployment, with a re-derivable chain of reasoning rather than a vendor assurance." |

## B. System scope (smallest meaningful)

| # | Question | Default answer |
|---|---|---|
| B1 | What is the system? | `:VerificationKiosk_001` (already in fixture; `ARCO_instances_verification.ttl:43-46`). |
| B2 | Real or hypothetical? | Hypothetical. The source packet labels itself "HYPOTHETICAL" prominently per CLAUDE.md forbidden-prose rules. |
| B3 | Deployment context (one sentence)? | LOCKED 2026-05-10: **corporate office access control with pre-enrolled employees, 1:1 face match against the employee's enrolled reference template**. Validation report at `runs/loop/2026-05-10_beverley-procedure/kiosk_demo_v1/real_world_validation.md` confirmed this scenario as the highest real-world relevance and cleanest fit to the existing fixture. |
| B4 | Affected population (one sentence)? | "Persons who present a claimed identity at the kiosk and are matched 1:1 against an enrolled reference." Fixture already designates `:NaturalPersonRole` (`ARCO_instances_verification.ttl:64`). |

**Hold rule.** B3 is the only open input. Once chosen, Section C source claims follow.

## C. Source-packet claims (each with verbatim or paraphrased excerpt)

For each row: write the source text that licenses the existing fixture commitment. If the source does not license a fixture triple, mark it as "fixture commits but source does not license" and either edit the source or hold the triple.

| # | Source-packet claim | Existing fixture commitment (TTL line) | Source-licensed? |
|---|---|---|---|
| C1 | What does the source say the system DOES? | `:Kiosk_VeriComp_Module ro:0000091 :Kiosk_VeriComp_Disposition` typed as `:BiometricVerificationCapability` (`verification.ttl:35-41`) | (fill from source text) |
| C2 | What does the source say the system is INTENDED TO DO? | `:Kiosk_IntendedUse_001 cco:prescribes :Kiosk_VerificationProcess_Token` typed as `:BiometricVerificationProcess` (`verification.ttl:52-58`) | (fill) |
| C3 | What does the source say about the affected population? | `:Kiosk_UseScenario_001 cco:designates :NaturalPersonRole` (`verification.ttl:60-64`) | (fill) |
| C4 | What does the source say the system DOES NOT do? | Fixture `rdfs:comment` at `verification.ttl:40, 45` and `:18` documents 1:1 only, NOT identification | (fill — must include explicit "does not perform 1:N identification" or the disqualifier test in E2 fires) |
| C5 | What about provider/deployer? | `:KioskProviderOrg_001`, `:KioskProviderRole_001`, `:KioskAssessmentDoc_001` already in fixture (`verification.ttl:84-101`) | (fill or hold if the demo wants to scope away provider details) |

## D. Per-claim BFO/CCO routing

Apply `docs/_archive/MODELING_QUESTION_MAP.md` to each claim. The fixture is already aligned, so this is a confirmation pass, not new modeling.

| Claim | Reality / Information / Regulatory / Output | BFO bucket | Existing class | Verdict |
|---|---|---|---|---|
| C1 capability | Reality | Disposition | `:BiometricVerificationCapability` (governance) | aligned |
| C2 prescribed process | Information | ICE (Directive ICE) | `:IntendedUseSpecification` + `:BiometricVerificationProcess` | aligned |
| C3 affected role | Information | ICE (Designative ICE) | `:UseScenarioSpecification` designating `:NaturalPersonRole` universal | aligned |
| C4 scope exclusion | Output / disclosed | Documentary | `rdfs:comment` annotation, no triple | aligned |
| C5 provider | Reality | Material bearer + Role | `:ProviderOrganization`, `:ProviderRole` | aligned |

If any row's "Verdict" comes back as `not aligned`, the source packet has licensed something the fixture does not commit to, OR the fixture commits to something the source does not license. Surface the divergence; do not silently align.

## E. Justify-or-disqualify test

| # | Question | Default answer |
|---|---|---|
| E1 | If C1-C5 hold as licensed, what entailment SHOULD fire? | Nothing on the Annex III axis. `HighRiskSystem`, `AnnexIII1aApplicableSystem`, `AnnexIII5bApplicableSystem` should all be False. Verified by `test_scenarios.py` and the prior backtest. |
| E2 | What single source claim WOULD disqualify the demo? | If the source said "matches against a database of all enrolled persons" or "1:N matching" or "identifies unknown individuals," the system would license a `:BiometricIdentificationCapability` triple and Gate 1 would fire. The demo's premise breaks. |
| E3 | Which existing test verifies E1? | `test_scenarios.py` runs the kiosk fixture and asserts negative entailment on all three. `hermit_cross_check.py` confirms OWL-RL and HermiT agree on this fixture. |
| E4 | Which existing query verifies E2 in the contrapositive? | `check_annex_iii_1a_entailment.sparql` against the kiosk fixture returns False. If the source ever licensed a `:BiometricIdentificationCapability` triple, the same query against an updated fixture would return True. |

## F. Output expectation

| # | Question | Default answer |
|---|---|---|
| F1 | What does the certificate say in plain English? | "Under the reviewed commitments asserted for this system, ARCO does not entail Annex III 1(a) applicability. The asserted capability is biometric verification (1:1), which is structurally outside the Annex III 1(a) scope as defined by Article 3(41). The classification is not 'this system cannot identify;' it is 'identification is not entailed under the current commitments,' under the Open World Assumption." |
| F2 | What does the certificate refuse to say? | (a) Closed-world claims that the hardware is incapable of identification. (b) Legal opinions on Article 5(1)(h) prohibition status. (c) Provider/deployer obligation entailment from the negative classification. (d) Any claim about runtime behavior. |

## G. Fit check

| # | Question | Default answer |
|---|---|---|
| G1 | Does the demo align with existing ARCO modeling? | Yes. `ARCO_instances_verification.ttl` already exists, is well-structured, and has been backtested. The demo wraps it with source packet + evidence ledger + side-by-side runner. |
| G2 | Are any ontology changes required? | None. The fixture is sufficient. The demo work is documentation + runner code, not new TTL. |
| G3 | What new files does the demo create? | `kiosk_demo_v1/source_packet.md`, `kiosk_demo_v1/evidence_ledger.md`, `kiosk_demo_v1/side_by_side.py`, `kiosk_demo_v1/what_this_shows.md`. All under `runs/loop/2026-05-10_beverley-procedure/kiosk_demo_v1/`. |
| G4 | Is any technical change to ARCO required by this demo? | No. If E2's disqualifier comes up, that is information about the source packet, not about ARCO. |

---

## Hold rule

If A1-A4, B3 do not have firm answers, do not start the source packet. Section C cannot be filled without B3.

## Default rule

If a row's "Default" is acceptable, mark accepted. Default acceptance covers most of the packet because the existing fixture already aligns. The real authoring work is C1-C5 (the source-text claims) and the four new files in G3.

## Why this packet is small

The kiosk fixture exists and is aligned. The demo's load-bearing work is the *input mile* (source → reviewed commitment), not new ontology. So most decisions reduce to "confirm fixture alignment" rather than "make new modeling commitment."

## What the demo proves

`docs/_archive/MODELING_ADEQUACY_BRIEF.md` Verdict 3 says input provenance is not yet demonstrated. The kiosk demo closes that gap for one fixture: it shows that the existing reviewed commitments in `ARCO_instances_verification.ttl` are *licensed by* a written source packet, with each licensure step adjudicated and recorded in the evidence ledger. That is the proof the brief identifies as missing.
