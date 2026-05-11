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
