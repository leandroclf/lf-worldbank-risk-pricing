"""Tests for World Bank telemetry and quality-contract helpers."""

from datetime import datetime

from backend.src.worldbank_governance import (
    evaluate_worldbank_quality_contract,
    get_last_worldbank_resolution,
    get_worldbank_metrics_snapshot,
    get_worldbank_quality_contract,
    record_batch_resolution,
    record_contract_breach,
    record_country_resolution,
    record_fetch_attempt,
    record_http_request,
    record_validation_failure,
    remember_worldbank_resolution,
    reset_worldbank_metrics,
)


def test_worldbank_quality_contract_exposes_owner_and_remediation_path():
    contract = get_worldbank_quality_contract()

    assert contract["source"] == "World Bank"
    assert contract["owner"] == "data-quality-steward"
    assert contract["completeness_target"] == 0.95
    assert contract["freshness_target_years"] == 2
    assert contract["validation_cadence"]["day_0"]
    assert "remediation" in contract["remediation_path"].lower()


def test_worldbank_contract_evaluation_flags_freshness_breach():
    current_year = datetime.now().year

    evaluation = evaluate_worldbank_quality_contract(
        "BR",
        resolved_year=current_year - 3,
        risk_value=4.2,
    )

    assert evaluation["compliant"] is False
    assert "freshness_breach" in evaluation["reasons"]
    assert evaluation["thresholds"]["freshness_target_years"] == 2


def test_worldbank_metrics_snapshot_tracks_latency_and_cost_proxy():
    reset_worldbank_metrics()
    current_year = datetime.now().year
    resolved_year = current_year - 1

    record_http_request("GET /v1/risk-score", 200, 0.010)
    record_http_request("GET /v1/risk-score", 200, 0.030)

    record_fetch_attempt("BR", current_year, 0.050, "success")
    record_fetch_attempt("BR", current_year - 1, 0.150, "timeout", error_type="timeout")

    remember_worldbank_resolution(
        country_code="BR",
        requested_year=current_year,
        resolved_year=resolved_year,
        attempts=2,
        success=True,
        risk_value=5.23,
    )
    assert get_last_worldbank_resolution("br")["resolved_year"] == resolved_year

    record_country_resolution(
        "BR",
        success=True,
        duration_seconds=0.180,
        resolved_year=resolved_year,
    )
    record_batch_resolution(total=2, successful=1, failed=1, duration_seconds=0.220)
    record_validation_failure("POST /v1/risk-score/batch", "invalid_payload")
    record_contract_breach("BR", "freshness_breach")

    snapshot = get_worldbank_metrics_snapshot()

    assert snapshot["requests_by_endpoint"]["GET /v1/risk-score"] == 2
    assert snapshot["latency"]["http"]["count"] == 2
    assert snapshot["latency"]["fetch"]["count"] == 2
    assert snapshot["latency"]["fetch"]["p50"] is not None
    assert snapshot["latency"]["batch"]["count"] == 1
    assert snapshot["latency"]["batch"]["p95"] is not None
    assert snapshot["rates"]["fetch_timeout_rate"] == 0.5
    assert snapshot["rates"]["country_success_rate"]["BR"] == 1.0
    assert snapshot["rates"]["country_success_rate_overall"] == 1.0
    assert snapshot["rates"]["batch_item_success_rate"] == 0.5
    assert snapshot["fallback_year_usage"]["total"] == 1
    assert snapshot["freshness_age_years"]["count"] == 1
    assert snapshot["freshness_age_years"]["max"] == 1
    assert snapshot["cost_proxy"]["requests_per_successful_country_resolution"] == 2.0
    assert snapshot["validation"]["failures"] == 1
    assert snapshot["contracts"]["world_bank"]["breaches"] == 1
    assert snapshot["contracts"]["world_bank"]["breaches_by_reason"]["freshness_breach"] == 1
