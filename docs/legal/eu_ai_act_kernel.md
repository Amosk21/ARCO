# EU AI Act Kernel — pinned legal text for every provision ARCO cites

**Regulation (EU) 2024/1689 (Artificial Intelligence Act), adopted text of 13 June 2024.**
CELEX: 32024R1689 — https://eur-lex.europa.eu/eli/reg/2024/1689/oj

**Rule (the Invariant-13 analog for legal text):** no EU AI Act quotation, provision name, or provision-content claim enters ARCO TTL, Python, SPARQL, or docs unless it grep-matches this kernel (verbatim blocks) or is explicitly cited as one of the labeled summaries below. Quoting from memory, from the 2021 Commission proposal, or from secondary sources is the legal-text equivalent of a wrong-version IRI. The "micro-enterprise exclusion" defect (a 2021-proposal provision carried into committed TTL as if it were adopted 5(b) text, removed 2026-06-10) is the precedent this rule exists to prevent.

**Verbatim provenance:** blocks marked VERBATIM are copied from a full-text capture of the adopted Regulation held in the project's local audit archive (`runs/audits/2026-05-14_eu_ai_act_full_text.md`; not tracked in the public repository) or, where noted, from in-repo constants independently re-verified verbatim against the adopted text during the 2026-06-10 audit's legal re-fetch pass. Blocks marked SUMMARY are accurate structural summaries verified against the adopted Regulation by that same re-fetch pass but are NOT verbatim — do not quote them as the Act's words. Replacing each SUMMARY with EUR-Lex verbatim is the open tail of register row X.18.

---

## Article 3 — Definitions

### Article 3(34) — biometric data [VERBATIM]

> 'biometric data' means personal data resulting from specific technical processing relating to the physical, physiological or behavioural characteristics of a natural person, such as facial images or dactyloscopic data;

### Article 3(35) — biometric identification [VERBATIM]

> 'biometric identification' means the automated recognition of physical, physiological, behavioural, or psychological human features for the purpose of establishing the identity of a natural person by comparing biometric data of that individual to biometric data of individuals stored in a database;

### Article 3(36) — biometric verification [VERBATIM]

> 'biometric verification' means the automated, one-to-one verification, including authentication, of the identity of natural persons by comparing their biometric data to previously provided biometric data;

Note: 3(36) is the clean 1:1 definition. It does NOT carry the "intended to be used" framing — that framing lives in Recitals 15/17 and the Annex III 1(a) carve-out.

### Article 3(41) — remote biometric identification system [VERBATIM]

> 'remote biometric identification system' means an AI system for the purpose of identifying natural persons, without their active involvement, typically at a distance through the comparison of a person's biometric data with the biometric data contained in a reference database;

### Article 3(42) — real-time remote biometric identification system [VERBATIM]

> 'real-time remote biometric identification system' means a remote biometric identification system, whereby the capturing of biometric data, the comparison and the identification all occur without a significant delay, comprising not only instant identification, but also limited short delays in order to avoid circumvention;

### Article 3(43) — post-remote biometric identification system [VERBATIM]

> 'post-remote biometric identification system' means a remote biometric identification system other than a real-time remote biometric identification system;

Note: 3(42)/(43) define SYSTEMS; ARCO's Process-subclass translation is disclosed at LIMITATIONS §3.7.c.

### Article 3(1) — AI system [SUMMARY — verbatim import pending]

Defines "AI system" as a machine-based system designed to operate with varying levels of autonomy, that may exhibit adaptiveness after deployment, and that infers from inputs how to generate outputs (predictions, content, recommendations, decisions) that can influence physical or virtual environments. Recital 12 excludes simpler traditional software and rule-based systems whose behavior is fully specified by humans. ARCO does NOT evaluate this threshold (LIMITATIONS §1, §2).

### Article 3(12) — intended purpose [SUMMARY — verbatim import pending]

The use for which an AI system is intended by the provider, including the specific context and conditions of use, as specified in the information supplied by the provider in the instructions for use, promotional or sales materials and statements, and in the technical documentation. Anchors ARCO's `:IntendedUseSpecification` (gov:278-292).

### Article 3(13) — reasonably foreseeable misuse [SUMMARY — verbatim import pending]

Use of an AI system in a way not in accordance with its intended purpose but which may result from reasonably foreseeable human behaviour or interaction with other systems. NOT modeled by ARCO (LIMITATIONS §2 non-goal).

---

## Article 6 — Classification rules for high-risk AI systems

### Article 6(1) [SUMMARY — verbatim import pending]

First high-risk route, independent of Annex III: an AI system is high-risk where (a) it is a safety component of a product, or is itself a product, covered by the Union harmonisation legislation listed in Annex I, AND (b) that product is required to undergo third-party conformity assessment under that legislation. **ARCO does not model this route** (LIMITATIONS §2); ARCO's `regime` strings must say "Article 6(2) / Annex III", not bare "Article 6".

### Article 6(2) [VERBATIM FRAGMENT — provenance: 2026-06-10 audit legal gap-fill re-fetch of the adopted Regulation; not contained in the in-repo capture]

> "AI systems referred to in Annex III shall be considered to be high-risk"

(in addition to the 6(1) systems). This is the route ARCO encodes.

### Article 6(3) [SUMMARY — verbatim import pending]

Derogation: an Annex III system shall not be considered high-risk where it does not pose a significant risk of harm to the health, safety or fundamental rights of natural persons, including by not materially influencing the outcome of decision making — where the system (a) performs a narrow procedural task; (b) improves the result of a previously completed human activity; (c) detects decision-making patterns or deviations without replacing or influencing the human assessment; or (d) performs a preparatory task. **Override: an Annex III system that performs profiling of natural persons is ALWAYS considered high-risk** (no derogation available). ARCO surfaces `:DerogationClaim` artifacts for human review and does not evaluate validity; the profiling override is not separately modeled (LIMITATIONS §2).

### Article 6(4) [SUMMARY — verbatim import pending]

A provider who considers an Annex III system not high-risk under 6(3) shall document its assessment before placing on the market / putting into service, and shall register the system per Article 49(2). Not modeled or surfaced by ARCO.

---

## Article 25 — Responsibilities along the AI value chain [SUMMARY — verbatim import pending]

A distributor, importer, deployer or other third party is considered a provider of a high-risk system (taking on provider obligations) where they put their name or trademark on it, make a substantial modification to it, or modify its intended purpose such that it becomes high-risk. Not modeled by ARCO (LIMITATIONS §6); the deployer-modifies-system case is stress case 6 of the 2026-06-10 audit.

---

## Article 43 — Conformity assessment

### Article 43(1) [SUMMARY with VERBATIM FRAGMENTS — fragment provenance: 2026-06-10 audit legal gap-fill re-fetch; not contained in the in-repo capture; full verbatim import pending]

For high-risk systems listed in Annex III point 1 (biometrics): where the provider has applied harmonised standards (Article 40) or, where applicable, common specifications (Article 41), the provider shall OPT for one of:

> "(a) the internal control referred to in Annex VI; or (b) the assessment of the quality management system and the assessment of the technical documentation, with the involvement of a notified body, referred to in Annex VII."

The notified-body route is mandatory only where harmonised standards do not exist / were not (fully) applied / common specifications are unavailable. **Notified-body involvement for Annex III point 1 systems is therefore CONDITIONAL, not automatic** — the unconditional certificate sentence corrected 2026-06-10 (`run_pipeline.py:1378`) is the precedent.

### Article 43(2) [VERBATIM FRAGMENT — provenance: 2026-06-10 audit legal gap-fill re-fetch of the adopted Regulation; not contained in the in-repo capture]

For high-risk systems in Annex III points 2-8:

> "providers shall follow the conformity assessment procedure based on internal control as referred to in Annex VI, which does not provide for the involvement of a notified body."

---

## Annex III — High-risk AI systems referred to in Article 6(2)

### Chapeau + category 1 [VERBATIM]

> High-risk AI systems pursuant to Article 6(2) are the AI systems listed in any of the following areas:
>
> 1. Biometrics, in so far as their use is permitted under relevant Union or national law:
>
> (a) remote biometric identification systems.
> This shall not include AI systems intended to be used for biometric verification the sole purpose of which is to confirm that a specific natural person is the person he or she claims to be;
>
> (b) AI systems intended to be used for biometric categorisation, according to sensitive or protected attributes or characteristics based on the inference of those attributes or characteristics;
>
> (c) AI systems intended to be used for emotion recognition.

Notes: the category-1 chapeau conditionality ("in so far as their use is permitted…") is not modeled or surfaced by ARCO (LIMITATIONS §2). Adopted 1(a)'s operative subject is "remote biometric identification systems" — purpose-keyed via Article 3(41), NOT via the "AI systems intended to be used for…" template; do not paraphrase 1(a) into that template (the `generate_walkthrough.py` defect corrected 2026-06-10).

### Point 5(b) [VERBATIM — provenance: verified verbatim against the adopted Regulation by the 2026-06-10 audit legal gap-fill agent; this kernel is the tracked carrier (the in-repo capture truncates Annex III items 2-8)]

> AI systems intended to be used to evaluate the creditworthiness of natural persons or establish their credit score, with the exception of AI systems used for the purpose of detecting financial fraud.

Note: the fraud-detection carve-out is the ONLY exception clause in adopted 5(b). There is no micro-enterprise exclusion in the adopted text (2021-proposal remnant; scrubbed from the repo 2026-06-10).

---

## Recitals (biometrics)

### Recital 15 (excerpt) [VERBATIM]

> This excludes AI systems intended to be used for biometric verification, which includes authentication, whose sole purpose is to confirm that a specific natural person is the person he or she claims to be and to confirm the identity of a natural person for the sole purpose of having access to a service, unlocking a device or having security access to premises.

### Recital 17 (excerpts) [VERBATIM]

> The notion of 'remote biometric identification system' referred to in this Regulation should be defined functionally, as an AI system intended for the identification of natural persons without their active involvement, typically at a distance, through the comparison of a person's biometric data with the biometric data contained in a reference database, irrespectively of the particular technology, processes or types of biometric data used.

> This excludes AI systems intended to be used for biometric verification, which includes authentication, the sole purpose of which is to confirm that a specific natural person is the person he or she claims to be and to confirm the identity of a natural person for the sole purpose of having access to a service, unlocking a device or having security access to premises. That exclusion is justified by the fact that such systems are likely to have a minor impact on fundamental rights of natural persons compared to the remote biometric identification systems which may be used for the processing of the biometric data of a large number of persons without their active involvement.

### Recital 22 — what it is actually about [VERBATIM EXCERPT]

> In light of their digital nature, certain AI systems should fall within the scope of this Regulation even when they are not placed on the market, put into service, or used in the Union.

Recital 22 concerns EXTRATERRITORIAL SCOPE (third-country operators whose AI output is used in the Union). It is NOT a basis for the biometric verification carve-out; citing it for the carve-out was a recurring miscitation corrected in the 2026-05-14 citation audit.

---

## Where each provision is load-bearing in ARCO

| Provision | ARCO surface |
|---|---|
| Art 3(35) | `:BiometricIdentificationProcess` genus (gov:337-341) |
| Art 3(36) | `:BiometricVerificationProcess` / `:BiometricVerificationCapability` carve-out classes |
| Art 3(41) | `:RemoteBiometricIdentificationProcess` (Gate 2 target, 1(a)) |
| Art 3(42)/(43) | real-time/post subclasses + disjointness (gov:349-379) |
| Annex III 1(a) | `:AnnexIII1aApplicableSystem`, `:AnnexIII_Condition_1a` |
| Annex III 5(b) | `:AnnexIII5bApplicableSystem`, `:AnnexIII_Condition_5b`, fraud flag |
| Art 6(2) | `:HighRiskSystem` regime framing; certificate REGIME line |
| Art 6(3) | `:DerogationClaim` + `flag_derogation_candidate.sparql` (flag only) |
| Art 43(1)/(2) | certificate obligations panel (static text) |
| Art 3(12) | `:IntendedUseSpecification` definition |
