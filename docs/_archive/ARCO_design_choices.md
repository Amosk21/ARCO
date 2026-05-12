# ARCO Design Choices

Active modeling choices, design rationale, and known boundaries. The README points here for design questions; the README itself stays focused on what ARCO does and how to use it.

These notes change as ARCO progresses. The current modeling adequacy synthesis lives in [MODELING_ADEQUACY_BRIEF.md](MODELING_ADEQUACY_BRIEF.md). The working checklist for evaluating new modeling commitments lives in [MODELING_QUESTION_MAP.md](MODELING_QUESTION_MAP.md).

---

## Why the approach is structural, not behavioral

Liability attaches to what a system **is able to do**, not only to what it happens to be doing. Modern regulation classifies by capability, not configuration.

ARCO treats capability as something that **resolves from structure**, traced from system components through dispositions to regulatory conditions. If the structural prerequisites for a regulated capability are not present, the capability does not exist for regulatory purposes. If they are present, the classification follows as a logical consequence.

This makes ARCO different from two adjacent categories of tool. **Post-hoc behavioral monitors** (red-teaming, content moderation, runtime policy enforcement) observe what a deployed system does. They cannot tell you whether a system *is* high-risk before it ships; they assume that classification has already happened. **Probabilistic scorers** (risk-rating LLMs, fine-tuned classifiers) produce confidence levels, not entailments. Regulators audit chains of reasoning, not probability distributions. ARCO produces the chain.

Given the hand-reviewed structured input, the classification is deterministic, traceable, and stable. It changes only when the structured description of the system changes.

---

## Why so many entailed triples

A typical pipeline run on Sentinel-ID materializes about 19,965 triples beyond the asserted ones. The figure reflects the depth of the upper-ontology hierarchy ARCO grounds in. Most of those derived triples are housekeeping under OWL 2 RL semantics: subclass closure across BFO, RO, IAO, and CCO; inverse-property materialization (every `is_about` assertion produces its inverse triple); property-characteristic propagation; and domain/range inferences.

The actually load-bearing classification triples are a small subset, including:

- `:Sentinel_ID_System rdf:type :HighRiskSystem` (entailed via the Gate-1 bridge axiom)
- `:Sentinel_ID_System rdf:type :AnnexIII1aApplicableSystem` (entailed via the three-gate `equivalentClass` axiom)
- `:Sentinel_FaceID_Disposition rdf:type :AnnexIIITriggeringCapability` (entailed via `owl:unionOf` membership propagation)
- A handful of inverse-aboutness triples supporting Gates 2 and 3

A regulatory determination is fundamentally a small number of bits of information ("does this system meet the conditions, yes or no, and which class does it instantiate"). The volume of derived triples is what allows downstream BFO-aligned consumers to reason over the same materialized graph without re-deriving the substrate.

---

## Active modeling considerations

A small set of modeling choices in the current axioms are under active review. These are not announced changes; they are open questions documented as part of the artifact at the time of writing.

1. **`HardwareComponent` requires a `CapabilityDisposition` filler.** The current restriction (`HardwareComponent ⊑ has_disposition some CapabilityDisposition`) is correct for capability-bearing hardware but over-specified for non-capability hardware such as power supplies, mounting, or cabling. A possible refinement would split the class so the disposition restriction lives on a more specific subclass (for example, `CapabilityBearingComponent ⊑ HardwareComponent`); whether that refinement is worth the modeling cost is being considered.

2. **`OperationalProcess` requires realizing a `CapabilityDisposition`.** Same shape as (1). Maintenance, calibration, and startup processes involve the system but do not realize an AI capability. Whether to weaken the restriction or introduce a more specific subclass for capability-realizing processes is being considered.

3. **Cloud-hosted and pure-software AI systems are out of current scope.** The mereology requires every `:System` to have at least one material `:SystemComponent` part. This accommodates on-device and on-prem AI; cloud-hosted systems whose physical infrastructure is shared do not satisfy the restriction without fictional component instances. Whether to revise the mereology, or to scope cloud-native AI to a sibling class with its own modeling, is being considered.

4. **`bfo:0000051 has_part` between Information Content Entities.** The regulatory scaffold uses the generic mereological relation between ICEs (e.g., `:AnnexIII_List bfo:0000051 :AnnexIII_Condition_1a`). CCO and IAO offer more specific properties for parts of information. Whether the generic property is the right choice for ICE-to-ICE parthood, or whether to migrate to a more specific information-parthood relation, is being considered.
