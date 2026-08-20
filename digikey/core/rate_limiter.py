"""
Thread-safe Token Bucket Rate Limiter for DigiKey API SDK.
"""
import threading
import time
from typing import Optional


class RateLimiter:
    """
    Thread-safe token bucket rate limiter to prevent quota exhaustion and WAF blocks.

    Args:
        rate_per_second: Maximum sustained requests permitted per second.
        burst_capacity: Maximum burst capacity of tokens.
    """

    def __init__(self, rate_per_second: float = 10.0, burst_capacity: Optional[int] = None):
        self.rate_per_second = max(0.1, float(rate_per_second))
        self.capacity = burst_capacity if burst_capacity is not None else max(1, int(rate_per_second))
        self.tokens = float(self.capacity)
        self.last_update = time.monotonic()
        self._lock = threading.Lock()

    def acquire(self) -> float:
        """
        Acquires permission to make a request. Blocks/sleeps if the rate limit is exceeded.
        Returns the number of seconds waited (0.0 if tokens were immediately available).
        """
        with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_update
            self.last_update = now

            # Replenish tokens based on elapsed time
            self.tokens = min(float(self.capacity), self.tokens + (elapsed * self.rate_per_second))

            if self.tokens >= 1.0:
                self.tokens -= 1.0
                return 0.0

            # Calculate required sleep duration for 1 token to regenerate
            deficit = 1.0 - self.tokens
            wait_time = deficit / self.rate_per_second

            # Update state assuming wait time is honored
            self.tokens = 0.0
            self.last_update = now + wait_time

        if wait_time > 0:
            time.sleep(wait_time)

        return wait_time
