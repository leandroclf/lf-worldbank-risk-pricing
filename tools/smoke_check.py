from backend.src.api import get_pricing_signal, compute_pricing_multiplier


def main():
    payload = get_pricing_signal()
    assert payload["issue"] == "ISSUE-003"
    assert payload["regionalScoreEnabled"] is True
    assert compute_pricing_multiplier(75) == 1.08
    print("smoke-check:ok")


if __name__ == "__main__":
    main()
