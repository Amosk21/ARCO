# ARCO's Three Layers: OWL, SHACL, SPARQL

OWL, SHACL, and SPARQL look like alternative tools for the same job. They are not. They answer different questions, and the regulatory determination case requires all three.

## Why each layer is required

**OWL operates under the Open World Assumption.** What is not asserted is unknown, not false. Reasoning over OWL adds new entailments because the world might contain facts that have not been recorded. This makes OWL the right tool for **classification**: "is this system high-risk?" becomes a logical question with a derivable answer that the reasoner produces from axioms and asserted facts.

**SHACL operates under the Closed World Assumption.** A dataset either matches the shape or it does not. Reasoning is irrelevant; what matters is whether the record is structurally complete against the constraint. This makes SHACL the right tool for **documentary completeness**: given that a determination must rest on specific evidence (an IntendedUseSpecification, a UseScenarioSpecification), SHACL checks the record for that evidence's structural presence.

**SPARQL queries the reasoned graph after both layers have run.** It does not entail; it inspects. This is the right tool for **audit**: pattern-match the post-reasoning graph for conditions worth human attention (derogation claims, fraud-exclusion candidates, regulatory alignment).

For regulatory determination, all three are required because three different audiences need three different artifacts:

- *"Is this system high-risk?"* needs an entailed answer re-derivable from public axioms. **OWL's job.**
- *"Is the supporting evidence structurally complete?"* needs a closed-world check that the record contains the required content. **SHACL's job.**
- *"Are there conditions warranting additional human review?"* needs a pattern-match on the reasoned graph. **SPARQL's job.**

Remove any layer and a different audience loses the artifact they need: a complete record with no determinative power, a determination with no defensible supporting record, or answers without inspectable transparency.

The OWL-vs-SHACL choice some practitioners frame as a tooling decision is really an artifact-of-different-audiences distinction; ARCO treats them as different layers of a single architecture rather than competing solutions.

## Concrete mapping (practitioner concern → tool → ARCO's specific use)

| Concern | Tool | How ARCO uses it |
|---|---|---|
| Open world; missing information does not cause an error; inference for classification | OWL | The three-gate `owl:equivalentClass owl:intersectionOf` axiom for `:AnnexIII1aApplicableSystem` and `:AnnexIII5bApplicableSystem`; the Gate-1 latent-flag axiom for `:HighRiskSystem`; the `owl:unionOf` defining `:AnnexIIITriggeringCapability`; pairwise `owl:disjointWith` between biometric identification, biometric verification, and creditworthiness capabilities. See `03_TECHNICAL_CORE/ontology/ARCO_governance_extension.ttl`. |
| Class definition, property domain/range, subclass relationships | OWL | Capability disposition hierarchy under `:CapabilityDisposition`; IUS subkinds via the CCO Specification family pattern; ICE typing through `cco:DirectiveInformationContentEntity` and `cco:DesignativeInformationContentEntity`. See `03_TECHNICAL_CORE/ontology/ARCO_core.ttl` and `ARCO_governance_extension.ttl`. |
| Closed world; missing information causes an error; data integrity / validation; restrictions and constraints for validation | SHACL | The named shapes in `03_TECHNICAL_CORE/validation/assessment_documentation_shape.ttl` enforce structural completeness on documentary entities: every `:System` has a part; every `:HardwareComponent` has a disposition; every `:IntendedUseSpecification` prescribes a typed Process and is about a System; every `:UseScenarioSpecification` designates `:NaturalPersonRole`; every `:ProviderRole` inheres in exactly one entity. |
| Pattern-match audit on the post-reasoning graph; conditions warranting human review | SPARQL ASK | Queries in `03_TECHNICAL_CORE/reasoning/`: `check_high_risk_inference`, `check_annex_iii_1a_entailment`, `check_annex_iii_5b_entailment`, `check_intended_use`, `check_assessment_traceability`, `check_obligation_link`, `check_regulatory_alignment`, `flag_derogation_candidate`, `flag_fraud_exclusion_candidate`. These inspect what the reasoning produced; they do not produce the classification themselves. |
| Mix of inference and validation in one architecture; multiple shapes for the same model | OWL + SHACL | A single instance graph is reasoned by OWL-RL, validated by SHACL against documentary shapes, and then audited by SPARQL on the reasoned graph. The same fixture passes through all three layers to produce the certificate. |
