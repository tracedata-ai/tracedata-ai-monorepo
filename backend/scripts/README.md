# Scripts Directory Guide

This folder has accumulated scripts for setup, demos, and diagnostics.

## Canonical scripts (recommended)

- `bootstrap_sg_baseline.py`  
  Idempotent startup bootstrap for local Docker runs:
  - ensures baseline entities (10 drivers, 10 trucks, 20 Singapore routes)
  - pushes baseline trip workflows to Redis once (`td:bootstrap:sg_baseline:v1`)
- `play_workflow.py`  
  Main fixture player for deterministic pipeline testing.
- `setup_db.py`  
  Initialize DB tables.

## Useful diagnostics

- `monitor_flow.py`
- `trace_ingestion.py`
- `inspect_debug_queues.py`
- `docker_verify_flow.py`

## Legacy/demo scripts (kept for compatibility)

- `send_telemetry.py`
- `fleet_support_agent_demo.py`
- `push_smoothness_to_buffer.py`
- `push_multi_truck_scoring_seed.py`
- `verify_scoring_agent_cache.py`
- `clean_datastores.py`
- `reset_db.py`

When adding new scripts, prefer extending `play_workflow.py` or adding new fixtures
under `common/workflow_fixtures/` instead of creating one-off generators.
# `backend/scripts`

Operational and developer entry points.

**Pipeline and agent workflow testing** (reset, Redis buffer, fixtures) is covered in **[`backend/docs/workflow_testing.md`](../docs/workflow_testing.md)**.

## `play_workflow.py` (quick reference)

Run from the **`backend/`** directory. Validates packets and pushes them in order to **`telemetry:{truck_id}:buffer`**.

```bash
python scripts/play_workflow.py --list-fixtures
python scripts/play_workflow.py --fixture scoring_harsh_long_trip --truck T12345
python scripts/play_workflow.py --fixture minimal_trip --no-reset --truck TK001
python scripts/play_workflow.py --json path/to/events.json --truck T12345
```

### `scoring_harsh_long_trip`: `--segments` (one trip, partial timeline)

**Fixture:** **`scoring_harsh_long_trip`**. Without **`--segments`**, you get the **full** sequence: **start of trip → 12× smoothness_log → harsh events (1 hard accel + 3 harsh brakes) → end of trip → driver feedback** (19 packets total; timeline order is fixed; the flag only *drops* steps you omit).

Pass **`--segments`** with a comma-separated subset. Names are short tokens; **order in the flag does not matter** (emission always follows the trip timeline).

| What you want | Command |
|---------------|---------|
| **Full trip** (all of the below in one run) | `python scripts/play_workflow.py --fixture scoring_harsh_long_trip` |
| **Start of trip** only (`start_of_trip`, 1 packet) | `python scripts/play_workflow.py --fixture scoring_harsh_long_trip --segments start` |
| Same as **`--segments start`** | `python scripts/play_workflow.py --fixture scoring_harsh_long_trip --start-only` |
| **Smoothness logs** only — **12** `smoothness_log` windows | `python scripts/play_workflow.py --fixture scoring_harsh_long_trip --segments smooth` |
| **Harsh events** only — **1** hard accel + **3** harsh brakes | `python scripts/play_workflow.py --fixture scoring_harsh_long_trip --segments harsh` |
| **End of trip** only (`end_of_trip`, 1 packet) | `python scripts/play_workflow.py --fixture scoring_harsh_long_trip --segments end` |
| **Driver feedback** only (`driver_feedback`, 1 packet) | `python scripts/play_workflow.py --fixture scoring_harsh_long_trip --segments feedback` |

**Combine** segments by joining tokens with commas (still one timeline; for example start + all 12 smooth logs + end, no harsh or feedback):

```bash
python scripts/play_workflow.py --fixture scoring_harsh_long_trip --segments start,smooth,end
```

```bash
python scripts/play_workflow.py --fixture scoring_harsh_long_trip --segments start,harsh,smooth,end,feedback
```

**Notes**

- **`--segments`** / **`--start-only`** only work for fixtures whose **`build_events`** accepts **`segments`** (right now **`scoring_harsh_long_trip`**).
- **`scoring_harsh_long_trip`** assigns **new UUID-style `event_id` / `device_event_id` per packet**; **`trip_id`** stays the same for the whole trip (override with **`--trip-id`**).
- Override ids when needed: **`--truck`**, **`--trip-id`**, **`--driver`**.
- Add **`--no-reset`** to skip a full DB/Redis reset and only clear this truck’s buffer (see **`workflow_testing.md`**).

Fixture code: **`common/workflow_fixtures/scoring_harsh_long_trip.py`**. Payload shape: **`docs/03-agents/0_input_data.md`**.

After pushing events, with the **ingestion worker** running (`python -m core.ingestion.worker` or the `docker compose` service), trace Redis → Postgres:

`python scripts/trace_ingestion.py --truck T12345 --trip-id TRP-2026-a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6`
