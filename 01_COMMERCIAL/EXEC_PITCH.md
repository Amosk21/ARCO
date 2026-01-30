# ARCO: Moving Regulatory Risk Upstream

## The Concept: Risk Management Through Classification

The easiest way to understand ARCO is to look at how the largest financial systems in the world actually make money.

In places like the New York Stock Exchange or major hedge funds, the most valuable people are not the ones picking individual trades. They are the risk management teams. Their job is not to make everything win, but to design the structure so losses are bounded, exits always exist, and the system remains viable regardless of what happens.

ARCO plays that same role for AI systems.

---

## The Problem: Compliance Is Currently a Sunk Cost Crisis

Today, companies are building AI systems without knowing with certainty whether those systems will later be deemed non-compliant under regulations such as the EU AI Act.

When that determination happens after deployment, the cost is enormous:

- Retraining and redesign
- Delayed product launches
- Lawsuits and regulatory fines
- Forced suspension or withdrawal of deployed systems

In practice, misclassification discovered post-deployment can dramatically escalate remediation costs.

ARCO exists to move that risk decision upstream, before any of that money is sunk.

---

## The Solution: A Pre-Deployment Regulatory Classification System

ARCO is a pre-deployment regulatory classification system.

### Operationalizing Regulatory Criteria

ARCO operationalizes a defensible interpretation of Article 6 and Annex III by modeling what regulatory criteria are actually about—systems, capabilities, and deployment contexts—using a formal realist ontology (BFO/CCO). This creates an explicit, structured representation of the real-world referents that regulation targets.

### Structural Validation and Classification

The proposed AI system is mapped into that structure. Using SHACL for structural validation and SPARQL for deterministic classification queries, ARCO produces an auditable regulatory classification.

### The Output

ARCO determines whether a system triggers regulatory classification conditions—for example, whether it qualifies as high-risk under Annex III. This is not a probabilistic score or an advisory opinion. It is a justifiable, repeatable classification determination.

### Crucial Distinction

AI is not making the decision. AI is used only to extract candidate information. The determination itself is driven by explicit rules, logic, and traceable reasoning. This makes the outcome auditable, reproducible, and defensible to regulators, auditors, and internal governance teams.

---

## The Economic Value

The primary value of ARCO is financial, not just legal.

ARCO provides organizations with decision clarity at the design phase. Instead of building in fear and hoping nothing breaks later, teams can move forward knowing their system has been structurally evaluated against regulatory requirements from the beginning.

This clarity:

- Saves time
- Prevents expensive rework
- Reduces legal and regulatory exposure
- Enables stronger and more credible claims about AI systems
- Protects revenue by avoiding delayed or blocked deployments

Ultimately, ARCO turns regulatory classification from a post-hoc legal crisis into a design-time engineering decision. It is risk management at the foundation layer of AI development.
