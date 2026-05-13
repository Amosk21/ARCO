# Kiosk Demo (Verification Kiosk Negative Case)

> *Items marked with (\*) are work-in-progress: a modeling discipline articulated in the technical core but not yet exercised in fixtures, or a pending modeling decision with a clear path forward. Tracked in ARCO's internal working register.*

## What this is

A worked example showing what ARCO does on a single fixture: a corporate verification kiosk. The fixture is a NEGATIVE case for Annex III 1(a). The demo walks the chain from source documentation to ARCO certificate and shows that ARCO does NOT entail Annex III 1(a) high-risk applicability for a system whose intended use is 1:1 verification, even though the underlying hardware would be configurable for 1:N identification.

The fixture (`03_TECHNICAL_CORE/ontology/ARCO_instances_verification.ttl`) is real, loaded by the pipeline, and exercised in CI on every push. The narrative source-packet and evidence-ledger sketches in this document show what the input-mile WOULD look like on a real system. Programmatic wiring of the source-to-commitment chain is `OPEN_PROBLEMS.md L1.1`.

## The CDO question this answers

A CDO arrives with: "Is my system high-risk under Annex III? If so, why? Can I trust the chain?"

The kiosk fixture exercises DSQ-1 (Annex III applicability) fully — implemented today for 1(a) and 5(b) per `docs/_archive/COMPETENCY_QUESTIONS.md`. It exercises DSQ-2 (which gate commitments caused the answer) partially — gate-evidence JSON and HTML view exist today; the full per-field receipts and G/M/D output discipline are queued at `OPEN_PROBLEMS.md` L4.4-L4.6. It exercises DSQ-3 (what ARCO knows vs reports vs refuses) partially — `LIMITATIONS.md` scope cuts and schema 1.3 `applicability_status` are there today; reasoned-graph artifact export, HermiT artifact upload, and a prose determination paragraph are queued at L4.8. The OWL three-gate axiom shape lives at `docs/modeling_decisions/three_gate_classifier.md`.

| Gate | What it tests | Kiosk |
|---|---|---|
| **Gate 1 (capability, reality side)** | System has a part bearing an `:AnnexIIITriggeringCapability` disposition | **FAILS** — `:BiometricVerificationCapability` is not in the triggering union; Annex III 1(a) covers RBI per Article 3(41), not verification per Article 3(36) |
| **Gate 2 (intended use, representation side)** | An `:IntendedUseSpecification` is_about the system AND prescribes the regulated process | **FAILS** — IUS prescribes `:BiometricVerificationProcess`, not `:RemoteBiometricIdentificationProcess`, so the IUS is not classified as `:RemoteBiometricIdentificationIntendedUseSpec` |
| **Gate 3 (affected role, representation side)** | A `:UseScenarioSpecification` is_about the system AND designates `:NaturalPersonRole` | **SATISFIED** — natural persons are designated as the affected population |

Annex III 1(a) is NOT entailed because the conjunction requires all three gates. Gate 3 alone does not fire the applicability class. This is the content-sensitivity claim: a kiosk whose hardware looks similar to an identification system but is configured for verification gets the correct negative answer because Gates 1 and 2 don't fit, even though Gate 3 does.

## Why a negative case

Most demos show positive cases ("yes, this is high-risk"). The negative case is the harder demonstration: a system whose hardware looks similar to a regulated one does NOT trigger Annex III 1(a) when its intended use is 1:1 verification rather than 1:N identification. The classifier's content-sensitivity is what makes that distinction stick.

ARCO's positive case is Sentinel-ID (`ARCO_instances_sentinel.ttl`, Annex III 1(a) applicable). The kiosk is the negative-case counterpart on the same architecture.

## The system

Corporate access kiosk for an office building. Pre-enrolled employees approach the kiosk; the verification module captures a face image and compares it against the single reference template stored for that employee under the claimed identity. The system returns match or no-match. Permitted or denied entry follows.

The system operates in 1:1 verification mode only. Each transaction matches against the one reference template associated with the externally-presented claimed identity (badge tap or PIN entry). The system does NOT perform 1:N identification against an enrolled-population database, does NOT enroll walk-ups, and does NOT match faces of unknown individuals.

## End-to-end chain (this fixture)

| Step | What it does | Status |
|---|---|---|
| Source packet | Hypothetical vendor product description | NARRATIVE (HYPOTHETICAL); real-vendor substitution is `OPEN_PROBLEMS.md L1.1` |
| Evidence ledger | Per-claim adjudication: source text → TTL triple | NARRATIVE; programmatic ledger storage is L1.1 |
| Reviewed RDF commitments | Typed instance graph in `ARCO_instances_verification.ttl` | REAL; loaded by pipeline |
| BFO-grounded reasoning | OWL-RL closure (~20,000 entailed triples) + HermiT cross-check | REAL; CI runs both on every push |
| SHACL completeness + SPARQL audit | Documentary structure + post-reasoning evidence queries | REAL |
| Certificate | `runs/demo/certificate.txt` reports negative outcome | REAL |

## Step 1: Source packet (NARRATIVE, HYPOTHETICAL)

A hypothetical vendor product description that licenses the existing reviewed commitments in the kiosk fixture. The source packet is structured to map row-by-row to the evidence ledger; it is not a real vendor document. Vendor framing patterns are drawn from publicly observable conventions in the corporate biometric kiosk market (Suprema, ZKTeco, Matrix, HID, IDEMIA).

Key claims the source makes:

- The kiosk is a biometric verification kiosk for corporate office building access.
- It operates in 1:1 verification mode only; it does NOT perform 1:N identification.
- Intended use: confirm pre-enrolled employees against their reference template at building or floor entry points.
- Configuration: 1:1 mode, per-employee single-template store, identification mode not enabled.
- Provider organization has produced an assessment documentation package.

The source explicitly refuses two closed-world claims:

- It does NOT claim the underlying hardware is structurally incapable of identification (the hardware is software-configurable).
- It does NOT claim what the hardware could be configured to in some other deployment.

Article 3(36) of EU Regulation 2024/1689 keys Annex III 1(a) on intended use, not on raw hardware capability. The source packet describes THIS deployment under THIS configuration.

(\*) **Real vendor document substitution is `OPEN_PROBLEMS.md L1.1`.** The next concrete move replaces this hypothetical with a real vendor packet (datasheet, conformity declaration, or equivalent), with each claim cited.

## Step 2: Evidence ledger (NARRATIVE)

Per-row mapping from source text to reviewed RDF commitment. Each row records a verbatim or close-paraphrase source excerpt, the adjudicator's note (what bucket the claim lands in, what is held), and the resulting triple in the fixture.

| # | Source claim | Adjudicator note | Resulting triple | Status |
|---|---|---|---|---|
| 1 | "Corporate Access Kiosk is a biometric verification kiosk..." | Material-bearer bucket: mint a `:System` individual | `:VerificationKiosk_001 a :System` | committed |
| 2 | "the verification module captures a face image..." | Material-bearer bucket: mint a `:HardwareComponent` and a `bfo:has_part` link | `:VerificationKiosk_001 bfo:0000051 :Kiosk_VeriComp_Module` ; `:Kiosk_VeriComp_Module a :HardwareComponent` | committed |
| 3 | "operates in 1:1 verification mode only" | Disposition bucket: source licenses verification disposition (1:1 per Article 3(36)). Source does NOT license biometric identification capability. | `:Kiosk_VeriComp_Module ro:0000091 :Kiosk_VeriComp_Disposition` ; `:Kiosk_VeriComp_Disposition a :BiometricVerificationCapability` | committed |
| 4 | "intended for use at building or floor entry points to verify the identity..." | Information bucket: mint a `:IntendedUseSpecification` directive ICE | `:Kiosk_IntendedUse_001 a :IntendedUseSpecification` ; `iao:0000136 :VerificationKiosk_001` | committed |
| 5 | "Verification mode: 1:1... Identification mode: not enabled" | The IUS prescribes a verification process token (typed `:BiometricVerificationProcess`, NOT `:RemoteBiometricIdentificationProcess`). | `:Kiosk_IntendedUse_001 cco:prescribes :Kiosk_VerificationProcess_Token` | committed |
| 6 | "Affected population: pre-enrolled employees..." | Information bucket: USS designates `:NaturalPersonRole` universal. No bearer instance minted (`LIMITATIONS.md §3.1`). | `:Kiosk_UseScenario_001 cco:designates :NaturalPersonRole` | committed |
| 7 | "Provider organization: Example Access Solutions..." | Material bearer + Role buckets: provider organization, provider role, assessment documentation. | `:KioskProviderOrg_001 a :ProviderOrganization` (and related triples) | committed |
| 8 | "does not claim the underlying hardware is structurally incapable of identification" | OWA scope-cut. Source explicitly refuses the closed-world hardware-incapability claim. | (no triple; recorded as documentary scope-cut at `LIMITATIONS.md §3.5`) | held / scope-cut |
| 9 | "the same hardware could be configured for identification mode" in a different deployment | OWA scope-cut. THIS deployment is the modeling target, not the hardware in isolation. | (no triple; documentary scope-cut) | held / scope-cut |

Every reality-side and information-side triple in `ARCO_instances_verification.ttl` traces to a row above. The two OWA scope-cuts at rows 8-9 are explicit refusals to over-commit.

(\*) **Programmatic ledger storage is `OPEN_PROBLEMS.md L1.1`.** Today the ledger is markdown narrative; the structural target is per-triple provenance citations (source document, version, page, adjudicator, adjudication date, evidence tier per `docs/_archive/EVIDENCE_TO_COMMITMENT_POLICY.md`).

## Step 3: Reviewed RDF commitments (REAL)

The reviewed commitments live in `03_TECHNICAL_CORE/ontology/ARCO_instances_verification.ttl`. The pipeline loads them at every run.

Reality side: a `:System` with a `:HardwareComponent` part bearing a `:BiometricVerificationCapability` disposition.

Information side: an `:IntendedUseSpecification` (typed Directive ICE) prescribing a `:BiometricVerificationProcess` token; a `:UseScenarioSpecification` (typed Designative ICE) designating `:NaturalPersonRole`; an `:AssessmentDocumentation` ICE; a `:ProviderOrganization` with a `:ProviderRole`.

(\*) **Software-hardware concretization layer not exercised in this fixture.** The discipline is articulated at `ARCO_core.ttl:126-130` (software is `iao:0000030` ICE; hardware concretizes via `bfo:0000058`); the fixture does not mint software particulars or assert concretization triples. The hardware-software amalgam is disclosed at `LIMITATIONS.md §3.5`.

## Step 4: Reasoning (REAL)

OWL-RL closure (`owlrl 7.1.4`) materializes ~20,000 entailed triples. HermiT (full OWL 2 DL profile) cross-checks via the CI workflow at `.github/workflows/robot-validate.yml`. Both reasoners agree on the negative outcome for this fixture:

- `:VerificationKiosk_001 rdf:type :AnnexIII1aApplicableSystem` is NOT entailed (Gate 1 fails: no `:BiometricIdentificationCapability` in the system's component disposition chain).
- `:VerificationKiosk_001 rdf:type :HighRiskSystem` is NOT entailed (Gate 1 fails on the latent flag too: `:BiometricVerificationCapability` is NOT a member of `:AnnexIIITriggeringCapability`).
- `:VerificationKiosk_001 rdf:type :AnnexIII5bApplicableSystem` is NOT entailed (cross-category isolation: no creditworthiness capability either).

(\*) **The full entailment chain is not yet exported as an inspectable artifact.** The reasoned graph TTL, HermiT classification output, and a prose determination narrative alongside the field-shaped certificate are queued at `OPEN_PROBLEMS.md L4.8`.

## Step 5: Audit and Certificate (REAL)

SHACL validates documentary structure (`assessment_documentation_shape.ttl`). SPARQL queries audit the post-reasoning graph for the conditions each classification rests on (`reasoning/check_*.sparql`).

The certificate at `runs/demo/certificate.txt` (when run with the kiosk fixture) reports:

```
PRIMARY ARCO CLASSIFICATION:  NOT_APPLICABLE
LATENT-RISK FLAG:             NOT_APPLICABLE (no triggering capability)
TRIGGERING CAPABILITY:        none
EVIDENCE PATH:                (gates not satisfied)

ANNEX III 1(a):               NOT APPLICABLE (Gate 1 not satisfied)
ANNEX III 5(b):               NOT APPLICABLE
```

(\*) **Output provenance tightening across surrounding fields is `OPEN_PROBLEMS.md L4.4-L4.6`** (G/M/D field labels, per-field source-query manifest, name/source mismatches).

## Real-world framing

The earlier framing of this demo as "ARCO's value comes from adjudicator hardware-level review distinguishing verification-capable from identification-capable systems" was incorrect. The 1:1 / 1:N distinction is a software/configuration boundary on the same hardware across all surveyed vendors:

| Vendor product | Configurable on same hardware for 1:1 + 1:N? |
|---|---|
| Suprema FaceStation F2 | Yes; spec table lists distinct user capacities for "1:N mode" and "1:1 mode" on one terminal |
| ZKTeco ProFace X (SL) | Yes; software-selectable |
| Matrix COSEC ARGO FACE | Yes; same controller for both |
| HID Amico | Capacity gated by license, not hardware |
| IDEMIA VisionPass | Same optics serve verification and authorized-list workflows |

EU AI Act anchors:
- **Article 3(36)** keys biometric verification on the 1:1 modality.
- **Article 3(41)** defines remote biometric identification system (1:N).
- **Annex III 1(a)** covers RBI per Article 3(41); the verification carve-out is the explicit exclusion.
- **Recital 15** broadens the verification carve-out to access-to-service, unlock, and premises-access purposes.

The corrected framing: ARCO turns a vendor's INTENDED-USE claims into a re-derivable, OWA-bounded entailment chain. The same kiosk hardware can be configured 1:1 or 1:N. What makes Annex III 1(a) inapplicable is the asserted intended purpose plus the configured matching policy, both committed in the graph and adjudicable by a reviewer. Hardware-incapability is NOT claimed.

## What this demo proves

- The pipeline runs end-to-end on a fixture: TTL → reasoner → SHACL → SPARQL → cert.
- Two reasoners (OWL-RL, HermiT) agree on the negative outcome.
- The classification is content-sensitive: a verification fixture does NOT trigger Annex III 1(a) even though hardware-side it looks similar to an identification system.
- Cross-category isolation: no Annex III 5(b) either.
- The OWA scope-cuts (rows 8-9 of the ledger) are honest refusals: ARCO does not claim hardware-incapability.

## What this demo does NOT yet prove

- Real-document warrant for the source packet (still HYPOTHETICAL; `OPEN_PROBLEMS.md L1.1`).
- Programmatic evidence ledger backing (markdown narrative only).
- Reasoned-graph artifact export and prose determination narrative (`OPEN_PROBLEMS.md L4.8`).
- Tightening of output provenance across surrounding cert fields (`L4.4-L4.6`).

## Downstream pieces planned (work-in-progress per asterisk legend)

The vision is the full input-mile-to-honest-certificate chain wired programmatically with all the foundation modeling decisions resolved. The pieces queued for that vision:

- (\*) **Real source document substitution** — replace HYPOTHETICAL packet with real vendor doc; programmatic per-triple provenance citations (`OPEN_PROBLEMS.md L1.1`).
- (\*) **ICE concretization to bearer particulars** — `cco:is_tokenized_by` on ARCO-generated ICEs, plus `bfo:0000058 is_concretized_by` from source-side ICEs to inscription qualities on document bearers (`L2.2`).
- (\*) **Interest modeling for capability accountability** — Beverley canonical capability framing is "disposition + interest of an organism or group"; ARCO models the disposition side only currently. Decision pending across three options (CCO relation only / Quality class per abi production / hybrid). `M-Capability-1 / L2.6`.
- (\*) **Configuration-level aboutness for regulatory ICEs** — `:AnnexIII_Condition_*` ICEs need explicit `iao:is_about` targets; canonical options surfaced (universal-only / particular continuant / multiple constituents). `M-Aboutness-Config-1 / L2.7`.
- (\*) **`:CapabilityDisposition` rename to `:Capability`** — Smith-Against-Idiosyncrasy Principle 8 compositional naming fix; mechanical PR. `M-NameDiscipline-1 / L2.8`.
- (\*) **Gate 3 role-relationship tightening** — current axiom designates the natural-person role universal but does not pin down whether natural persons are subjects of identification, operators, or another role-in-context. `L2.9`.
- (\*) **Gate 2 use-purpose proxy tightening** — current axiom maps Article 3(36) "intended to be used for" to `cco:prescribes someValuesFrom :Process`; defensible structural proxy but loose. `L2.10`.
- (\*) **Reasoned-graph and HermiT classification artifact export** — surface the full entailment chain inspectably. `L4.8 parts 1-2`.
- (\*) **Prose determination narrative emission** — generated from existing SPARQL gate evidence so a non-ARCO-glossary reader can read the conclusion + the reason in one paragraph. `L4.8 part 3`.
- (\*) **Output provenance tightening** — G/M/D field labels, per-field source-query manifest, name/source mismatches across surrounding cert fields. `L4.4-L4.6`.
- (\*) **Article 6(3) derogation handling** — currently surfaces `:DerogationClaim` as audit flag without evaluation; the non-evaluation is disclosed at `OPEN_PROBLEMS.md` D.7 (and `LIMITATIONS.md` §3, §7), and the question of whether derogation could become an OWL consequence is queued at `OPEN_PROBLEMS.md` Q7.
- (\*) **Software-hardware amalgam modeling** — disclosed at `LIMITATIONS.md §3.5` as a deliberate simplification; deeper amalgam modeling activates when use case demands.

## What it would look like with all of these landed

A reviewer downloads the certificate. Alongside the field-shaped status board, they see:

- A reasoned-graph TTL artifact with all ~20,000 entailed triples inspectable.
- HermiT's classification output as a separate downloadable artifact, confirming OWL-RL agreement.
- A prose narrative paragraph: "Under the reviewed commitments asserted for this system, ARCO does not entail Annex III 1(a) applicability. The asserted capability is biometric verification (1:1), which is structurally outside the Annex III 1(a) scope as defined by Article 3(41). Identification is not entailed under the current commitments per the Open World Assumption; ARCO does not claim the hardware is structurally incapable of identification."
- Per-claim source citations: each TTL triple traces to a vendor document, page, and adjudicator review entry.
- Each output field labeled G (graph-derived), M (run metadata), or D (documentary scope text).
- A `:DerogationClaim` artifact (if the provider asserted one) surfaced with its supporting structure for human legal review.
- The Capability + Interest framing wired: the natural-person role designated in the use scenario carries an explicit interest hookup to the rights protection the regulation operates on behalf of.
- Configuration-level aboutness on the regulatory ICE: `:AnnexIII_Condition_1a iao:is_about` the constituent system + capability + IUS + role together, expressing the regulatory commitment as a configuration not just a universal.

The pipeline shape stays the same. The added pieces are surfacing work, not architecture work.

## What this demo is not

- It is not a deployable compliance product. It is a structural sketch on a hypothetical vendor input.
- It is not a legal opinion. The encoded interpretation has not been externally reviewed by counsel.
- It is not a runtime classifier. The classification is over reviewed design-time commitments, not deployed behavior.
- It is not a claim that the kiosk hardware cannot identify. The hardware is software-configurable; ARCO models THIS deployment's commitments, not the hardware's theoretical capacity.

## Where the pieces live

- TTL fixture: `03_TECHNICAL_CORE/ontology/ARCO_instances_verification.ttl`
- Pipeline: `03_TECHNICAL_CORE/scripts/run_pipeline.py`
- HermiT cross-check workflow: `.github/workflows/robot-validate.yml`
- SHACL shapes: `03_TECHNICAL_CORE/validation/`
- SPARQL audit queries: `03_TECHNICAL_CORE/reasoning/`
- Certificate output: `runs/demo/certificate.txt` (when run with kiosk fixture)
- Evidence-to-commitment policy: `docs/_archive/EVIDENCE_TO_COMMITMENT_POLICY.md`
- Scope cuts and disclosed non-claims: `LIMITATIONS.md`
- Foundation modeling decisions: `docs/modeling_decisions/decisions_justification_map.md`

## When to update this document

- L1.1 ships real source document: replace the HYPOTHETICAL framing in Step 1 with real-document framing; replace the narrative ledger with the programmatic ledger output.
- L4.8 parts 1-3 ship: remove the asterisks on Step 4-5 audit chain visibility items.
- M-Capability-1 / M-Aboutness-Config-1 / M-NameDiscipline-1 land: remove the asterisks on the corresponding downstream items; update the "what it would look like" section to reflect the now-implemented pieces.
- Gate 3 (L2.9) / Gate 2 (L2.10) tightening lands: remove the asterisks; update the axiom-shape references.
- Article 6(3) derogation handling tightens (Q7 promotes to a structural row): remove the asterisk; update the Step 5 certificate description.
