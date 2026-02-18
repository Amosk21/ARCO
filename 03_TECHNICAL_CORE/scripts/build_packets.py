"""
build_packets.py — Extract ARCO candidate packets from GraphRAG parquet output.

PURPOSE: Takes the GraphRAG output (entities.parquet, relationships.parquet,
text_units.parquet) and builds evidence-grounded packets for ARCO mapping.

Each packet = { entity + neighbor relationships + source text evidence }

Run this on your local machine where the GraphRAG output lives:
    python build_packets.py

Output: exports/arco_candidate_packets.json

USAGE NOTE:
    - Adjust ROOT below to point to your GraphRAG project root
    - Adjust KW list to match ARCO concepts you care about
    - Adjust TOP_N to control how many entities get packetized (keep small)
"""

import json
import re
from pathlib import Path

import duckdb

# ---------------------------------------------------------------
# CONFIGURATION — EDIT THESE FOR YOUR ENVIRONMENT
# ---------------------------------------------------------------

# Point this to your GraphRAG project root (where output/ lives)
ROOT = Path(r"C:\Users\subdu\Documents\graphrag_arco")
OUT = ROOT / "output"
EXPORTS = ROOT / "exports"
EXPORTS.mkdir(parents=True, exist_ok=True)

entities_pq = str(OUT / "entities.parquet")
rels_pq = str(OUT / "relationships.parquet")
texts_pq = str(OUT / "text_units.parquet")

con = duckdb.connect()

# Keywords tuned to ARCO ontology concepts
# (system parts, roles, artifacts, processes, governance)
KW = [
    "system", "model", "api", "deployment", "inference", "pipeline",
    "tool", "computer use", "vision", "multimodal", "agent", "agentic",
    "capability", "risk", "safety", "oversight", "audit", "logging",
    "trace", "evaluation", "benchmark", "red-team", "red team",
    "policy", "responsible scaling", "rsp", "asl", "mitigation",
    "incident", "provider", "deployer", "operator", "user", "customer",
    "data", "training", "documentation", "model card", "addendum",
]

# How many entities to packetize (keep small = cheap mapping step)
TOP_N = 40

# How much evidence per entity
MAX_TEXT_UNITS_PER_ENTITY = 12
MAX_CHARS_PER_SNIPPET = 900


# ---------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------

def norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())

def clip(s: str, n: int) -> str:
    s = s or ""
    return s if len(s) <= n else s[: n - 3] + "..."

def flatten_ids(series):
    ids = []
    for v in series.dropna().tolist():
        if isinstance(v, (list, tuple)):
            ids.extend([str(x) for x in v])
        else:
            ids.append(str(v))
    return ids


# ---------------------------------------------------------------
# 1) PULL CANDIDATE ENTITIES BY KEYWORD MATCH
# ---------------------------------------------------------------

where = " OR ".join(
    [f"lower(title) LIKE '%{k.lower()}%'" for k in KW]
    + [f"lower(description) LIKE '%{k.lower()}%'" for k in KW]
)

cand = con.sql(f"""
SELECT id, human_readable_id, title, type, description,
       text_unit_ids, frequency, degree
FROM read_parquet('{entities_pq}')
WHERE {where}
ORDER BY degree DESC, frequency DESC
LIMIT {TOP_N}
""").df()

# Fallback: if keyword match yields too few, take top-degree entities
if len(cand) < 10:
    cand = con.sql(f"""
    SELECT id, human_readable_id, title, type, description,
           text_unit_ids, frequency, degree
    FROM read_parquet('{entities_pq}')
    ORDER BY degree DESC, frequency DESC
    LIMIT {TOP_N}
    """).df()

entity_ids = cand["id"].astype(str).tolist()


# ---------------------------------------------------------------
# 2) PULL NEIGHBOR RELATIONSHIPS
# ---------------------------------------------------------------

neighbors = con.sql(f"""
SELECT id, human_readable_id, source, target, description,
       weight, combined_degree, text_unit_ids
FROM read_parquet('{rels_pq}')
WHERE source IN ({",".join([repr(x) for x in cand["title"].astype(str).tolist()])})
   OR target IN ({",".join([repr(x) for x in cand["title"].astype(str).tolist()])})
ORDER BY combined_degree DESC
LIMIT 400
""").df()


# ---------------------------------------------------------------
# 3) PULL EVIDENCE SNIPPETS FROM TEXT_UNITS
# ---------------------------------------------------------------

tu_ids = list(dict.fromkeys(
    flatten_ids(cand["text_unit_ids"])
    + flatten_ids(neighbors["text_unit_ids"])
))
tu_ids = tu_ids[:1500]  # cap for speed

if tu_ids:
    evidence_all = con.sql(f"""
    SELECT id, human_readable_id, text, n_tokens,
           document_id, entity_ids, relationship_ids
    FROM read_parquet('{texts_pq}')
    WHERE id IN ({",".join([repr(x) for x in tu_ids])})
    """).df()
else:
    evidence_all = con.sql(f"""
    SELECT id, human_readable_id, text, n_tokens,
           document_id, entity_ids, relationship_ids
    FROM read_parquet('{texts_pq}')
    LIMIT 0
    """).df()

evidence_by_id = {str(r["id"]): r for _, r in evidence_all.iterrows()}


# ---------------------------------------------------------------
# 4) BUILD PACKETS
# ---------------------------------------------------------------

packets = []
for _, e in cand.iterrows():
    title = str(e["title"])
    etype = str(e["type"])
    desc = norm(str(e["description"])) if e["description"] is not None else ""
    e_tu = e["text_unit_ids"] if e["text_unit_ids"] is not None else []
    if not isinstance(e_tu, (list, tuple)):
        e_tu = [e_tu]

    # neighbor rels for this entity
    rels = neighbors[
        (neighbors["source"] == title) | (neighbors["target"] == title)
    ].copy()
    rels = rels.sort_values(by="combined_degree", ascending=False).head(25)

    # evidence ids: entity text_unit_ids first, then relationship ones
    rel_tu = flatten_ids(rels["text_unit_ids"])
    ev_ids = list(dict.fromkeys([str(x) for x in e_tu] + rel_tu))
    ev_ids = [x for x in ev_ids if x in evidence_by_id][:MAX_TEXT_UNITS_PER_ENTITY]

    ev = []
    for tid in ev_ids:
        row = evidence_by_id[tid]
        ev.append({
            "text_unit_id": str(row["id"]),
            "human_readable_id": (
                int(row["human_readable_id"])
                if row["human_readable_id"] is not None else None
            ),
            "n_tokens": (
                int(row["n_tokens"])
                if row["n_tokens"] is not None else None
            ),
            "text": clip(norm(str(row["text"])), MAX_CHARS_PER_SNIPPET),
            "document_id": row["document_id"],
        })

    packets.append({
        "entity": {
            "id": str(e["id"]),
            "human_readable_id": (
                int(e["human_readable_id"])
                if e["human_readable_id"] is not None else None
            ),
            "title": title,
            "type": etype,
            "description": desc,
            "degree": int(e["degree"]) if e["degree"] is not None else None,
            "frequency": int(e["frequency"]) if e["frequency"] is not None else None,
        },
        "neighbors": [
            {
                "source": str(r["source"]),
                "target": str(r["target"]),
                "description": (
                    norm(str(r["description"]))
                    if r["description"] is not None else ""
                ),
                "combined_degree": (
                    int(r["combined_degree"])
                    if r["combined_degree"] is not None else None
                ),
                "relationship_id": str(r["id"]),
            }
            for _, r in rels.iterrows()
        ],
        "evidence": ev,
    })

out_path = EXPORTS / "arco_candidate_packets.json"
out_path.write_text(json.dumps(packets, indent=2), encoding="utf-8")

print(f"Wrote packets: {out_path}")
print(f"Entities packetized: {len(packets)}")
print(f"Total evidence snippets: {sum(len(p['evidence']) for p in packets)}")
print(f"Total neighbor relations: {sum(len(p['neighbors']) for p in packets)}")
