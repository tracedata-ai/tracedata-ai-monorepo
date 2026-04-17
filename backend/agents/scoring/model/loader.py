"""
Local wrapper for the smoothness ML model bundle.

Reads model.joblib + serving/ contract files downloaded via
scripts/fetch_model_release.py and matches the SmoothnessInference output
contract from tracedata-ai/tracedata-ai-ml.

Input path: smoothness_log device-aggregate envelopes (what the pipeline caches
in all_pings). Features are derived to match SMOOTHNESS_FEATURE_COLUMNS from
the ML repo's model_contract.json.

Output contract (aligned with SmoothnessInference.score_trip_from_ping_windows):
    {
        "trip_smoothness_score": float,          # 0–100
        "explanation": {
            "feature_attributions": {str: float},  # per-feature contribution
            "base_value": float,
            "window_count": int,
            "worst_window_index": int,
            "worst_window_score": float,
            "method": "pred_contribs" | "deterministic_heuristic",
        }
    }
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import joblib
import numpy as np

from agents.scoring.features import metrics_from_smoothness_details

logger = logging.getLogger(__name__)

_REQUIRED_SERVING = frozenset({"model_contract.json", "background_features.json"})


class ContractMismatchError(RuntimeError):
    """Raised when the bundle is incomplete or feature columns mismatch."""


class SmoothnessBundleLoader:
    """
    Wraps the downloaded model bundle and exposes score_trip() aligned with
    the SmoothnessInference API from the ML repo.

    Usage:
        loader = SmoothnessBundleLoader.from_local_paths(
            model_path="agents/scoring/model_bundle/model.joblib",
            serving_dir="agents/scoring/model_bundle/serving",
        )
        result = loader.score_trip(smoothness_log_envelopes)
    """

    def __init__(
        self,
        model: Any,
        feature_columns: list[str],
        background: dict[str, Any],
        contract_version: str,
    ) -> None:
        self._model = model
        self._feature_columns = feature_columns
        self._background = background
        self._contract_version = contract_version

    # ── Factory ──────────────────────────────────────────────────────────────

    @classmethod
    def is_available(cls, model_path: str, serving_dir: str) -> bool:
        """True only when all bundle files exist on disk."""
        mp = Path(model_path)
        sd = Path(serving_dir)
        return mp.is_file() and all((sd / f).is_file() for f in _REQUIRED_SERVING)

    @classmethod
    def from_local_paths(
        cls, model_path: str, serving_dir: str
    ) -> SmoothnessBundleLoader:
        """
        Mirror of SmoothnessInference.from_local_paths(model_path, serving_dir).
        Validates the serving contract before loading the model.
        """
        mp = Path(model_path)
        sd = Path(serving_dir)

        missing = sorted(f for f in _REQUIRED_SERVING if not (sd / f).is_file())
        if missing:
            raise ContractMismatchError(
                f"Bundle incomplete — missing serving files: {missing}"
            )
        if not mp.is_file():
            raise ContractMismatchError(f"Model file not found: {mp}")

        contract: dict = json.loads((sd / "model_contract.json").read_text())
        background: dict = json.loads((sd / "background_features.json").read_text())

        feature_columns: list[str] = contract.get("feature_columns", [])
        if not feature_columns:
            raise ContractMismatchError(
                "model_contract.json must declare 'feature_columns'"
            )

        contract_version: str = contract.get("contract_version", "unknown")
        model = joblib.load(mp)

        logger.info(
            {
                "action": "smoothness_model_loaded",
                "contract_version": contract_version,
                "feature_columns": feature_columns,
                "model_type": type(model).__name__,
            }
        )
        return cls(model, feature_columns, background, contract_version)

    # ── Public API (mirrors SmoothnessInference) ─────────────────────────────

    def score_trip(self, smoothness_log_envelopes: list[dict]) -> dict[str, Any]:
        """
        Score a trip from its smoothness_log window envelopes.

        Equivalent to SmoothnessInference.score_trip_from_ping_windows() but
        accepts device-aggregate envelopes instead of raw ping lists.

        Args:
            smoothness_log_envelopes: list of ``details`` dicts extracted from
                smoothness_log pipeline events (one per ~10-min window).

        Returns:
            Dict matching the SmoothnessInference output contract.
        """
        if not smoothness_log_envelopes:
            raise ValueError("score_trip requires at least one smoothness_log envelope")

        rows = [self._extract_features(env) for env in smoothness_log_envelopes]
        X = np.array(
            [[row.get(col, 0.0) for col in self._feature_columns] for row in rows],
            dtype=np.float64,
        )

        window_scores = self._predict_scores(X)

        # Trip score = weighted mean (weight by window_seconds, matching reference)
        weights = np.array(
            [
                float(env.get("window_seconds") or 600.0)
                for env in smoothness_log_envelopes
            ],
            dtype=np.float64,
        )
        weights = weights / weights.sum()
        trip_score = float(np.clip(np.dot(window_scores, weights), 0.0, 100.0))

        worst_idx = int(np.argmin(window_scores))
        attributions, method = self._compute_attributions(X, weights)

        return {
            "trip_smoothness_score": round(trip_score, 1),
            "explanation": {
                "feature_attributions": attributions,
                "base_value": 0.0,
                "window_count": len(smoothness_log_envelopes),
                "worst_window_index": worst_idx,
                "worst_window_score": round(float(window_scores[worst_idx]), 1),
                "method": method,
                "contract_version": self._contract_version,
                "narrative": self._build_narrative(attributions, trip_score, method),
            },
        }

    # ── Internals ────────────────────────────────────────────────────────────

    def _extract_features(self, details: dict[str, Any]) -> dict[str, float]:
        """
        Map one smoothness_log details dict onto the model's feature space.

        Derives SMOOTHNESS_FEATURE_COLUMNS from device-aggregate metrics.
        Mirrors extract_smoothness_features() from the ML repo's src.core.features,
        adapted for pre-aggregated envelopes instead of raw pings.
        """
        base = metrics_from_smoothness_details(details)

        jerk_mean = float(base.get("jerk_mean", 0.0))
        jerk_max = float(base.get("jerk_max", 0.0))
        speed_std = float(base.get("speed_std", 0.0))
        lateral_mean = float(base.get("lateral_mean", 0.0))
        lateral_max = float(base.get("lateral_max", 0.0))
        mean_rpm = float(base.get("mean_rpm", 0.0))
        idle_sec = float(base.get("idle_seconds", 0.0))
        window_harsh = float(base.get("window_harsh", 0))
        window_sec = float(details.get("window_seconds") or 600.0)
        idle_ratio = idle_sec / max(window_sec, 1.0)

        # 3-feature production columns (SMOOTHNESS_FEATURE_COLUMNS from ML repo)
        # Derived from aggregate metrics to approximate ping-level computation.
        accel_fluidity = float(np.clip(jerk_mean * 10.0, 0.0, 1.0))
        driving_consistency = float(np.clip(speed_std / 30.0, 0.0, 1.0))
        comfort_zone_pct = float(
            np.clip((lateral_mean / 0.3) + (jerk_max / 5.0), 0.0, 1.0)
        )

        return {
            # 3-feature ping-window contract (production path)
            "accel_fluidity": accel_fluidity,
            "driving_consistency": driving_consistency,
            "comfort_zone_percent": comfort_zone_pct,
            # Device-aggregate extended columns (DeviceAggregateTripScorer contract)
            "jerk_mean": jerk_mean,
            "jerk_max": jerk_max,
            "speed_std": speed_std,
            "lateral_mean": lateral_mean,
            "lateral_max": lateral_max,
            "mean_rpm": mean_rpm,
            "idle_seconds": idle_sec,
            "idle_ratio": idle_ratio,
            "window_seconds": window_sec,
            "harsh_event_count": window_harsh,
        }

    def _predict_scores(self, X: np.ndarray) -> np.ndarray:
        """Run model.predict(), normalise to [0, 100]."""
        try:
            raw = self._model.predict(X)
        except TypeError:
            # XGBoost booster requires DMatrix (not ndarray)
            try:
                import xgboost as xgb  # noqa: PLC0415

                dm = xgb.DMatrix(X, feature_names=self._feature_columns)
                raw = self._model.predict(dm)
            except Exception as e:
                raise RuntimeError(f"Model predict failed: {e}") from e

        arr = np.asarray(raw, dtype=np.float64).ravel()
        # Normalise to [0, 100] regardless of model output range
        if arr.max() <= 1.01:
            arr = arr * 100.0
        elif arr.max() <= 10.1:
            arr = arr * 10.0
        return np.clip(arr, 0.0, 100.0)

    def _compute_attributions(
        self, X: np.ndarray, weights: np.ndarray
    ) -> tuple[dict[str, float], str]:
        """
        Return (feature_attributions dict, method string).

        Tries XGBoost pred_contribs (true SHAP), falls back to deterministic
        heuristic matching the reference's _deterministic_heuristic_explanation.
        """
        # ── XGBoost pred_contribs ─────────────────────────────────────────────
        try:
            import xgboost as xgb  # noqa: PLC0415

            dm = xgb.DMatrix(X, feature_names=self._feature_columns)
            # XGBRegressor wraps a Booster — use get_booster() for pred_contribs
            booster = (
                self._model.get_booster()
                if hasattr(self._model, "get_booster")
                else self._model
            )
            contribs = booster.predict(dm, pred_contribs=True)
            # shape: (n_windows, n_features + 1) — last col is bias
            weighted_contribs = np.dot(weights, contribs[:, :-1])
            attributions = {
                col: round(float(v), 4)
                for col, v in zip(self._feature_columns, weighted_contribs)
            }
            return attributions, "pred_contribs"
        except Exception:
            pass

        # ── Deterministic heuristic fallback (matches reference coefficients) ──
        # Coefficients from synthetic label generation in ML repo reference.
        coeffs: dict[str, float] = {
            "accel_fluidity": -80.0,
            "driving_consistency": -40.0,
            "comfort_zone_percent": 0.4,
        }
        attributions = {}
        for i, col in enumerate(self._feature_columns):
            coeff = coeffs.get(col, 0.0)
            vals = X[:, i]
            attributions[col] = round(float(np.dot(vals * coeff, weights)), 4)
        return attributions, "deterministic_heuristic"

    def _build_narrative(
        self,
        attributions: dict[str, float],
        score: float,
        method: str,
    ) -> str:
        label = (
            "Excellent"
            if score >= 85
            else (
                "Good"
                if score >= 70
                else (
                    "Average"
                    if score >= 55
                    else "Below Average" if score >= 40 else "Poor"
                )
            )
        )
        top = sorted(attributions, key=lambda k: abs(attributions[k]), reverse=True)[:3]
        top_str = ", ".join(top) if top else "unknown"
        return (
            f"ML score {score:.1f} ({label}). "
            f"Method: {method}. Top contributors: {top_str}."
        )
