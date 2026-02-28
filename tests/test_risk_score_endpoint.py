"""Tests for risk score endpoint implementation."""
import pytest
from unittest.mock import patch
from backend.src.risk_score_endpoint import (
    get_risk_score_for_country,
    batch_get_risk_scores
)


class TestGetRiskScoreForCountry:
    """Test suite for get_risk_score_for_country function."""
    
    def test_invalid_country_code_too_short(self):
        """Test with invalid country code (too short)."""
        result = get_risk_score_for_country("B")
        assert "error" in result
        assert result["error"] == "Invalid country code"
    
    def test_invalid_country_code_too_long(self):
        """Test with invalid country code (too long)."""
        result = get_risk_score_for_country("BRA")
        assert "error" in result
        assert result["error"] == "Invalid country code"
    
    def test_invalid_country_code_numeric(self):
        """Test with invalid country code (contains numbers)."""
        result = get_risk_score_for_country("B1")
        assert "error" in result
        assert result["error"] == "Invalid country code"
    
    def test_successful_fetch(self):
        """Test successful risk score retrieval."""
        with patch('backend.src.risk_score_endpoint.get_current_year_risk', return_value=5.23):
            result = get_risk_score_for_country("BR")
            assert "error" not in result
            assert result["country_code"] == "BR"
            assert result["risk_score"] == 5.23
            assert result["source_attribution"] == "World Bank (CC BY 4.0)"
            assert "data_freshness" in result
            assert "timestamp" in result
    
    def test_no_data_available(self):
        """Test when no data is available for country."""
        with patch('backend.src.risk_score_endpoint.get_current_year_risk', return_value=None):
            result = get_risk_score_for_country("XX")
            assert "error" in result
            assert result["error"] == "Data not available"
            assert result["country_code"] == "XX"
            assert result["source_attribution"] == "World Bank (CC BY 4.0)"
    
    def test_lowercase_country_code(self):
        """Test that lowercase country codes are converted to uppercase."""
        with patch('backend.src.risk_score_endpoint.get_current_year_risk', return_value=3.45):
            result = get_risk_score_for_country("br")
            assert result["country_code"] == "BR"
    
    def test_risk_score_rounding(self):
        """Test that risk scores are rounded to 2 decimal places."""
        with patch('backend.src.risk_score_endpoint.get_current_year_risk', return_value=5.23456):
            result = get_risk_score_for_country("BR")
            assert result["risk_score"] == 5.23
    
    def test_response_structure(self):
        """Test that response has all required fields for valid request."""
        with patch('backend.src.risk_score_endpoint.get_current_year_risk', return_value=4.5):
            result = get_risk_score_for_country("US")
            required_fields = ["country_code", "risk_score", "data_freshness", "source_attribution", "timestamp"]
            for field in required_fields:
                assert field in result, f"Missing required field: {field}"


class TestBatchGetRiskScores:
    """Test suite for batch_get_risk_scores function."""
    
    def test_empty_list(self):
        """Test with empty country codes list."""
        result = batch_get_risk_scores([])
        assert result["total"] == 0
        assert result["successful"] == 0
        assert result["failed"] == 0
        assert result["results"] == []
    
    def test_single_country(self):
        """Test batch request with single country."""
        with patch('backend.src.risk_score_endpoint.get_current_year_risk', return_value=5.0):
            result = batch_get_risk_scores(["BR"])
            assert result["total"] == 1
            assert result["successful"] == 1
            assert result["failed"] == 0
            assert len(result["results"]) == 1
    
    def test_multiple_countries_all_successful(self):
        """Test batch request with multiple countries, all successful."""
        def mock_risk(country_code):
            return {"BR": 5.0, "US": 2.5, "DE": 1.8}.get(country_code, 3.0)
        
        with patch('backend.src.risk_score_endpoint.get_current_year_risk', side_effect=mock_risk):
            result = batch_get_risk_scores(["BR", "US", "DE"])
            assert result["total"] == 3
            assert result["successful"] == 3
            assert result["failed"] == 0
    
    def test_mixed_valid_invalid(self):
        """Test batch request with mix of valid and invalid codes."""
        def mock_risk(country_code):
            if country_code in ["BR", "US"]:
                return 4.0
            return None
        
        with patch('backend.src.risk_score_endpoint.get_current_year_risk', side_effect=mock_risk):
            result = batch_get_risk_scores(["BR", "XX", "US", "YY"])
            assert result["total"] == 4
            # BR and US should succeed, XX and YY should fail (either invalid or no data)
            assert result["failed"] > 0
    
    def test_all_failed(self):
        """Test batch request where all requests fail."""
        with patch('backend.src.risk_score_endpoint.get_current_year_risk', return_value=None):
            result = batch_get_risk_scores(["XX", "YY", "ZZ"])
            assert result["total"] == 3
            assert result["failed"] >= 1  # At least some should fail
    
    def test_response_structure(self):
        """Test that batch response has all required fields."""
        with patch('backend.src.risk_score_endpoint.get_current_year_risk', return_value=3.0):
            result = batch_get_risk_scores(["BR"])
            required_fields = ["results", "total", "successful", "failed", "timestamp"]
            for field in required_fields:
                assert field in result, f"Missing required field: {field}"
