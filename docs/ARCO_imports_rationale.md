# Why ROBOT BOT slim modules

This document explains why ARCO loads RO, IAO, and CCO as ROBOT BOT-extracted slim modules rather than full upstream releases, and what bridge declarations the ARCO governance extension carries on top of the BOT modules.

---

## Foundational ontology versions

| Ontology | Version / release | IRI namespace used | How it's loaded |
|----------|------------------|--------------------|------------------|
| **BFO** | BFO 2020 (ISO/IEC 21838-2:2021) | `http://purl.obolibrary.org/obo/BFO_` | Full ontology explicitly loaded by the pipeline/CI from `03_TECHNICAL_CORE/ontology/imports/bfo-2020.owl` |
| **RO** | OBO Relations Ontology release `2025-12-17` | `http://purl.obolibrary.org/obo/RO_` | ROBOT BOT-extracted slim module explicitly loaded by the pipeline/CI from `03_TECHNICAL_CORE/ontology/imports/ro_bot.owl` |
| **IAO** | Information Artifact Ontology release `2026-03-30` | `http://purl.obolibrary.org/obo/IAO_` | ROBOT BOT-extracted slim module explicitly loaded by the pipeline/CI from `03_TECHNICAL_CORE/ontology/imports/iao_bot.owl` |
| **CCO** | Common Core Ontologies v1.7 pinned semantic-IRI release | `http://www.ontologyrepository.com/CommonCoreOntologies/` | ROBOT BOT-extracted slim module explicitly loaded by the pipeline/CI from `03_TECHNICAL_CORE/ontology/imports/cco_bot.owl`, plus local bridge/readability declarations in `ARCO_governance_extension.ttl` |

**BFO 2020** is the second edition of Basic Formal Ontology, standardized as ISO/IEC 21838-2:2021. ARCO uses the OBO Foundry numeric-ID namespace (`BFO_0000015`, `BFO_0000016`, etc.) that is definitive of this release. BFO is loaded as a full local file because it is small (~100 KB), ISO-standardized, and the authoritative grounding for everything else; this matches IAO's own pattern of full-importing BFO while extracting slim modules of any other dependency.

**RO**, **IAO**, and **CCO** are loaded as ROBOT-extracted slim modules using `--method BOT`, a syntactic locality variant. The seed term lists ARCO depends on are version-controlled in `03_TECHNICAL_CORE/ontology/imports/seeds/{ro,iao,cco}_seed.txt`, and the slim modules can be regenerated reproducibly from the pinned upstream releases. This is the OBO Foundry / Ontology Development Kit (ODK) standard pattern, used by Gene Ontology, the OBO Relations Ontology itself, and the hundreds of ODK-managed projects.

**ARCO bridge declarations for CCO / IAO / BFO alignment.** CCO maintains its own information-content hierarchy in parallel to IAO's. ARCO's `ARCO_governance_extension.ttl` locally declares the three CCO ICE specializations used by the gates (`cco:DirectiveInformationContentEntity`, `cco:DescriptiveInformationContentEntity`, `cco:DesignativeInformationContentEntity`) as subclasses of `iao:0000030`; maps ARCO regulatory, output, and determination classes into that CCO layer; asserts `cco:designates rdfs:subPropertyOf iao:0000136`; and keeps local BFO subsumption declarations for `cco:Person` and `cco:Organization` for readability against the pinned module. These declarations integrate the BOT-extracted CCO module with ARCO's IAO aboutness gates; they are not new ARCO predicates.

---

## Five practical reasons for BOT over MIREOT or full imports

Using `robot extract --method BOT` to pull slim, version-pinned modules is the OBO Foundry's standard pattern for depending on external ontologies. The choice rests on five practical points:

1. **Formal entailment-preservation guarantee.** BOT is a syntactic locality module variant (Syntactic Locality Module Extraction, SLME, formalized 2007-2008): for any axiom α whose signature is contained in the seed signature Σ, the extracted module entails α iff the full upstream ontology does. This includes property characteristics (`FunctionalProperty`, `Transitive`, `Symmetric`), property chain axioms, inverse-of axioms, and `rdfs:domain` / `rdfs:range`. ARCO's gate axioms depend on these, particularly OWL inverse-property restrictions on `iao:0000136`, so this is the strict property the project needs.

2. **OBO Foundry / ODK convention.** The Ontology Development Kit, which scaffolds ~hundreds of OBO Foundry projects, hardcodes `module_type_slme: "BOT"` as default. Gene Ontology, OBI, ChEBI, and the OBO Relations Ontology itself all ship BOT-extracted slim modules for their dependencies. ARCO matching this convention shortens the trust chain for any reviewer fluent in OBO practice.

3. **MIREOT is legacy and unsafe for reasoning-critical projects.** ROBOT's own documentation states MIREOT "preserves the hierarchy of the input ontology (subclass and subproperty relationships), but does not try to preserve the full set of logical entailments." The documented MIREOT failure mode is silently dropping property typing and characteristic axioms. For a project whose headline product is OWL-DL reasoning correctness over inverse-property gate axioms, MIREOT is the wrong choice on principle and BOT is the right one.

4. **Reproducibility.** Each slim module is regenerable from a pinned upstream release using a single ROBOT command with a version-controlled seed file. The seed lists are in `03_TECHNICAL_CORE/ontology/imports/seeds/`. A reviewer auditing ARCO can re-run the extraction and verify byte-equivalent output.

5. **Operational scaling.** A pipeline run on Sentinel-ID with the BOT modules loads roughly 7,800 asserted triples and produces 27,765 post-reasoning (about 19,965 derived). The HermiT reasoning step in the ROBOT validation workflow runs in approximately seven minutes on the merged ontology. An earlier intermediate state of ARCO loaded the full upstream releases of RO and IAO, which took the HermiT step to thirty to forty minutes and was projected to grow to one to three hours when CCO was added; this is operationally noisy without adding any reasoning-correctness signal that BOT does not already provide. The full-import experiments are preserved in git history and confirmed that the slim modules produce byte-identical classification outputs.

The conventional argument for full imports, single-hash audit traceability against published upstream releases, is recovered here by the seed-file plus version-pin pattern: the seed lists are version-controlled, the upstream releases are pinned, and the extraction tool (ROBOT v1.9.10) is pinned in CI. The audit story becomes "ARCO uses BOT-extracted modules of these specific upstream releases, regenerable from these seed files using this specific ROBOT command," which is a tighter and more reproducible claim than "ARCO uses these full upstream releases" because every step is mechanically verifiable.
