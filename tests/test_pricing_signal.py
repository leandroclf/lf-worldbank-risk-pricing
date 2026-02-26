from backend.src.api import get_pricing_signal


def test_pricing_signal():
    p=get_pricing_signal()
    assert p["regionalScoreEnabled"] is True
    assert p["proposalTarget"]==2


from backend.src.api import build_risk_score_response


def test_build_risk_score_response():
    r = build_risk_score_response("br", 72.5)
    assert r["countryCode"] == "BR"
    assert r["riskScore"] == 72.5
    assert "World Bank" in r["sourceAttribution"]


from backend.src.api import is_valid_country_code


def test_is_valid_country_code():
    assert is_valid_country_code("BR") is True
    assert is_valid_country_code("b") is False
    assert is_valid_country_code("123") is False


from backend.src.api import build_pricing_adjustment


def test_build_pricing_adjustment():
    assert build_pricing_adjustment(80)["tier"] == "high"
    assert build_pricing_adjustment(60)["adjustmentPct"] == 3
    assert build_pricing_adjustment(30)["adjustmentPct"] == 0


from backend.src.api import compute_pricing_multiplier


def test_compute_pricing_multiplier():
    assert compute_pricing_multiplier(80) == 1.08
    assert compute_pricing_multiplier(60) == 1.03
    assert compute_pricing_multiplier(20) == 1.0


from backend.src.api import build_pricing_decision
from backend.src.api import score_pricing_portfolio
from backend.src.api import summarize_country_risk_bands
from backend.src.api import estimate_portfolio_adjustment_pct
from backend.src.api import summarize_pricing_tiers_with_multiplier
from backend.src.api import count_high_risk_countries
from backend.src.api import estimate_high_risk_rate
from backend.src.api import calculate_multiplier_delta


def test_build_pricing_decision():
    d = build_pricing_decision("br", 78)
    assert d["countryCode"] == "BR"
    assert d["tier"] == "high"
    assert d["adjustmentPct"] == 8


def test_score_pricing_portfolio():
    p = score_pricing_portfolio([
        {"countryCode": "br", "riskScore": 80},
        {"countryCode": "cl", "riskScore": 55},
        {"countryCode": "uy", "riskScore": 30},
    ])
    assert p == {"total": 3, "highRiskCount": 1, "avgMultiplier": 1.0367}


def test_score_pricing_portfolio_empty():
    assert score_pricing_portfolio([]) == {"total": 0, "highRiskCount": 0, "avgMultiplier": 1.0}


def test_summarize_country_risk_bands():
    out = summarize_country_risk_bands([
        {"countryCode": "br", "riskScore": 80},
        {"countryCode": "cl", "riskScore": 55},
        {"countryCode": "uy", "riskScore": 30},
        {"countryCode": "ar", "riskScore": 90},
    ])
    assert out == {"high": 2, "medium": 1, "low": 1}


def test_summarize_country_risk_bands_empty():
    assert summarize_country_risk_bands([]) == {"high": 0, "medium": 0, "low": 0}


def test_estimate_portfolio_adjustment_pct():
    out = estimate_portfolio_adjustment_pct([
        {"countryCode": "br", "riskScore": 80},
        {"countryCode": "cl", "riskScore": 55},
        {"countryCode": "uy", "riskScore": 30},
    ])
    assert out == 3.67


def test_estimate_portfolio_adjustment_pct_empty():
    assert estimate_portfolio_adjustment_pct([]) == 0.0


def test_summarize_pricing_tiers_with_multiplier():
    out = summarize_pricing_tiers_with_multiplier([
        {"countryCode": "br", "riskScore": 80},
        {"countryCode": "cl", "riskScore": 55},
        {"countryCode": "uy", "riskScore": 30},
    ])
    assert out == {
        "bands": {"high": 1, "medium": 1, "low": 1},
        "avgMultiplier": 1.0367,
    }


def test_summarize_pricing_tiers_with_multiplier_empty():
    assert summarize_pricing_tiers_with_multiplier([]) == {
        "bands": {"high": 0, "medium": 0, "low": 0},
        "avgMultiplier": 1.0,
    }


def test_count_high_risk_countries():
    out = count_high_risk_countries([
        {"countryCode": "br", "riskScore": 80},
        {"countryCode": "cl", "riskScore": 55},
        {"countryCode": "ar", "riskScore": 90},
    ], threshold=75)
    assert out == {"threshold": 75.0, "total": 3, "highRisk": 2}


def test_count_high_risk_countries_empty():
    assert count_high_risk_countries([], threshold=75) == {"threshold": 75.0, "total": 0, "highRisk": 0}


def test_estimate_high_risk_rate():
    out = estimate_high_risk_rate([
        {"countryCode": "br", "riskScore": 80},
        {"countryCode": "cl", "riskScore": 55},
        {"countryCode": "ar", "riskScore": 90},
        {"countryCode": "uy", "riskScore": 30},
    ], threshold=75)
    assert out == 0.5


def test_estimate_high_risk_rate_empty():
    assert estimate_high_risk_rate([], threshold=75) == 0.0


def test_calculate_multiplier_delta():
    entries = [
        {"countryCode": "br", "riskScore": 80},
        {"countryCode": "cl", "riskScore": 55},
        {"countryCode": "uy", "riskScore": 30},
    ]
    delta = calculate_multiplier_delta(entries, baseline_multiplier=1.02)
    assert delta == 1.64


def test_calculate_multiplier_delta_zero_baseline():
    assert calculate_multiplier_delta([{"countryCode": "br", "riskScore": 80}], baseline_multiplier=0) == 0.0
