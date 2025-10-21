"""
Prometheus Metrics Middleware

Automatically collects metrics for all HTTP requests including:
- Request count by method, endpoint, and status
- Request duration histograms
- Active requests gauge
- Rate limit tracking
"""
import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from backend.utils.prometheus_metrics import MetricsCollector
from backend.utils.logging import get_logger

logger = get_logger(__name__)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    Middleware to collect Prometheus metrics for all HTTP requests
    """

    def __init__(
        self,
        app: ASGIApp,
        skip_paths: list[str] | None = None,
    ):
        """
        Initialize Prometheus middleware

        Args:
            app: ASGI application
            skip_paths: List of paths to skip metrics collection (e.g., ["/metrics", "/health"])
        """
        super().__init__(app)
        self.skip_paths = skip_paths or []

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and collect metrics

        Args:
            request: FastAPI request object
            call_next: Next middleware/endpoint in chain

        Returns:
            Response from endpoint
        """
        # Skip metrics collection for certain paths
        if any(request.url.path.startswith(skip) for skip in self.skip_paths):
            return await call_next(request)

        method = request.method
        endpoint = request.url.path

        # Track request in progress
        with MetricsCollector.track_request_in_progress(method, endpoint):
            start_time = time.time()

            try:
                # Process request
                response = await call_next(request)

                # Calculate duration
                duration = time.time() - start_time

                # Record metrics
                MetricsCollector.record_request(
                    method=method,
                    endpoint=endpoint,
                    status_code=response.status_code,
                    duration=duration
                )

                # Track rate limit info if present
                if "x-ratelimit-remaining" in response.headers:
                    try:
                        remaining = int(response.headers["x-ratelimit-remaining"])
                        identifier = response.headers.get("x-identifier", "unknown")
                        MetricsCollector.update_rate_limit_remaining(
                            identifier=identifier,
                            endpoint=endpoint,
                            remaining=remaining
                        )
                    except (ValueError, KeyError):
                        pass

                # Track rate limit hits (429 status)
                if response.status_code == 429:
                    identifier = response.headers.get("x-identifier", "unknown:unknown")
                    identifier_type = identifier.split(":")[0] if ":" in identifier else "unknown"
                    MetricsCollector.record_rate_limit_hit(
                        identifier_type=identifier_type,
                        endpoint=endpoint
                    )

                # Track errors
                if 400 <= response.status_code < 500:
                    error_type = f"client_error_{response.status_code}"
                    MetricsCollector.record_error(
                        error_type=error_type,
                        endpoint=endpoint
                    )
                elif response.status_code >= 500:
                    error_type = f"server_error_{response.status_code}"
                    MetricsCollector.record_error(
                        error_type=error_type,
                        endpoint=endpoint
                    )

                return response

            except Exception as e:
                # Record exception
                duration = time.time() - start_time

                MetricsCollector.record_exception(
                    exception_type=type(e).__name__,
                    endpoint=endpoint
                )

                MetricsCollector.record_request(
                    method=method,
                    endpoint=endpoint,
                    status_code=500,
                    duration=duration
                )

                logger.error(
                    "prometheus_middleware_exception",
                    exc_info=True,
                    exception_type=type(e).__name__,
                    endpoint=endpoint,
                    method=method,
                    duration=duration
                )

                # Re-raise to let error handlers deal with it
                raise
