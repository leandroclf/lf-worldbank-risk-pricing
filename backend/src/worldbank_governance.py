"""World Bank observability and quality-contract helpers."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from math import ceil, floor
from typing import Any


WORLD_BANK_SOURCE = "World Bank"
WORLD_BANK_SOURCE_ATTRIBUTION = "World Bank (CC BY 4.0)"

WORLD_BANK_QUALITY_CONTRACT = {
    "source": WORLD_BANK_SOURCE,
    "owner": "data-quality-steward",
    "completeness_target": 0.95,
    "freshness_target_years": 2,
    "consistency_target": "2-letter ISO country code and numeric FR.INR.RISK values",
    "remediation_path": (
        "Retry through the fallback years, then route remediation to data-quality-steward "
        "when the feed remains incomplete, stale, or inconsistent."
    ),
    "validation_cadence": {
        "day_0": "Capture the baseline for completeness, freshness, and consistency before enforcement.",
        "during_sprint": "Review source-level breaches and assign remediation ownership.",
        "end_of_sprint": "Confirm the contract can be enforced without manual guessing.",
    },
}

_METRICS_TEMPLATE = {
    "requests_by_endpoint": {},
    "http_status_by_endpoint": {},
    "http_latencies_seconds": [],
    "fetch_attempts": 0,
    "fetch_outcomes": {"success": 0, "empty": 0, "timeout": 0, "error": 0},
    "fetch_error_types": {},
    "fetch_latencies_seconds": [],
    "last_resolution_by_country": {},
    "fallback_year_uses": 0,
    "country_attempts": {},
    "country_successes": {},
    "country_failures": {},
    "country_latencies_seconds": [],
    "freshness_age_years": [],
    "batch_calls": 0,
    "batch_total_items": 0,
    "batch_successful_items": 0,
    "batch_failed_items": 0,
    "batch_success_rate_samples": [],
    "batch_latencies_seconds": [],
    "validation_failures": 0,
    "validation_failures_by_reason": {},
    "contract_breaches": 0,
    "contract_breaches_by_reason": {},
    "contract_breaches_by_country": {},
}

_METRICS = deepcopy(_METRICS_TEMPLATE)


def _normalize_country_code(code: Any) -> str:
    return str(code).strip().upper()


def _is_valid_country_code(code: Any) -> bool:
    normalized = _normalize_country_code(code)
    return len(normalized) == 2 and normalized.isalpha()


def _bump(mapping: dict[str, int], key: str, amount: int = 1) -> None:
    mapping[key] = mapping.get(key, 0) + amount


def _append_sample(bucket_name: str, value: float | int | None) -> None:
    if value is None:
        return
    _METRICS[bucket_name].append(float(value))


def _percentile(values: list[float], percentile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]

    rank = (len(ordered) - 1) * (percentile / 100.0)
    lower = floor(rank)
    upper = ceil(rank)
    if lower == upper:
        return ordered[lower]

    lower_value = ordered[lower]
    upper_value = ordered[upper]
    weight = rank - lower
    return lower_value + ((upper_value - lower_value) * weight)


def _summary(values: list[float], unit_scale: float = 1.0) -> dict[str, Any]:
    if not values:
        return {
            "count": 0,
            "avg": None,
            "p50": None,
            "p95": None,
            "min": None,
            "max": None,
        }

    scaled = [value * unit_scale for value in values]
    return {
        "count": len(scaled),
        "avg": round(sum(scaled) / len(scaled), 4),
        "p50": round(_percentile(scaled, 50) or 0.0, 4),
        "p95": round(_percentile(scaled, 95) or 0.0, 4),
        "min": round(min(scaled), 4),
        "max": round(max(scaled), 4),
    }


def _rate(numerator: int | float, denominator: int | float) -> float | None:
    if denominator in (0, 0.0):
        return None
    return round(float(numerator) / float(denominator), 4)


def reset_worldbank_metrics() -> None:
    """Reset all recorded World Bank telemetry."""
    global _METRICS
    _METRICS = deepcopy(_METRICS_TEMPLATE)


def record_http_request(endpoint: str, status_code: int, duration_seconds: float | None) -> None:
    """Record HTTP endpoint counts and latency."""
    endpoint_key = str(endpoint)
    _bump(_METRICS["requests_by_endpoint"], endpoint_key)

    status_bucket = _METRICS["http_status_by_endpoint"].setdefault(endpoint_key, {})
    _bump(status_bucket, str(int(status_code)))
    _append_sample("http_latencies_seconds", duration_seconds)


def record_fetch_attempt(
    country_code: str,
    year: int,
    duration_seconds: float | None,
    outcome: str,
    error_type: str | None = None,
) -> None:
    """Record a single World Bank API fetch attempt."""
    _METRICS["fetch_attempts"] += 1
    _METRICS["fetch_outcomes"][outcome] = _METRICS["fetch_outcomes"].get(outcome, 0) + 1
    if error_type:
        _bump(_METRICS["fetch_error_types"], error_type)
    _append_sample("fetch_latencies_seconds", duration_seconds)


def remember_worldbank_resolution(
    country_code: str,
    requested_year: int,
    resolved_year: int | None,
    attempts: int,
    success: bool,
    risk_value: float | None = None,
) -> None:
    """Remember the latest World Bank resolution outcome for a country."""
    country = _normalize_country_code(country_code)
    age_years = None
    if resolved_year is not None:
        age_years = datetime.now(timezone.utc).year - int(resolved_year)

    _METRICS["last_resolution_by_country"][country] = {
        "country_code": country,
        "requested_year": int(requested_year),
        "resolved_year": int(resolved_year) if resolved_year is not None else None,
        "attempts": int(attempts),
        "success": bool(success),
        "freshness_age_years": age_years,
        "risk_value": risk_value,
        "observed_at": datetime.now(timezone.utc).isoformat(),
    }

    if attempts > 1:
        _METRICS["fallback_year_uses"] += int(attempts) - 1


def get_last_worldbank_resolution(country_code: str) -> dict[str, Any] | None:
    """Return the most recent remembered resolution for a country, if any."""
    country = _normalize_country_code(country_code)
    resolution = _METRICS["last_resolution_by_country"].get(country)
    return deepcopy(resolution) if resolution is not None else None


def record_country_resolution(
    country_code: str,
    success: bool,
    duration_seconds: float | None = None,
    resolved_year: int | None = None,
) -> None:
    """Record endpoint-level country resolution success and latency."""
    country = _normalize_country_code(country_code)
    _bump(_METRICS["country_attempts"], country)
    if success:
        _bump(_METRICS["country_successes"], country)
        if resolved_year is not None:
            _METRICS["freshness_age_years"].append(
                datetime.now(timezone.utc).year - int(resolved_year)
            )
    else:
        _bump(_METRICS["country_failures"], country)
    _append_sample("country_latencies_seconds", duration_seconds)


def record_batch_resolution(
    total: int,
    successful: int,
    failed: int,
    duration_seconds: float | None = None,
) -> None:
    """Record a batch endpoint execution and its item-level outcome."""
    _METRICS["batch_calls"] += 1
    _METRICS["batch_total_items"] += int(total)
    _METRICS["batch_successful_items"] += int(successful)
    _METRICS["batch_failed_items"] += int(failed)
    if total > 0:
        _METRICS["batch_success_rate_samples"].append(_rate(successful, total) or 0.0)
    _append_sample("batch_latencies_seconds", duration_seconds)


def record_validation_failure(endpoint: str, reason: str) -> None:
    """Record a validation failure at the ingestion boundary."""
    _METRICS["validation_failures"] += 1
    reason_key = f"{endpoint}:{reason}"
    _bump(_METRICS["validation_failures_by_reason"], reason_key)


def record_contract_breach(country_code: str | None, reason: str) -> None:
    """Record a source-quality contract breach."""
    _METRICS["contract_breaches"] += 1
    reason_key = str(reason)
    _bump(_METRICS["contract_breaches_by_reason"], reason_key)
    country_key = _normalize_country_code(country_code) if country_code is not None else "GLOBAL"
    _bump(_METRICS["contract_breaches_by_country"], country_key)


def get_worldbank_quality_contract() -> dict[str, Any]:
    """Return a copy of the World Bank source contract definition."""
    return deepcopy(WORLD_BANK_QUALITY_CONTRACT)


def evaluate_worldbank_quality_contract(
    country_code: str,
    resolved_year: int | None,
    risk_value: float | None,
) -> dict[str, Any]:
    """Evaluate the current World Bank observation against the quality contract."""
    contract = get_worldbank_quality_contract()
    current_year = datetime.now(timezone.utc).year
    freshness_age_years = None if resolved_year is None else current_year - int(resolved_year)

    reasons: list[str] = []
    if not _is_valid_country_code(country_code):
        reasons.append("consistency_breach")
    if risk_value is None:
        reasons.append("completeness_breach")
    if freshness_age_years is None and risk_value is not None:
        reasons.append("freshness_unknown")
    elif freshness_age_years is not None and freshness_age_years > contract["freshness_target_years"]:
        reasons.append("freshness_breach")

    return {
        "source": contract["source"],
        "owner": contract["owner"],
        "compliant": not reasons,
        "reasons": reasons,
        "freshness_age_years": freshness_age_years,
        "thresholds": {
            "completeness_target": contract["completeness_target"],
            "freshness_target_years": contract["freshness_target_years"],
            "consistency_target": contract["consistency_target"],
        },
        "remediation_path": contract["remediation_path"],
    }


def get_worldbank_metrics_snapshot() -> dict[str, Any]:
    """Build a stable snapshot of the recorded telemetry."""
    fetch_total = _METRICS["fetch_attempts"]
    country_attempts_total = sum(_METRICS["country_attempts"].values())
    country_success_total = sum(_METRICS["country_successes"].values())
    country_failure_total = sum(_METRICS["country_failures"].values())
    batch_total_items = _METRICS["batch_total_items"]
    batch_success_total = _METRICS["batch_successful_items"]

    country_success_rates = {
        country: _rate(
            _METRICS["country_successes"].get(country, 0),
            _METRICS["country_attempts"].get(country, 0),
        )
        for country in _METRICS["country_attempts"]
    }
    batch_success_rate = _summary(_METRICS["batch_success_rate_samples"])
    freshness_summary = _summary(_METRICS["freshness_age_years"], unit_scale=1.0)

    cost_proxy = {
        "requests_per_successful_country_resolution": _rate(
            fetch_total,
            country_success_total,
        ),
        "requests_per_successful_fetch_attempt": _rate(
            fetch_total,
            _METRICS["fetch_outcomes"].get("success", 0),
        ),
        "fallback_years_per_successful_country_resolution": _rate(
            _METRICS["fallback_year_uses"],
            country_success_total,
        ),
    }

    return {
        "requests_by_endpoint": deepcopy(_METRICS["requests_by_endpoint"]),
        "http_status_by_endpoint": deepcopy(_METRICS["http_status_by_endpoint"]),
        "latency": {
            "http": _summary(_METRICS["http_latencies_seconds"], unit_scale=1000.0),
            "fetch": _summary(_METRICS["fetch_latencies_seconds"], unit_scale=1000.0),
            "country_resolution": _summary(
                _METRICS["country_latencies_seconds"],
                unit_scale=1000.0,
            ),
            "batch": _summary(_METRICS["batch_latencies_seconds"], unit_scale=1000.0),
        },
        "rates": {
            "fetch_success_rate": _rate(
                _METRICS["fetch_outcomes"].get("success", 0),
                fetch_total,
            ),
            "fetch_timeout_rate": _rate(
                _METRICS["fetch_outcomes"].get("timeout", 0),
                fetch_total,
            ),
            "fetch_error_rate": _rate(
                _METRICS["fetch_outcomes"].get("error", 0),
                fetch_total,
            ),
            "country_success_rate": country_success_rates,
            "country_success_rate_overall": _rate(country_success_total, country_attempts_total),
            "country_failure_rate_overall": _rate(country_failure_total, country_attempts_total),
            "batch_success_rate": batch_success_rate,
            "batch_item_success_rate": _rate(batch_success_total, batch_total_items),
        },
        "fallback_year_usage": {
            "total": _METRICS["fallback_year_uses"],
            "by_country": {
                country: resolution["attempts"] - 1
                for country, resolution in _METRICS["last_resolution_by_country"].items()
                if resolution.get("attempts", 0) > 1
            },
        },
        "freshness_age_years": freshness_summary,
        "cost_proxy": cost_proxy,
        "validation": {
            "failures": _METRICS["validation_failures"],
            "by_reason": deepcopy(_METRICS["validation_failures_by_reason"]),
        },
        "contracts": {
            "world_bank": {
                "definition": get_worldbank_quality_contract(),
                "breaches": _METRICS["contract_breaches"],
                "breaches_by_reason": deepcopy(_METRICS["contract_breaches_by_reason"]),
                "breaches_by_country": deepcopy(_METRICS["contract_breaches_by_country"]),
            }
        },
        "last_resolution_by_country": deepcopy(_METRICS["last_resolution_by_country"]),
    }
