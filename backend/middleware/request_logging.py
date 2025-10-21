"""
Request Logging Middleware

Logs all HTTP requests and responses with structured data including:
- Request ID (correlation ID)
- Request method, path, query params
- Response status code
- Request duration
- Rate limit information
- User context (if authenticated)
- Error details (if any)
"""
import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from backend.utils.logging import get_logger, set_request_context, clear_request_context


logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all HTTP requests and responses with structured logging

    Automatically adds request context to all logs within the request lifecycle
    """

    def __init__(
        self,
        app: ASGIApp,
        skip_paths: list[str] | None = None,
        log_request_body: bool = False,
        log_response_body: bool = False,
    ):
        """
        Initialize request logging middleware

        Args:
            app: ASGI application
            skip_paths: List of paths to skip logging (e.g., ["/health", "/metrics"])
            log_request_body: Whether to log request body (WARNING: may log sensitive data)
            log_response_body: Whether to log response body (WARNING: may be large)
        """
        super().__init__(app)
        self.skip_paths = skip_paths or []
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and add logging

        Args:
            request: FastAPI request object
            call_next: Next middleware/endpoint in chain

        Returns:
            Response from endpoint
        """
        # Skip logging for certain paths
        if any(request.url.path.startswith(skip) for skip in self.skip_paths):
            return await call_next(request)

        # Generate unique request ID
        request_id = str(uuid.uuid4())

        # Extract user context from request
        user_id = None
        if hasattr(request.state, "user_id"):
            user_id = request.state.user_id
        elif "x-user-id" in request.headers:
            user_id = request.headers["x-user-id"]

        # Set request context for all logs in this request
        set_request_context(
            request_id=request_id,
            user_id=user_id,
            endpoint=request.url.path
        )

        # Add request_id to request state for use in endpoints
        request.state.request_id = request_id

        # Log incoming request
        start_time = time.time()
        log_data = {
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params) if request.query_params else None,
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        }

        # Optionally log request body (be careful with sensitive data!)
        if self.log_request_body and request.method in ("POST", "PUT", "PATCH"):
            try:
                # Note: This consumes the body stream, so we need to be careful
                # In practice, you might want to skip this or use a custom approach
                log_data["request_body_available"] = True
            except:
                pass

        logger.info("request_received", **log_data)

        # Process request
        try:
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Extract rate limit info from response headers
            rate_limit_info = {}
            if "x-ratelimit-limit" in response.headers:
                rate_limit_info = {
                    "limit": response.headers.get("x-ratelimit-limit"),
                    "remaining": response.headers.get("x-ratelimit-remaining"),
                    "reset": response.headers.get("x-ratelimit-reset"),
                }
                # Update context with rate limit info
                set_request_context(rate_limit=rate_limit_info)

            # Log response
            response_data = {
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
            }

            if rate_limit_info:
                response_data["rate_limit"] = rate_limit_info

            # Add request_id to response headers for client correlation
            response.headers["X-Request-ID"] = request_id

            # Log based on status code
            if response.status_code >= 500:
                logger.error("request_failed", **response_data)
            elif response.status_code >= 400:
                logger.warning("request_error", **response_data)
            elif duration_ms > 1000:
                # Warn on slow requests (>1s)
                logger.warning("request_slow", **response_data)
            else:
                logger.info("request_completed", **response_data)

            return response

        except Exception as e:
            # Log exception
            duration_ms = (time.time() - start_time) * 1000

            logger.error(
                "request_exception",
                exc_info=True,
                error_type=type(e).__name__,
                error_message=str(e),
                duration_ms=round(duration_ms, 2),
            )

            # Re-raise to let error handlers deal with it
            raise

        finally:
            # Clean up request context
            clear_request_context()


async def request_logging_middleware(request: Request, call_next: Callable) -> Response:
    """
    Simple function-based request logging middleware

    Alternative to RequestLoggingMiddleware class for simpler use cases

    Args:
        request: FastAPI request
        call_next: Next handler

    Returns:
        Response from handler
    """
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    set_request_context(
        request_id=request_id,
        endpoint=request.url.path
    )

    start_time = time.time()

    logger.info(
        "request_start",
        method=request.method,
        path=request.url.path,
        client=request.client.host if request.client else None
    )

    try:
        response = await call_next(request)
        duration_ms = (time.time() - start_time) * 1000

        response.headers["X-Request-ID"] = request_id

        logger.info(
            "request_complete",
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2)
        )

        return response
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000

        logger.error(
            "request_error",
            exc_info=True,
            error=str(e),
            duration_ms=round(duration_ms, 2)
        )
        raise
    finally:
        clear_request_context()
