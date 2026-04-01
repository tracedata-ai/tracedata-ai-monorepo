"""
Ring Buffer for Ingestion

Stages raw TelemetryPackets in memory before pushing to Redis processed queue.

Pattern:
  1. Packets arrive asynchronously
  2. Pushed into ring buffer (FIFO)
  3. Buffer auto-flushes when:
     - Size threshold reached (batch_size)
     - Time threshold reached (max_wait_seconds)
     - On manual flush()
  4. Flushed → TripEvent pushed to processed queue

Benefits:
  - Reduces Redis LPUSH calls (batch efficiency)
  - Smooths load spikes
  - Backpressure: if buffer full, signals producer to slow down
"""

import asyncio
import logging
from collections import deque
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)


class RingBuffer:
    """
    Fixed-size ring buffer for batching ingested packets.

    Thread-safe via asyncio locks.
    """

    def __init__(
        self,
        max_size: int = 100,
        batch_flush_size: int = 50,
        max_wait_seconds: int = 5,
    ):
        """
        Initialize ring buffer.

        Args:
            max_size: Maximum capacity (soft limit)
            batch_flush_size: Auto-flush when buffer reaches this size
            max_wait_seconds: Auto-flush if oldest packet older than this
        """
        self._buffer: deque = deque(maxlen=max_size)
        self._max_size = max_size
        self._batch_flush_size = batch_flush_size
        self._max_wait_seconds = max_wait_seconds

        self._lock = asyncio.Lock()
        self._not_empty = asyncio.Condition(self._lock)
        self._last_flush_time = datetime.now(UTC)

    async def push(self, packet: dict[str, Any]) -> bool:
        """
        Push packet into buffer.

        Args:
            packet: Ingested telemetry packet

        Returns:
            True if accepted, False if buffer full (backpressure)
        """
        async with self._lock:
            if len(self._buffer) >= self._max_size:
                logger.warning(
                    {
                        "action": "buffer_full_backpressure",
                        "buffer_size": len(self._buffer),
                        "max_size": self._max_size,
                    }
                )
                return False

            self._buffer.append(packet)
            self._not_empty.notify_all()
            return True

    async def flush(self) -> list[dict[str, Any]]:
        """
        Manually flush buffer (get all packets for processing).

        Clears buffer. Called after batch is processed.

        Returns:
            List of packets in buffer (oldest first)
        """
        async with self._lock:
            packets = list(self._buffer)
            self._buffer.clear()
            self._last_flush_time = datetime.now(UTC)
            logger.info(
                {
                    "action": "buffer_flushed",
                    "packets_flushed": len(packets),
                }
            )
            return packets

    async def peek(self, max_packets: int | None = None) -> list[dict[str, Any]]:
        """
        Peek at buffer without removing (for monitoring).

        Args:
            max_packets: Max to peek (None = all)

        Returns:
            List of packets
        """
        async with self._lock:
            all_packets = list(self._buffer)
            return all_packets[:max_packets] if max_packets else all_packets

    async def should_flush(self) -> bool:
        """
        Check if buffer should auto-flush.

        Returns True if:
          - Size >= batch_flush_size
          - Oldest packet is older than max_wait_seconds

        Returns:
            True if should flush
        """
        async with self._lock:
            # Check size threshold
            if len(self._buffer) >= self._batch_flush_size:
                return True

            # Check time threshold
            if len(self._buffer) > 0:
                elapsed = (datetime.now(UTC) - self._last_flush_time).total_seconds()
                if elapsed > self._max_wait_seconds:
                    return True

            return False

    async def size(self) -> int:
        """Get current buffer size."""
        async with self._lock:
            return len(self._buffer)

    async def wait_for_data(self, timeout_seconds: int = 1) -> bool:
        """
        Wait for buffer to have data (blocking).

        Used by worker to wait for ingestion.

        Args:
            timeout_seconds: Max time to wait

        Returns:
            True if data available, False on timeout
        """
        async with self._not_empty:
            try:
                await asyncio.wait_for(
                    self._not_empty.wait(),
                    timeout=timeout_seconds,
                )
                return True
            except TimeoutError:
                return False
