# ARCO Modeling Question Map

This page is the per-commitment workbench for keeping ARCO's graph from becoming decorative. Use it when proposing a new term, triple, source packet, certificate field, or modeling change.

Pair this with [MODELING_ADEQUACY_BRIEF.md](MODELING_ADEQUACY_BRIEF.md): the adequacy brief states what ARCO's current model does and does not justify; this map is the checklist for deciding whether a new commitment belongs in that model. Use [COMPETENCY_QUESTIONS.md](COMPETENCY_QUESTIONS.md) as the CQ0-CQ17 interview script for turning a whole CDO question or new case into answerable requirements.

Boundary between the two files:

- `COMPETENCY_QUESTIONS.md` owns the session-level question: "What must ARCO answer for this system, and what proof chain is required?"
- This file owns the local modeling question: "Given one proposed commitment, what kind of entity is it, what relation may connect it, and what must be refused?"

The rule is simple: first decide what kind of entity the claim is about, then choose the smallest BFO/RO/IAO/CCO relation that says it. A material component can bear a disposition. An intended-use specification can prescribe a process. A use-scenario specification can designate a role universal. A source document can license a reviewed commitment. A certificate field can report an entailment. These are different jobs; mixing them is where the model loses clarity.

```mermaid
flowchart TB
    Q["What are we trying to say?"]

    Q --> REAL["A thing in reality?"]
    Q --> INFO["An information artifact?"]
    Q --> RULE["A regulatory rule or category?"]
    Q --> OUT["An output or certificate claim?"]

    REAL --> BEARER["Material bearer<br/>System / component / organization"]
    REAL --> DISP["Realizable entity<br/>Capability disposition or role"]
    REAL --> PROC["Occurrent<br/>Process the system may realize"]

    BEARER --> REL1["Use bfo:has_part or RO participant/role relations"]
    DISP --> REL2["Use ro:has_disposition<br/>Ask: what bearer has this capability?"]
    PROC --> REL3["Use process type only when the source licenses it<br/>Ask: intended process or runtime event?"]

    INFO --> ABOUT["What is it about?<br/>iao:is_about"]
    INFO --> PRESCRIBE["Does it prescribe a process?<br/>cco:prescribes"]
    INFO --> DESIGNATE["Does it designate a role/category?<br/>cco:designates"]
    INFO --> EVIDENCE["What source licenses this commitment?<br/>evidence ledger"]

    RULE --> OWLDEF["Formalized as an OWL defined class<br/>equivalentClass / intersectionOf"]
    RULE --> SCOPE["What is outside this rule?<br/>limitations / queued work"]

    OUT --> GRAPHVAL["Graph-backed value?<br/>named SPARQL query"]
    OUT --> METADATA["Run metadata?<br/>fixture, run id, schema version"]
    OUT --> DOCVAL["Documentary text?<br/>explicitly labeled, not an entailment"]

    REL1 --> GATE["Can the graph answer a CDO question?"]
    REL2 --> GATE
    REL3 --> GATE
    ABOUT --> GATE
    PRESCRIBE --> GATE
    DESIGNATE --> GATE
    OWLDEF --> GATE
    GRAPHVAL --> GATE

    GATE --> TEST["Backtest it:<br/>OWL entailment, SHACL structure,<br/>SPARQL witness, gate-removal regression"]

    style REAL fill:#eaf3ea
    style INFO fill:#eef2fb
    style RULE fill:#fbf2e8
    style OUT fill:#f7eefb
    style TEST fill:#f5f5f5
```

## Seven-Bucket Coverage

The seven buckets are the seven structural questions any complete model of a thing must answer. See `CLAUDE.md` § The Seven Buckets (BFO modeling framework) for the canonical definitions, which were corrected 2026-05-12 to match Beverley canonical seven (Design_Pattern_Lecture_5_Disambiguation.md lines 50-58 + BFO 2020 standard). The table below records what ARCO currently asserts in each bucket and what is still gap or scope cut.

| # | Question / Bucket | What ARCO currently uses it for | Status and gap |
|---|---|---|---|
| 1 | **What is it?** Material Entity (Independent Continuant) | `:System`, `:SystemComponent`, `:HardwareComponent`, `:ProviderOrganization`, `cco:Person` | **Populated.** Whole-system vs component-level bearer is a documented modeling choice; SaaS/API bearers are out of v1 scope. |
| 2 | **How is it?** Quality (Specifically Dependent Continuant) | Not yet populated. Inscription qualities on source documents enter here when the kiosk demo gains real source documents. | **Gap.** Slot pattern reserved against `OPEN_PROBLEMS.md` L1.1 (source-derived side) and L2.2 (pipeline-emitted side). |
| 3 | **What can it do?** Realizable Entity (Disposition, Role, Function) | `:CapabilityDisposition` and Annex III triggering capability subclasses; `:ProviderRole`, `:DeployerRole`, `:NaturalPersonRole` | **Populated.** Capabilities are modeled as dispositions, not functions; function-level refinement waits for stronger design-intent evidence. `:NaturalPersonRole` referenced as a universal via `cco:designates owl:hasValue`; role-bearer particulars are not minted without source warrant. |
| 4 | **What is happening?** Process (Occurrent) | Regulated process classes (`:RemoteBiometricIdentificationProcess`, `:BiometricVerificationProcess`, `:CreditworthinessEvaluationProcess`, `:AssessmentDocumentationProcess`) and Gate-2 prescribed process tokens | **Populated as typed tokens.** Bare process tokens are disclosed at `LIMITATIONS.md` §3.7.a (no asserted participants beyond the system, no temporal regions, no realizer chain). Path Gamma remediation queued. |
| 5 | **Where is it?** Immaterial Entity (Sites and immaterial boundaries) | Not modeled in the current Annex III 1(a)/5(b) classifier | **Deliberate scope cut.** Sites of deployment, jurisdictional boundaries, and public-space context activate this bucket only if ARCO extends to deployment-monitoring scope. Disclosed at `LIMITATIONS.md`. |
| 6 | **When is it?** Temporal Region (Occurrent boundaries) | Not modeled in the current Annex III 1(a)/5(b) classifier | **Deliberate scope cut.** Deployment dates, runtime events, and substantial-modification tracking activate this bucket only if ARCO extends to deployment-monitoring scope. Disclosed at `LIMITATIONS.md`. |
| 7 | **How do we know?** Generically Dependent Continuant (Information Content Entities) | `:RegulatoryContent`, `:IntendedUseSpecification`, `:UseScenarioSpecification`, `:AssessmentDocumentation`, `:ComplianceDetermination`, `:HighRiskDetermination`, regulator-defined `:AnnexIII_Condition_*` and `:AnnexIII1aApplicableSystem` classes | **Populated as typed ICE instances and regulator-defined classes.** Concretization back to bearer particulars (which inscription on which document) is the realist gap that L1.1 and L2.2 close together. |

**Cross-bucket structural check (not a bucket itself).** The realization chain is the load-bearing structural test that runs across buckets. It uses `ro:0000091 has_disposition` (Bucket 1 to Bucket 3) and `bfo:0000055 realizes` (Bucket 4 to Bucket 3). "What grounds the risk or capability?" is answered by the structure of these relations across Buckets 1, 3, and 4, not by a separate bucket. ARCO's current state: Sentinel exercises the realization triple (`bfo:0000055`); other fixtures leave realization unmodeled at design time per `LIMITATIONS.md §3.7.a`. Earlier versions of this table treated "material basis and realization" as a separate Bucket 7; that conflated a relation pattern (cross-bucket) with a category (a bucket), and is corrected here per the 2026-05-12 canon backtest.

## How To Use This Map

Before adding a modeling commitment, answer four questions:

1. Which of the seven buckets does the entity belong to (which of the seven questions does it answer)?
2. Which BFO/RO/IAO/CCO relation connects it to the rest of the graph?
3. What source or reviewed commitment licenses the assertion?
4. What test, query, shape, or limitation would catch the mistake if the assertion is wrong?

If a proposed change does not answer those questions, it should stay out of the ontology until the modeling decision is clearer.

## Hard Questions Requiring Human Review

These are not routine implementation tasks. They are modeling decisions where ARCO needs explicit human judgment before the graph should change.

| Question | Why it matters | Current posture |
|----------|----------------|-----------------|
| Should Gate 2 reference process tokens or prescribed process kinds? | Bare process tokens can look like fake occurrent witnesses if the source only licenses intended use. | Held in `OPEN_PROBLEMS.md` L2.1. |
| Which ICEs need explicit concretizing bearers? | Concretization matters for output trust, but modeling every bearer can bloat the graph. | `cco:is_tokenized_by` is tracked in `OPEN_PROBLEMS.md` L2.2. |
| When is verification formally disjoint from identification at the process level? | Capability disjointness exists; process disjointness may be needed for the kiosk negative case to be visually and formally crisp. | Hold until a test or fixture makes it load-bearing. |
| Are provider and deployer roles disjoint? | One organization can bear different roles for different systems; disjointness must apply to role instances, not organizations. | Human-session question. |
| How should cloud/SaaS systems be represented as material bearers? | Current `:System` mereology assumes material components and can force fictional parts for pure SaaS. | Active modeling consideration in `README.md`. |
| When does Annex III 1(a) branch to Article 5 prohibited-practice routing? | Real-time RBI in public law-enforcement contexts needs site, actor, and purpose modeling that v1 lacks. | Disclosed scope gap. |
| What source evidence is enough to assert a disposition? | Documents license commitments; they do not become reality by themselves. | Evidence-ledger demo is the next proof move. |
| For each certificate field, what is the provenance class? | Graph-backed, run metadata, and documentary text must not be visually merged. | Output manifest v2 governs this. |

Use this table as the starting agenda for human-in-the-loop modeling sessions. Do not turn these into code changes just because they are written down.
