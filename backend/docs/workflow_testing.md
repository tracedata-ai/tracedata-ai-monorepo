# Workflow testing (Redis → ingestion → agents)

Telemetry enters the pipeline as **`TelemetryPacket`** JSON on **`telemetry:{truck_id}:buffer`**. Use the tools below from the **`backend/`** directory unless noted otherwise.

## Reset state

| Command | What it does |
|---------|----------------|
| `python scripts/clean_datastores.py` | **Redis FLUSHALL** + Postgres **drop_all / create_all** (destructive). |
| `python scripts/clean_datastores.py --skip-postgres` | Redis only. |
| `python scripts/clean_datastores.py --skip-redis` | Postgres only. |
| `python scripts/reset_db.py` | Postgres only (legacy alias; prefer `clean_datastores` when you also need Redis). |

Docker example:

```bash
docker compose exec -T api python scripts/clean_datastores.py
```

## Play a named workflow (recommended)

**`scripts/play_workflow.py`** validates each packet with Pydantic, then ZADDs them in order to one truck buffer.

```bash
# List built-in sequences (see ``common/workflow_fixtures/``)
python scripts/play_workflow.py --list-fixtures

# Full reset + push (~2h trip: smoothness, harsh events, end, feedback)
python scripts/play_workflow.py --fixture scoring_harsh_long_trip --truck T12345

# Short smoke: start → one smoothness → end
python scripts/play_workflow.py --fixture minimal_trip --truck TK001

# Custom trip id / driver
python scripts/play_workflow.py --fixture minimal_trip --trip-id TRP-DEV-001 --driver DRV-ANON-7829

# Only clear this truck’s buffer (no DB reset)
python scripts/play_workflow.py --fixture minimal_trip --no-reset --truck TK001

# Load packets from JSON (array or ``{ "events": [ ... ] }``)
python scripts/play_workflow.py --json path/to/events.json --truck T12345
```

Fixture modules live under **`common/workflow_fixtures/`** and expose **`build_events(...)`**. Add a new workflow by creating a module and registering it in **`common/workflow_fixtures/__init__.py`** (`FIXTURE_REGISTRY`).

Reference payloads: **`docs/03-agents/0_input_data.md`**.

## Multi-truck load seed (many trips)

For **five buffers** (TK001–TK005), each with many **start → smoothness → end** trips (E2E load):

```bash
REDIS_URL=redis://127.0.0.1:6379/0 python scripts/push_multi_truck_scoring_seed.py
python scripts/push_multi_truck_scoring_seed.py --trips-per-truck 5
```

Logic is in **`common/workflow_fixtures/multi_truck_scoring_seed.py`**. The PowerShell smoke **`scripts/scoring_e2e_docker.ps1`** calls this script inside the API container.

## Focused helpers

| Script | Use when |
|--------|-----------|
| **`push_smoothness_to_buffer.py`** | One **`smoothness_log`** with variants (`--exact-reference`, `--variant-seed`). |
| **`send_telemetry.py`** | Legacy DB seed + assorted Redis demos (`db`, `trips`, `diverse`, …). Prefer **`play_workflow`** for pipeline-shaped tests. |
| **`monitor_flow.py`** / **`inspect_debug_queues.py`** | Inspect queues. |
| **`docker_verify_flow.py`** | In-container smoke (buffer → pipeline_events). |

## End-to-end (Docker)

From repo root:

```powershell
pwsh -File backend/scripts/scoring_e2e_docker.ps1
```

Adjust **`-WaitSeconds`** if Postgres row counts are still catching up.
