# Value Chain: Source Document to Honest Certificate

## Purpose

This diagram shows the end-to-end chain ARCO names as its target: source documentation, reviewed RDF commitments, BFO/CCO-aligned graph, reasoner entailment, inspectable answer, honest certificate. Every node traces to the file that grounds it; every edge traces to the BFO/CCO/RO/IAO predicate that connects it.

## Diagram

```mermaid
flowchart TB
  classDef source fill:#fff7ed,stroke:#c2410c,color:#431407
  classDef sdc fill:#fef3c7,stroke:#92400e,color:#451a03
  classDef ice fill:#dbeafe,stroke:#1e40af,color:#0c1e4f
  classDef reality fill:#dcfce7,stroke:#15803d,color:#052e16
  classDef reasoner fill:#fef9c3,stroke:#a16207,color:#3f2a00
  classDef witness fill:#e9d5ff,stroke:#6d28d9,color:#2e1065
  classDef output fill:#fce7f3,stroke:#9d174d,color:#3b0827
  classDef scope fill:#fee2e2,stroke:#b91c1c,color:#450a0a,stroke-dasharray:5 4
  classDef human fill:#f1f5f9,stroke:#475569,color:#0f172a,stroke-dasharray:5 4
  classDef inProgress fill:#fffbe6,stroke:#7c5e10,color:#3f2a00,stroke-dasharray:3 3

  CDO["CDO question<br/>e.g. Is system X Annex III 1(a) applicable?"]:::human

  subgraph SRC ["Source side: kiosk demo v1 input-mile shape; deeper inscription modeling pending"]
    DOC["Source document<br/>HYPOTHETICAL or real<br/>docs/kiosk_demo_v1/source_packet.md"]:::source
    IBE["cco:InformationBearingEntity<br/>(document as material bearer)<br/>seed not in cco_seed.txt; pending"]:::inProgress
    IQE["cco:InformationQualityEntity<br/>(inscription on document)<br/>seed pending"]:::inProgress
    TXT["cco:has_text_value<br/>verbatim source text<br/>seed pending"]:::inProgress
  end

  LEDGER["Evidence ledger<br/>human adjudicates source-text to triple<br/>docs/kiosk_demo_v1/evidence_ledger.md"]:::human

  subgraph REAL ["Reality side: POPULATED (BFO IC and SDC subkinds)"]
    SYS[":System ⊑ bfo:0000027<br/>Sentinel, CreditScorer, Kiosk +3<br/>ARCO_core.ttl:58"]:::reality
    COMP[":HardwareComponent ⊑ bfo:0000030<br/>bears dispositions<br/>ARCO_core.ttl:74"]:::reality
    DISP[":CapabilityDisposition ⊑ bfo:0000016<br/>latent-capability target<br/>(rationale at ARCO_core.ttl:26-38)<br/>ARCO_core.ttl:84"]:::reality
    ROLE[":ProviderRole / :DeployerRole / :NaturalPersonRole<br/>⊑ bfo:0000023 Role"]:::reality
  end

  subgraph INFO ["Information side: POPULATED (CCO ICE subkinds, typed instances)"]
    IUS[":IntendedUseSpecification<br/>⊑ cco:DirectiveInformationContentEntity<br/>ARCO_governance_extension.ttl:233"]:::ice
    USS[":UseScenarioSpecification<br/>⊑ cco:DesignativeInformationContentEntity<br/>ARCO_governance_extension.ttl:279"]:::ice
    DET[":ComplianceDetermination / :HighRiskDetermination<br/>⊑ cco:DescriptiveInformationContentEntity<br/>ARCO_core.ttl:142, 148"]:::ice
    REG[":RegulatoryContent<br/>e.g. :AnnexIII_Condition_1a<br/>ARCO_core.ttl:137"]:::ice
  end

  subgraph CLF ["OWL-RL three-gate classifier: POPULATED"]
    G1["Gate 1 (reality)<br/>System bfo:0000051 (has_part) Component<br/>Component ro:0000091 (has_disposition) AnnexIIITriggeringCapability<br/>ARCO_governance_extension.ttl:421-433"]:::reasoner
    G2["Gate 2 (representation)<br/>IUS inverse iao:0000136 System<br/>+ IUS cco:prescribes someValuesFrom RegulatedProcess<br/>ARCO_governance_extension.ttl:441-444"]:::reasoner
    G3["Gate 3 (representation)<br/>USS inverse iao:0000136 System<br/>+ USS cco:designates owl:hasValue NaturalPersonRole<br/>ARCO_governance_extension.ttl:454-466"]:::reasoner
  end

  HER["HermiT cross-check<br/>OWL 2 DL CI matrix<br/>03_TECHNICAL_CORE/scripts/hermit_cross_check.py"]:::reasoner

  subgraph AUDIT ["SPARQL audit + SHACL validation on reasoned graph: POPULATED"]
    SP1["select_gate_1_capability.sparql"]:::witness
    SP2["select_gate_2_prescribed_process.sparql"]:::witness
    SP3["select_gate_3_designated_role.sparql"]:::witness
    SP4["select_primary_classification.sparql"]:::witness
    SP5["select_determination_node.sparql"]:::witness
    SHACL["assessment_documentation_shape.ttl<br/>documentary completeness"]:::witness
  end

  subgraph OUT ["Honest certificate: POPULATED (schema 1.3, post-PR #36)"]
    PRI["PRIMARY ARCO classification<br/>:AnnexIII1aApplicableSystem or :AnnexIII5bApplicableSystem<br/>(all three gates) or NOT_APPLICABLE<br/>field: primary_arco_classification"]:::output
    LAT["LATENT-RISK FLAG<br/>:HighRiskSystem (Gate 1 alone)<br/>not the legal high-risk classification<br/>field: latent_risk_class"]:::output
    META["run_metadata<br/>fixture id, schema 1.3<br/>BFO 2020 + RO 2025-12-17 + IAO 2026-03-30 + CCO v1.7-2024-11-03"]:::output
  end

  SCOPE["Scope cuts disclosed at LIMITATIONS.md<br/>Article 6(3) derogation (provider-asserted, not evaluated)<br/>Article 5 routing<br/>temporal / site / runtime context<br/>software-configurable bearer disclosure"]:::scope

  CDO --> DOC
  DOC --> IBE
  IBE --> TXT
  IQE -.->|"ro:0000052 characteristic_of<br/>(asserted SDC to IC; via PR #41 binding to bfo:0000197)"| IBE
  IQE -.->|"adjudication target"| LEDGER

  LEDGER -->|"adjudicator commits<br/>info-side ICEs"| IUS
  LEDGER --> USS
  LEDGER --> DET
  LEDGER -->|"reality-side warrant"| SYS

  IUS -.->|"bfo:0000058 is concretized by<br/>(asserted GDC to SDC; pending)"| IQE
  USS -.->|"bfo:0000058"| IQE
  DET -.->|"bfo:0000058"| IQE

  SYS -->|"bfo:0000051 has_part"| COMP
  COMP -->|"ro:0000091 has_disposition"| DISP
  SYS -->|"ro:0000087 has_role"| ROLE

  IUS -->|"iao:0000136 is_about"| SYS
  USS -->|"iao:0000136"| SYS
  DET -->|"iao:0000136"| SYS
  DET -.->|"iao:0000136"| REG

  DISP --> G1
  IUS --> G2
  USS --> G3

  G1 --> PRI
  G2 --> PRI
  G3 --> PRI
  G1 --> LAT

  PRI -.->|"verification"| HER
  LAT -.-> HER

  PRI --> SP4
  PRI --> SP5
  G1 --> SP1
  G2 --> SP2
  G3 --> SP3
  PRI --> SHACL

  SP4 --> META
  PRI --> SCOPE
  LAT --> SCOPE
  SCOPE -.->|"hard questions escalate to human review"| CDO
```

## Verification table

Every node above traces to a file. Every edge traces to a BFO/CCO/RO/IAO/ARCO axiom or declaration.

| Diagram node | What it is | Where it's defined |
|---|---|---|
| `:System` | The assessment target class | `03_TECHNICAL_CORE/ontology/ARCO_core.ttl:58-66` |
| `:HardwareComponent` | Material component bearing dispositions | `03_TECHNICAL_CORE/ontology/ARCO_core.ttl:74-82` |
| `:CapabilityDisposition` | Latent-capability target class | `03_TECHNICAL_CORE/ontology/ARCO_core.ttl:84-87` |
| `:IntendedUseSpecification` | Directive ICE class | `03_TECHNICAL_CORE/ontology/ARCO_governance_extension.ttl:233-247` |
| `:UseScenarioSpecification` | Designative ICE class | `03_TECHNICAL_CORE/ontology/ARCO_governance_extension.ttl:279-288` |
| `:ComplianceDetermination` | Descriptive ICE (entailment record) | `03_TECHNICAL_CORE/ontology/ARCO_core.ttl:142-146` |
| `:HighRiskDetermination` | Descriptive ICE (Gate-1 latent or three-gate applicability record) | `03_TECHNICAL_CORE/ontology/ARCO_core.ttl:148-152` |
| `:RegulatoryContent` | Directive ICE for regulatory text | `03_TECHNICAL_CORE/ontology/ARCO_core.ttl:137-140` |
| `:AnnexIII1aApplicableSystem` | Three-gate defined class for Annex III 1(a) | `03_TECHNICAL_CORE/ontology/ARCO_governance_extension.ttl:405-468` |
| `:AnnexIII5bApplicableSystem` | Three-gate defined class for Annex III 5(b) | `03_TECHNICAL_CORE/ontology/ARCO_governance_extension.ttl:491-550` |
| `:HighRiskSystem` | Gate-1-only latent-risk flag class | `03_TECHNICAL_CORE/ontology/ARCO_governance_extension.ttl:199-221` |
| `cco:InformationBearingEntity` (pending) | Document material bearer class | CCO v1.7 (canonical IRI; not yet in `cco_seed.txt`) |
| `cco:InformationQualityEntity` (pending) | Inscription quality class | CCO v1.7 (canonical IRI; not yet in `cco_seed.txt`) |
| `cco:has_text_value` (pending) | Verbatim text predicate | CCO v1.7 line 437-442 in `runs/scratch/cco-v1.7/CommonCoreOntologiesMerged.ttl`; not yet in `cco_seed.txt` |

| Diagram edge | Relation IRI | Where it's defined |
|---|---|---|
| Inscription inheres in document (asserted IQE to IBE) | `ro:0000052` (characteristic_of) | `03_TECHNICAL_CORE/ontology/imports/ro_bot.owl:534-549` plus ARCO binding `ro:0000052 rdfs:subPropertyOf bfo:0000197` at `ARCO_core.ttl:193-194` (PR #41). Asserted-subject: IQE (SDC); asserted-object: IBE (IC). Inverse `ro:0000053` (bearer_of) materializes via OWL-RL prp-inv1. |
| ICE is concretized by inscription (asserted ICE to IQE) | `bfo:0000058` (is concretized by) | `03_TECHNICAL_CORE/ontology/imports/bfo-2020.owl:225-241`. Asserted-subject: ICE (GDC); asserted-object: IQE (SDC). Domain BFO_0000031 (GDC); range union of BFO_0000015 (Process) and BFO_0000020 (SDC). Inverse `bfo:0000059` (concretizes) materializes via OWL-RL prp-inv1. |
| System has component | `bfo:0000051` (has_part) | `03_TECHNICAL_CORE/ontology/imports/bfo-2020.owl` |
| Component has disposition | `ro:0000091` (has_disposition) | `03_TECHNICAL_CORE/ontology/imports/ro_bot.owl:712+` |
| Bearer has role | `ro:0000087` (has_role) | `03_TECHNICAL_CORE/ontology/imports/ro_bot.owl:696-708` |
| ICE is about system | `iao:0000136` (is_about) | `03_TECHNICAL_CORE/ontology/imports/iao_bot.owl` |
| IUS prescribes process | `cco:prescribes` | `03_TECHNICAL_CORE/ontology/ARCO_governance_extension.ttl:132-134` |
| USS designates role | `cco:designates` | `03_TECHNICAL_CORE/ontology/ARCO_governance_extension.ttl:136-139` |

## Status notes

**POPULATED nodes** are present in the current graph and exercised by the pipeline. The reality side, information side, three-gate classifier, audit layer, and certificate output all qualify.

**PENDING nodes** (the source-side subgraph: IBE / IQE / TXT, plus the concretization edges to ICEs) are scoped and canon-verified, but the seeds are not in `cco_seed.txt` and the work is not in the active register today. The kiosk demo v1 holds the input-mile shape with a hypothetical source packet; deeper inscription modeling is conditional on real-document warrant. Current work sequence prioritizes the foundation modeling map (per `docs/CANON_BACKTEST_2026-05-12.md` §F.1) before the kiosk demo substitution and before the inscription seed re-add.

**SCOPE CUT** (the `SCOPE` node at the bottom right) names the things ARCO deliberately refuses to claim under current commitments. These appear in `LIMITATIONS.md` with rationale. Key items:

- Article 6(3) derogation: ARCO surfaces `:DerogationClaim` ICEs for human legal review but does not evaluate validity.
- Article 5 routing (prohibited-practice classification): out of v1 scope; future work.
- Temporal regions, sites, runtime context: design-time classifier only.
- Software-configurable hardware capability: OWA-bounded; ARCO does not assert hardware-incapability.

## What this diagram does NOT show

- The full RO / IAO / BFO / CCO import chain. The slim modules at `03_TECHNICAL_CORE/ontology/imports/*.owl` provide everything the diagram cites. See `docs/ARCO_imports_rationale.md` for the import-chain discussion.
- Fixture-specific data. The 6 fixtures (Sentinel, CreditScorer, Verification, flag_tests, adversarial_blanknode, adversarial_decoy) instantiate the reality and information sides for specific systems. See `three_gate_classifier.md` for which fixture exercises which gate combination.
- The accountability-to-individual extension (canon-grounded in conversation; activates when a specific use case demands named-individual chain).
- The CCO version provenance hardening (the version pin lives in `ARCO_governance_extension.ttl:15` comment, not in `cco_bot.owl` itself).

## When to update

- Kiosk demo v1 substitutes a real vendor document for the current hypothetical source packet: revise the SRC subgraph to reflect the populated input-mile chain.
- Inscription seed work is re-prioritized and committed to `cco_seed.txt` and a fixture: change the PENDING subgraph status to POPULATED and remove the "seed pending" labels.
- A new Annex III category enters ARCO: extend the classifier subgraph and the `:AnnexIIITriggeringCapability` membership commentary.
- The certificate schema bumps past 1.3: update the schema reference in the `META` and `PRI` nodes.
- A new SHACL shape lands: add it to the AUDIT subgraph.
- The accountability-to-individual layer activates: extend the reality side with a Person + Role chain.
- Any of the version pins (BFO / RO / IAO / CCO) advances: update the `META` node and re-verify all cited line numbers.
