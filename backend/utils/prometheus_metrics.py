"""
Prometheus Metrics for PURPURA API

Exports application metrics in Prometheus format for monitoring and alerting.

Metrics Exported:
- HTTP request count (by method, endpoint, status)
- HTTP request duration (histogram)
- Active requests (gauge)
- Rate limit hits
- API errors
- Cache hit/miss ratio
"""
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Info,
    generate_latest,
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
)
from typing import Optional
import time

# Create a custom registry (optional - allows multiple registries)
registry = CollectorRegistry()

# Application Info
app_info = Info(
    "purpura_app",
    "PURPURA Climate OS API Information",
    registry=registry
)

# HTTP Request Metrics
http_requests_total = Counter(
    "purpura_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
    registry=registry
)

http_request_duration_seconds = Histogram(
    "purpura_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
    registry=registry
)

http_requests_in_progress = Gauge(
    "purpura_http_requests_in_progress",
    "Number of HTTP requests currently being processed",
    ["method", "endpoint"],
    registry=registry
)

# Rate Limit Metrics
rate_limit_hits_total = Counter(
    "purpura_rate_limit_hits_total",
    "Total number of rate limit hits",
    ["identifier_type", "endpoint"],
    registry=registry
)

rate_limit_remaining = Gauge(
    "purpura_rate_limit_remaining",
    "Remaining rate limit allowance",
    ["identifier", "endpoint"],
    registry=registry
)

# Error Metrics
api_errors_total = Counter(
    "purpura_api_errors_total",
    "Total API errors",
    ["error_type", "endpoint"],
    registry=registry
)

api_exceptions_total = Counter(
    "purpura_api_exceptions_total",
    "Total unhandled exceptions",
    ["exception_type", "endpoint"],
    registry=registry
)

# Cache Metrics
cache_operations_total = Counter(
    "purpura_cache_operations_total",
    "Total cache operations",
    ["operation", "result"],
    registry=registry
)

cache_hit_ratio = Gauge(
    "purpura_cache_hit_ratio",
    "Cache hit ratio (0.0 to 1.0)",
    registry=registry
)

# External API Metrics
external_api_calls_total = Counter(
    "purpura_external_api_calls_total",
    "Total external API calls",
    ["api_name", "status"],
    registry=registry
)

external_api_duration_seconds = Histogram(
    "purpura_external_api_duration_seconds",
    "External API call duration in seconds",
    ["api_name"],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0),
    registry=registry
)

# Database/Trino Metrics
trino_queries_total = Counter(
    "purpura_trino_queries_total",
    "Total Trino queries executed",
    ["query_type", "status"],
    registry=registry
)

trino_query_duration_seconds = Histogram(
    "purpura_trino_query_duration_seconds",
    "Trino query duration in seconds",
    ["query_type"],
    buckets=(0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0),
    registry=registry
)

# LLM Extraction Metrics
llm_extractions_total = Counter(
    "purpura_llm_extractions_total",
    "Total LLM extractions",
    ["model", "status"],
    registry=registry
)

llm_extraction_duration_seconds = Histogram(
    "purpura_llm_extraction_duration_seconds",
    "LLM extraction duration in seconds",
    ["model"],
    buckets=(0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0),
    registry=registry
)

llm_tokens_used_total = Counter(
    "purpura_llm_tokens_used_total",
    "Total LLM tokens used",
    ["model", "token_type"],
    registry=registry
)


class MetricsCollector:
    """
    Helper class for collecting and managing Prometheus metrics
    """

    @staticmethod
    def record_request(method: str, endpoint: str, status_code: int, duration: float):
        """
        Record HTTP request metrics

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            status_code: HTTP status code
            duration: Request duration in seconds
        """
        http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).inc()

        http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)

    @staticmethod
    def track_request_in_progress(method: str, endpoint: str):
        """
        Context manager to track requests in progress

        Usage:
            with MetricsCollector.track_request_in_progress("GET", "/api/v1/test"):
                # Process request
                pass
        """
        class RequestTracker:
            def __enter__(self):
                http_requests_in_progress.labels(
                    method=method,
                    endpoint=endpoint
                ).inc()
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                http_requests_in_progress.labels(
                    method=method,
                    endpoint=endpoint
                ).dec()

        return RequestTracker()

    @staticmethod
    def record_rate_limit_hit(identifier_type: str, endpoint: str):
        """
        Record rate limit hit

        Args:
            identifier_type: Type of identifier (ip, user, apikey)
            endpoint: API endpoint that was rate limited
        """
        rate_limit_hits_total.labels(
            identifier_type=identifier_type,
            endpoint=endpoint
        ).inc()

    @staticmethod
    def update_rate_limit_remaining(identifier: str, endpoint: str, remaining: int):
        """
        Update rate limit remaining gauge

        Args:
            identifier: Unique identifier
            endpoint: API endpoint
            remaining: Remaining requests allowed
        """
        rate_limit_remaining.labels(
            identifier=identifier,
            endpoint=endpoint
        ).set(remaining)

    @staticmethod
    def record_error(error_type: str, endpoint: str):
        """
        Record API error

        Args:
            error_type: Type of error (validation, not_found, etc.)
            endpoint: API endpoint where error occurred
        """
        api_errors_total.labels(
            error_type=error_type,
            endpoint=endpoint
        ).inc()

    @staticmethod
    def record_exception(exception_type: str, endpoint: str):
        """
        Record unhandled exception

        Args:
            exception_type: Exception class name
            endpoint: API endpoint where exception occurred
        """
        api_exceptions_total.labels(
            exception_type=exception_type,
            endpoint=endpoint
        ).inc()

    @staticmethod
    def record_cache_operation(operation: str, result: str):
        """
        Record cache operation

        Args:
            operation: Operation type (get, set, delete)
            result: Result (hit, miss, success, error)
        """
        cache_operations_total.labels(
            operation=operation,
            result=result
        ).inc()

    @staticmethod
    def update_cache_hit_ratio(hit_ratio: float):
        """
        Update cache hit ratio

        Args:
            hit_ratio: Hit ratio from 0.0 to 1.0
        """
        cache_hit_ratio.set(hit_ratio)

    @staticmethod
    def record_external_api_call(api_name: str, status: str, duration: float):
        """
        Record external API call

        Args:
            api_name: Name of external API (INPE, ANA, etc.)
            status: Call status (success, error, timeout)
            duration: Call duration in seconds
        """
        external_api_calls_total.labels(
            api_name=api_name,
            status=status
        ).inc()

        external_api_duration_seconds.labels(
            api_name=api_name
        ).observe(duration)

    @staticmethod
    def record_trino_query(query_type: str, status: str, duration: float):
        """
        Record Trino query

        Args:
            query_type: Type of query (select, insert, create, etc.)
            status: Query status (success, error)
            duration: Query duration in seconds
        """
        trino_queries_total.labels(
            query_type=query_type,
            status=status
        ).inc()

        trino_query_duration_seconds.labels(
            query_type=query_type
        ).observe(duration)

    @staticmethod
    def record_llm_extraction(model: str, status: str, duration: float, tokens_used: Optional[dict] = None):
        """
        Record LLM extraction

        Args:
            model: LLM model used (gpt-4o-mini, etc.)
            status: Extraction status (success, error)
            duration: Extraction duration in seconds
            tokens_used: Dict with prompt_tokens and completion_tokens
        """
        llm_extractions_total.labels(
            model=model,
            status=status
        ).inc()

        llm_extraction_duration_seconds.labels(
            model=model
        ).observe(duration)

        if tokens_used:
            if "prompt_tokens" in tokens_used:
                llm_tokens_used_total.labels(
                    model=model,
                    token_type="prompt"
                ).inc(tokens_used["prompt_tokens"])

            if "completion_tokens" in tokens_used:
                llm_tokens_used_total.labels(
                    model=model,
                    token_type="completion"
                ).inc(tokens_used["completion_tokens"])


def get_metrics():
    """
    Generate Prometheus metrics in text format

    Returns:
        Tuple of (metrics_text, content_type)
    """
    return generate_latest(registry), CONTENT_TYPE_LATEST


def initialize_app_info(version: str, environment: str):
    """
    Initialize application info metric

    Args:
        version: Application version
        environment: Environment name (development, staging, production)
    """
    app_info.info({
        "version": version,
        "environment": environment,
        "service": "purpura-api"
    })
