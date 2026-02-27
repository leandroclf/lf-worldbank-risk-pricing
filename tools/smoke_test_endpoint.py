#!/usr/bin/env python3
"""Smoke test for risk score endpoint."""

import sys
import os
sys.path.insert(0, '.')

from backend.src.risk_score_endpoint import get_risk_score_for_country, batch_get_risk_scores


def test_endpoint_validation():
    """Test endpoint validation logic."""
    print("Testing endpoint validation...")
    
    # Test invalid country codes
    invalid_codes = ["B", "BRA", "B1", "1B", ""]
    for code in invalid_codes:
        result = get_risk_score_for_country(code)
        assert "error" in result, f"Should reject invalid code: {code}"
        assert result["error"] == "Invalid country code"
    print(f"✓ All {len(invalid_codes)} invalid codes rejected")
    
    # Test valid format (will fail data fetch without network, but that's OK)
    result = get_risk_score_for_country("BR")
    assert "country_code" in result
    assert result["country_code"] == "BR"
    assert "source_attribution" in result
    assert result["source_attribution"] == "World Bank (CC BY 4.0)"
    print("✓ Valid code format accepted")
    
    print("✓ Endpoint validation tests passed!\n")


def test_batch_endpoint():
    """Test batch endpoint logic."""
    print("Testing batch endpoint...")
    
    # Test empty batch
    result = batch_get_risk_scores([])
    assert result["total"] == 0
    assert result["successful"] == 0
    assert result["failed"] == 0
    print("✓ Empty batch handled correctly")
    
    # Test batch with mix of valid format codes
    codes = ["BR", "US", "XX"]
    result = batch_get_risk_scores(codes)
    assert result["total"] == len(codes)
    assert "results" in result
    assert len(result["results"]) == len(codes)
    assert "timestamp" in result
    print(f"✓ Batch of {len(codes)} codes processed")
    
    print("✓ Batch endpoint tests passed!\n")


def test_response_structure():
    """Test that responses have the required structure."""
    print("Testing response structure...")
    
    result = get_risk_score_for_country("BR")
    
    # Required fields in response (either success or error)
    base_fields = ["country_code", "timestamp", "source_attribution"]
    for field in base_fields:
        assert field in result, f"Missing required field: {field}"
    
    print("✓ Response structure validated")
    print("✓ All response fields present!\n")


def main():
    """Run all smoke tests."""
    print("=" * 60)
    print("SMOKE TEST: Risk Score Endpoint")
    print("=" * 60 + "\n")
    
    try:
        test_endpoint_validation()
        test_batch_endpoint()
        test_response_structure()
        
        print("=" * 60)
        print("✓ ALL ENDPOINT SMOKE TESTS PASSED")
        print("=" * 60)
        print("\n⚠  Note: These tests validate structure and logic only.")
        print("⚠  Actual World Bank API calls require 'requests' library")
        print("⚠  and network access (tested separately).\n")
        return 0
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
