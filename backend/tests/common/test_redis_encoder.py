"""
Unit tests for Redis client helper classes and utilities.
Tests the DateTimeEncoder and other serialization logic.
"""

import json
from datetime import UTC, datetime, timedelta

import pytest

from common.redis.client import DateTimeEncoder


class TestDateTimeEncoder:
    """Tests for DateTimeEncoder JSON serialization."""

    def test_datetime_encoder_with_utc_aware(self):
        """DateTimeEncoder serializes UTC-aware datetime."""
        now_utc = datetime.now(UTC)
        data = {"timestamp": now_utc, "value": 42}

        # Should not raise
        json_str = json.dumps(data, cls=DateTimeEncoder)
        result = json.loads(json_str)

        assert isinstance(result["timestamp"], str)
        assert "T" in result["timestamp"]  # ISO format
        assert result["value"] == 42

    def test_datetime_encoder_with_naive(self):
        """DateTimeEncoder serializes naive datetime."""
        now_naive = datetime.now()
        data = {"timestamp": now_naive}

        # Should not raise
        json_str = json.dumps(data, cls=DateTimeEncoder)
        result = json.loads(json_str)

        assert isinstance(result["timestamp"], str)
        assert "T" in result["timestamp"]

    def test_datetime_encoder_produces_isoformat(self):
        """DateTimeEncoder produces ISO 8601 format strings."""
        dt = datetime(2026, 3, 28, 13, 20, 45, 123456, tzinfo=UTC)
        data = {"dt": dt}

        json_str = json.dumps(data, cls=DateTimeEncoder)
        result = json.loads(json_str)

        # Should be ISO format: 2026-03-28T13:20:45.123456+00:00
        assert result["dt"] == "2026-03-28T13:20:45.123456+00:00"

    def test_datetime_encoder_handles_nested_datetimes(self):
        """DateTimeEncoder handles nested structures with datetimes."""
        now = datetime.now(UTC)
        data = {
            "event": {
                "timestamp": now,
                "details": {"created_at": now - timedelta(hours=1)},
            },
            "list": [now, "string", 123],
        }

        json_str = json.dumps(data, cls=DateTimeEncoder)
        result = json.loads(json_str)

        assert isinstance(result["event"]["timestamp"], str)
        assert isinstance(result["event"]["details"]["created_at"], str)
        assert isinstance(result["list"][0], str)
        assert result["list"][1] == "string"
        assert result["list"][2] == 123

    def test_datetime_encoder_preserves_non_datetime_types(self):
        """DateTimeEncoder leaves non-datetime types unchanged."""
        data = {
            "string": "hello",
            "number": 42,
            "float": 3.14,
            "bool": True,
            "null": None,
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
        }

        json_str = json.dumps(data, cls=DateTimeEncoder)
        result = json.loads(json_str)

        assert result == data

    def test_datetime_encoder_handles_microseconds(self):
        """DateTimeEncoder preserves microseconds in ISO format."""
        dt = datetime(2026, 3, 28, 13, 20, 45, 987654, tzinfo=UTC)
        data = {"dt": dt}

        json_str = json.dumps(data, cls=DateTimeEncoder)

        # ISO format should include microseconds
        assert "987654" in json_str

    def test_datetime_encoder_with_different_timezones(self):
        """DateTimeEncoder handles datetimes with different UTC offsets."""
        from datetime import timezone

        utc_plus_5_30 = timezone(timedelta(hours=5, minutes=30))
        dt = datetime(2026, 3, 28, 13, 20, 45, tzinfo=utc_plus_5_30)
        data = {"dt": dt}

        json_str = json.dumps(data, cls=DateTimeEncoder)
        result = json.loads(json_str)

        # Should show the offset in ISO format
        assert "+05:30" in result["dt"]

    def test_datetime_encoder_with_empty_dict(self):
        """DateTimeEncoder handles empty structures."""
        data = {}
        json_str = json.dumps(data, cls=DateTimeEncoder)
        result = json.loads(json_str)
        assert result == {}

    def test_datetime_encoder_error_on_unsupported_type(self):
        """DateTimeEncoder raises TypeError for unsupported types."""

        class CustomObject:
            pass

        data = {"obj": CustomObject()}

        with pytest.raises(TypeError):
            json.dumps(data, cls=DateTimeEncoder)

    def test_datetime_encoder_roundtrip(self):
        """DateTimeEncoder can roundtrip datetime serialization."""
        original_dt = datetime(2026, 3, 28, 13, 20, 45, 123456, tzinfo=UTC)
        data = {"timestamp": original_dt}

        # Serialize
        json_str = json.dumps(data, cls=DateTimeEncoder)

        # Deserialize
        result = json.loads(json_str)

        # Parse ISO string back to datetime
        parsed_dt = datetime.fromisoformat(result["timestamp"])

        # Should match original (allowing for microsecond precision)
        assert parsed_dt == original_dt
