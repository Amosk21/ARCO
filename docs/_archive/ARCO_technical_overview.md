# ARCO Technical Overview

This document holds the structural diagrams and per-axiom captions that explain what ARCO models. The README points here for technical depth; the README itself stays focused on what ARCO does and how to use it.

---

## Class hierarchy at a glance

```mermaid
flowchart TB
    subgraph BFO_TIER[BFO 2020 and IAO upper categories]
        BFO_OA[bfo:ObjectAggregate]
        BFO_OBJ[bfo:Object]
        BFO_DISP[bfo:Disposition]
        IAO_ICE[iao:InformationContentEntity]
    end

    subgraph CCO_TIER[CCO ICE specializations]
        CCO_DIR["cco:DirectiveInformationContentEntity<br/>(Directive ICE)"]
        CCO_DESIG["cco:DesignativeInformationContentEntity<br/>(Designative ICE)"]
    end

    subgraph REALITY[Reality side - dispositions in independent continuants]
        SYS[:System]
        SC[:SystemComponent]
        HW[:HardwareComponent]
        CAP[:CapabilityDisposition]
        BIC[:BiometricIdentificationCapability]
        BVC[:BiometricVerificationCapability]
        CEC[:CreditworthinessEvaluationCapability]
        ATC[":AnnexIIITriggeringCapability<br/><i>defined class</i>"]
    end

    subgraph REPR[Representation side - ICEs about systems]
        IUS[:IntendedUseSpecification]
        USS[:UseScenarioSpecification]
    end

    subgraph REG[Entailed regulatory determinations]
        HRS[":HighRiskSystem<br/><i>Gate 1 latent flag</i>"]
        AIII1A[:AnnexIII1aApplicableSystem]
        AIII5B[:AnnexIII5bApplicableSystem]
    end

    SYS --> BFO_OA
    SC --> BFO_OBJ
    HW --> SC
    CAP --> BFO_DISP
    BIC --> CAP
    BVC --> CAP
    CEC --> CAP
    CCO_DIR --> IAO_ICE
    CCO_DESIG --> IAO_ICE
    IUS --> CCO_DIR
    USS --> CCO_DESIG

    HRS -.entailed.-> SYS
    AIII1A --> SYS
    AIII5B --> SYS

    BIC -.unionOf.-> ATC
    CEC -.unionOf.-> ATC

    BIC === BVC
    BIC === CEC
    BVC === CEC

    style REALITY fill:#eaf3ea
    style REPR fill:#eef2fb
    style REG fill:#fbf2e8
    style BFO_TIER fill:#f5f5f5
    style CCO_TIER fill:#f5f5f5
    style ATC stroke:#444,stroke-width:2px,stroke-dasharray:3 3
```

**Legend.** Solid arrow = `rdfs:subClassOf` (child points to parent, OBO Foundry convention). Dotted arrow labeled `unionOf` = member of the `owl:equivalentClass owl:unionOf` defining `:AnnexIIITriggeringCapability`. Dotted arrow labeled `entailed` = membership entailed via `owl:equivalentClass` intersection rather than asserted as a subclass (`:HighRiskSystem` is the example: not asserted as a subclass of `:System`; entailed when the bridge axiom fires). Thick line `===` = `owl:disjointWith`. `:BiometricVerificationCapability` is intentionally NOT a member of `:AnnexIIITriggeringCapability` because Annex III 1(a) excludes systems intended solely for biometric verification to confirm a claimed identity; Article 3(36) supplies the one-to-one biometric verification definition. The disjointness edges visualize the formal exclusion.

---

## The three-gate axiom (Annex III 1(a))

```mermaid
flowchart LR
    SYSTEM[":System x<br/>(also a conjunct)"]

    subgraph G1["Gate 1 - Reality side: capability"]
        G1D["x bfo:has_part some<br/>(:SystemComponent and<br/>ro:has_disposition some<br/>:BiometricIdentificationCapability)<br/><br/><i>the system actually contains a component<br/>capable of biometric identification</i>"]
    end

    subgraph G2["Gate 2 - Representation side: prescribed process"]
        G2D["x [inverseOf iao:is_about] some<br/>:RemoteBiometricIdentificationIntendedUseSpec<br/><br/><i>IUS subkind defined as<br/>IntendedUseSpecification and<br/>cco:prescribes someValuesFrom<br/>:RemoteBiometricIdentificationProcess</i>"]
    end

    subgraph G3["Gate 3 - Representation side: designated role"]
        G3D["x [inverseOf iao:is_about] some<br/>(:UseScenarioSpecification and<br/>cco:designates <b>hasValue</b><br/>:NaturalPersonRole)<br/><br/><i>the use scenario designates natural<br/>persons as the affected role universal</i>"]
    end

    SYSTEM --> G1
    SYSTEM --> G2
    SYSTEM --> G3
    G1 --> CONJ{"ALL THREE REQUIRED<br/>owl:equivalentClass<br/>owl:intersectionOf"}
    G2 --> CONJ
    G3 --> CONJ
    CONJ --> RESULT[":AnnexIII1aApplicableSystem<br/><i>high-risk under Annex III 1(a)</i><br/>entailed by OWL-RL"]

    style G1 fill:#eaf3ea
    style G2 fill:#eef2fb
    style G3 fill:#eef2fb
    style RESULT fill:#fbf2e8
```

**Legend.** Green box = reality side (BFO disposition borne by an independent continuant). Blue box = representation side (IAO information content entity describing the system). Gates 2 and 3 use the anonymous inverse-aboutness wrapper `[owl:inverseOf iao:0000136]` so the restriction is on the system itself, not on the spec. Gate 2 uses `owl:someValuesFrom` over a regulated intended-use subkind; the subkind's own `owl:equivalentClass` definition performs the prescribed-process type check. Gate 3 uses `owl:hasValue` against the role universal class IRI (designation by inscription is a documented IAO/CCO pattern; the universal is named directly, not a role-bearer instance). The same shape applies to `:AnnexIII5bApplicableSystem` with `:CreditworthinessEvaluationCapability` / `:CreditworthinessEvaluationIntendedUseSpec` substituted in Gates 1 and 2. **Gate independence is verified by `03_TECHNICAL_CORE/scripts/test_gate_removal.py`**: removing any one of the three triples causes the classification entailment to fail.

**Plain-English read.** ARCO does not legally enforce the EU AI Act; it formalizes a bounded slice of the rule as an OWL defined class. `IUS` means `IntendedUseSpecification`: a reviewed information artifact about a system that prescribes the process the system is intended to realize, not the vendor document itself. Vendor instructions, technical documentation, or source packets license the reviewed RDF commitment that an IUS exists and prescribes a process; the evidence ledger records that licensing step.

**Concretization boundary.** Regulatory text, vendor documentation, intended-use specifications, use-scenario specifications, and ARCO determinations are information content entities that exist in the world by being concretized in documents, files, records, or other bearers. The current ontology models those information artifacts and their aboutness, prescription, and designation relations, not every physical or digital bearer. Full source-document provenance and output provenance are necessary for a defensible application but live outside the three OWL gates in the evidence-to-commitment policy and the output-provenance contract.

---

## The Reality / Representation cut

ARCO commits to a clean separation: dispositions, roles, and processes are real (BFO continuants, occurrents, and universals). Specifications and determinations are information content entities ABOUT the system, not parts of it. The cut is what makes compliance claims inspectable: you can disagree about whether a disposition is present, but you cannot conflate "the documentation says the system has the disposition" with "the system has the disposition."

```mermaid
flowchart TB
    subgraph REPR["Representation side - IAO information content entities (real GDCs whose role is representational)"]
        REG[":RegulatoryContent<br/>(Directive ICE) regulatory text passage"]
        IUS[":IntendedUseSpecification<br/>(Directive ICE)"]
        USS[":UseScenarioSpecification<br/>(Designative ICE)"]
        CD[":ComplianceDetermination<br/>(Descriptive ICE)"]
        HRD[":HighRiskDetermination<br/>(Descriptive ICE)"]
    end

    subgraph REALITY["Reality side - BFO continuants, processes, universals"]
        SYS[":System<br/>(object aggregate, bfo:0000027)"]
        HW[":HardwareComponent"]
        DISP[":CapabilityDisposition<br/>inhering in the component"]
        PROC[":RemoteBiometricIdentificationProcess<br/>(regulated process class)"]
        ROLE[":NaturalPersonRole<br/>(role universal; tokens inhere in<br/>persons at deployment)"]
        PROV[":ProviderOrganization"]
        PROVR[":ProviderRole"]
    end

    SYS -->|bfo:has_part| HW
    HW -->|ro:has_disposition| DISP
    PROV -->|ro:has_role| PROVR

    REG -.iao:is_about.-> SYS
    IUS -.iao:is_about.-> SYS
    IUS ==>|cco:prescribes someValuesFrom| PROC
    USS -.iao:is_about.-> SYS
    USS ==>|cco:designates hasValue| ROLE
    CD -.iao:is_about.-> SYS
    HRD -.iao:is_about.-> SYS

    style REALITY fill:#eaf3ea
    style REPR fill:#eef2fb
```

**Legend.** Solid arrow = reality-side relation (`bfo:has_part`, `ro:has_disposition`, `ro:has_role`). Dotted arrow = reference-style aboutness (`iao:is_about`, used to anchor any ICE to its referent). Thick arrow `==>` = cross-cut constraint with a typed CCO property (`cco:prescribes` typing the prescribed process; `cco:designates` naming the role universal as designation target). Information Content Entities are themselves real entities (generically dependent continuants per BFO 2020); the "Representation side" label denotes their *role in the model* (representing reality) rather than lower ontological status. This matches the realist commitments of the BFO 2020 specification (ISO/IEC 21838-2:2021). The choice to model `:System` as `bfo:ObjectAggregate` rather than as a unitary Object is documented as arguable in [LIMITATIONS.md §3.4](../LIMITATIONS.md).

---

## End-to-end walkthrough: Sentinel test fixture

```mermaid
flowchart TB
    subgraph ASSERTED["1. Asserted (three-gate inputs from ARCO_instances_sentinel.ttl)"]
        direction LR
        SYS[":Sentinel_ID_System<br/><i>a :System</i>"]
        MOD[":Sentinel_FaceID_Module<br/><i>a :HardwareComponent</i>"]
        DISP[":Sentinel_FaceID_Disposition<br/><i>a :BiometricIdentificationCapability</i>"]
        IUS[":Sentinel_IntendedUse_001<br/><i>a :IntendedUseSpecification</i>"]
        PROC[":Sentinel_RBIP_Process<br/><i>prescribed process token,<br/>a :RemoteBiometricIdentificationProcess</i>"]
        USS[":Sentinel_UseScenario_001<br/><i>a :UseScenarioSpecification</i>"]
        NPR(((":NaturalPersonRole<br/><i>class IRI<br/>designated by USS</i>")))
        SYS -->|bfo:has_part| MOD
        MOD -->|ro:has_disposition| DISP
        IUS -->|iao:is_about| SYS
        IUS -->|cco:prescribes| PROC
        USS -->|iao:is_about| SYS
        USS -->|cco:designates| NPR
    end
    subgraph ENTAILED["2. Entailed by OWL-RL (no LLM, no rules engine; mechanical entailment)"]
        E1[":Sentinel_FaceID_Disposition a :AnnexIIITriggeringCapability<br/>(via owl:unionOf membership; reality side)"]
        E2[":Sentinel_ID_System a :HighRiskSystem<br/>(via Gate 1 bridge axiom; reality side: capability precondition)"]
        E3[":Sentinel_ID_System a :AnnexIII1aApplicableSystem<br/>(via three-gate equivalentClass intersection;<br/>Gate 1 reality + Gates 2/3 representation)"]
    end
    subgraph CERT["3. Pipeline emits two artifacts"]
        TXT["certificate.txt:<br/>PRIMARY: AnnexIII1aApplicableSystem<br/>LATENT-RISK FLAG: HighRiskSystem<br/>ANNEX III 1(a): VERIFIED<br/>(ENTAILED, Article 6(3) derogation not evaluated)"]
        AUDIT["Audit-layer SPARQL ASKs independently confirm:<br/>traceability PASS, intended-use PASS,<br/>regulatory-alignment PASS, union-sync PASS<br/><i>two-layer cross-check, not just reasoner output</i>"]
    end
    ASSERTED ==>|OWL-RL three-gate axiom| ENTAILED
    ENTAILED ==> TXT
    ENTAILED ==> AUDIT

    style ASSERTED fill:#f5f9ff
    style ENTAILED fill:#fbf2e8
    style CERT fill:#fff7e6
```

**Caption.** `Sentinel_ID_System` is the in-repo test fixture, not a real product. The same pipeline runs on any typed instance: `CreditScorer_001` (correctly entailed as `:AnnexIII5bApplicableSystem`), `VerificationKiosk_001` (correctly NOT entailed as Annex III 1(a) because verification is one-to-one and Annex III 1(a) excludes systems intended solely for biometric verification), and the gate-removal regression suite (one triple removed at a time, classification confirmed to fail). The Sentinel fixture intentionally omits provider-side modeling (`ProviderOrganization`, `AssessmentDocumentation`, `DerogationClaim`, etc.) from this view to keep the three-gate trace clear; those instances exist in the same fixture and feed the audit-layer SPARQL ASKs separately. Bearer simplification: `:HardwareComponent` stands in for the configured-system that bears the disposition. For software-configurable AI systems the same hardware can be configured for different modes, so the disposition assertion describes what THIS specific deployment is intended to do under its current commitments, not what the hardware-in-isolation could theoretically do. See [LIMITATIONS.md §3.5](../LIMITATIONS.md).
