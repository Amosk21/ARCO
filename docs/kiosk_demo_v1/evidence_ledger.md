# Kiosk Demo v1 — Evidence Ledger

**Purpose.** Per-row mapping showing how each claim in `source_packet.md` (HYPOTHETICAL) is adjudicated into a reviewed RDF commitment in `03_TECHNICAL_CORE/ontology/ARCO_instances_verification.ttl`. This is the input mile of ARCO's chain: source documentation → adjudicator review → reviewed RDF commitment.

**Source:** `source_packet.md` (HYPOTHETICAL).
**Target fixture:** `03_TECHNICAL_CORE/ontology/ARCO_instances_verification.ttl`.
**Policy:** `docs/EVIDENCE_TO_COMMITMENT_POLICY.md`.

Each row shows: a verbatim or close-paraphrase source-text excerpt; the adjudicator's note (what the claim licenses, what bucket it lands in, what is held); the resulting triple in the fixture; and the disposition status.

---

## Ledger

| # | Source-text excerpt | Adjudicator note | Resulting triple | Status |
|---|---|---|---|---|
| 1 | "Corporate Access Kiosk is a biometric verification kiosk for corporate office building access." | Source identifies a single deployed system. Material-bearer bucket; mint a `:System` individual. | `:VerificationKiosk_001 a :System` (verification.ttl:43) | committed |
| 2 | "When a pre-enrolled employee approaches the kiosk, the verification module captures a face image..." | The verification module is a hardware component of the system. Material-bearer bucket; mint a `:HardwareComponent` and a `bfo:has_part` link from the system. | `:VerificationKiosk_001 bfo:0000051 :Kiosk_VeriComp_Module` ; `:Kiosk_VeriComp_Module a :HardwareComponent` (verification.ttl:38, 46) | committed |
| 3 | "The system operates in 1:1 verification mode only. Each transaction matches a presented face against the one reference template associated with the claimed identity." | Disposition bucket. Source licenses a verification disposition (1:1 per Article 3(36)) on the verification module. Source does NOT license biometric identification capability anywhere in the document. | `:Kiosk_VeriComp_Module ro:0000091 :Kiosk_VeriComp_Disposition` ; `:Kiosk_VeriComp_Disposition a :BiometricVerificationCapability` (verification.ttl:35-41) | committed |
| 4 | "The product is intended for use at building or floor entry points to verify the identity of pre-enrolled employees against their enrolled reference template." | Information-side ICE bucket. Mint an `:IntendedUseSpecification` directive ICE that is `iao:is_about` the system. | `:Kiosk_IntendedUse_001 a :IntendedUseSpecification` ; `:Kiosk_IntendedUse_001 iao:0000136 :VerificationKiosk_001` (verification.ttl:52-55) | committed |
| 5 | "Verification mode: 1:1... Identification mode: not enabled in this deployment." | The IUS prescribes a verification process token (typed `:BiometricVerificationProcess`, NOT `:RemoteBiometricIdentificationProcess`). Process bucket; the typed-token pattern is the current ARCO modeling convention (see LIMITATIONS §3.7.a). | `:Kiosk_IntendedUse_001 cco:prescribes :Kiosk_VerificationProcess_Token` ; `:Kiosk_VerificationProcess_Token a :BiometricVerificationProcess` (verification.ttl:54, 57-58) | committed |
| 6 | "Affected population: pre-enrolled employees presenting a claimed identity at the kiosk." | Information-side ICE bucket. The use-scenario specification designates `:NaturalPersonRole` as the affected role universal (designation by inscription). No `:NaturalPersonRole` bearer instance is minted (LIMITATIONS §3.1; bucket-test rule against fake-witness creation). | `:Kiosk_UseScenario_001 a :UseScenarioSpecification` ; `:Kiosk_UseScenario_001 iao:0000136 :VerificationKiosk_001` ; `:Kiosk_UseScenario_001 cco:designates :NaturalPersonRole` (verification.ttl:60-64) | committed |
| 7 | "Provider organization: Example Access Solutions (HYPOTHETICAL). The provider has produced an assessment documentation package..." | Material bearer + Role buckets. Source licenses provider organization, provider role, assessment documentation process, and assessment documentation ICE. | `:KioskProviderOrg_001 a :ProviderOrganization` ; `:KioskProviderRole_001 a :ProviderRole` ; `:KioskAssessmentDoc_001 a :AssessmentDocumentation` (verification.ttl:84-101) | committed |
| 8 | "This document does not claim that the underlying hardware is structurally incapable of identification." | OWA scope-cut. Source explicitly refuses the closed-world hardware-incapability claim. No reality-side triple is minted from this excerpt; the refusal is recorded in the fixture's ontology header `rdfs:comment` (verification.ttl:12-18) as the OWA framing. The same scope-cut is documented in LIMITATIONS §3.5. | (no triple; recorded as documentary scope-cut) | held / scope-cut |
| 9 | "the underlying hardware ... is software-configurable; in a different deployment, with a different reference-template store and a different matching policy, the same hardware could be configured for identification mode." | OWA scope-cut. Source explicitly states this deployment, not the hardware in isolation, is the modeling target. A different deployment of the same hardware would be modeled as a separate `:System` instance. No triple is minted from this excerpt. | (no triple; documentary scope-cut, LIMITATIONS §3.5 third paragraph) | held / scope-cut |

---

## Coverage check

Every reality-side and information-side triple in `ARCO_instances_verification.ttl` traces to a row above. The kiosk fixture is fully licensed by the source packet under this ledger. The two OWA scope-cuts at rows 8-9 are explicit refusals to over-commit; the reasoner answers "Annex III 1(a) is not entailed under the current commitments," not "the hardware cannot do identification."

## What this ledger does NOT do

- Does not claim every triple in the fixture is automatically derivable from the source. Rows 1-7 are adjudicator commitments; the adjudicator's review is the load-bearing step.
- Does not capture every detail in the source packet. Rows 8-9 explicitly hold (no triple) because the source's OWA framing must remain documentary, not be flattened into a closed-world claim.
- Does not provide a runtime extraction pipeline. The source packet is hand-authored prose for this demonstration; LLM-assisted extraction is out of scope per `docs/EVIDENCE_TO_COMMITMENT_POLICY.md`.

---

## Bearer particulars (currently HYPOTHETICAL slots)

Rows 4 (IntendedUseSpecification) and 6 (UseScenarioSpecification) above mint information artifacts that, in BFO 2020 terms, are generically dependent continuants. A generically dependent continuant exists by being concretized in something more specific. For a document-derived specification, that something is an inscription on a particular document file. The kiosk source packet is HYPOTHETICAL, so the bearer particulars for these information artifacts are not asserted in the fixture today.

The fixture reserves the slot pattern at `03_TECHNICAL_CORE/ontology/ARCO_instances_verification.ttl` section 5 (commented out). When the kiosk source becomes a real published document, uncommenting and filling those slots closes the realist chain back to the real world. Until then, the information artifacts exist as existential commitments under the Open World Assumption without an asserted concretizer. BFO 2020 declares the relation that closes the chain (`bfo:0000059` concretizes) but does not enforce it as an OWL restriction, so the reasoner accepts the unconcretized state without inconsistency.

| Information artifact | Source-side bearer slot | Status |
|---|---|---|
| `:Kiosk_IntendedUse_001` (row 4) | `:Kiosk_SourceDoc_Inscription_PLACEHOLDER` concretizes the IUS via `bfo:0000059`. The inscription inheres in `:Kiosk_SourceDoc_PLACEHOLDER` (a material entity) via `ro:0000052`. | slot reserved, currently HYPOTHETICAL |
| `:Kiosk_UseScenario_001` (row 6) | Same source document inscription concretizes the USS as well (the same source document covers both intended use and use scenario). | slot reserved, currently HYPOTHETICAL |
| `:KioskAssessmentDoc_001` (row 7) | Pipeline-emitted side. The bearer slot for this kind of information artifact lives at `OPEN_PROBLEMS.md` L2.2: the assessment documentation should be tokenized by the certificate file the pipeline writes for this run. | tracked separately (L2.2) |
| `:Kiosk_Determination_001` (no row in this ledger; pipeline-emitted) | Same as above. L2.2 acceptance criterion covers the pipeline-emitted determination information artifact. | tracked separately (L2.2) |

When the kiosk demo gains a real source document, the source-side slots (rows 4 and 6) get filled mechanically. The pipeline-emitted side (row 7 and the determination information artifact) gets filled by L2.2's planned pipeline emission of `cco:is_tokenized_by` triples to the certificate file. Both ends of the chain anchor in real-world particulars then.
