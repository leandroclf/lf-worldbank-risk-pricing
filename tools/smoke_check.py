from backend.src.api import (
    get_pricing_signal,
    compute_pricing_multiplier,
    build_pricing_quote,
    build_pricing_bands_response,
)


def main():
    payload = get_pricing_signal()
    assert payload["issue"] == "ISSUE-003"
    assert payload["regionalScoreEnabled"] is True
    assert compute_pricing_multiplier(75) == 1.08
    quote = build_pricing_quote("BR", 80, 1000, currency="BRL")
    assert quote["finalPrice"] == 1080.0
    bands = build_pricing_bands_response(
        [{"countryCode": "BR", "riskScore": 80}, {"countryCode": "US", "riskScore": 40}]
    )
    assert bands["total"] == 2
    print("smoke-check:ok")


if __name__ == "__main__":
    main()
