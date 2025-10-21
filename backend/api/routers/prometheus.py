"""
Prometheus Metrics Endpoint

Exposes Prometheus metrics at /metrics for scraping
"""
from fastapi import APIRouter, Response
from backend.utils.prometheus_metrics import get_metrics

router = APIRouter(prefix="/metrics", tags=["Observability"])


@router.get("", summary="Prometheus metrics endpoint")
async def metrics():
    """
    Prometheus metrics endpoint

    Returns metrics in Prometheus text format for scraping.
    This endpoint should be configured in prometheus.yml:

    ```yaml
    scrape_configs:
      - job_name: 'purpura-api'
        static_configs:
          - targets: ['purpura-api:8000']
        metrics_path: '/metrics'
    ```

    Returns:
        Prometheus metrics in text format
    """
    metrics_output, content_type = get_metrics()

    return Response(
        content=metrics_output,
        media_type=content_type
    )
