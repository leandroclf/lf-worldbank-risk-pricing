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
