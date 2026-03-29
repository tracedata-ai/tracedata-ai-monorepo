# agents/sentiment

Zhicheng's agent for feedback and sentiment analysis. Runs as an independent Celery worker container.

- **agent.py**: `SentimentAgent` class inheriting from `TDAgentBase`.
- **graph.py**: Sentiment-specific LangGraph nodes.
- **tools.py**: LLM call, pgvector search, and embedding tools.
- **tasks.py**: Celery task definition for `analyse_feedback`.
