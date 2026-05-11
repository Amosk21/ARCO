# Kiosk Demo v1 — Source Packet (HYPOTHETICAL)

**HYPOTHETICAL.** This document is a hypothetical vendor product description created for the ARCO kiosk demo. It does not represent any specific real product. Vendor framing patterns are drawn from publicly observable conventions in the corporate biometric access kiosk market (Suprema, ZKTeco, Matrix, HID, IDEMIA), per `real_world_validation.md`. The document is structured to license the reviewed commitments already asserted in `03_TECHNICAL_CORE/ontology/ARCO_instances_verification.ttl`.

---

## Product Description

**Corporate Access Kiosk** is a biometric verification kiosk for corporate office building access. The product is intended for use at building or floor entry points to verify the identity of pre-enrolled employees against their enrolled reference template.

## Operation

When a pre-enrolled employee approaches the kiosk, the verification module captures a face image and compares it against the single reference template stored for that employee. The system returns a match or no-match decision. The employee is then permitted or denied entry to the access-controlled space.

The system operates in 1:1 verification mode only. Each transaction matches a presented face against the one reference template associated with the claimed identity. The claimed identity is provided externally (badge tap or PIN entry) before the face capture step. The system does not perform 1:N identification against a database of all enrolled employees, does not enroll walk-up persons whose identity is not pre-registered, and does not log or match faces of unknown individuals.

## Configuration (this deployment)

- Verification mode: 1:1
- Reference template source: pre-enrolled employee record
- Identification mode: not enabled in this deployment
- Database structure: per-employee single-template store, keyed by employee ID
- Affected population: pre-enrolled employees presenting a claimed identity at the kiosk

## Provider

Provider organization: Example Access Solutions (HYPOTHETICAL). The provider has produced an assessment documentation package describing the system's intended use, configuration, and scope.

## Scope refusal (what this document does not claim)

This document does not claim that the underlying hardware is structurally incapable of identification. The hardware (camera, face-recognition algorithm, processor) is software-configurable; in a different deployment, with a different reference-template store and a different matching policy, the same hardware could be configured for identification mode. This document describes THIS specific deployment under the verification configuration. Annex III 1(a) of EU Regulation 2024/1689 classifies by intended use (Article 3(36); Recital 15), not by raw hardware capability, so the scope of this document is the deployment, not the hardware in isolation.

## What becomes real when the source is real

This source packet is HYPOTHETICAL. The vendor name, the product name, the operation description, the configuration details, all of it is composed for the demo. The point of writing it as HYPOTHETICAL rather than as undeclared fiction is that every commitment in the packet is structurally identical to a commitment a real source document would license. When a real published kiosk specification arrives (a vendor product page, an EU AI Act compliance filing, a public NIST AI RMF example), the conversion is mechanical. Replace HYPOTHETICAL prose with real document citations, and add three triples to the fixture that close the realist chain back to the real document.

The three triples that become real-asserted, with the slot pattern reserved in `03_TECHNICAL_CORE/ontology/ARCO_instances_verification.ttl` section 5:

1. **The source document particular.** A typed instance of the real document (a material entity in BFO terms) with file hash, retrieval timestamp, and citation. Currently `:Kiosk_SourceDoc_PLACEHOLDER` in commented-out form. When real, replaced with the actual file IRI, hash, and metadata.

2. **The inscription on that document.** A typed instance of the inscription quality (a specifically dependent continuant). It inheres in the document particular and characterizes its pattern. Currently `:Kiosk_SourceDoc_Inscription_PLACEHOLDER` in commented-out form.

3. **The concretization link.** The inscription concretizes the IntendedUseSpecification and the UseScenarioSpecification via `bfo:0000059` (BFO 2020 "concretizes"). This is the triple that closes the chain. The specification information artifacts are no longer floating; they exist by being concretized in a real document particular.

What this design accomplishes even while HYPOTHETICAL. Three commitments are visible in the fixture today, even before the source is real:

- The specification information artifacts need bearer particulars. The slots are reserved with placeholder IRIs.
- The realist chain has a complete structural shape. The commented-out block shows what fills in.
- The kind of real-world artifact that fills each slot is named. A document file, an inscription quality, a concretization triple.

When a real document arrives, the work to convert this demo from a structural template to a working applied case is not "rewrite the source packet from scratch." It is "fill in the slots." The same applies to the equivalent slot on the pipeline-emitted side (tracked at `OPEN_PROBLEMS.md` L2.2), which links the output determination information artifact to the certificate file the pipeline writes. Both ends of the chain anchor in real-world particulars then.
