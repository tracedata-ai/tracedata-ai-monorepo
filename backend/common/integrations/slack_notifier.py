from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import httpx

from common.config.settings import get_settings
from common.models.events import TripEvent

logger = logging.getLogger(__name__)
settings = get_settings()


class SlackNotifier:
    """Best-effort Slack notifier for operational alerts."""

    def __init__(
        self,
        webhook_url: str | None = None,
        trips_webhook_url: str | None = None,
    ) -> None:
        self.webhook_url = webhook_url or settings.slack_webhook_url
        self.trips_webhook_url = (
            trips_webhook_url or settings.slack_webhook_url_tracedata_trips
        )

    @property
    def is_enabled(self) -> bool:
        return bool(settings.slack_notifications_enabled and self.webhook_url)

    @property
    def is_trips_enabled(self) -> bool:
        return bool(settings.slack_notifications_enabled and self.trips_webhook_url)

    async def send_high_priority_event(
        self,
        event: TripEvent,
        *,
        extra_context: dict[str, Any] | None = None,
    ) -> bool:
        """
        Send critical/high event notification to Slack.
        Returns True on successful post; False on skip/failure.
        """
        priority = str(event.priority).lower()
        if priority not in {"critical", "high"}:
            return False

        if not self.is_enabled:
            return False

        payload = self._build_priority_payload(event, extra_context=extra_context)
        return await self._post(payload, webhook_url=self.webhook_url)

    async def send_trip_started(self, event: TripEvent) -> bool:
        if event.event_type != "start_of_trip" or not self.is_trips_enabled:
            return False
        payload = self._build_trip_lifecycle_payload(
            event, title="Trip Started", emoji=":white_check_mark:"
        )
        return await self._post(payload, webhook_url=self.trips_webhook_url)

    async def send_trip_ended(self, event: TripEvent) -> bool:
        if event.event_type != "end_of_trip" or not self.is_trips_enabled:
            return False
        payload = self._build_trip_lifecycle_payload(
            event, title="Trip Ended", emoji=":checkered_flag:"
        )
        return await self._post(payload, webhook_url=self.trips_webhook_url)

    async def send_trip_summary(
        self,
        event: TripEvent,
        *,
        summary: dict[str, Any],
    ) -> bool:
        if not self.is_trips_enabled:
            return False
        payload = self._build_trip_summary_payload(event, summary=summary)
        return await self._post(payload, webhook_url=self.trips_webhook_url)

    async def _post(self, payload: dict[str, Any], *, webhook_url: str | None) -> bool:
        if not webhook_url:
            return False
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(webhook_url, json=payload)
                response.raise_for_status()
            return True
        except Exception as exc:
            # Do not break the event pipeline if Slack is unavailable.
            logger.warning(
                {
                    "action": "slack_notification_failed",
                    "error": str(exc)[:200],
                }
            )
            return False

    def _build_priority_payload(
        self,
        event: TripEvent,
        *,
        extra_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        priority = str(event.priority).upper()
        timestamp_iso = (
            event.timestamp.isoformat()
            if isinstance(event.timestamp, datetime)
            else str(event.timestamp)
        )
        context = extra_context or {}
        context_line = ""
        if context:
            context_line = (
                f"\nsource: orchestrator | event_id: {context.get('event_id', '-')}"
            )

        text = (
            f"[{priority}] {event.event_type} | trip={event.trip_id} | "
            f"truck={event.truck_id} | driver={event.driver_id}"
        )
        body = (
            f"*{priority} alert* `{event.event_type}`\n"
            f"trip: `{event.trip_id}`\n"
            f"truck: `{event.truck_id}`\n"
            f"driver: `{event.driver_id}`\n"
            f"device_event_id: `{event.device_event_id}`\n"
            f"time: `{timestamp_iso}`"
            f"{context_line}"
        )

        return {
            "text": text,
            "blocks": [
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": body},
                }
            ],
        }

    def _build_trip_lifecycle_payload(
        self,
        event: TripEvent,
        *,
        title: str,
        emoji: str,
    ) -> dict[str, Any]:
        text = f"{title}: trip={event.trip_id} truck={event.truck_id}"
        body = (
            f"{emoji} *{title}*\n"
            f"trip: `{event.trip_id}`\n"
            f"truck: `{event.truck_id}`\n"
            f"driver: `{event.driver_id}`\n"
            f"event_type: `{event.event_type}`\n"
            f"device_event_id: `{event.device_event_id}`"
        )
        return {
            "text": text,
            "blocks": [
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": body},
                }
            ],
        }

    def _build_trip_summary_payload(
        self,
        event: TripEvent,
        *,
        summary: dict[str, Any],
    ) -> dict[str, Any]:
        scoring = summary.get("scoring") or {}
        safety = summary.get("safety") or {}
        support = summary.get("support") or {}
        text = f"Trip summary: trip={event.trip_id}"
        body = (
            ":memo: *Trip Summary Snapshot*\n"
            f"trip: `{event.trip_id}`\n"
            f"truck: `{event.truck_id}`\n"
            f"driver: `{event.driver_id}`\n"
            f"trigger_event: `{event.event_type}`\n\n"
            f"*Scoring*: `{scoring.get('status', 'pending')}`"
            f" | score=`{scoring.get('trip_score', scoring.get('score', '-'))}`\n"
            f"*Safety*: `{safety.get('status', 'pending')}`"
            f" | decision=`{safety.get('decision', '-')}`\n"
            f"*Support*: `{support.get('status', 'pending')}`"
            f" | category=`{support.get('coaching_category', '-')}`"
        )
        return {
            "text": text,
            "blocks": [
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": body},
                }
            ],
        }
