# ARCO MCP Server

A thin Model Context Protocol (MCP) server that exposes ARCO's deterministic
EU AI Act Annex III classification pipeline as typed tools an MCP client
(such as Claude Code or Claude Desktop) can call.

The server is read-only. It dispatches to existing pipeline scripts and
on-disk SPARQL queries / SHACL shapes. It does not modify any ARCO source
file. ARCO's classification remains deterministic (OWL-RL + SHACL + SPARQL).
The MCP layer is purely a transport.

## Tools

| Tool | What it does |
|---|---|
| `arco_run_pipeline` | Runs `run_pipeline.py` against an instances file and returns parsed structured output (classification, certificate, two-layer pass/fail, exception flags). |
| `arco_run_hermit_crosscheck` | Materializes the HermiT-reasoned graph via ROBOT, runs the seven Sentinel SPARQL queries against it, and diffs against the OWL-RL baseline. Mirrors the CI cross-check in `.github/workflows/robot-validate.yml`. |
| `arco_competency_check` | Runs a single competency question (CQ1..CQ12 from `docs/COMPETENCY_QUESTIONS.md`) against a system. Returns the question text, regulatory anchor, layer (OWL-RL / SHACL / SPARQL_ASK), implementing file, raw result, and a one-sentence interpretation. |

## Prerequisites

- Python 3.10+
- ARCO repo cloned (this directory must live at `mcp/` inside the repo)
- Dependencies installed: `pip install -r mcp/requirements.txt`
- For `arco_run_hermit_crosscheck` only: ROBOT v1.9.10 JAR at `~/.local/share/robot/robot.jar` or a `ROBOT_JAR` environment variable pointing to the JAR. Java 17+ on `PATH`. ROBOT is only required for the cross-check tool; the other two tools work without it.

The pipeline-invoking tool (`arco_run_pipeline`) shells out to the real
`03_TECHNICAL_CORE/scripts/run_pipeline.py`, so the same Python environment
that runs the MCP server must also be able to run the ARCO pipeline.

## Install

```bash
cd "<ARCO repo root>"
pip install -r mcp/requirements.txt
python mcp/test_arco_mcp.py
```

The smoke test prints `ALL SMOKE TESTS PASSED` and exits 0 on success.

## Running the server

The server uses STDIO transport, the standard MCP local-server pattern.

```bash
python mcp/arco_mcp.py
```

This will block on stdio waiting for a client to send JSON-RPC messages.
Direct invocation is mainly useful for sanity-checking that the server
starts. In normal use, the client (e.g. Claude Code) launches the server
on demand.

### Registering with Claude Code

See the official MCP docs at https://modelcontextprotocol.io for the most
current instructions. Typical pattern: add the server to Claude Code's
config (e.g. `claude_desktop_config.json` or `.mcp.json`) with a `command`
of `python` and `args` of `["<absolute-path>/mcp/arco_mcp.py"]`.

Example config snippet:

```json
{
  "mcpServers": {
    "arco": {
      "command": "python",
      "args": ["C:/Github Repos/ARCO/mcp/arco_mcp.py"]
    }
  }
}
```

After registering, the three tools (`arco_run_pipeline`,
`arco_run_hermit_crosscheck`, `arco_competency_check`) appear in the
client's tool list.

## Example tool calls

### `arco_run_pipeline`

Default Sentinel run:

```json
{
  "tool": "arco_run_pipeline",
  "arguments": { "system": "Sentinel_ID_System" }
}
```

Returns (abridged):

```json
{
  "classification": "AnnexIII1aApplicableSystem",
  "primary_arco_classes": ["AnnexIII1aApplicableSystem"],
  "latent_risk_flag": true,
  "latent_risk_mode": "INFERRED",
  "annex_iii_1a": "VERIFIED (ENTAILED, Article 6(3) derogation not evaluated)",
  "annex_iii_5b": "NOT APPLICABLE",
  "derogation_flagged": false,
  "fraud_flagged": false,
  "entailed_triples_added": 19886,
  "classification_layer": "PASS",
  "audit_layer": "PASS",
  "all_checks_passed": true,
  "certificate_text": "===... ARCO CONDITION ASSESSMENT CERTIFICATE ...==="
}
```

Custom system + instances file:

```json
{
  "tool": "arco_run_pipeline",
  "arguments": {
    "system": "CreditScorer_001",
    "instances": "03_TECHNICAL_CORE/ontology/ARCO_instances_credit_scorer.ttl"
  }
}
```

### `arco_run_hermit_crosscheck`

```json
{ "tool": "arco_run_hermit_crosscheck", "arguments": {} }
```

Returns:

```json
{
  "hermit_status": "PASS",
  "agreement": true,
  "queries_total": 7,
  "queries_matching": 7,
  "query_results": [
    {"name": "high_risk", "hermit_result": true,  "owlrl_result": true,  "expected": true,  "match": true},
    {"name": "annex_1a",  "hermit_result": true,  "owlrl_result": true,  "expected": true,  "match": true},
    {"name": "annex_5b",  "hermit_result": false, "owlrl_result": false, "expected": false, "match": true}
  ],
  "mismatches": []
}
```

If ROBOT is not installed:

```json
{
  "error": true,
  "hermit_status": "UNAVAILABLE",
  "message": "ROBOT JAR not found. Install ROBOT v1.9.10 to ~/.local/share/robot/robot.jar or set ROBOT_JAR..."
}
```

### `arco_competency_check`

```json
{
  "tool": "arco_competency_check",
  "arguments": { "cq_id": "CQ2", "system": "Sentinel_ID_System" }
}
```

Returns:

```json
{
  "cq_id": "CQ2",
  "cq_question": "Does this system meet all three gates for Annex III item 1(a)?",
  "regulatory_anchor": "Annex III item 1(a) (biometric identification)",
  "layer": "OWL-RL",
  "answered_by": "03_TECHNICAL_CORE/reasoning/check_annex_iii_1a_entailment.sparql",
  "result": true,
  "interpretation": "Sentinel_ID_System is in the AnnexIII1aApplicableSystem extension.",
  "system": "Sentinel_ID_System"
}
```

## Manual stdio test

The server speaks the MCP JSON-RPC protocol over stdio. To verify the
process starts and accepts an initialize message, you can pipe one in:

```bash
printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"smoke","version":"0.0.1"}}}' | python mcp/arco_mcp.py
```

The server should respond with a JSON-RPC `result` containing
`serverInfo.name == "arco"`. (The process will then keep waiting on stdin;
hit Ctrl+C to exit.)

## Limitations

- `arco_run_hermit_crosscheck` requires ROBOT v1.9.10 + Java 17+. Without ROBOT, the tool returns a structured `hermit_status: "UNAVAILABLE"` error rather than crashing.
- `arco_competency_check` re-reasons the graph in-process on each call (10-30s). For batch competency-check runs, consider calling `arco_run_pipeline` once and then mapping its output rather than calling each CQ separately.
- ARCO currently models Annex III item 1(a) (biometric identification) and 5(b) (creditworthiness) only. CQs covering those categories are answerable; categories not yet modeled return NotApplicable.
- Tools resolve paths relative to the ARCO repo root (computed from this script's location). Moving `arco_mcp.py` outside the `mcp/` subdirectory will break path resolution.

## Files

- `arco_mcp.py` — the MCP server (FastMCP + three tools).
- `requirements.txt` — Python dependencies.
- `test_arco_mcp.py` — smoke test suite.
- `README.md` — this file.
