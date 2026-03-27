"""HTTP contract tests for the World Bank risk pricing server."""

from __future__ import annotations

import json
from contextlib import contextmanager
from http.server import HTTPServer
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from unittest.mock import patch

from backend.src.http_server import Handler


class QuietHandler(Handler):
    def log_message(self, format, *args):  # noqa: A003 - BaseHTTPRequestHandler API
        return


@contextmanager
def run_server():
    server = HTTPServer(("127.0.0.1", 0), QuietHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=1)


def request_json(url, method="GET", payload=None):
    headers = {}
    data = None
    if payload is not None:
        if isinstance(payload, bytes):
            data = payload
        else:
            data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=5) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def test_get_risk_score_route_success():
    payload = {
        "country_code": "BR",
        "risk_score": 5.23,
        "data_freshness": "2023",
        "source_attribution": "World Bank (CC BY 4.0)",
        "timestamp": "2026-03-22T00:00:00Z",
    }

    with patch("backend.src.http_server.get_risk_score_for_country", return_value=payload):
        with run_server() as server:
            status, result = request_json(
                f"http://127.0.0.1:{server.server_port}/v1/risk-score?country_code=BR"
            )

    assert status == 200
    assert result == payload


def test_get_risk_score_route_invalid_country():
    payload = {
        "error": "Invalid country code",
        "message": "Country code must be a 2-letter ISO code",
        "country_code": "BRA",
        "timestamp": "2026-03-22T00:00:00Z",
    }

    with patch("backend.src.http_server.get_risk_score_for_country", return_value=payload):
        with run_server() as server:
            status, result = request_json(
                f"http://127.0.0.1:{server.server_port}/v1/risk-score?country_code=BRA"
            )

    assert status == 400
    assert result == payload


def test_get_risk_score_route_not_available():
    payload = {
        "error": "Data not available",
        "message": "No risk data available for country: XX",
        "country_code": "XX",
        "source_attribution": "World Bank (CC BY 4.0)",
        "timestamp": "2026-03-22T00:00:00Z",
    }

    with patch("backend.src.http_server.get_risk_score_for_country", return_value=payload):
        with run_server() as server:
            status, result = request_json(
                f"http://127.0.0.1:{server.server_port}/v1/risk-score?country_code=XX"
            )

    assert status == 404
    assert result == payload


def test_batch_risk_score_route():
    payload = {
        "results": [
            {
                "country_code": "BR",
                "risk_score": 5.23,
                "data_freshness": "2023",
                "source_attribution": "World Bank (CC BY 4.0)",
                "timestamp": "2026-03-22T00:00:00Z",
            }
        ],
        "total": 1,
        "successful": 1,
        "failed": 0,
        "timestamp": "2026-03-22T00:00:00Z",
    }

    with patch("backend.src.http_server.batch_get_risk_scores", return_value=payload):
        with run_server() as server:
            status, result = request_json(
                f"http://127.0.0.1:{server.server_port}/v1/risk-score/batch",
                method="POST",
                payload={"country_codes": ["BR"]},
            )

    assert status == 200
    assert result == payload


def test_batch_risk_score_route_requires_list():
    with run_server() as server:
        status, result = request_json(
            f"http://127.0.0.1:{server.server_port}/v1/risk-score/batch",
            method="POST",
            payload={"country_codes": "BR"},
        )

    assert status == 400
    assert result["error"] == "missing_required_fields"


def test_batch_risk_score_route_rejects_invalid_json():
    with run_server() as server:
        status, result = request_json(
            f"http://127.0.0.1:{server.server_port}/v1/risk-score/batch",
            method="POST",
            payload=b"{",
        )

    assert status == 400
    assert result["error"] == "invalid_json"


def test_batch_risk_score_route_rejects_non_object_json():
    with run_server() as server:
        status, result = request_json(
            f"http://127.0.0.1:{server.server_port}/v1/risk-score/batch",
            method="POST",
            payload=[],
        )

    assert status == 400
    assert result["error"] == "invalid_payload"


def test_batch_risk_score_route_rejects_invalid_country_code_item():
    with run_server() as server:
        status, result = request_json(
            f"http://127.0.0.1:{server.server_port}/v1/risk-score/batch",
            method="POST",
            payload={"country_codes": ["BR", 123]},
        )

    assert status == 400
    assert result["error"] == "invalid_country_codes"


def test_batch_risk_score_route_normalizes_country_codes():
    payload = {
        "results": [
            {
                "country_code": "BR",
                "risk_score": 5.23,
                "data_freshness": "2025",
                "source_attribution": "World Bank (CC BY 4.0)",
                "timestamp": "2026-03-22T00:00:00Z",
            }
        ],
        "total": 1,
        "successful": 1,
        "failed": 0,
        "timestamp": "2026-03-22T00:00:00Z",
    }

    with patch("backend.src.http_server.batch_get_risk_scores", return_value=payload) as mock_batch:
        with run_server() as server:
            status, result = request_json(
                f"http://127.0.0.1:{server.server_port}/v1/risk-score/batch",
                method="POST",
                payload={"country_codes": ["br"]},
            )

    assert status == 200
    assert result == payload
    assert mock_batch.call_args.args[0] == ["BR"]
    assert mock_batch.call_args.kwargs["record_metrics"] is False
