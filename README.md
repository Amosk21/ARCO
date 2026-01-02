ARCO

Assurance & Regulatory Classification Ontology

What this is

ARCO is a framework for producing clear, defensible regulatory classifications for high-stakes AI systems.

Instead of generating scores, probabilities, or confidence levels, ARCO produces deterministic yes/no regulatory determinations that can be traced directly back to the structure and capabilities of the system being evaluated.

This repository demonstrates how such determinations can be constructed, validated, and audited end-to-end using formal methods.

Why ARCO exists

Most AI compliance tooling answers questions like:

“How risky does this system appear?”

“How confident are we that it complies?”

“What score does the model produce?”

Those approaches break down in regulated environments.

Regulators, auditors, and courts do not evaluate probability.
They evaluate justification.

ARCO exists to answer a different question:

Given what this system is capable of doing, does it meet the legal criteria for a specific regulatory classification — yes or no?

And to make that answer:

Deterministic

Explainable

Auditable

Reproducible

What ARCO does

At a high level, ARCO operates as follows:

Start from system documentation
The system’s components, deployment context, and capabilities.

Represent those capabilities formally
Using an ontology that distinguishes what a system does from what it is capable of doing.

Enforce structural completeness
SHACL rules ensure required information is explicit and nothing is assumed.

Apply regulatory logic deterministically
SPARQL queries test whether the encoded system satisfies legal criteria.

Produce a traceable determination
Every conclusion can be followed back to explicit facts and rules.

The output is not advice or opinion.
It is a conclusion that follows logically from system structure.

What this repository represents

This repository is not a SaaS product or automated compliance platform.

It is a reference-grade assurance methodology and implementation that demonstrates:

How deterministic regulatory classification can be performed

What artifacts such a process produces

How reasoning can be validated and audited

What a regulatory determination output looks like in practice

The included pilot materials show how the framework could be operationalized in a real engagement. They are intended to demonstrate capability and structure, not to imply production readiness, automation, or market scale.

Where to start

For first-time readers, the recommended order is:

ARCO_Assurance_Engine.pdf
Explains the motivation behind deterministic assurance and why probabilistic approaches fail in regulated domains.

ARCO_Regulatory_Determination_Case.pdf
A concrete example of a determination produced by the framework.

CommandCenter.pdf
Defines the strategic boundaries of what ARCO is and is not.

The technical files are included to show how the reasoning actually works, not because every reader is expected to run the pipeline.

What ARCO is not

Not a probabilistic risk scoring tool

Not a compliance checklist generator

Not a substitute for legal counsel

Not a plug-and-play automation platform

ARCO is best understood as a formal assurance instrument — similar in spirit to safety cases used in aerospace or medical systems, applied to AI regulatory classification.

Status

ARCO is presented here as a reference-grade methodology and demonstration of capability.

The technical foundation is intentionally explicit and auditable.
Future work focuses on validation, operational deployment, and refinement through real-world use.
