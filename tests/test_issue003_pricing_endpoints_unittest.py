import unittest

from backend.src.api import build_pricing_bands_response, build_pricing_quote


class TestIssue003PricingEndpoints(unittest.TestCase):
    def test_build_pricing_quote_contract(self):
        quote = build_pricing_quote(country_code="br", risk_score="80", base_price="1000", currency="brl")
        self.assertEqual(quote["issue"], "ISSUE-003")
        self.assertEqual(quote["countryCode"], "BR")
        self.assertEqual(quote["tier"], "high")
        self.assertEqual(quote["multiplier"], 1.08)
        self.assertEqual(quote["finalPrice"], 1080.0)
        self.assertEqual(quote["currency"], "BRL")

    def test_build_pricing_bands_response_contract(self):
        payload = build_pricing_bands_response(
            [
                {"countryCode": "BR", "riskScore": 80},
                {"countryCode": "AR", "riskScore": 60},
                {"countryCode": "US", "riskScore": 40},
            ],
            high_risk_threshold=75,
        )
        self.assertEqual(payload["issue"], "ISSUE-003")
        self.assertEqual(payload["total"], 3)
        self.assertEqual(payload["bands"]["high"], 1)
        self.assertEqual(payload["bands"]["medium"], 1)
        self.assertEqual(payload["bands"]["low"], 1)
        self.assertEqual(payload["highRisk"]["highRisk"], 1)


if __name__ == "__main__":
    unittest.main()
