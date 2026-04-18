import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from datetime import datetime, timezone
from time import perf_counter
from urllib.parse import parse_qs, urlparse

from backend.src.api import (
    get_sample_payload,
    build_pricing_bands_response,
    build_pricing_quote,
    is_valid_country_code,
)
from backend.src.risk_score_endpoint import (
    batch_get_risk_scores,
    get_risk_score_for_country,
)
from backend.src.worldbank_governance import (
    record_http_request,
    record_validation_failure,
)

class Handler(BaseHTTPRequestHandler):
    def _send(self, code, payload):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode('utf-8'))

    def _read_body(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length <= 0:
            return {}
        body = self.rfile.read(content_length)
        return json.loads(body.decode('utf-8'))

    def _send_risk_score_response(self, payload):
        status = 200
        error = payload.get("error")
        if error == "Invalid country code":
            status = 400
        elif error == "Data not available":
            status = 404
        self._send(status, payload)

    def _handle_risk_score(self, query_params):
        country_code = query_params.get("country_code", [""])[0].strip()
        if not country_code:
            record_validation_failure("GET /v1/risk-score", "missing_required_fields")
            self._send(400, {
                "error": "missing_required_fields",
                "message": "country_code is required",
            })
            return 400

        result = get_risk_score_for_country(country_code, record_metrics=False)
        self._send_risk_score_response(result)
        if result.get("error") == "Invalid country code":
            return 400
        if result.get("error") == "Data not available":
            return 404
        return 200

    def _handle_risk_score_batch(self, body):
        country_codes = body.get("country_codes")
        if not isinstance(country_codes, list):
            record_validation_failure("POST /v1/risk-score/batch", "missing_required_fields")
            self._send(400, {
                "error": "missing_required_fields",
                "message": "country_codes must be provided as a list",
            })
            return 400

        normalized_codes = []
        for code in country_codes:
            if not is_valid_country_code(code):
                record_validation_failure("POST /v1/risk-score/batch", "invalid_country_codes")
                self._send(400, {
                    "error": "invalid_country_codes",
                    "message": "country_codes must contain only 2-letter ISO codes",
                })
                return 400
            normalized_codes.append(str(code).strip().upper())

        self._send(200, batch_get_risk_scores(normalized_codes, record_metrics=False))
        return 200

    def do_GET(self):
        started_at = perf_counter()
        parsed = urlparse(self.path)
        path = parsed.path
        query_params = parse_qs(parsed.query)
        endpoint = f"GET {path}"
        status = 404

        try:
            if path == '/health':
                status = 200
                self._send(200, {'status':'ok','service':'lf-worldbank-risk-pricing'})
                return
            if path == '/sample':
                payload=get_sample_payload()
                payload['transport']='http'
                payload['generatedAtHttp']=datetime.now(timezone.utc).isoformat()
                status = 200
                self._send(200,payload)
                return
            if path == '/v1/risk-score':
                status = self._handle_risk_score(query_params)
                return
            status = 404
            self._send(404, {'error':'not_found','path':path})
        finally:
            record_http_request(endpoint, status, perf_counter() - started_at)

    def do_POST(self):
        started_at = perf_counter()
        try:
            body = self._read_body()
        except json.JSONDecodeError:
            parsed = urlparse(self.path)
            endpoint = f"POST {parsed.path}"
            record_validation_failure(endpoint, "invalid_json")
            self._send(400, {"error": "invalid_json"})
            record_http_request(endpoint, 400, perf_counter() - started_at)
            return

        parsed = urlparse(self.path)
        path = parsed.path
        endpoint = f"POST {path}"
        status = 404

        if not isinstance(body, dict):
            record_validation_failure(endpoint, "invalid_payload")
            self._send(400, {"error": "invalid_payload", "message": "JSON body must be an object"})
            record_http_request(endpoint, 400, perf_counter() - started_at)
            return

        try:
            if path == "/v1/risk-score/batch":
                status = self._handle_risk_score_batch(body)
                return

            if path == "/v1/pricing/bands":
                entries = body.get("entries", [])
                if not isinstance(entries, list):
                    record_validation_failure(endpoint, "invalid_entries")
                    status = 400
                    self._send(400, {"error": "invalid_entries"})
                    return
                status = 200
                self._send(200, build_pricing_bands_response(entries))
                return

            if path == "/v1/pricing/quote":
                country_code = body.get("countryCode")
                base_price = body.get("basePrice")
                risk_score = body.get("riskScore")
                currency = body.get("currency", "USD")
                if country_code in (None, "") or base_price is None or risk_score is None:
                    record_validation_failure(endpoint, "missing_required_fields")
                    status = 400
                    self._send(400, {"error": "missing_required_fields"})
                    return
                quote = build_pricing_quote(country_code, risk_score, base_price, currency=currency)
                quote["generatedAtHttp"] = datetime.now(timezone.utc).isoformat()
                status = 200
                self._send(200, quote)
                return

            status = 404
            self._send(404, {'error': 'not_found', 'path': path})
        finally:
            record_http_request(endpoint, status, perf_counter() - started_at)


def run(host="0.0.0.0", port=None):
    port = port or int(os.environ.get("PORT", 8000))
    server = HTTPServer((host, port), Handler)
    print(f'Starting lf-worldbank-risk-pricing on {host}:{port}')
    server.serve_forever()

if __name__ == '__main__':
    run()
