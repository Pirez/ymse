from unittest.mock import MagicMock, patch

import pytest
import requests

from ymse.doffin import search_doffin


def _make_response(hits, raise_for_status=None):
    resp = MagicMock()
    resp.json.return_value = {"hits": hits}
    if raise_for_status:
        resp.raise_for_status.side_effect = raise_for_status
    else:
        resp.raise_for_status.return_value = None
    return resp


SAMPLE_HIT = {
    "id": "abc123",
    "heading": "Test Notice",
    "description": "A test description",
    "buyer": [{"name": "Test Buyer"}],
    "type": "COMPETITION",
    "issueDate": "2026-03-01T00:00:00",
    "estimatedValue": {"amount": 500000, "currencyCode": "NOK"},
}


@patch("ymse.doffin.requests.get")
def test_single_query(mock_get):
    mock_get.return_value = _make_response([SAMPLE_HIT])

    results = search_doffin("IT-tjenester", days=7, api_key="test-key")

    assert len(results) == 1
    r = results[0]
    assert r["id"] == "abc123"
    assert r["title"] == "Test Notice"
    assert r["buyer"] == "Test Buyer"
    assert r["type"] == "COMPETITION"
    assert r["published"] == "2026-03-01"
    assert r["value"] == 500000
    assert r["currency"] == "NOK"
    assert r["url"] == "https://doffin.no/notices/abc123"
    assert r["query"] == "IT-tjenester"


@patch("ymse.doffin.requests.get")
def test_multiple_queries_combined(mock_get):
    mock_get.return_value = _make_response([SAMPLE_HIT])

    results = search_doffin(
        ["IT-tjenester", "renholdsutstyr"], days=7, api_key="test-key"
    )

    assert len(results) == 2
    assert results[0]["query"] == "IT-tjenester"
    assert results[1]["query"] == "renholdsutstyr"


@patch("ymse.doffin.requests.get")
def test_autopagination(mock_get):
    page1_hits = [dict(SAMPLE_HIT, id=f"id{i}") for i in range(3)]
    page2_hits = [dict(SAMPLE_HIT, id="last")]

    mock_get.side_effect = [
        _make_response(page1_hits),
        _make_response(page2_hits),
    ]

    results = search_doffin("consulting", days=7, api_key="test-key", page_size=3)

    assert len(results) == 4
    assert mock_get.call_count == 2
    assert mock_get.call_args_list[0][1]["params"]["page"] == 1
    assert mock_get.call_args_list[1][1]["params"]["page"] == 2


@patch("ymse.doffin.requests.get")
def test_days_param_sets_date(mock_get):
    from datetime import datetime, timedelta

    mock_get.return_value = _make_response([])

    search_doffin("query", days=14, api_key="test-key")

    params = mock_get.call_args[1]["params"]
    expected = (datetime.today() - timedelta(days=14)).strftime("%Y-%m-%d")
    assert params["issueDateFrom"] == expected


def test_missing_api_key_raises(monkeypatch):
    monkeypatch.delenv("DOFFIN_API_KEY", raising=False)

    with pytest.raises(KeyError):
        search_doffin("query")


@patch("ymse.doffin.requests.get")
def test_http_error_propagates(mock_get):
    resp = MagicMock()
    resp.raise_for_status.side_effect = requests.HTTPError("403 Forbidden")
    mock_get.return_value = resp

    with pytest.raises(requests.HTTPError):
        search_doffin("query", api_key="bad-key")


@patch("ymse.doffin.requests.get")
def test_empty_results(mock_get):
    mock_get.return_value = _make_response([])

    results = search_doffin("nothing", api_key="test-key")

    assert results == []


@patch("ymse.doffin.requests.get")
def test_max_results_cap(mock_get):
    # Always return page_size hits so pagination continues
    mock_get.return_value = _make_response(
        [dict(SAMPLE_HIT, id=f"id{i}") for i in range(10)]
    )

    results = search_doffin("query", api_key="test-key", page_size=10, max_results=25)

    assert len(results) == 25
    assert mock_get.call_count == 3
