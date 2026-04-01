"""
TraceData Backend — Test Suite.

Layout:
  tests/agents, tests/common, tests/core  — unit + integration modules

SQLite integration (no Docker): ``@pytest.mark.integration`` on
``test_repositories_integration``, ``test_ingestion_db_integration``,
``test_full_pipeline_integration``, ``test_cache_warming_orchestrator_integration``.

Run only integration-marked tests::

    uv run pytest -m integration -v

Full suite::

    uv run pytest tests/ -v
"""
