"""情绪代理（使用受限仓储）。

仅通过 SentimentRepository 写入 sentiment_schema 下的表。
"""

import logging
from datetime import UTC, datetime
from typing import Any

from agents.base.agent import TDAgentBase
from agents.sentiment.analysis import (
    EMOTIONS,
    avg,
    clamp_score,
    compute_risk_level,
    compute_trend,
    compute_window_stats,
    dominant_emotion_info,
    sentiment_label_from_risk,
)
from agents.sentiment.graph import SentimentState, build_sentiment_graph
from common.cache.reader import CacheReader
from common.db.engine import engine
from common.db.repositories.support_repo import SentimentRepository
from common.embeddings import OpenAIEmbeddingService, vector_to_pgvector_literal
from common.llm import OpenAIModel, load_llm
from common.models.security import IntentCapsule
from common.redis.client import RedisClient

logger = logging.getLogger(__name__)

# 历史情绪上下文的滑动窗口天数。
WINDOW_DAYS = 5
# 每次分析最多读取的历史记录条数。
TOP_K_HISTORY = 10
# 相似度聚合时使用的最近锚点向量数量。
ANCHOR_TOP_K = 8

EMOTION_ANCHORS: dict[str, tuple[str, ...]] = {
    "fatigue": ("tired", "fatigue", "exhausted", "drained", "sleepy", "worn out"),
    "anxiety": ("anxious", "nervous", "worried", "uneasy", "tense", "stressed"),
    "anger": ("angry", "frustrated", "irritated", "annoyed", "furious", "mad"),
    "sadness": ("sad", "down", "low", "discouraged", "upset", "disappointed"),
}

SENTIMENT_VECTOR_ANCHORS: tuple[dict[str, str], ...] = (
    {
        "key": "fatigue-1",
        "emotion": "fatigue",
        "text": "I feel exhausted, drained, low on energy, and mentally tired after driving.",
    },
    {
        "key": "fatigue-2",
        "emotion": "fatigue",
        "text": "I am very tired and it is harder than usual to stay focused.",
    },
    {
        "key": "anxiety-1",
        "emotion": "anxiety",
        "text": "I feel nervous, tense, and worried about the trip and what could go wrong.",
    },
    {
        "key": "anxiety-2",
        "emotion": "anxiety",
        "text": "I feel stressed and uneasy, like I cannot fully relax.",
    },
    {
        "key": "anger-1",
        "emotion": "anger",
        "text": "I feel angry, irritated, and frustrated by what happened on the road.",
    },
    {
        "key": "anger-2",
        "emotion": "anger",
        "text": "I feel upset and annoyed, and small things are making me react strongly.",
    },
    {
        "key": "sadness-1",
        "emotion": "sadness",
        "text": "I feel low, discouraged, and emotionally heavy after this trip.",
    },
    {
        "key": "sadness-2",
        "emotion": "sadness",
        "text": "I feel down and disappointed, and it is hard to stay positive.",
    },
)

SENTIMENT_EXPLANATION_SYSTEM_PROMPT = (
    """You are the Sentiment Explanation Agent in the TraceData platform.
Your task is to explain the emotional assessment result for a truck driver.

Important rules:
1. Do not calculate or change any scores.
2. Do not infer emotions that are not supported by the provided results.
3. Do not give any medical, psychological, or clinical diagnosis.
4. Keep the explanation clear, supportive, and professional.
5. Focus on operationally relevant emotional signals such as fatigue, anxiety, anger, sadness, stress, frustration, or emotional stability.
6. If trend information is provided, mention whether the driver's emotional condition appears stable, improving, or worsening.
7. Avoid punishment-oriented language. The tone should be constructive and human-centered.
8. Keep the explanation concise, around 3 to 5 sentences.
9. Treat sentiment labels as risk bands only: positive=low emotional risk, neutral=moderate emotional risk, negative=high emotional risk; do not interpret them as medical positive/negative test results.

Output requirements:
- Write one short explanation paragraph in plain English.
- Explain the main emotional signals shown in the results.
- Mention the most important risk-relevant emotional factor if one exists.
- If appropriate, mention whether the recent pattern suggests stability or growing concern.
- If you mention the label, explain it as emotional risk level (low/moderate/high), not a medical test outcome.
- Do not output JSON.
""".strip()
)


class SentimentAgent(TDAgentBase):
    """分析司机反馈中的情绪信号。"""

    AGENT_NAME = "sentiment"

    def __init__(
        self,
        engine_param=None,
        redis_client: RedisClient | None = None,
    ):
        """使用情绪专用仓储初始化代理。"""
        # 基类负责注入 DB 引擎、Redis 客户端、执行生命周期与基础保护逻辑。
        super().__init__(engine_param or engine, redis_client)
        # 仅允许通过情绪仓储进行受限写入。
        self.sentiment_repo = SentimentRepository(self._engine)
        # 进程内标记：避免重复播种静态情绪锚点。
        self._anchors_seeded = False
        try:
            # 用于生成解释文本的专用聊天模型。
            self._llm = load_llm(OpenAIModel.GPT_4O_MINI).adapter.get_chat_model()
        except Exception as exc:
            logger.warning(
                {
                    "action": "sentiment_llm_unavailable",
                    "error": str(exc),
                }
            )
            self._llm = None
        try:
            # Embedding 服务用于语义锚点匹配（pgvector 路径）。
            self._embedding_service = OpenAIEmbeddingService()
        except Exception as exc:
            logger.warning(
                {
                    "action": "sentiment_embeddings_unavailable",
                    "error": str(exc),
                }
            )
            self._embedding_service = None
        # 构建确定性的节点图，确保打分、历史、趋势与解释按固定顺序执行。
        self._graph = build_sentiment_graph(
            score_current=self._score_current_node,
            load_history=self._load_history_node,
            analyze_window=self._analyze_window_node,
            explain=self._explain_node,
            assemble_output=self._assemble_output_node,
        )

    async def run(self, capsule_data: dict) -> dict[str, Any]:
        # 先校验输入 capsule，保证下游可按类型字段访问。
        capsule = IntentCapsule.model_validate(capsule_data)
        logger.info(
            {
                "action": "sentiment_run_started",
                "trip_id": capsule.trip_id,
            }
        )

        # 执行标准代理生命周期；内部会调用 _execute。
        result = await super().run(capsule_data)
        if result.get("status") != "success":
            logger.info(
                {
                    "action": "sentiment_run_finished_non_success",
                    "trip_id": capsule.trip_id,
                    "status": result.get("status"),
                }
            )
            return result

        from agents.orchestrator.sentiment_followup import (
            schedule_sentiment_ready_if_success,
        )

        # 仅在成功分析后发送后续流程就绪信号。
        await schedule_sentiment_ready_if_success(
            redis=self._redis,
            engine=self._engine,
            trip_id=capsule.trip_id,
        )
        logger.info(
            {
                "action": "sentiment_followup_scheduled",
                "trip_id": capsule.trip_id,
            }
        )
        return result

    async def _execute(
        self,
        trip_id: str,
        cache_data: dict[str, Any],
    ) -> dict[str, Any]:
        """执行司机反馈情绪分析。"""
        try:
            logger.info(
                {
                    "action": "sentiment_execute_started",
                    "trip_id": trip_id,
                }
            )
            # 从混合缓存结构中只提取当前分析所需字段。
            raw = CacheReader.by_key_markers(
                cache_data, "trip_context", "current_event"
            )
            trip_context = (
                raw["trip_context"] if isinstance(raw["trip_context"], dict) else None
            )
            current_event = (
                raw["current_event"] if isinstance(raw["current_event"], dict) else None
            )

            # 防御式提取：即使事件载荷不完整，也尽量保证流程可继续。
            driver_id = (
                (trip_context or {}).get("driver_id", "driver_id_placeholder")
                if trip_context
                else "driver_id_placeholder"
            )
            event_id = self._extract_submission_id(current_event)
            event_timestamp = self._extract_submission_timestamp(current_event)
            feedback_text = self._extract_feedback_text(current_event)
            logger.info(
                {
                    "action": "sentiment_input_extracted",
                    "trip_id": trip_id,
                    "driver_id": driver_id,
                    "submission_id": event_id,
                    "feedback_length": len(feedback_text),
                }
            )

            # 构建最小图状态，后续由各节点逐步补充。
            initial_state: SentimentState = {
                "driver_id": driver_id,
                "submission_id": event_id,
                "timestamp": event_timestamp.isoformat(),
                "text": feedback_text,
            }

            # 执行情绪图流程（打分 -> 历史 -> 趋势/风险 -> 解释）。
            graph_result = await self._graph.ainvoke(initial_state)
            logger.info(
                {
                    "action": "sentiment_graph_completed",
                    "trip_id": trip_id,
                    "submission_id": event_id,
                }
            )
            final_output = graph_result.get("final_output") or {}

            # 对图输出做兜底归一化，避免 KeyError。
            emotion_scores = final_output.get("current_scores") or {
                emotion: 0.0 for emotion in EMOTIONS
            }
            window_stats = final_output.get("window_stats") or {}
            trend = final_output.get("trend") or {}
            risk_level = float(final_output.get("risk_level", 0.0))
            sentiment = sentiment_label_from_risk(risk_level)
            dominant_emotion, dominant_score = dominant_emotion_info(emotion_scores)
            explanation = str(final_output.get("explanation") or "").strip()
            if not explanation:
                # 若图解释节点返回空文本，则再次执行解释回退。
                explanation = await self._build_explanation(
                    feedback_text=feedback_text,
                    sentiment=sentiment,
                    emotion_scores=emotion_scores,
                    window_stats=window_stats,
                    trend=trend,
                    risk_level=risk_level,
                )

            # 仅在向量路径生效时保留当前 embedding 用于落库。
            current_embedding = graph_result.get("current_embedding")

            # 将结果写入 sentiment schema，并附带紧凑分析元数据。
            sentiment_id = await self.sentiment_repo.write_feedback_sentiment(
                trip_id=trip_id,
                driver_id=driver_id,
                feedback_text=feedback_text,
                sentiment_score=risk_level,
                sentiment_label=sentiment,
                analysis={
                    # 记录打分路径，便于审计和离线对比。
                    "method": (
                        "pgvector_anchor_similarity_v1"
                        if self._embedding_service is not None
                        else "anchor_heuristic_fallback_v1"
                    ),
                    "current_scores": emotion_scores,
                    "window_stats": window_stats,
                    "trend": trend,
                    "risk_level": risk_level,
                    "dominant_emotion": dominant_emotion,
                    "dominant_emotion_score": dominant_score,
                    "history_count": len(final_output.get("history_rows", [])),
                    "explanation": explanation,
                },
                event_id=event_id,
                device_event_id=(
                    # device_event_id 为可选字段，某些生产者可能不提供。
                    str(current_event.get("device_event_id"))
                    if isinstance(current_event, dict)
                    and current_event.get("device_event_id")
                    else None
                ),
                submission_timestamp=event_timestamp,
                feedback_embedding_literal=(
                    # 仅在存在合法 embedding 时写入向量。
                    vector_to_pgvector_literal(current_embedding)
                    if isinstance(current_embedding, list)
                    else None
                ),
            )

            logger.info(
                {
                    "action": "sentiment_analysis_complete",
                    "trip_id": trip_id,
                    "sentiment": sentiment,
                    "risk_level": risk_level,
                    "sentiment_id": sentiment_id,
                }
            )

            return {
                "status": "success",
                "sentiment": sentiment,
                "sentiment_score": risk_level,
                # 同时保留两个字段名，兼容下游消费者。
                "risk_level": risk_level,
                "emotion_scores": emotion_scores,
                "current_scores": emotion_scores,
                "window_stats": window_stats,
                "trend": trend,
                "dominant_emotion": dominant_emotion,
                "dominant_emotion_score": dominant_score,
                "explanation": explanation,
                "sentiment_id": sentiment_id,
                "trip_id": trip_id,
                "driver_id": driver_id,
                "submission_id": event_id,
                "timestamp": event_timestamp.isoformat(),
            }

        except Exception as e:
            logger.error(
                {
                    "action": "sentiment_analysis_error",
                    "trip_id": trip_id,
                    "error": str(e),
                }
            )
            raise

    def _get_repos(self) -> dict[str, Any]:
        """返回 SentimentAgent 持有的仓储对象。"""
        # 基类会用它做归属校验与受控清理。
        return {"sentiment_repo": self.sentiment_repo}

    async def _score_current_node(self, state: SentimentState) -> dict[str, Any]:
        # 对当前反馈进行向量锚点打分；失败时记录错误并中断流程。
        current_scores, current_embedding = await self._score_text_against_anchors(
            state["text"]
        )
        logger.info(
            {
                "action": "sentiment_node_score_current_success",
                "driver_id": state.get("driver_id"),
                "submission_id": state.get("submission_id"),
                "has_embedding": isinstance(current_embedding, list),
            }
        )
        return {
            "current_scores": current_scores,
            "current_embedding": current_embedding,
        }

    async def _load_history_node(self, state: SentimentState) -> dict[str, Any]:
        # 查询历史前先解析图状态中的 ISO 时间。
        timestamp = datetime.fromisoformat(state["timestamp"])
        history_rows = await self.sentiment_repo.fetch_recent_feedback_history(
            driver_id=state["driver_id"],
            current_timestamp=timestamp,
            window_days=WINDOW_DAYS,
            limit=TOP_K_HISTORY,
        )
        logger.info(
            {
                "action": "sentiment_node_load_history_success",
                "driver_id": state.get("driver_id"),
                "submission_id": state.get("submission_id"),
                "history_count": len(history_rows),
                "window_days": WINDOW_DAYS,
                "limit": TOP_K_HISTORY,
            }
        )
        return {"history_rows": history_rows}

    def _analyze_window_node(self, state: SentimentState) -> dict[str, Any]:
        # 聚合最近历史，生成按情绪维度的窗口统计。
        window_stats = compute_window_stats(state.get("history_rows", []))
        # 将当前分数与历史基线对比，推断趋势方向。
        trend = compute_trend(state["current_scores"], window_stats)
        # 将当前信号和趋势信号压缩为单一风险标量。
        risk_level = compute_risk_level(state["current_scores"], trend)
        logger.info(
            {
                "action": "sentiment_node_analyze_window_success",
                "driver_id": state.get("driver_id"),
                "submission_id": state.get("submission_id"),
                "risk_level": risk_level,
            }
        )
        return {
            "window_stats": window_stats,
            "trend": trend,
            "risk_level": risk_level,
        }

    async def _explain_node(self, state: SentimentState) -> dict[str, Any]:
        # 解释节点基于风险标签和辅助指标生成最终说明。
        sentiment = sentiment_label_from_risk(float(state["risk_level"]))
        explanation = await self._build_explanation(
            feedback_text=state["text"],
            sentiment=sentiment,
            emotion_scores=state["current_scores"],
            window_stats=state.get("window_stats"),
            trend=state.get("trend"),
            risk_level=state.get("risk_level"),
        )
        logger.info(
            {
                "action": "sentiment_node_explain_success",
                "driver_id": state.get("driver_id"),
                "submission_id": state.get("submission_id"),
                "sentiment": sentiment,
                "explanation_length": len(explanation),
            }
        )
        return {"explanation": explanation}

    def _assemble_output_node(self, state: SentimentState) -> dict[str, Any]:
        # 组装标准化输出，供 _execute 统一落库并返回。
        final_output = {
            "driver_id": state["driver_id"],
            "submission_id": state["submission_id"],
            "timestamp": state["timestamp"],
            "text": state["text"],
            "current_scores": state["current_scores"],
            "window_stats": state.get("window_stats", {}),
            "trend": state.get("trend", {}),
            "risk_level": state.get("risk_level", 0.0),
            "history_rows": state.get("history_rows", []),
            "explanation": state.get("explanation", ""),
        }
        logger.info(
            {
                "action": "sentiment_node_assemble_output_success",
                "driver_id": state.get("driver_id"),
                "submission_id": state.get("submission_id"),
                "output_keys": sorted(list(final_output.keys())),
            }
        )
        return {"final_output": final_output}

    async def _ensure_anchor_vectors_seeded(self) -> None:
        # 若当前进程已播种，或 embedding 服务不可用，则直接跳过。
        if self._anchors_seeded or self._embedding_service is None:
            branch = "already_seeded" if self._anchors_seeded else "embedding_service_unavailable"
            logger.info(
                {
                    "action": "sentiment_anchor_seeding_skipped",
                    "branch": branch,
                }
            )
            return

        # 先查已有锚点键，确保播种幂等。
        existing_keys = await self.sentiment_repo.list_emotion_anchor_keys()
        skipped_existing = 0
        inserted_count = 0
        for anchor in SENTIMENT_VECTOR_ANCHORS:
            if anchor["key"] in existing_keys:
                skipped_existing += 1
                continue

            # 对静态锚点文本做 embedding，并写入 pgvector 支持的表。
            embedding = await self._embedding_service.embed_text(anchor["text"])
            await self.sentiment_repo.upsert_emotion_anchor(
                anchor_key=anchor["key"],
                emotion=anchor["emotion"],
                anchor_text=anchor["text"],
                embedding_literal=vector_to_pgvector_literal(embedding),
            )
            inserted_count += 1

        # 标记播种完成，避免同进程内重复访问数据库。
        self._anchors_seeded = True
        logger.info(
            {
                "action": "sentiment_anchor_seeding_completed",
                "branch": "seed_executed",
                "total_anchors": len(SENTIMENT_VECTOR_ANCHORS),
                "inserted_count": inserted_count,
                "skipped_existing": skipped_existing,
            }
        )

    async def _score_text_against_anchors(
        self,
        text: str,
        *,
        k: int = ANCHOR_TOP_K,
    ) -> tuple[dict[str, float], list[float] | None]:
        # embedding 服务不可用时，直接报错，避免静默降级。
        if self._embedding_service is None:
            logger.error(
                {
                    "action": "sentiment_vector_scoring_error",
                    "reason": "embedding_service_unavailable",
                }
            )
            raise RuntimeError("Embedding service unavailable for sentiment scoring")

        try:
            # 相似度检索前先确保向量锚点已就绪。
            await self._ensure_anchor_vectors_seeded()
            embedding = await self._embedding_service.embed_text(text)
            matches = await self.sentiment_repo.find_similar_emotion_anchors(
                embedding_literal=vector_to_pgvector_literal(embedding),
                limit=k,
            )
            logger.info(
                {
                    "action": "sentiment_vector_match_completed",
                    "branch": "vector_search",
                    "top_k": k,
                    "match_count": len(matches),
                }
            )
            if not matches:
                logger.error(
                    {
                        "action": "sentiment_vector_scoring_error",
                        "reason": "no_anchor_matches",
                        "limit": k,
                    }
                )
                raise RuntimeError("No emotion anchor matches found for sentiment scoring")

            # 将 top-k 近邻按情绪分桶聚合。
            buckets: dict[str, list[float]] = {emotion: [] for emotion in EMOTIONS}
            for match in matches:
                emotion = str(match.get("emotion") or "").lower()
                if emotion not in buckets:
                    continue
                raw_distance = float(match.get("distance", 1.0))
                # 将距离转换为 (0, 1] 区间的相似度。
                similarity = 1.0 / (1.0 + raw_distance)
                buckets[emotion].append(similarity)

            # 每个情绪分数 = 截断后的平均相似度。
            scores = {
                emotion: round(clamp_score(avg(buckets[emotion])), 4)
                for emotion in EMOTIONS
            }
            logger.info(
                {
                    "action": "sentiment_vector_scoring_success",
                    "branch": "vector_scoring",
                    "top_k": k,
                }
            )
            return scores, embedding
        except Exception as exc:
            logger.error(
                {
                    "action": "sentiment_vector_scoring_error",
                    "error": str(exc),
                }
            )
            raise

    @staticmethod
    def _score_emotions(lower_feedback: str) -> dict[str, float]:
        """基于关键词命中的原型锚点打分。"""
        scores: dict[str, float] = {}
        for emotion, anchors in EMOTION_ANCHORS.items():
            # 统计每个情绪词表在文本中的命中数。
            hits = sum(1 for token in anchors if token in lower_feedback)
            # 原型阶段保持简单且有界。
            scores[emotion] = min(1.0, round(0.2 * hits, 4))
        return scores

    @staticmethod
    def _derive_sentiment(emotion_scores: dict[str, float]) -> tuple[str, float]:
        # 兼容保留的旧辅助函数；主流程优先使用 risk-level 映射。
        max_score = max(emotion_scores.values()) if emotion_scores else 0.0
        if max_score >= 0.4:
            return "negative", 0.25
        if max_score > 0.0:
            return "neutral", 0.5
        return "positive", 0.75

    async def _build_explanation(
        self,
        *,
        feedback_text: str,
        sentiment: str,
        emotion_scores: dict[str, float],
        window_stats: dict[str, float] | None = None,
        trend: dict[str, str] | None = None,
        risk_level: float | None = None,
    ) -> str:
        """基于 LLM 生成解释，并提供确定性回退。"""
        # 使用当前最强情绪信号作为回退解释锚点。
        dominant = (
            max(emotion_scores, key=lambda key: emotion_scores[key])
            if emotion_scores
            else "fatigue"
        )
        dominant_score = emotion_scores.get(dominant, 0.0)
        if self._llm is None:
            # 聊天模型不可用时，返回严格确定性文本。
            logger.info(
                {
                    "action": "sentiment_explanation_success",
                    "branch": "deterministic_without_llm",
                    "sentiment": sentiment,
                    "dominant": dominant,
                }
            )
            return (
                f"Sentiment is {sentiment}. Dominant emotion signal is "
                f"{dominant} ({dominant_score:.2f})."
            )

        # 传入结构化上下文，尽量避免模型隐式重算。
        payload = {
            "text": feedback_text,
            "sentiment": sentiment,
            "current_scores": emotion_scores,
            "window_stats": window_stats,
            "trend": trend,
            "risk_level": risk_level if risk_level is not None else dominant_score,
        }
        prompt = (
            f"{SENTIMENT_EXPLANATION_SYSTEM_PROMPT}\n\n"
            f"Input:\n{payload}\n\n"
            "Generate the explanation now."
        )
        try:
            response = await self._llm.ainvoke(prompt)
            content = getattr(response, "content", "") or ""
            clean = str(content).strip()
            # 若模型返回空文本，仍走确定性回退。
            logger.info(
                {
                    "action": "sentiment_explanation_success",
                    "branch": "llm_response",
                    "sentiment": sentiment,
                    "response_empty": not bool(clean),
                }
            )
            return clean or (
                f"Sentiment is {sentiment}. Dominant emotion signal is "
                f"{dominant} ({dominant_score:.2f})."
            )
        except Exception as exc:
            logger.warning(
                {
                    "action": "sentiment_explanation_fallback",
                    "error": str(exc),
                }
            )
            # 安全回退：在模型瞬时失败时保持行为稳定。
            return (
                f"Sentiment is {sentiment}. Dominant emotion signal is "
                f"{dominant} ({dominant_score:.2f})."
            )

    @staticmethod
    def _extract_feedback_text(current_event: dict[str, Any] | None) -> str:
        # 事件载荷缺失或格式异常时，使用平滑兜底。
        if not isinstance(current_event, dict):
            return "Sample feedback"

        # 某些数据生产者会把自然语言文本放在嵌套 data 中。
        nested_data = current_event.get("data")
        data = nested_data if isinstance(nested_data, dict) else {}

        # 提取优先级：显式 notes/description > 嵌套 message 字段 > event_type 兜底。
        candidates = [
            current_event.get("notes"),
            current_event.get("description"),
            data.get("message"),
            data.get("notes"),
            data.get("description"),
            data.get("comment"),
            current_event.get("event_type"),
        ]
        for candidate in candidates:
            if candidate is None:
                continue
            text = str(candidate).strip()
            if text:
                return text
        # 最终兜底，确保下游打分输入非空。
        return "Sample feedback"

    @staticmethod
    def _extract_submission_id(current_event: dict[str, Any] | None) -> str:
        # 优先 event_id，其次 device_event_id，最后使用稳定兜底值。
        if not isinstance(current_event, dict):
            return "sentiment-submission"
        return str(
            current_event.get("event_id")
            or current_event.get("device_event_id")
            or "sentiment-submission"
        )

    @staticmethod
    def _extract_submission_timestamp(
        current_event: dict[str, Any] | None,
    ) -> datetime:
        # 若存在生产者时间戳则优先解析，并兼容带 Z 的 ISO 字符串。
        if isinstance(current_event, dict):
            raw_timestamp = current_event.get("timestamp")
            if isinstance(raw_timestamp, str) and raw_timestamp.strip():
                try:
                    return datetime.fromisoformat(raw_timestamp.replace("Z", "+00:00"))
                except ValueError:
                    # 时间格式异常时忽略并回退到处理时间。
                    pass
        # 使用 UTC 当前时间，保证入库值带时区信息。
        return datetime.now(UTC)
