"""Local, dependency-free browser console for the offline demo benchmark."""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .demo import DemoSystem
from .evaluators import default_evaluators
from .models import Scenario, Suite
from .runner import BenchmarkRunner

CONSOLE_HTML = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SystemBench local lab</title><style>body{font:16px system-ui;max-width:900px;margin:2rem auto;padding:0 1rem}input,button{font:inherit;padding:.6rem}pre{background:#f3f5f7;padding:1rem;overflow:auto}.note{border-left:4px solid #1769aa;padding:.8rem;background:#eef6ff}</style></head><body><h1>SystemBench local lab</h1><p class="note">Runs the bundled deterministic offline system. No model, account, API key, or database is used.</p><label>Trials per scenario <input id="trials" type="number" min="1" max="10" value="2"></label> <button id="run">Run benchmark</button><pre id="result" aria-live="polite">Ready.</pre><script>document.querySelector('#run').onclick=async()=>{const out=document.querySelector('#result');out.textContent='Running…';try{const response=await fetch('/api/run',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({trials:Number(document.querySelector('#trials').value)})});out.textContent=JSON.stringify(await response.json(),null,2)}catch(error){out.textContent=String(error)}};</script></body></html>"""


def demo_suite() -> Suite:
    return Suite(
        "browser-demo",
        "1",
        (
            Scenario(
                "sum",
                "Add synthetic integers",
                {"question": "Sum 12 and 30"},
                {"output": "42"},
                {"max_latency_ms": 1_000, "max_cost_usd": 0.01},
            ),
            Scenario(
                "fallback",
                "Exercise a synthetic retrieval failure",
                {"question": "Sum 4 and 5"},
                {"output": "9"},
                {"max_latency_ms": 1_000, "max_cost_usd": 0.01},
                failure_injection={"retrieval_unavailable": True},
            ),
        ),
    )


def run_demo(trials: int) -> dict[str, Any]:
    if isinstance(trials, bool) or not isinstance(trials, int) or not 1 <= trials <= 10:
        raise ValueError("trials must be an integer between 1 and 10")
    return BenchmarkRunner(DemoSystem(), default_evaluators()).run(
        demo_suite(), trials=trials, bootstrap_samples=200, bootstrap_seed=0
    )


class ConsoleHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path != "/":
            self.send_error(404)
            return
        self._send(200, CONSOLE_HTML, "text/html; charset=utf-8")

    def do_POST(self) -> None:
        if self.path != "/api/run":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("content-length", "0"))
            if length > 4096:
                raise ValueError("request is too large")
            body = json.loads(self.rfile.read(length))
            report = run_demo(body.get("trials", 2))
            self._send(200, json.dumps({"summary": report["summary"], "run_id": report["run_id"]}))
        except (ValueError, TypeError, json.JSONDecodeError) as error:
            self._send(400, json.dumps({"error": str(error)}))

    def log_message(self, format: str, *args: object) -> None:
        return

    def _send(self, status: int, body: str, content_type: str = "application/json") -> None:
        payload = body.encode()
        self.send_response(status)
        self.send_header("content-type", content_type)
        self.send_header("content-length", str(len(payload)))
        self.send_header("cache-control", "no-store")
        self.end_headers()
        self.wfile.write(payload)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local SystemBench browser lab")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), ConsoleHandler)
    print(f"SystemBench local lab: http://127.0.0.1:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
