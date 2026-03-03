from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from datetime import datetime, timezone
from backend.src.api import (
    get_sample_payload,
    build_pricing_bands_response,
    build_pricing_quote,
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

    def do_GET(self):
        if self.path == '/health':
            self._send(200, {'status':'ok','service':'lf-worldbank-risk-pricing'})
            return
        if self.path == '/sample':
            payload=get_sample_payload()
            payload['transport']='http'
            payload['generatedAtHttp']=datetime.now(timezone.utc).isoformat()
            self._send(200,payload)
            return
        self._send(404, {'error':'not_found','path':self.path})

    def do_POST(self):
        try:
            body = self._read_body()
        except json.JSONDecodeError:
            self._send(400, {"error": "invalid_json"})
            return

        if self.path == "/v1/pricing/bands":
            entries = body.get("entries", [])
            if not isinstance(entries, list):
                self._send(400, {"error": "invalid_entries"})
                return
            self._send(200, build_pricing_bands_response(entries))
            return

        if self.path == "/v1/pricing/quote":
            country_code = body.get("countryCode")
            base_price = body.get("basePrice")
            risk_score = body.get("riskScore")
            currency = body.get("currency", "USD")
            if country_code in (None, "") or base_price is None or risk_score is None:
                self._send(400, {"error": "missing_required_fields"})
                return
            quote = build_pricing_quote(country_code, risk_score, base_price, currency=currency)
            quote["generatedAtHttp"] = datetime.now(timezone.utc).isoformat()
            self._send(200, quote)
            return

        self._send(404, {'error': 'not_found', 'path': self.path})


def run(host='0.0.0.0', port=8000):
    server = HTTPServer((host, port), Handler)
    print(f'Starting lf-worldbank-risk-pricing on {host}:{port}')
    server.serve_forever()

if __name__ == '__main__':
    run()
