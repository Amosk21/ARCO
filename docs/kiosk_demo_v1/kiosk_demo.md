# Kiosk Demo v1 — Main Artifact

**Date:** 2026-05-10.
**Scope:** Demonstrate the source → reviewed-commitment → entailment → answer chain end-to-end on one negative case (verification kiosk, NOT subject to Annex III 1(a)) paired with one positive case (Sentinel-ID, IS subject to Annex III 1(a)). Same pipeline, same axioms, different fixtures, different outcomes.

**Why this demo exists.** `docs/MODELING_ADEQUACY_BRIEF.md` Verdict 3 says input provenance is not yet demonstrated. The kiosk demo closes that gap for one fixture: it shows that the existing reviewed commitments in `ARCO_instances_verification.ttl` are *licensed by* a written source packet, with each licensure step adjudicated and recorded.

---

## The chain

```text
HYPOTHETICAL vendor source packet (source_packet.md)
  --> adjudicator review per evidence_ledger.md
  --> reviewed RDF commitments (ARCO_instances_verification.ttl)
  --> OWL-RL reasoning (run_pipeline.py)
  --> HermiT cross-check (hermit_cross_check.py, CI on push to main)
  --> SPARQL ASK queries on the reasoned graph
  --> certificate (runs/demo/certificate.txt)
  --> CDO-readable answer + disclosed gaps
```

Every arrow is backtested. The chain is re-derivable from the source packet plus the public ARCO axiom set.

---

## Side-by-side: positive vs negative case

Both runs use the same `run_pipeline.py`, the same axiom set, and the same SPARQL queries.

### Positive case: Sentinel-ID System

```bash
python 03_TECHNICAL_CORE/scripts/run_pipeline.py
```

Headline result (verified by pipeline run on current main):

```
PRIMARY ARCO CLASSIFICATION:  AnnexIII1aApplicableSystem
LATENT-RISK FLAG:             HighRiskSystem (PRESENT)
ANNEX III 1(a):               VERIFIED (ENTAILED, Article 6(3) derogation not evaluated)
ANNEX III 5(b):               NOT APPLICABLE
```

The reasoner entails Annex III 1(a) applicability because all three gates are satisfied: a hardware component bears `:BiometricIdentificationCapability` (Gate 1), the IUS prescribes a `:RemoteBiometricIdentificationProcess` (Gate 2), and the USS designates `:NaturalPersonRole` (Gate 3). The classification headline is the pure class IRI; the entailment mode (`ENTAILED` / `NOT_ENTAILED`) and gate provenance live in separate fields of `summary.json` (`classification_mode`, `primary_arco_classes`, `applicability_status`).

### Negative case: Verification Kiosk

```bash
python 03_TECHNICAL_CORE/scripts/run_pipeline.py \
  --system VerificationKiosk_001 \
  --instances 03_TECHNICAL_CORE/ontology/ARCO_instances_verification.ttl
```

Headline result:

```
PRIMARY ARCO CLASSIFICATION:  No ARCO classification within currently modeled categories: Annex III 1(a) and 5(b).
LATENT-RISK FLAG:             HighRiskSystem (NOT PRESENT)
ANNEX III 1(a):               NOT APPLICABLE
ANNEX III 5(b):               NOT APPLICABLE
```

In `summary.json`: `applicability_status: "not_applicable"`, `all_checks_passed: null`, `determination_node_uri: null` — the non-applicable case emits honest absences rather than forcing PASS or a Sentinel-shaped default. Gate 1 does not fire because the asserted disposition is `:BiometricVerificationCapability`, which is `owl:disjointWith :BiometricIdentificationCapability` and is NOT a member of the `:AnnexIIITriggeringCapability` `owl:unionOf` (verified at `ARCO_governance_extension.ttl:184-190`). Without Gate 1, the three-gate intersection cannot fire. The reasoner correctly does not entail Annex III 1(a) applicability.

**Same procedure. Different commitments. Different entailment outcome.** Both reasoners (OWL-RL and HermiT) agree on this, verified by `hermit_cross_check.py` in CI.

---

## What this demo shows

ARCO transforms a vendor source description into a re-derivable, formally entailed answer to a CDO question. For the Verification Kiosk, the answer is *"under the current asserted commitments, this system is not in scope of Annex III 1(a)."* The chain to that answer is fully inspectable: source text (HYPOTHETICAL) → adjudicator-licensed triple (evidence ledger row) → reasoner entailment (OWL-RL with HermiT cross-check) → certificate field (`ANNEX III 1(a): NOT APPLICABLE`).

The non-entailment is principled, not assumed. The fixture asserts `:BiometricVerificationCapability` (not identification) on the hardware module, asserts the IUS prescribes a `:BiometricVerificationProcess` (not RBI), and the reasoner therefore does not entail `:AnnexIII1aApplicableSystem`. The disjointness axioms ensure that Gate 1 cannot fire on a verification-only assertion. Two reasoners (OWL-RL and HermiT) agree, on this and across all certificate-grade fixtures.

Under the Open World Assumption, ARCO does NOT claim the underlying hardware is incapable of identification. The hardware is software-configurable; a different deployment of the same hardware (different software, different database, different intended use) would be modeled as a separate `:System` instance with its own asserted disposition (`LIMITATIONS.md §3.5`). What ARCO claims is: under THIS deployment's reviewed commitments, identification is not entailed; therefore Annex III 1(a) does not apply.

---

## What a CDO reading this gets

1. **The source packet** (`source_packet.md`): the vendor description that started the process. Hand-authored, HYPOTHETICAL, structured to license a real fixture.
2. **The evidence ledger** (`evidence_ledger.md`): the audit trail showing how each commitment was licensed. Every triple in the fixture traces to a source-text excerpt or to a documented OWA scope-cut.
3. **The reasoner output**: formal OWL-RL entailment, confirmed by HermiT cross-check. Same answer, two independent reasoner families.
4. **The certificate** (`runs/demo/certificate.txt` after running the pipeline): the CDO-readable summary line.
5. **The OWA scope-cut**: the explicit refusal to over-claim. ARCO does not say "the device cannot do X"; ARCO says "X is not entailed under the asserted commitments."

That is the input mile + reasoning + output, end-to-end, for one concrete case. Not a confidence score, not a vendor assurance, not a legal opinion: a formal classification with a re-derivable evidence chain.

---

## What this demo does NOT do

- Does not claim legal compliance approval. Per `LIMITATIONS.md §8`, the encoded interpretation has not been externally reviewed by qualified counsel.
- Does not evaluate Article 6(3) derogation. ARCO flags `:DerogationClaim` artifacts for human review only.
- Does not route Article 5(1)(h) prohibition for real-time RBI. `LIMITATIONS.md §3.7.c` discloses this scope cut.
- Does not entail provider/deployer obligations from the negative classification.
- Does not ingest raw vendor PDFs at runtime. The source packet is hand-authored prose for this demonstration; runtime extraction is a separate problem outside ARCO's current scope (`docs/EVIDENCE_TO_COMMITMENT_POLICY.md`).
- Does not enforce cross-property SHACL consistency between disposition + IUS + USS. The OWL disjointness axioms catch the structural inconsistency case at the OWL layer; a SHACL-SPARQL consistency shape would catch adjudicator-error cases earlier in the pipeline, but is a Tier 2 enhancement not authored for this demo.

---

## Files in this demo

| File | Role |
|---|---|
| `source_packet.md` | HYPOTHETICAL vendor description (input) |
| `evidence_ledger.md` | Per-row source → triple licensure (audit trail) |
| `decision_packet.md` | Pre-authoring modeling decisions |
| `real_world_validation.md` | Pre-commit empirical check (validated framing) |
| `kiosk_demo.md` | This file: side-by-side + what this shows + scope refusals |

Together: five files, one cohesive demo, end-to-end input → output chain visible to a CDO. No new ontology, no new SHACL, no new SPARQL. Uses what ARCO already has.
