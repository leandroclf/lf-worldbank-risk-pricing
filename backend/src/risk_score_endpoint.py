"""
Risk Score API Endpoint Implementation for World Bank data.

This module keeps the public response shapes stable while recording endpoint
latency, fallback-year usage, and source-quality contract outcomes.
"""

from datetime import datetime, timezone
from time import perf_counter

from backend.src.api import is_valid_country_code
from backend.src.worldbank_governance import (
    evaluate_worldbank_quality_contract,
    get_last_worldbank_resolution,
    get_worldbank_metrics_snapshot,
    get_worldbank_quality_contract,
    record_batch_resolution,
    record_contract_breach,
    record_country_resolution,
    record_http_request,
    record_validation_failure,
    remember_worldbank_resolution,
    reset_worldbank_metrics,
)

# Try to import data_ingestion, but handle case where 'requests' is not available
try:
    from backend.src.data_ingestion import get_current_year_risk

    DATA_INGESTION_AVAILABLE = True
except ImportError:
    DATA_INGESTION_AVAILABLE = False

    def get_current_year_risk(country_code):
        """Fallback stub when data_ingestion is not available."""
        return None


def _normalize_country_code(country_code: str) -> str:
    return str(country_code).strip().upper()


def get_risk_score_for_country(
    country_code: str,
    record_metrics: bool = True,
) -> dict:
    """
    Get risk score for a country from World Bank data.

    The function records internal resolution metrics and, when requested,
    endpoint-level request counts for baseline analysis.
    """
    endpoint = "GET /v1/risk-score"
    started_at = perf_counter()
    status_code = 200
    normalized_country_code = _normalize_country_code(country_code)

    try:
        if not is_valid_country_code(country_code):
            status_code = 400
            record_validation_failure(endpoint, "invalid_country_code")
            return {
                "error": "Invalid country code",
                "message": "Country code must be a 2-letter ISO code",
                "country_code": normalized_country_code,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        # Fetch risk data from World Bank.
        risk_value = get_current_year_risk(normalized_country_code)
        resolution = get_last_worldbank_resolution(normalized_country_code) or {}
        resolved_year = resolution.get("resolved_year")
        if not resolution:
            remember_worldbank_resolution(
                country_code=normalized_country_code,
                requested_year=datetime.now(timezone.utc).year,
                resolved_year=resolved_year if risk_value is not None else None,
                attempts=1,
                success=risk_value is not None,
                risk_value=risk_value,
            )
            resolution = get_last_worldbank_resolution(normalized_country_code) or {}
            resolved_year = resolution.get("resolved_year")

        # Handle case where no data is available.
        if risk_value is None:
            status_code = 404
            record_contract_breach(normalized_country_code, "completeness_breach")
            record_country_resolution(
                normalized_country_code,
                success=False,
                duration_seconds=perf_counter() - started_at,
            )
            return {
                "error": "Data not available",
                "message": f"No risk data available for country: {normalized_country_code}",
                "country_code": normalized_country_code,
                "source_attribution": "World Bank (CC BY 4.0)",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        if resolved_year is None:
            resolved_year = datetime.now(timezone.utc).year - 1

        contract_check = evaluate_worldbank_quality_contract(
            normalized_country_code,
            resolved_year,
            risk_value,
        )
        if not contract_check["compliant"]:
            for reason in contract_check["reasons"]:
                record_contract_breach(normalized_country_code, reason)

        record_country_resolution(
            normalized_country_code,
            success=True,
            duration_seconds=perf_counter() - started_at,
            resolved_year=resolved_year,
        )

        # Build successful response.
        return {
            "country_code": normalized_country_code,
            "risk_score": round(risk_value, 2),
            "data_freshness": str(resolved_year),
            "source_attribution": "World Bank (CC BY 4.0)",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    finally:
        if record_metrics:
            record_http_request(endpoint, status_code, perf_counter() - started_at)


def batch_get_risk_scores(
    country_codes: list,
    record_metrics: bool = True,
) -> dict:
    """
    Get risk scores for multiple countries in a single call.

    Args:
        country_codes (list): List of 2-letter ISO country codes
    """
    endpoint = "POST /v1/risk-score/batch"
    started_at = perf_counter()
    successful = 0
    failed = 0
    results = []

    for code in country_codes:
        result = get_risk_score_for_country(code, record_metrics=record_metrics)
        results.append(result)

        if "error" in result:
            failed += 1
        else:
            successful += 1

    duration_seconds = perf_counter() - started_at
    record_batch_resolution(len(country_codes), successful, failed, duration_seconds)

    if record_metrics:
        record_http_request(endpoint, 200, duration_seconds)

    return {
        "results": results,
        "total": len(country_codes),
        "successful": successful,
        "failed": failed,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


__all__ = [
    "DATA_INGESTION_AVAILABLE",
    "get_risk_score_for_country",
    "batch_get_risk_scores",
    "get_worldbank_metrics_snapshot",
    "get_worldbank_quality_contract",
    "reset_worldbank_metrics",
]


if __name__ == "__main__":
    # Example usage and manual testing.
    print("=" * 60)
    print("Risk Score Endpoint - Manual Test")
    print("=" * 60)

    print("\n1. Testing Brazil (BR):")
    result_br = get_risk_score_for_country("BR")
    print(f"   {result_br}")

    print("\n2. Testing United States (US):")
    result_us = get_risk_score_for_country("US")
    print(f"   {result_us}")

    print("\n3. Testing invalid country code (XX):")
    result_invalid = get_risk_score_for_country("XX")
    print(f"   {result_invalid}")

    print("\n4. Testing batch request:")
    batch_result = batch_get_risk_scores(["BR", "US", "DE", "CN"])
    print(f"   Total: {batch_result['total']}")
    print(f"   Successful: {batch_result['successful']}")
    print(f"   Failed: {batch_result['failed']}")

    print("\n" + "=" * 60)
