"""Tests for World Bank data ingestion module."""
import pytest
from unittest.mock import patch, Mock
from backend.src.data_ingestion import (
    fetch_risk_indicator,
    get_current_year_risk,
    RISK_INDICATOR_CODE,
    WORLD_BANK_API_BASE_URL
)


class TestFetchRiskIndicator:
    """Test suite for fetch_risk_indicator function."""
    
    def test_successful_fetch(self):
        """Test successful data retrieval from World Bank API."""
        mock_response = Mock()
        mock_response.json.return_value = [
            {"page": 1, "pages": 1},
            [{"value": 5.23, "date": "2023"}]
        ]
        mock_response.raise_for_status = Mock()
        
        with patch('backend.src.data_ingestion.requests.get', return_value=mock_response):
            result = fetch_risk_indicator("BR", 2023)
            assert result == 5.23
    
    def test_no_data_available(self):
        """Test when no data is available for the requested country/year."""
        mock_response = Mock()
        mock_response.json.return_value = [
            {"page": 1, "pages": 1},
            []
        ]
        mock_response.raise_for_status = Mock()
        
        with patch('backend.src.data_ingestion.requests.get', return_value=mock_response):
            result = fetch_risk_indicator("XX", 2023)
            assert result is None
    
    def test_null_value(self):
        """Test when API returns null value."""
        mock_response = Mock()
        mock_response.json.return_value = [
            {"page": 1, "pages": 1},
            [{"value": None, "date": "2023"}]
        ]
        mock_response.raise_for_status = Mock()
        
        with patch('backend.src.data_ingestion.requests.get', return_value=mock_response):
            result = fetch_risk_indicator("US", 2023)
            assert result is None
    
    def test_http_error(self):
        """Test handling of HTTP errors."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("404 Not Found")
        
        with patch('backend.src.data_ingestion.requests.get', return_value=mock_response):
            result = fetch_risk_indicator("INVALID", 2023)
            assert result is None
    
    def test_connection_error(self):
        """Test handling of connection errors."""
        with patch('backend.src.data_ingestion.requests.get', side_effect=Exception("Connection failed")):
            result = fetch_risk_indicator("BR", 2023)
            assert result is None
    
    def test_correct_url_construction(self):
        """Test that the API URL is correctly constructed."""
        mock_response = Mock()
        mock_response.json.return_value = [{"page": 1}, []]
        mock_response.raise_for_status = Mock()
        
        with patch('backend.src.data_ingestion.requests.get', return_value=mock_response) as mock_get:
            fetch_risk_indicator("BR", 2023)
            expected_url = f"{WORLD_BANK_API_BASE_URL}/BR/indicator/{RISK_INDICATOR_CODE}?date=2023&format=json"
            mock_get.assert_called_once()
            assert expected_url in str(mock_get.call_args)


class TestGetCurrentYearRisk:
    """Test suite for get_current_year_risk function."""
    
    def test_current_year_available(self):
        """Test when data for current year is available."""
        with patch('backend.src.data_ingestion.fetch_risk_indicator', return_value=4.5):
            result = get_current_year_risk("BR")
            assert result == 4.5
    
    def test_fallback_to_previous_year(self):
        """Test fallback to previous years when current year unavailable."""
        def mock_fetch(country, year):
            # Return None for current year, data for previous year
            from datetime import datetime
            current_year = datetime.now().year
            if year == current_year:
                return None
            elif year == current_year - 1:
                return 3.8
            return None
        
        with patch('backend.src.data_ingestion.fetch_risk_indicator', side_effect=mock_fetch):
            result = get_current_year_risk("BR")
            assert result == 3.8
    
    def test_no_data_available_any_year(self):
        """Test when no data is available for any recent year."""
        with patch('backend.src.data_ingestion.fetch_risk_indicator', return_value=None):
            result = get_current_year_risk("XX")
            assert result is None
    
    def test_tries_multiple_years(self):
        """Test that the function tries multiple years."""
        call_count = 0
        
        def mock_fetch(country, year):
            nonlocal call_count
            call_count += 1
            if call_count == 3:  # Return data on third attempt
                return 2.1
            return None
        
        with patch('backend.src.data_ingestion.fetch_risk_indicator', side_effect=mock_fetch):
            result = get_current_year_risk("DE")
            assert result == 2.1
            assert call_count == 3


class TestIntegration:
    """Integration tests for data ingestion (require network)."""
    
    @pytest.mark.skip(reason="Integration test - requires network access")
    def test_real_api_call(self):
        """Test actual API call to World Bank (skip by default)."""
        result = fetch_risk_indicator("BR", 2020)
        # Just check that we get a valid response or None
        assert result is None or isinstance(result, (int, float))
