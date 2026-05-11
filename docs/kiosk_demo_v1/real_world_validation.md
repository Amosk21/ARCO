# Kiosk Demo v1 — Real-World Validation

**Question.** Is the proposed framing — "ARCO's value comes from adjudicator hardware-level review distinguishing verification-capable from identification-capable systems" — actually grounded in how real biometric kiosks work, and would it provide real value to a real audience?

## 1. Verdict

**ARTIFICIAL** for the proposed hardware-disposition framing. **GROUNDED** for an alternative framing the same demo can carry without code changes.

The 1:1 / 1:N distinction is, on every vendor surveyed, a software/configuration boundary on the same hardware. Camera, sensor, and template-extraction pipeline are shared; mode is a database/matching-policy setting. The EU AI Act anchors high-risk classification on **"intended to be used"** language, not on hardware structure. An adjudicator reviewing a spec sheet cannot conclude "this hardware is structurally limited to 1:1," because, on these devices, it is not.

The demo's load-bearing value still exists — but in the *input mile* (source-text → reviewed commitment → entailment audit), not in hardware-disposition adjudication.

## 2. Vendor evidence

| Vendor / Product | 1:1 vs 1:N disclosure | Configurable on same hardware? |
|---|---|---|
| Suprema FaceStation F2 | Spec table lists distinct user capacities for "1:N mode" (50,000 face) and "1:1 mode" (100,000 face); same device, same camera ([Suprema product page](https://www.supremainc.com/en/hardware/fusion-multimodal-terminal-facestation-f2.asp)) | Yes — both modes on one terminal |
| ZKTeco ProFace X (SL) | Marketed for 1:N (30k–50k templates); manuals show 1:1 mode entry from main interface ([ZKTeco product page](https://zkteco.technology/en/product/proface-x-sl/)) | Yes — software-selectable |
| Matrix COSEC ARGO FACE | "100,000 users and 200,000 face templates supporting both 1:1 and 1:N verification modes" ([Matrix product page](https://www.matrixcomsec.com/product/cosec-argo-face-door-controllers/)) | Yes — same controller |
| HID Amico | Described as "1:N face verification, 10,000 → 100,000 with license" — capacity is a license/SKU axis, not a hardware axis ([HID product page](https://www.hidglobal.com/products/amico)) | Capacity gated by license, not hardware |
| IDEMIA VisionPass / VisionPass SP | 2D + 3D + IR optics; 20,000 user records, 250,000 IDs in authorized list, 1M transaction logs ([IDEMIA brochure landing](https://www.idemia.com/facial-recognition-access-control), [VisionPass SP datasheet PDF](https://www.idemia.com/wp-content/uploads/2024/01/brochure-visionpass-sp-idemia-12012024.pdf)) | Same optics serve verification and authorized-list workflows |

What product pages do **not** uniformly disclose: image-sensor resolution as a numeric MP figure, algorithm version (e.g. NIST FRVT submission ID), template-extraction model parameters, or a database schema. Spec sheets list capacities and recognition speed; they do not give an adjudicator a structural mode lock.

## 3. Hardware vs software boundary

NIST distinguishes the two as algorithmic test tracks ([FRTE 1:1 Verification](https://pages.nist.gov/frvt/html/frvt11.html), [FRTE 1:N Identification](https://pages.nist.gov/frvt/html/frvt1N.html)) — a vendor submits the same model to either evaluation; the boundary is a matching-policy boundary, not a sensor boundary. Industry survey material confirms that "modern facial recognition access control hardware is typically designed to support both 1:1 and 1:N verification modes through software configuration" ([CyberLink FaceMe guide](https://www.cyberlink.com/faceme/insights/articles/473/build-an-access-control-system-with-facial-recognition-technology), [Innovatrics SmartFace](https://www.innovatrics.com/face-recognition-solutions/smartface-facial-access-control/)).

Implication for ARCO's BFO commitment: the hardware-software amalgam *does* bear a disposition, but the disposition that maps to Annex III 1(a) is "configured + deployed for 1:N matching against an enrolled database." That disposition is a property of the configured system + database state, not of the bare device. Calling the bare hardware a `BiometricVerificationCapability` bearer is reasonable for a specifically configured deployment; it is not licensed by the spec sheet alone.

## 4. Who actually benefits

Annex III 1(a) carves out systems "intended to be used for biometric verification the sole purpose of which is to confirm that a specific natural person is the person he or she claims to be" ([Annex III 1(a)](https://artificialintelligenceact.eu/annex/3/), [Recital 15](https://ai-act-law.eu/recital/15/)). The trigger word is "intended." Article 3 keys verification on the 1:1 modality; Recital 15 expands the carve-out to access-to-service / device-unlock / premises-access purposes ([Article 3 definitions](https://artificialintelligenceact.eu/article/3/)).

So the realistic audience splits:

- **Vendor compliance / DPIA author.** Needs to evidence "intended purpose = verification only" with documentation tying the kiosk's configured deployment to the 1:1 modality. ARCO's per-claim source-licensure trail (Section C of `decision_packet.md`) is directly useful here.
- **Enterprise compliance team doing pre-deployment review.** Needs the same evidence chain for procurement DPIA ([GDPR DPIA framework](https://learn.microsoft.com/en-us/compliance/regulatory/gdpr-data-protection-impact-assessments)). Cares about *intended-use commitments*, not hardware adjudication.
- **EU AI Office / notified body.** Biometric-system conformity assessment is third-party-assessed, not pure self-assessment ([Bird & Bird overview](https://www.twobirds.com/en/insights/2023/global/biometrics-under-the-eu-ai-act)). They want a re-derivable evidence trail and disclosure of misuse risk, not a hardware-mode certificate.
- **Adjudicator reviewing spec-sheet hardware fields.** Not a real role on this question. The hardware fields do not carry the determination.

## 5. (skipped — verdict is not GROUNDED)

## 6. Refined framing

Drop "hardware-disposition adjudication" as the headline. Keep the existing `ARCO_instances_verification.ttl` fixture; its commitments hold under a corrected story:

**Headline.** "ARCO turns a vendor's *intended-use* claims into a re-derivable, OWA-bounded entailment chain. The same kiosk hardware can be configured 1:1 or 1:N; what makes Annex III 1(a) inapplicable is the asserted intended purpose plus the configured matching policy, both committed in the graph and adjudicable by a reviewer." 

**What changes in the demo.** Source-packet C1–C5 (`decision_packet.md`) emphasizes the *intended-purpose* and *configured-database* facts the fixture commits, not "the hardware structurally cannot identify." `:Kiosk_VeriComp_Disposition` stays as `BiometricVerificationCapability` but the `rdfs:comment` on `:Kiosk_VeriComp_Module` is tightened to "configured for 1:1 matching against per-user enrolled references; not configured for 1:N database matching." F2 already refuses closed-world hardware-incapability claims; that refusal becomes the demo's headline, not a footnote.

**What stays the same.** The chain: source packet → reviewed commitment → entailment audit → certificate that names what it does and does not claim. That value is real and currently undemonstrated for any ARCO fixture.

Word count: ~770.
