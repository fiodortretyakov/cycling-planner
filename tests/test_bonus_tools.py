import pytest
from unittest.mock import patch, MagicMock
from src.tools.poi import get_points_of_interest, POIRequest
from src.tools.visa import check_visa_requirements, VisaRequest
from src.tools.budget import estimate_budget, BudgetRequest


@patch('src.tools.poi.httpx.Client')
def test_poi_returns_results(mock_client):
    """Test POI returns results with mocked API calls."""
    mock_response = MagicMock()
    mock_response.json.return_value = []
    mock_response.raise_for_status = MagicMock()
    
    mock_http = MagicMock()
    mock_http.get.return_value = mock_response
    mock_http.post.return_value = mock_response
    mock_http.__enter__.return_value = mock_http
    mock_http.__exit__.return_value = None
    mock_client.return_value = mock_http
    
    req = POIRequest(location="Amsterdam")
    result = get_points_of_interest(req)
    assert len(result) > 0
    assert result[0].name
    assert result[0].location


def test_visa_schengen_travel():
    """Test visa requirements for Schengen travel."""
    req = VisaRequest(citizenship="Netherlands", destinations=["Germany", "Denmark"])
    result = check_visa_requirements(req)
    assert result.requires_visa is False
    assert "Schengen" in result.notes


def test_visa_us_to_europe():
    """Test visa requirements for US citizen to Europe."""
    req = VisaRequest(citizenship="USA", destinations=["France", "Italy"])
    result = check_visa_requirements(req)
    assert result.requires_visa is False
    assert "90 days" in result.notes


def test_visa_unknown_country():
    """Test visa requirements for unknown scenario."""
    req = VisaRequest(citizenship="Unknown", destinations=["Mars"])
    result = check_visa_requirements(req)
    assert result.requires_visa is True
    assert "check" in result.notes.lower()


def test_budget_estimation():
    """Test budget estimation with accommodation mix."""
    req = BudgetRequest(
        days=7,
        accommodation_mix={"camping": 0.5, "hostel": 0.3, "hotel": 0.2},
        country="Netherlands"
    )
    result = estimate_budget(req)
    assert result.estimated_total_eur > 0
    assert "accommodation" in result.breakdown
    assert "food" in result.breakdown
    assert result.breakdown["daily_average"] > 0


def test_budget_norway_expensive():
    """Test that Norway budget is more expensive than Spain."""
    req_norway = BudgetRequest(
        days=5,
        accommodation_mix={"camping": 1.0},
        country="Norway"
    )
    req_spain = BudgetRequest(
        days=5,
        accommodation_mix={"camping": 1.0},
        country="Spain"
    )
    
    result_norway = estimate_budget(req_norway)
    result_spain = estimate_budget(req_spain)
    
    assert result_norway.estimated_total_eur > result_spain.estimated_total_eur
