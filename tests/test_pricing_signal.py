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


def test_build_pricing_decision():
    d = build_pricing_decision("br", 78)
    assert d["countryCode"] == "BR"
    assert d["tier"] == "high"
    assert d["adjustmentPct"] == 8
