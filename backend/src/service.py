"""Core service bootstrap for lf-worldbank-risk-pricing."""

def healthcheck():
    return {"status": "ok", "component": "lf-worldbank-risk-pricing"}


def roadmap_items():
    return [
        "ingest",
        "normalize",
        "publish-metrics"
    ]
