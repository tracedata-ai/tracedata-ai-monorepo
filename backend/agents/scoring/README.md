# agents/scoring

Sree's agent for behavior scoring and XAI. Runs as an independent Celery worker container.

- **agent.py**: `ScoringAgent` class inheriting from `TDAgentBase`.
- **graph.py**: Scoring-specific LangGraph nodes.
- **tools.py**: XGBoost, SHAP, and Fairness tools.
- **model/**: Directory for trained model artifacts and training scripts.
- **tasks.py**: Celery task definition for `score_trip`.
