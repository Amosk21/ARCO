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

The same map can be read as the seven-bucket modeling check used in the Sentinel 1(a) audit.

| Bucket | What ARCO currently uses it for | Current gap / boundary |
|--------|---------------------------------|------------------------|
| Material bearer | `:System`, `:SystemComponent`, `:HardwareComponent`, provider organizations | Whole-system vs component-level bearer is a documented modeling choice; SaaS/API bearers are out of v1 scope. |
| Disposition | Capability classes such as biometric identification, biometric verification, and creditworthiness evaluation | Capabilities are modeled as dispositions, not functions; function-level refinement waits for stronger design-intent evidence. |
| ICE / GDC / documents | Regulatory content, intended-use specs, use-scenario specs, assessment docs, determinations | Source-document provenance and tokenization/concretization of every ICE are not fully modeled yet; evidence ledger and output-provenance work cover this boundary. |
| Process | Regulated process classes and Gate-2 prescribed process tokens | Bare process tokens are disclosed debt; richer participants, temporal regions, and realization structure are deferred. |
| Role | Provider/deployer roles and the `:NaturalPersonRole` universal designated by Gate 3 | Gate 3 references a role universal, not role-bearer particulars; deployment-time role bearers are deferred. |
| Temporal / spatial | No load-bearing temporal-region or site model in the current Annex III 1(a)/5(b) classifier | Deliberate gap. Deployment dates, runtime events, places, jurisdiction, and public-space context are future scope. |
| Regulatory fiat | Annex III applicability classes, triggering-capability grouping, EU AI Act category cuts | ARCO encodes bounded Annex III 1(a) and 5(b) criteria; Article 5 routing, derogation validity, obligations, and the rest of Annex III are disclosed gaps. |

## How To Use This Map

Before adding a modeling commitment, answer four questions:

1. What bucket does the entity belong to?
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
