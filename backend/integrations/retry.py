"""
Retry logic with exponential backoff for API calls

Handles transient failures gracefully with configurable retry strategies
"""

import time
import logging
import random
from typing import Optional, Callable, Any, Type, Tuple
from functools import wraps
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RetryConfig:
    """Configuration for retry behavior"""
    max_attempts: int = 3
    initial_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    exponential_base: float = 2.0
    jitter: bool = True  # Add randomness to prevent thundering herd
    retriable_exceptions: Tuple[Type[Exception], ...] = (Exception,)


def exponential_backoff(
    attempt: int,
    initial_delay: float = 1.0,
    exponential_base: float = 2.0,
    max_delay: float = 60.0,
    jitter: bool = True
) -> float:
    """
    Calculate delay for exponential backoff

    Args:
        attempt: Current attempt number (0-indexed)
        initial_delay: Initial delay in seconds
        exponential_base: Base for exponential growth
        max_delay: Maximum delay in seconds
        jitter: Add random jitter to prevent thundering herd

    Returns:
        Delay in seconds
    """
    delay = min(initial_delay * (exponential_base ** attempt), max_delay)

    if jitter:
        # Add random jitter (±25%)
        jitter_range = delay * 0.25
        delay = delay + random.uniform(-jitter_range, jitter_range)

    return max(0, delay)


def retry_with_backoff(
    config: Optional[RetryConfig] = None,
    log_attempts: bool = True
):
    """
    Decorator to retry function calls with exponential backoff

    Usage:
        @retry_with_backoff(RetryConfig(max_attempts=5))
        def api_call():
            # potentially failing operation
            return result

    Args:
        config: Retry configuration (uses defaults if None)
        log_attempts: Whether to log retry attempts
    """
    if config is None:
        config = RetryConfig()

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(config.max_attempts):
                try:
                    result = func(*args, **kwargs)

                    # Log success after retries
                    if attempt > 0 and log_attempts:
                        logger.info(
                            f"✅ {func.__name__} succeeded on attempt {attempt + 1}/{config.max_attempts}"
                        )

                    return result

                except config.retriable_exceptions as e:
                    last_exception = e

                    # Don't retry on last attempt
                    if attempt == config.max_attempts - 1:
                        break

                    # Calculate backoff delay
                    delay = exponential_backoff(
                        attempt,
                        initial_delay=config.initial_delay,
                        exponential_base=config.exponential_base,
                        max_delay=config.max_delay,
                        jitter=config.jitter
                    )

                    if log_attempts:
                        logger.warning(
                            f"⚠️  {func.__name__} failed (attempt {attempt + 1}/{config.max_attempts}): {e}. "
                            f"Retrying in {delay:.2f}s..."
                        )

                    time.sleep(delay)

            # All retries exhausted
            if log_attempts:
                logger.error(
                    f"❌ {func.__name__} failed after {config.max_attempts} attempts"
                )

            if last_exception:
                raise last_exception

            return None

        return wrapper
    return decorator


# Async version
def retry_with_backoff_async(
    config: Optional[RetryConfig] = None,
    log_attempts: bool = True
):
    """
    Async version of retry_with_backoff

    Usage:
        @retry_with_backoff_async(RetryConfig(max_attempts=5))
        async def api_call():
            # potentially failing async operation
            return result
    """
    if config is None:
        config = RetryConfig()

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            import asyncio

            last_exception = None

            for attempt in range(config.max_attempts):
                try:
                    result = await func(*args, **kwargs)

                    if attempt > 0 and log_attempts:
                        logger.info(
                            f"✅ {func.__name__} succeeded on attempt {attempt + 1}/{config.max_attempts}"
                        )

                    return result

                except config.retriable_exceptions as e:
                    last_exception = e

                    if attempt == config.max_attempts - 1:
                        break

                    delay = exponential_backoff(
                        attempt,
                        initial_delay=config.initial_delay,
                        exponential_base=config.exponential_base,
                        max_delay=config.max_delay,
                        jitter=config.jitter
                    )

                    if log_attempts:
                        logger.warning(
                            f"⚠️  {func.__name__} failed (attempt {attempt + 1}/{config.max_attempts}): {e}. "
                            f"Retrying in {delay:.2f}s..."
                        )

                    await asyncio.sleep(delay)

            if log_attempts:
                logger.error(
                    f"❌ {func.__name__} failed after {config.max_attempts} attempts"
                )

            if last_exception:
                raise last_exception

            return None

        return wrapper
    return decorator


class CircuitBreaker:
    """
    Circuit breaker pattern to prevent cascading failures

    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, requests fail immediately
    - HALF_OPEN: Testing if service recovered
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception
    ):
        """
        Initialize circuit breaker

        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before trying again
            expected_exception: Exception type to track
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self._failure_count = 0
        self._last_failure_time: Optional[float] = None
        self._state = "CLOSED"

        logger.info(
            f"CircuitBreaker initialized: threshold={failure_threshold}, "
            f"timeout={recovery_timeout}s"
        )

    @property
    def state(self) -> str:
        """Get current circuit state"""
        # Check if we should transition to HALF_OPEN
        if (
            self._state == "OPEN"
            and self._last_failure_time
            and (time.time() - self._last_failure_time) >= self.recovery_timeout
        ):
            self._state = "HALF_OPEN"
            logger.info("🔄 Circuit breaker: OPEN → HALF_OPEN")

        return self._state

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Call function through circuit breaker

        Args:
            func: Function to call
            *args, **kwargs: Arguments to pass to function

        Returns:
            Function result

        Raises:
            Exception: If circuit is OPEN or function fails
        """
        if self.state == "OPEN":
            raise Exception(
                f"Circuit breaker is OPEN. Service unavailable. "
                f"Retry after {self.recovery_timeout}s"
            )

        try:
            result = func(*args, **kwargs)

            # Success - reset if we were in HALF_OPEN
            if self._state == "HALF_OPEN":
                self._reset()
                logger.info("✅ Circuit breaker: HALF_OPEN → CLOSED (recovered)")

            return result

        except self.expected_exception as e:
            self._record_failure()
            raise e

    def _record_failure(self):
        """Record a failure and potentially open circuit"""
        self._failure_count += 1
        self._last_failure_time = time.time()

        if self._failure_count >= self.failure_threshold:
            self._state = "OPEN"
            logger.error(
                f"🔴 Circuit breaker OPENED after {self._failure_count} failures"
            )

    def _reset(self):
        """Reset circuit breaker"""
        self._failure_count = 0
        self._last_failure_time = None
        self._state = "CLOSED"

    def reset_manually(self):
        """Manually reset circuit breaker"""
        self._reset()
        logger.info("🔄 Circuit breaker manually reset")


# Example usage
if __name__ == "__main__":
    import httpx

    logging.basicConfig(level=logging.INFO)

    # Test retry with backoff
    print("\n🧪 Testing retry with exponential backoff:")

    attempt_count = 0

    @retry_with_backoff(
        RetryConfig(
            max_attempts=4,
            initial_delay=0.5,
            exponential_base=2.0,
            retriable_exceptions=(ValueError,)
        )
    )
    def flaky_function():
        global attempt_count
        attempt_count += 1
        print(f"  Attempt {attempt_count}")

        if attempt_count < 3:
            raise ValueError("Simulated failure")

        return "Success!"

    try:
        result = flaky_function()
        print(f"✅ Result: {result}")
    except Exception as e:
        print(f"❌ Failed: {e}")

    # Test circuit breaker
    print("\n🧪 Testing circuit breaker:")

    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=2.0)

    def failing_service():
        raise Exception("Service unavailable")

    for i in range(5):
        try:
            result = breaker.call(failing_service)
        except Exception as e:
            print(f"  Call {i+1}: {e}")

        time.sleep(0.5)

    print(f"\n📊 Circuit state: {breaker.state}")
