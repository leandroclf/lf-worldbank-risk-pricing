"""Tests for portfolio risk summary function."""
import pytest
from backend.src.api import get_portfolio_risk_summary


class TestGetPortfolioRiskSummary:
    """Test suite for get_portfolio_risk_summary function."""
    
    def test_empty_portfolio_results(self):
        """Test with empty portfolio results list."""
        result = get_portfolio_risk_summary([])
        assert result == {
            "total_portfolios": 0,
            "avg_exposure": 0.0,
            "total_at_risk": 0
        }
    
    def test_none_portfolio_results(self):
        """Test with None as input."""
        result = get_portfolio_risk_summary(None)
        assert result == {
            "total_portfolios": 0,
            "avg_exposure": 0.0,
            "total_at_risk": 0
        }
    
    def test_single_portfolio(self):
        """Test with a single portfolio result."""
        portfolio_results = [
            {
                "exposure": 0.25,
                "positions_at_risk": 3,
                "total_positions": 10
            }
        ]
        result = get_portfolio_risk_summary(portfolio_results)
        assert result["total_portfolios"] == 1
        assert result["avg_exposure"] == 0.25
        assert result["total_at_risk"] == 3
    
    def test_multiple_portfolios(self):
        """Test with multiple portfolio results."""
        portfolio_results = [
            {"exposure": 0.2, "positions_at_risk": 2},
            {"exposure": 0.4, "positions_at_risk": 5},
            {"exposure": 0.3, "positions_at_risk": 3}
        ]
        result = get_portfolio_risk_summary(portfolio_results)
        assert result["total_portfolios"] == 3
        # Average exposure should be (0.2 + 0.4 + 0.3) / 3 = 0.3
        assert result["avg_exposure"] == 0.3
        # Total at risk should be 2 + 5 + 3 = 10
        assert result["total_at_risk"] == 10
    
    def test_rounding_precision(self):
        """Test that average exposure is rounded to 4 decimal places."""
        portfolio_results = [
            {"exposure": 0.123456, "positions_at_risk": 1},
            {"exposure": 0.234567, "positions_at_risk": 2}
        ]
        result = get_portfolio_risk_summary(portfolio_results)
        # Average should be (0.123456 + 0.234567) / 2 = 0.1790115, rounded to 0.1790
        assert result["avg_exposure"] == 0.1790
    
    def test_missing_exposure_key(self):
        """Test handling of missing exposure key (should default to 0)."""
        portfolio_results = [
            {"positions_at_risk": 3},
            {"exposure": 0.5, "positions_at_risk": 2}
        ]
        result = get_portfolio_risk_summary(portfolio_results)
        # Average should be (0 + 0.5) / 2 = 0.25
        assert result["avg_exposure"] == 0.25
        assert result["total_at_risk"] == 5
    
    def test_missing_positions_at_risk_key(self):
        """Test handling of missing positions_at_risk key (should default to 0)."""
        portfolio_results = [
            {"exposure": 0.3},
            {"exposure": 0.2, "positions_at_risk": 4}
        ]
        result = get_portfolio_risk_summary(portfolio_results)
        assert result["total_at_risk"] == 4
    
    def test_zero_exposure_portfolios(self):
        """Test with portfolios that have zero exposure."""
        portfolio_results = [
            {"exposure": 0.0, "positions_at_risk": 0},
            {"exposure": 0.0, "positions_at_risk": 0},
            {"exposure": 0.0, "positions_at_risk": 0}
        ]
        result = get_portfolio_risk_summary(portfolio_results)
        assert result["total_portfolios"] == 3
        assert result["avg_exposure"] == 0.0
        assert result["total_at_risk"] == 0
    
    def test_high_risk_scenario(self):
        """Test scenario with high risk across multiple portfolios."""
        portfolio_results = [
            {"exposure": 0.85, "positions_at_risk": 12},
            {"exposure": 0.92, "positions_at_risk": 15},
            {"exposure": 0.78, "positions_at_risk": 10}
        ]
        result = get_portfolio_risk_summary(portfolio_results)
        assert result["total_portfolios"] == 3
        # Average exposure: (0.85 + 0.92 + 0.78) / 3 = 0.85
        assert result["avg_exposure"] == 0.85
        assert result["total_at_risk"] == 37
