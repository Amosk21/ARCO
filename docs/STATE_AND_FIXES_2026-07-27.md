# ARCO and the outward corpus: everything found, and what to fix

**Written 2026-07-27 at the end of a full-day audit pass. Supersedes the scattered findings from that day's workflow runs.**

Every claim below is labeled **[exhaustive]** (enumerated search across every route that could carry it) or **[single-pass]** (checked once, could be incomplete). That distinction exists because on this same day a confident four-round conclusion turned out to be wrong: I searched for `owl:AllDisjointClasses` in QName form four separate times while the file serializes the expanded IRI `owl#AllDisjointClasses`. I varied *what* I searched for and never varied *how*. Treat every single-pass label as a live risk.

## CITATION PROVENANCE, READ BEFORE ACTING ON ANY LINE NUMBER

**This audit found that fifteen of nineteen checked locators in `LIMITATIONS.md` were wrong.** The base rate for stale line numbers in this repo is roughly eighty percent, so a line number is the least trustworthy thing in this document.

**Opened and verified directly, 2026-07-27:** `README.md:13`, `:137`, `:139` (all three re-checked after that day's edits shifted the file), `LIMITATIONS.md:14`, `:24`, `:29`, `:316`, `:318`, `:333`, `ARCO_core.ttl:200-215`, `bfo-2020.owl:1623-1630` plus its property domains and labels, `arco-smoke-test.yml:69`, `NCOR_STATE.md:47`, `:65`, `source-note_barry-smith-bfo-value-talk.md:66` and `:267`. Also executed: the full pipeline, the claim guard scan, the BFO prose-direction check and its backtest, and the git state.

**Relayed from agent reports and NOT opened by me:** every other `file:line` in this document. That includes `LIMITATIONS.md:3`, `:95`, `:117`, `:186`, `:209`, `:335`, `run_pipeline.py:361`, `:688`, `:2097`, `check_intended_use.sparql:31`, `arco-smoke-test.yml:63`, `OPEN_PROBLEMS.md:88`, every `four-layer-stack` line, `spine-paper-feed-2026-06-20.md:12`, `the-whole-story_spine.md:57`, `canon_barry-smith-and-the-gene-ontology.md:247`, `ncor-lineage-...:63`, `meaning-mismatch-failure-corpus.md:64`, `source-note_...systems-engineering.md:90`, `the-one-story:49`, commit `3692272`, and the `hermit_cross_check.py` counts.

**The substance of a relayed finding may well be right while its line number is stale.** Open the file before editing at any relayed locator, and expect the number to have moved.

---

## 0. The one structural finding

Four independent audits of four unrelated documents each found the same move: **coordination, formalism, or conformance substituted for realism, in a summary sentence, unflagged, written from inside the Smith and Beverley lineage.**

The mechanism is always the same and it is worth naming precisely. Formalism answers *how do you check*. Realism answers *what do the categories answer to*. Those are different questions. Listing them as competing routes concedes the argument silently, because it puts BFO on a menu as one option when it is the only item on the menu addressing the second question at all.

This is not four coincidences. It is one habit, and it is the reason outward material written by realists keeps reading like Neuhaus.

**The fix is never to drop the honesty.** Say plainly that several routes give you machine-checkability, OntoClean included, with no upper ontology required. Then say that none of them tells you what the categories should answer to, and that is a separate question with a separate answer. Nothing true is lost and the pluralism stops functioning as a shrug.

---

## 1. README fixes

| # | Site | Problem | Fix | Effort |
|---|---|---|---|---|
| 1 | `README.md:137` | "the classification follows what a system is rather than how it happens to be described" contradicts `LIMITATIONS.md:29`, which says ARCO classifies the description and not the deployed system. **CORRECTED: no precedence declaration exists.** The relayed claim that `LIMITATIONS.md:3` gives itself precedence is false; line 3 is the Purpose statement and a search for precedence language across the file returns nothing else. The contradiction is real and LIMITATIONS is right on the merits, because every input triple is a human transcription, but the fix does not rest on a precedence rule. | Delete the trailing clause. The three sentences after it already carry the payoff. | 5 min |
| 2 | `README.md:13` | "the answer tracks what your system actually is, not how the paperwork happens to be worded." Paperwork is exclusively what ARCO consumes. This site is more exposed than 137 because it sits in the lede. | Replace the consequent with the invariance claim: fixed vocabulary means synonym drift does not change the answer. True, and what the sentence was reaching for. | 10 min |

Both clauses are byte-identical carryovers through commit `b5b2c2a`. That day's edit preserved the drift rather than introducing it. **[exhaustive]**, eleven routes across README, LIMITATIONS and `docs/`, exactly two instances, no drift into internal modeling docs.

**Already fixed this day, do not redo:** the unvetted adoption count and biology attribution at line 11, the twice-stated unsourced prevalence claim, the blended two-values paragraph, the wrong `ARCO_core.ttl` citation, the undashed source-to-commitment arrows in the chain diagram, and the concretization direction.

---

## 2. ARCO fixes, ordered by what an expert concludes on hitting it

### 2.1 Gate 3 forward-incompatibility. Disclose, do not fix. One hour.

**The finding.** `owl:hasValue :NaturalPersonRole` and a properly borne role particular are mutually exclusive. A reviewer who obtains real source warrant and mints the role particular correctly **loses** the 1(a) entailment and trips a SHACL violation telling them they modeled it wrong. ARCO's classification is currently conditional on the reviewer having *less* evidence, not more. Locked into four layers: the OWL axiom, `sh:hasValue` in the shape, `check_intended_use.sparql:31`, and `run_pipeline.py:688`.

**Do not fix the axiom before showing the repo.** That change touches the joint ICE-to-kind question spanning L2.1, L2.7 and L2.9. A rushed encoding decision is worse than a documented limit.

**The bound, which must appear in the disclosure.** One role-particular shape tested. OWL-RL only. Four downstream layers checked, at least four unswept. A disclosure claiming "no filler satisfies both" when one shape was tried is the overclaim this exercise exists to prevent.

**[single-pass]** on the sweep of downstream layers. **[exhaustive]** on the 2x2 itself, which was executed.

### 2.2 The false blocker. Fifteen minutes.

`LIMITATIONS.md:333` says no parameterized negative-test harness exists because the pipeline loads all TTL into one graph. It does not. `load_union_graph` takes explicit varargs with one call site passing seven named paths. No glob, rglob, iterdir, listdir or os.walk reads inputs. `--instances` has existed since commit `3692272`, 2026-03-11. The harness the disclosure says is missing is `test_ice_subfamily_trap.py`, wired at `arco-smoke-test.yml:63`. **[exhaustive]**, five enumerated routes plus an executed isolated run.

This one makes the project look less capable than it is.

### 2.3 Stale operational disclosures. One hour.

- `LIMITATIONS.md:318` says the provenance test is not invoked by CI. `arco-smoke-test.yml:69` invokes it. Wired 2026-07-03, false for 24 days. **[exhaustive]**, all three workflow files checked.
- `LIMITATIONS.md:186` calls the intent-without-capability flag queued. `OPEN_PROBLEMS.md:88` records L3.10 landed via PR #73. Verified from file existence through to live console output.
- `LIMITATIONS.md:316` says "24/24 agreement." Counted from `hermit_cross_check.py`: six fixtures, seven system names, four queries, so 28. The prose three paragraphs above enumerates all seven correctly.
- `LIMITATIONS.md:14` reads "Last reviewed: 2026-06-10" after six substantive commits including one today.
- Section 7.3 describes a SPARQL surface of two ASKs when five ASKs and eight SELECTs run.
- Ten-plus total in this class. **[single-pass]** on the completeness of that count.

### 2.4 Locator sweep. One to two hours, and script it.

Nineteen precise locators checked, fifteen wrong. Worst is `LIMITATIONS.md:95` pointing at a file the triple left in the 2026-05-14 migration, contradicted by `LIMITATIONS.md:335` two hundred and forty lines later, inside the document that declares itself authoritative. Two dangling non-file locators at `LIMITATIONS.md:209`.

**Every substantive claim behind the bad pointers checked out.** This is pointer hygiene, not prose surgery.

**Do not hand-fix.** A script that resolves every `file:line` in the public docs and fails on mismatch is about an hour, catches all fifteen, and goes into `arco-smoke-test.yml` beside `test_bfo_prose_direction.py`. Then it cannot recur.

### 2.5 Claim the one-bearer enforcement. Twenty minutes. Free credibility.

Asserting that two components bear the same disposition entails `sameAs`. Adding `differentFrom` produces a reasoner error that `run_pipeline.py:361` raises on. Two deployments cannot share a disposition token, and that is a hard run failure. **Nothing outward claims this.** It is the strongest realist bite in the repo and it is unclaimed.

### 2.6 Disclose the Gate-2 versus Gate-3 minting asymmetry. One paragraph.

Gate 2 mints bare process tokens with disclosure. Gate 3 refuses to mint role particulars and puns instead. There is a real principle behind the split: a Process needs no co-existing bearer, while an SDC Role logically requires one and RO enforces that through functional and inverse-functional property declarations. **[exhaustive]**, six routes checked, and the principle is written nowhere. A defensible split currently reads as arbitrary.

---

## 3. Corpus and positioning fixes

### 3.1 `four-layer-stack-and-value-ladder.md` refutes itself

Line 70 states that a realist commitment "is not a point on a strength-of-formalism series at all." Line 86 then heads the central table's third column "Adds over the layer below," and line 91 opens layer 4 with "everything in layer 3, plus." The correction is made once in prose and abandoned in the artifact carrying the argument. Line 97 says trust "turns on" at layer 3, which is the thesis of *Against Idiosyncrasy* inverted, in a file citing that paper at line 128. **[exhaustive]**, verified verbatim.

Also: line 131 files Cagle under a heading reading `## Canon anchors`, breaking the standing rule that he is a position to beat and never an authority. The concession at line 82 is defensible, but `realist-value-decomposition.md:126` already grounds the same concession in Adequatism, from inside the lineage, at no cost.

### 3.2 The gap register is about to institutionalize the habit

Section 6 assigns checkability to formalism and federation to the shared standard, and §4.B.4 recommends hardening the tradecraft-versus-standard separation into a house do-not-say rule. That is Neuhaus's two-predicate pluralism promoted to policy by people who do not hold it. **Accidental in origin, indefensible if shipped.**

### 3.3 The NCOR lineage claim, correctable at zero cost

The 2006 Obrst, Hughes and Ray paper is stance-neutral by construction, names Methontology as its example of principled methodology, and lists philosophical stance among the distinctions the field glosses over. Recruiting it as patrimony for a BFO and CCO conformance business claims a pluralist document as realist inheritance.

The honest version is stronger and survives a reader opening the PDF: **proposed graded, stance-neutral certification in 2006, ships framework conformance in 2026, and never shipped either.**

Citation defect in the same family: `ncor-lineage-...-2026-07-25.md:63` says "Lisa M. Hughes, EON Workshop hosted at NIST." It is **Todd Hughes, Lockheed Martin ATL, WWW 2006, Edinburgh.** NIST hosts the file. Section 7 of the paper disclaims all three institutions and NCOR, so "institutionally backed" falls.

### 3.4 NCOR's own site outruns what you are allowed to say

The live Mission page says BFO was "adopted by the U.S. Department of Defense as a standard." Two officials directed three baselines within their councils' scope.

**Resolution: reporting and asserting are different acts.** You may report what NCOR says, attributed. You may not assert it. The line that does both, and demonstrates the capability being sold:

> NCOR describes it as adopted as a standard. The signed memo I have read directs three baselines within the two councils' scope, attaches no enforcement or procurement mechanism, and twice preserves producer latitude.

Also: `ncor-self-description-2026-07-02` reads "Barry Smith, Director of NCOR" from image alt text. The Affiliates page says **Chair of the Board.** The same capture drops a hedge, truncates a stage, and reads a table as a quotation. Re-pull before any outward use.

### 3.5 Figures that must not travel

- **550.** `spine-paper-feed-2026-06-20.md:12` says "more than 550 ontology-driven endeavors build on BFO (VERIFIED per Barry Smith talks)." The figure occurs in no Barry source we hold. **[exhaustive]**, six enumerated routes. It is the only adoption figure carrying a VERIFIED label and the label is false.
- **$3B is not hedged.** `source-note_barry-smith-bfo-value-talk.md:66` claims Barry hedged both ~490 and $3B. The 490 is hedged, "probably about 490." The three billion is **"upwards of three billion dollars,"** which is a floor, the opposite of a hedge. That false premise is the stated reason a challenge edge was never set in the graph.
- **$300M versus $3B.** `the-whole-story_spine.md:57` says ~$300M. Same speaker says ~$3B in a later talk. Unreconciled, and `canon_barry-smith-and-the-gene-ontology.md:247` already names this line as needing the fix.
- **100+ coordinated biomedical ontologies (Nature Biotechnology 2007).** Called verified at `four-layer-stack:142`. The paper is not in the corpus. Four sites, one lineage, zero primary reads.

### 3.6 The A380 correction never propagated

`meaning-mismatch-failure-corpus.md:64` carries the card titled FLAGSHIP with the model named. `source-note_...systems-engineering.md:90` asserts the card "inherits the register's attribution correction." **Grep for that caveat returns zero.** The asserted propagation did not happen, and asserting it retired the todo. Also uncorrected at `the-one-story:49`. Barry never names the model in any of the five parts.

---

## 4. The asset nobody has used

**Barry defines failure, and the definition is BFO-shaped.** Systems engineering part 4, roughly 47:12 to 53:08.

A system fails when it can no longer achieve its purpose. There are two kinds of system, those that can suffer failure and those that cannot. The solar system cannot. He settles on **function** as the criterion, which makes **failability a disposition, borne in virtue of having a function.**

That is the same realizable-entity machinery ARCO already runs on, arriving from the strongest realist voice available, and it reframes the project as being about systems that can fail rather than about compliance. **It appears nowhere in the outward material.** **[single-pass]**, pin the video timestamp before outward use, since this is a machine transcript at captured-unverified tier.

---

## 5. What was verified clean

- The reality-versus-representation disjointness claim at `README.md:139` is **backed by a real axiom**, not an annotation. `bfo-2020.owl:1623-1630` declares `AllDisjointClasses` over independent, specifically dependent and generically dependent continuant. **[exhaustive]**, and it took four wrong rounds to establish, all failing on QName versus expanded-IRI serialization.
- Every tool the CV and README name is real at volume: ROBOT 88 references, HermiT 64, RDFLib 53, pySHACL 9.
- CI genuinely runs on push and pull request to main. Pages genuinely deploys and currently serves a live determination.
- The pipeline passes all six checks and emits exactly the artifacts claimed.
- The OWA discipline at `README.md:155` and in the re-derivation section is stated correctly.
- The dual-use disclosure and the falsification offer are rare and sound.

---

## 6. Sequence

1. README, both sites. 15 minutes.
2. The false blocker. 15 minutes.
3. Gate 3 disclosure with its bound. 1 hour.
4. Stale disclosures. 1 hour.
5. One-bearer claim and the Gate-2/3 asymmetry paragraph. 40 minutes.
6. Locator script, wired into CI. 1 to 2 hours.
7. Corpus and positioning items in section 3, which are not blocking a repo visit.

**Held deliberately:** the Gate 3 axiom itself, concretization build-out, and the joint ICE-to-kind question across L2.1, L2.7 and L2.9. Those are a modeling session, not pre-show cleanup.

---

## 7. How to not get this wrong

Everything reasoned toward on 2026-07-27 was wrong. Everything executed was right. The four-round disjointness failure, the false diagram overclaim, and a claim checker that shipped 46 percent typography were all reasoning. The 2x2 mutation, the pipeline runs, and the reintroduced-defect backtests were execution.

So: if a claim can be executed, execute it and paste the output. For any absence claim in a serialized file, search case-insensitively for the bare substring before any structured pattern, and enumerate serialization forms as explicitly as construct names. And when a domain expert says that cannot be right, treat their intuition as evidence the search is wrong rather than that the artifact is deficient.
