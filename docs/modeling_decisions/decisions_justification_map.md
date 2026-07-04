# Modeling Decisions and Their Justifications

## Purpose

Every modeling decision in ARCO is open to challenge with traceable evidence (the Fallibilism conviction). A reader who wants to challenge a decision should be able to walk to the file, line, or canon citation that defends it. This map is that walk: each load-bearing decision, the plain-English rationale, and the canonical anchor it rests on.

The map is tested against the same accuracy bar as the three diagram files in this folder. Where a decision rests on multiple anchors, all are listed. TTL line anchors were re-verified 2026-05-26 against the working tree after the X.13 annotation pass; `LIMITATIONS.md` section anchors were not re-checked in that pass, and the governance anchors below line 385 (S5, S7, I3, I4) will shift again when the queued X.14 pass lands.

## How to use this map

- **Before challenging a decision**: read the anchor and the cited section. The decision is defensible if the anchor holds; the work to challenge it is to argue against the anchor, not the decision.
- **Before authoring a new decision**: check whether an existing decision already covers the case. If yes, follow the existing pattern. If no, draft the new decision with its anchor before any TTL changes.
- **Before disclosing a new limitation**: check whether the limitation is implicit in an existing decision here. Often the decision IS the disclosure (e.g., "component-level bearer is a design choice; whole-system would also be defensible").

---

## Foundational decisions (project-level)

These flow from ARCO's foundational disciplines and govern everything else. They are not subject to per-PR re-litigation.

### F1. ARCO surfaces latent dispositions at design time

The hardware bears a capability disposition whether or not the disposition is currently being realized. ARCO uses BFO-grounded reasoning to entail Annex III applicability from a reviewed system description, before runtime, with two-reasoner cross-check.

**Anchor**: ARCO's stated target (surface latent dispositions at design time); operationalized throughout the technical core (`ARCO_core.ttl`, `ARCO_governance_extension.ttl`) and visualized in `value_chain.md`.

**Why it matters**: This is ARCO's stated value proposition. Any modeling decision that breaks the latent-disposition framing collapses ARCO into regulatory pattern-match search instead of BFO-grounded classification. See F2 for the load-bearing parent class choice that protects this.

### F2. `:Capability ⊑ bfo:0000016 (Disposition)`, not `bfo:0000034 (Function)`

ARCO targets the latent capability the bearer's physical make-up grounds, regardless of whether the make-up was designed for that purpose. Function is a disposition-subkind whose physical make-up exists *for that purpose*; typing capability as Function would narrow ARCO out of the latent case (a hardware that physically grounds biometric capacity without being designed-for-it would not bear a Function but does bear a Disposition).

**Anchor**: `ARCO_core.ttl:124-127` (`:Capability ⊑ bfo:0000016` declaration; rationale comment at `:28`); BFO 2020 [064-001] Function elucidation at `bfo-2020.owl:1326-1327`.

**Why it matters**: Disposition admits both latent-only capacities AND designed-for functions as subkinds. Function would exclude the latent case. Terminal choice, not deferred upgrade.

### F3. Reality ≠ Representation

Capabilities are BFO dispositions inhering in independent continuants. Intended uses and use scenarios are IAO/CCO information content entities (ICEs). The split is load-bearing for the whole architecture; collapsing it makes "what the system can do" and "what documents say" indistinguishable.

**Anchor**: `LIMITATIONS.md §3.6` (lines 118-120, the Reality / Representation split); enforced at materialization time by BFO 2020 standard disjointness between Independent Continuant and Generically Dependent Continuant; binding mechanism verified by `03_TECHNICAL_CORE/scripts/probe_disjointness_and_binding.py`.

**Why it matters**: Every modeling decision that crosses this line (putting a disposition on an ICE, or a specification on a hardware component) quietly breaks ARCO's classification guarantees.

### F4. OWL-RL + SHACL + SPARQL only; no LLMs in classification

ARCO is deterministic. LLMs may assist source extraction (out of v1 scope per policy) but never participate in classification. The reasoner produces entailments; SPARQL audits the reasoned graph; SHACL validates documentary structure.

**Anchor**: ARCO's two-layer rule: OWL-RL materializes classification entailments; SPARQL audits the reasoned graph. The rule is operationalized in `03_TECHNICAL_CORE/reasoning/` SPARQL files (audit) and in the OWL-RL closure inside `run_pipeline.py` (classification).

**Why it matters**: A non-deterministic classifier cannot be challenged at the triple level (Fallibilism failure). Deterministic-by-construction is the discipline that makes the certificate defensible.

### F5. Source documents don't directly become reality

No automated extraction writes to reality-side ARCO instance TTL. Source documents may generate `cco:DescriptiveICE` claim artifacts; promotion of a claim to a reality-side commitment is rare, conditional, and human-adjudicated.

ARCO commits to no automated extraction writing reality-side instance TTL.

**Why it matters**: The realism conviction. Asserting reality-side commitments from unreviewed source text would be fake-witness creation at scale. The human-adjudication step IS the warrant.

### F6. No fake-witness creation

Adding participant facts, temporal regions, sites, or role-bearer particulars to ARCO instance data is forbidden when source evidence does not warrant them. Hand-authored fixtures (Sentinel, adversarial fixtures) cannot host runtime-shaped commitments. The legitimate place to ask participant-asserting questions is a fixture with source-document warrant.

**Anchor**: ARCO's modeling discipline (no participant facts, no temporal regions, no role-bearer particulars without source warrant); reinforced by `LIMITATIONS.md §3.1` (NaturalPersonRole universal-designation pattern; bearer-less role tokens explicitly avoided).

**Why it matters**: A graph full of fake witnesses looks more populated but is structurally false. The discipline accepts honest sparseness over dishonest completeness.

### F7. CCO v1.7-2024-11-03 pin (readable IRIs)

ARCO uses readable v1.7 IRIs (`cco:Person`, `cco:InformationBearingEntity`, `cco:designates`). The post-v1.7 release line (CCO v2.0-2024-11-06 introduced the namespace migration; current upstream is v2.1-2026-04-04) switched to ont-numbered IRIs (`cco:ont00000016`, `cco:ont00000253`, `cco:ont00001017`, etc.) under the new canonical namespace `https://www.commoncoreontologies.org/`. ARCO does NOT import this v2.x line. Canon-checks against the wrong version's IRIs are a canon hallucination of the same shape as wrong-direction BFO predicates.

**Anchor**: `ARCO_governance_extension.ttl:16` (CCO version pin in `owl:versionInfo`); the CCO v1.7-2024-11-03 readable-IRI pin governs all CCO references in ARCO TTL.

**Why it matters**: Cross-references between ARCO and external work (abi, Tradecraft, both of which track the v2.x line) fail silently if the version isn't pinned and tracked explicitly. The pin is deliberate (stay-on-v1.7 preserves namespace stability across ARCO instance fixtures); migration to v2.x is future work that activates only on an external constraint (real source document references v2.x classes, partner standardizes on v2.x, or v1.7 falls out of upstream tooling support).

---

## Structural decisions (class hierarchy and relations)

### S1. `:System ⊑ bfo:0000027 (Object Aggregate)`

ARCO treats a system as an aggregate of material hardware components. Defensible for component-level disposition tracing. Some systems (cloud-native, SaaS, purely software-as-a-service) don't decompose cleanly as material aggregates; the pattern may need adjustment for those.

**Anchor**: `ARCO_core.ttl:22-24` (design-decision comment); `LIMITATIONS.md §3.4` (line 106-108).

**Quote from LIMITATIONS §3.4**:
> "Many AI systems decompose cleanly as aggregates of material hardware components. Some (cloud-native, service-like, or purely software-as-a-service) do not. BFO does not compel either choice. ARCO commits to the aggregate pattern because it enables component-level capability tracing and produces meaningful evidence paths. A different system pattern (e.g., system as `MaterialEntity` without aggregate decomposition) would also be defensible..."

**Why it matters**: Kiosk-shaped systems fit cleanly. Cloud AI / model-as-a-service systems don't. The pattern is shape-fit for ARCO's current scope; cloud extension is future work.

### S2. Component-level bearer for Gate 1 capability

The capability disposition is located on a `SystemComponent`, not on the `System` itself. This produces evidence paths the certificate can show: "system → component → disposition → triggering capability." A whole-system bearer would also be ontologically defensible (BFO allows ObjectAggregates to bear dispositions) but loses the granularity to say *which specific part* of the system bears the regulated capability.

**Anchor**: `LIMITATIONS.md §3.5` (lines 110-116, the three-stacked rationale).

**The three-stacked rationale** from `LIMITATIONS §3.5`:

1. **Traceability primary**: "Gate 1 locates the capability disposition on a `SystemComponent`, not on the `System` itself. This is a design choice for traceability: it produces evidence paths like 'system → component → disposition → triggering capability.' The EU AI Act talks about systems, not hardware subcomponents. A whole-system bearer pattern would also be ontologically defensible. The component-level choice is not legally compelled."

2. **Hardware-software amalgam is the deeper realist target ARCO simplifies away from**: "for a model-driven biometric module, the in-repo Sentinel fixture types the bearer as `:HardwareComponent` only, but a strict realist reading would locate the disposition on the *amalgam* of hardware plus the concretized model artifact running on it. The 2024 Capabilities paper's hardware-software-amalgam discussion treats software qua pattern as a generically dependent continuant, not itself a capable continuant; capabilities require a material bearer that concretizes the pattern. ARCO's classification result does not depend on which of these two bearer choices is taken..."

3. **Software-configurable hardware is where the choice matters most**: "for software-configurable AI systems where the same hardware can be configured for different modes (e.g., 1:1 verification vs 1:N identification on the same biometric kiosk hardware), the disposition assertion describes what THIS specific deployment is intended to do under its current commitments, not what the hardware-in-isolation could theoretically do. ARCO does not make closed-world hardware-incapability claims; per-fixture disposition assertions reflect the configured-system commitments under OWA. A different deployment of the same hardware (different configuration, software, or database) would be modeled as a separate `:System` instance with its own asserted disposition. This matches the EU AI Act's classification on intended use (Article 3(36), Recital 15), not on raw hardware capability."

**Empirical grounding**: §3.5 names five biometric kiosk vendors (Suprema, ZKTeco, Matrix, HID, IDEMIA) whose hardware advertises configuration for both 1:1 and 1:N modes, validating the software-configurable framing against real product documentation.

**Why it matters**: The user's intuition that "the whole system isn't always the right way to model that" lands hardest on point (3). Software-configurable hardware can't be modeled as "the system has capability X" without losing the configuration-dependence. Per-`:System` modeling with component-level disposition gives ARCO the granularity to say "THIS deployment, configured this way, bears this disposition" while declining (under OWA) to claim what the hardware could be configured to in some other deployment.

### S3. `:AnnexIIITriggeringCapability` as regulatory fiat partition (owl:unionOf), not natural kind

There is no mind-independent property shared by all "triggering capabilities" in reality. What makes a capability "triggering" is the legal text of Annex III. ARCO models this as a defined class whose extension is fixed by `owl:unionOf` over the listed member capability classes. Each member IS a real BFO disposition (subclass of `:Capability`); the grouping is by extrinsic regulatory criterion under Article 6.

**Anchor**: `ARCO_governance_extension.ttl:219-232` (class declaration + rdfs:comment + owl:unionOf); `LIMITATIONS.md §3.2` (regulatory grouping disclosure).

**Why it matters**: Treating the grouping as a primitive subsumption would be Realism conviction failure: there is no real shared property to subsume by. ARCO's fiat partition model (cut + bearer + consequence) is the BFO-defensible move when membership is institutional, not natural.

### S3a. Regulatory fiat-boundary annotation pattern (machine-readable provenance)

Building on S3's fiat-partition framing, ARCO marks regulatory fiat boundaries with machine-readable annotations rather than only prose. Each regulatory universal carries `:hasRegulatoryBasis` (a subproperty of both `cco:doctrinal_source` and `cco:definition_source`) with two values per class: a human-readable citation as `@en` literal and the EUR-Lex CELEX URI as `xsd:anyURI`. Full CCO v1.7 declares `cco:doctrinal_source` as a subproperty of `cco:definition_source`; ARCO states both parent links locally because the BOT slim extraction does not preserve that annotation-property hierarchy. Each class also carries `skos:scopeNote` with the fiat-extension prose. The same pattern applies via OWL Axiom reification to two disjointness axioms: capability identification vs verification (`ARCO_core.ttl`) and real-time vs post remote biometric identification process (`ARCO_governance_extension.ttl`).

The fiat/bona-fide boundary distinction from the mereotopology literature is used analogically. The original distinction targets spatial boundaries (the line between Kansas and Colorado, the surface of an organism). ARCO borrows the methodological pattern (partition by extrinsic regulatory criterion rather than natural joint; cut + bearer + consequence) and applies it to regulatory extension partitions over universals. The analogy is disclosed explicitly here so a reader does not assume ARCO is literally minting BFO `Continuant Fiat Boundary` instances.

Working-precedent note (2026-05-24): no direct working-code precedent was found in the CCO-aligned reference implementations surveyed or in IOF Core for this exact regulatory-fiat-universal annotation pattern. IOF Core verifies the broader documentary-ICE pattern for specifications, agreements, plans, and objectives; it does not verify this specific regulatory-fiat labeling move. ARCO therefore defends S3a on the fiat/bona-fide theoretical grounding, canonical CCO citation predicates, and the four-conviction check, not on a claim that existing reference implementations already use the exact pattern.

`:hasRegulatoryBasis` is minted as a narrow annotation-only exception to Invariant 6 (no custom properties), documented at the property declaration in `ARCO_core.ttl`. The property does not participate in classification, object-property reasoning, or BFO relation modeling. It propagates only via OWL-RL subproperty closure as inferred `cco:doctrinal_source` triples and inferred `cco:definition_source` triples — CCO consumers querying either the sharper doctrinal-source predicate or the broader definition-source predicate find the regulatory citations transparently.

Enforcement is review-based in this patch. SHACL shape requiring `:hasRegulatoryBasis` on every regulatory universal is deferred; a future contributor adding a new Annex III applicable-system class and forgetting the annotation will be caught only by code review until the SHACL gate lands.

**Anchor**: `ARCO_core.ttl` (property mint + capability disjointness axiom annotation); `ARCO_governance_extension.ttl` (four-class annotations + process disjointness axiom annotation); `OPEN_PROBLEMS.md` X.13 (fix tracking row); `OPEN_PROBLEMS.md` X.14 (second-pass extension to `:NaturalPersonRole`, `:DerogationClaim`, `:FraudDetectionProcess`); the fiat/bona-fide boundary distinction, used analogically; standard naming discipline: canonical-vocabulary deference (`cco:doctrinal_source` parent with upward closure to `cco:definition_source`) and terminological moderation (only one custom annotation property, narrowly scoped).

**Cross-references**: extends S3 (regulatory fiat partition); applies to S4 (`:HighRiskSystem` latent-flag annotation includes the pin-back scope-note "The class denotes systems bearing the triggering capability, not the act of flagging them"); applies to S7 (three-gate applicable-system classes); compatible with S5 (the `cco:designates owl:hasValue` Gate 3 pattern; OWL-punned individual reading per S5). Does NOT close L2.3 (file-header `dc:source` citation hygiene is a different shape).

**Why it matters**: makes fiat-boundary status machine-queryable rather than buried in `rdfs:comment` prose. A reviewer querying for "what regulatory text grounds this class" gets a typed answer via the canonical CCO predicates. The pattern is reproducible across other regulatory domains (FDA SaMD, GDPR Article 22, NIST 800-53) without renegotiating the canonical vocabulary. Empirically verified: in-memory simulation across all seven fixtures showed `classification_same = True`; after the `cco:doctrinal_source` tightening, each fixture gains 12 inferred `cco:doctrinal_source` triples plus 12 inferred `cco:definition_source` triples via subproperty closure, with no classification class memberships changed.

### S4. `:HighRiskSystem` as Gate-1-only latent flag, NOT the legal high-risk category

Membership fires from Gate 1 alone (capability precondition): the system has a SystemComponent bearing a disposition belonging to `:AnnexIIITriggeringCapability`. This is a latent-risk indicator, not the EU AI Act legal high-risk classification. The full Annex III applicability requires all three gates and is captured by category-specific applicable-system classes (`:AnnexIII1aApplicableSystem`, `:AnnexIII5bApplicableSystem`).

**Anchor**: `ARCO_governance_extension.ttl:241-266` (skos:definition + rdfs:comment + equivalentClass); `LIMITATIONS.md §3.3` (latent-flag disclosure); `ARCO_core.ttl:203-207` `:HighRiskDetermination` skos:definition (which records either kind of entailment).

**Why it matters**: The IRI `:HighRiskSystem` is retained for backward compatibility with downstream consumers, but the rdfs:label is "Annex III Capability-Precondition Flag" to reflect what the axiom actually entails. The certificate's PRIMARY (three-gate) vs LATENT-RISK FLAG (Gate-1 only) split is what makes this honest at the output layer.

### S5. `cco:designates owl:hasValue :NaturalPersonRole` for Gate 3 (no bearer-less role tokens)

Gate 3 references the role universal at the class-IRI level via `cco:designates owl:hasValue`. BFO Roles are bearer-dependent specifically dependent continuants requiring `ro:0000052` to an independent continuant. ARCO does not mint role-bearer particulars without source warrant; the designation pattern lets the gate reference the role category by its class IRI without inventing a bearer-less role token.

**Anchor**: `ARCO_governance_extension.ttl:534-554` (inline rationale block within the 1(a) Gate 3 axiom restriction); `LIMITATIONS.md §3.1` (Gate 3 role-category encoding via universal-designation, not bearer-less role token).

**Why it matters**: `cco:designates` carries no range declaration of its own in the pinned CCO; the `bfo:0000001` (Entity) range is inherited from its parent `cco:is_about`. Using the class IRI as the `owl:hasValue` filler makes it an OWL-punned individual: legal under OWL 2 DL, consumed by the entailment only in its individual interpretation, and not a use CCO itself documents (CCO's own examples all designate particulars: a URL designates a Web Page, a name designates a person). This category-designation reading is ARCO's documented modeling intent (LIMITATIONS §3.1), and it avoids fake-witness role tokens.

### S6. `ro:0000052 rdfs:subPropertyOf bfo:0000197` binding (PR #41)

ARCO commits RO's `characteristic_of` as a specialization of BFO 2020's `inheres_in` so the reasoner inherits BFO's IndependentContinuant range on the inferred inherence triple. RO removed the range to support qualities-of-processes and inherence in ICE; ARCO doesn't model those cases. Bounded enforcement: catches wrong-typed bearer only when typed as a disjoint sibling of IC.

**Anchor**: `ARCO_core.ttl:248-249` (the binding + rdfs:comment); `LIMITATIONS.md §3.8` (line 149+).

**Why it matters**: The binding is hub-and-spoke discipline applied at the property level: using RO's relation for assertions while inheriting BFO's stricter range for reasoning. The mirror direction (`ro:0000053 → bfo:0000196`, the bearer-of side) is NOT yet bound; the parallel-binding work is the next bridging step.

### S7. Three-gate axiom for Annex III applicability

`:AnnexIII1aApplicableSystem` and `:AnnexIII5bApplicableSystem` are defined classes via `owl:equivalentClass owl:intersectionOf`. Three gates: Gate 1 (reality, capability disposition via component), Gate 2 (representation, IUS prescribes regulated process via subkind), Gate 3 (representation, USS designates affected role universal). Each gate is independently necessary; classification is OWL-entailed, not pattern-matched.

**Anchor**: `ARCO_governance_extension.ttl:490-556` (1(a) full axiom); `ARCO_governance_extension.ttl:579-641` (5(b) parallel axiom); regression test `test_gate_removal.py` verifies gate independence; `docs/modeling_decisions/three_gate_classifier.md` (visual artifact).

**Why it matters**: The three-gate factoring is what makes ARCO answer "does this system satisfy Annex III?" as a formal entailment. The IUS subkind factoring (Gate 2 via defined-class type-check rather than ad-hoc process-token typing) mirrors the CCO Specification family pattern. The Gate 3 universal-designation pattern (S5) is the bearer-less role move.

### S8. ARCO ICEs are typed to the CCO three-D subtypes (Directive / Descriptive / Designative), not bare ICE

Every ARCO information artifact is refined from `iao:0000030` (Information Content Entity) to one of CCO's three speech-act subtypes, rather than left as a bare ICE. The regulation and the vendor's intended-use spec are **Directive** ICEs (they prescribe: world-to-word fit, a rule or guide for behavior): `:RegulatoryContent` and `:IntendedUseSpecification`. ARCO's own entailment records and the provider's claims are **Descriptive** ICEs (they report a state of affairs: word-to-world fit): `:InformationOutput`, `:ComplianceDetermination`, `:HighRiskDetermination` (via `:ComplianceDetermination`), `:DerogationClaim`. The use-scenario spec is a **Designative** ICE (it denotes the affected-role universal): `:UseScenarioSpecification`.

Bare ICE would be correct but mute. The subtype does three things bare ICE cannot. (1) It states what the artifact actually is: a regulation is a rule that prescribes, not a description of how the world is. (2) It licenses `cco:prescribes` (domain `DirectiveICE`), the property carrying "the regulation prescribes the regulated process kind" and "the IUS prescribes the intended process"; using `cco:prescribes` entails the `DirectiveICE` type via the domain under OWL-RL regardless. (3) The three subtypes are pairwise disjoint, so the reasoner rejects any graph that types the regulation (a directive) as a determination (a descriptive), or vice versa. That makes F3's reality/representation cut enforceable at the finer grain of rule-vs-finding-vs-name, all within representation.

**Anchor**: `ARCO_governance_extension.ttl:114-131` (three-D bridge declarations + the `:RegulatoryContent` / `:InformationOutput` / `:ComplianceDetermination` subtype mapping at 129-131); `:282` (`:IntendedUseSpecification ⊑ DirectiveICE`), `:328` (`:UseScenarioSpecification ⊑ DesignativeICE`), `:401` (`:DerogationClaim ⊑ DescriptiveICE`); `ARCO_core.ttl:187-207` (the ICE class declarations refined in governance); `cco_bot.owl:827-855` (three-D pairwise disjointness); `cco_bot.owl:437` (`cco:prescribes` domain `DirectiveICE`). The three-D taxonomy follows the classic direction-of-fit distinction from speech-act theory (directives have world-to-word fit; descriptives/assertives have word-to-world fit).

**Why it matters**: bare ICE would let the rule and the finding be the same kind of thing, and would not support `cco:prescribes`. This typing keeps "the regulation that sets the rule" formally distinct from "the determination ARCO produced about a system," and it is what the Gate 2 `prescribes` mechanism (S7) rests on. Extends F3 (Reality ≠ Representation) with the within-representation cut; the same regulatory classes also carry the S3a `:hasRegulatoryBasis` provenance annotation.

---

## Instance-level discipline decisions

### I1. Bare process tokens (no asserted participants beyond System)

ARCO's fixtures mint typed process individuals to satisfy Gate 2's `owl:someValuesFrom` existence-witness requirement. These tokens carry only the type assertion (no participants, no temporal region, no realizer, no output). The process has not unfolded at design time, so participants and temporal extent would be assertions of facts that are not true. ARCO declines to adorn tokens with placeholder context that would be known-not-true.

**Anchor**: `LIMITATIONS.md §3.7.a` (lines 126-128); OWA sparseness is not a category error (the bare token carries only its type assertion and is OWL-consistent under the design-time framing).

**Why it matters**: Under OWA, "no participants asserted" is silence about participants, not denial. The token is OWL-consistent. The architectural alternative (redesign Gate 2 to avoid token witnesses entirely) is Path Gamma, queued behind real-document warrant.

### I2. Real-time vs post RBI subclass scoped to future work

ARCO declares `:PostRemoteBiometricIdentificationProcess` and `:RealTimeRemoteBiometricIdentificationProcess` as subclasses of `:RemoteBiometricIdentificationProcess` for forward extensibility, but no fixture types into these subclasses. Article 5(1)(h) routing for real-time RBI (prohibited-practice classification) is not modeled. Under the current parent-class Gate 2, an IUS prescribing a real-time RBI particular would entail Annex III 1(a) applicability WITHOUT an Article 5 prohibition flag.

**Anchor**: `ARCO_governance_extension.ttl:349-362` (subclass declarations); `LIMITATIONS.md §3.7.c` (real-time routing scoped future); rdfs:comment on `:RemoteBiometricIdentificationProcess` at line 338 carries the DISCLOSURE inline.

**Why it matters**: This is a deliberate scope-narrowing. The classifier produces correct Annex III 1(a) entailment for current scope; future deployer-context modeling (law-enforcement deployer, publicly-accessible-space deployment) would activate Article 5 routing as a separate layer.

### I3. Article 6(3) derogation as provider-asserted ICE, not evaluated

`:DerogationClaim` is a Descriptive ICE representing a provider's claim that their system qualifies for the Article 6(3) derogation ("shall not be considered to be high-risk where it does not pose a significant risk of harm"). ARCO surfaces the claim in the audit layer (SPARQL flag) but does NOT evaluate validity. The ontology cannot evaluate whether a derogation claim is valid; that requires human legal judgment.

**Anchor**: `ARCO_governance_extension.ttl:420-423` `:DerogationClaim` rdfs:comment; explicit "PROVIDER-ASSERTED ARTIFACT" warning; "NEVER use this class as a gate condition or in an equivalentClass axiom."

**Why it matters**: The derogation evaluation is outside what an ontology can do. ARCO's discipline is to surface the claim for human review, not to silently fold it into the classification. The class is used by the audit layer only and is explicitly forbidden from gate axioms.

### I4. Fraud-detection exclusion (Annex III 5(b)) as provider-declared, not verified

Annex III 5(b) excludes "AI systems used for the purpose of detecting financial fraud" from creditworthiness applicability. ARCO's `:FraudDetectionProcess` class is used by the audit-layer SPARQL flag only; it does not participate in any OWL gate condition. The classification cannot be verified by the ontology; fraud-detection-as-primary-purpose is provider-declared.

**Anchor**: `ARCO_governance_extension.ttl:414-418` rdfs:comment.

**Why it matters**: Same pattern as I3. The ontology surfaces the relevant artifact for human review; the validity assessment is human judgment, not OWL entailment.

---

## Audit layer is audit, not classification

### A1. SPARQL queries audit the reasoned graph; they do NOT participate in entailment

OWL-RL classification fires on the closed graph. SPARQL ASK and SELECT queries report on what fired and on documentary content; they cannot change the classification.

**Anchor**: ARCO's two-layer rule (OWL-RL = classification; SPARQL = audit); reinforced in every Annex III applicability class rdfs:comment ("SPARQL ASK queries are downstream audit-layer checks; they do not contribute to this entailment and cannot affect it").

**Why it matters**: Folding entailment-gating into SPARQL emission SELECTs would invert the invariant. The two-layer rule is what makes the certificate auditable: the reasoner's answer is the answer; SPARQL shows the evidence.

### A2. HermiT OWL 2 DL cross-check verifies consistency

The certificate is grade-A only when OWL-RL closure (rule-based) AND HermiT (model-theoretic) agree. The HermiT cross-check runs in CI as a matrix workflow across all fixtures.

**Anchor**: `03_TECHNICAL_CORE/scripts/hermit_cross_check.py`; HermiT OWL 2 DL cross-check workflow at `.github/workflows/robot-validate.yml`.

**Why it matters**: OWL-RL is a profile that may admit models OWL 2 DL would rule out (and vice versa). The cross-check catches consistency issues a single reasoner would miss. Two-reasoner verification is ARCO's "show your work" mechanism.

---

## Pending modeling decisions (surfaced 2026-05-12 canon backtest)

The 2026-05-12 canon backtest surfaced three foundation-level modeling decisions that are NOT yet locked. They are sequenced ahead of the kiosk evidence-ledger demo so the correct modeling shapes bake into the kiosk fixture rather than requiring retrofit. Canon-anchored options are durable in `docs/CANON_BACKTEST_2026-05-12.md`.

### M-NameDiscipline-1. `:CapabilityDisposition` compositional naming

The class name `:CapabilityDisposition` is a compositional construction (Capability + Disposition) without an anchoring `:Capability` class in ARCO. Standard ontology naming discipline treats this pattern as undisciplined: when an ontology uses terms of the form `a † b`, it should also include the corresponding `a` and `b` terms.

**Resolutions**:
- R1: add `:Capability` as a separate class; demote `:CapabilityDisposition` to subclass or remove.
- R2 (preferred per Adequatism and the terminological-moderation naming discipline): rename `:CapabilityDisposition` to `:Capability`; let BFO subsumption (`:Capability ⊑ bfo:0000016`) carry the Disposition typing.

**Anchor**: `docs/CANON_BACKTEST_2026-05-12.md §D.2`.

**Why it matters**: This rename can ship independently of foundation map work; it is the smallest-cost M-decision but touches many files (TTL, SHACL, SPARQL, Python, tests). The name then says exactly what the axiom says, and nothing more.

### M-Capability-1. Interest modeling for capability accountability

The canonical capability framing is a disposition whose realization is associated with the interest of an organism or group. ARCO's `:Capability` currently models the disposition side only; there is no Interest hookup. Three canonical options surfaced:

- A: use `cco:has_interest_in` relation only. Domain `cco:Agent`; range `bfo:0000015` Process. Matches CCO v1.7 + the canonical relational treatment. No class minted; satisfies the terminological-moderation naming discipline.
- B: mint `:Interest ⊑ bfo:0000019` Quality per abi production extension (`CapabilityOntology.ttl:60-64`). Expands Bucket 2 from empty to populated. abi's `:bearerOfInterest` and `:hasInterestIn` over-mints must NOT be copied if this option is chosen (use BFO `bearer_of` and `inheres_in` instead).
- C: hybrid (Quality typing + canonical relation direction Interest to Process).

**Anchor**: `docs/CANON_BACKTEST_2026-05-12.md §B`.

**Why it matters**: Capability accountability for Annex III applicability needs an interest-bearing organism on the regulatory side (natural-person rights, deployer interest, and so on). Decision blocked on foundation map work.

### M-Aboutness-Config-1. Regulatory ICE aboutness target

Regulatory ICEs (`:AnnexIII_Condition_1a`, `:AnnexIII_Condition_5b`) need explicit `iao:is_about` targets. The canonical aboutness framing permits aboutness to portions of reality including configurations, but configurations are NOT BFO entities (Aboutness §2 line 65), which rejects any option that mints a `:SystemConfiguration` BFO class. Real options:

- B: universal-only target (`:AnnexIII_Condition_1a iao:is_about :AnnexIII1aApplicableSystem`).
- C-lite: particular continuant target (per-assessment, `:AnnexIII_Condition_1a iao:is_about :Sentinel_ID_System`).
- C-multi: multiple constituent targets (system + capability + IUS + USS together; configuration implicit in the typed relations among them).

C-multi is canonically richest per Aboutness §2 line 67. None of these require unlocking Bucket 5 (Immaterial Entity) or Bucket 6 (Temporal Region).

**Anchor**: `docs/CANON_BACKTEST_2026-05-12.md §C`.

**Why it matters**: Without an explicit `iao:is_about` target, regulatory ICEs float free of what they refer to. The aboutness assertion is what makes the regulatory layer cash out against specific system instances in the certificate. Decision blocked on foundation map work.

---

## What this map does NOT cover

- Implementation details of the pipeline, manifest, or schema versions (those live in `03_TECHNICAL_CORE/scripts/` and the output-provenance contract at `03_TECHNICAL_CORE/scripts/output_manifest_v2.yaml`)
- Per-fixture specifics (which fixture exercises which path): see `three_gate_classifier.md` fixture coverage table
- Future-work decisions that have been scoped but not committed (accountability extension, Article 5 routing, cloud system shape, and so on); those live as OPEN_PROBLEMS rows or conversation queues, not yet here
- Decisions that flow obviously from BFO/CCO/RO/IAO without ARCO-specific tradeoff (e.g., using `iao:0000136` (is_about) for ICE-to-system aboutness is canonical and needs no per-decision defense)

## When to update

- A new modeling decision lands in the codebase → add an entry with anchor citations
- An existing decision is revisited or refactored → update the entry; record the change in the relevant OPEN_PROBLEMS row
- A LIMITATIONS section is renumbered or rewritten → re-verify the anchor citations here
- A foundational discipline rule is added or modified → check whether existing entries here flow from it; update cross-references
- An anchor's line numbers shift due to a file edit → re-verify and update (same drift discipline as the other diagram files)
