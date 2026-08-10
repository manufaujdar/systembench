"""Local, dependency-free browser workbench and JSON API."""

from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from typing import Any
from urllib.parse import urlsplit

from .demo import DemoSystem
from .evaluators import default_evaluators
from .integrity import strict_json_dumps, strict_json_loads
from .interaction import analyze_design, catalog, observe_session, start_session
from .models import Scenario, Suite
from .runner import BenchmarkRunner


def _static(name: str) -> str:
    return files("systembench").joinpath("static").joinpath(name).read_text(encoding="utf-8")


CONSOLE_HTML = _static("index.html")
CONSOLE_CSS = _static("styles.css")
CONSOLE_JS = _static("app.js")


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


def api_response(path: str, body: dict[str, Any]) -> dict[str, Any]:
    """Dispatch a validated API request without coupling tests to HTTP transport."""

    if path == "/api/run":
        report = run_demo(body.get("trials", 2))
        return {"summary": report["summary"], "run_id": report["run_id"]}
    if path == "/api/analyze":
        return analyze_design(body)
    if path == "/api/session/start":
        return start_session(body)
    if path == "/api/session/observe":
        return observe_session(body)
    raise KeyError(path)


class ConsoleHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        path = urlsplit(self.path).path
        static_routes = {
            "/": (CONSOLE_HTML, "text/html; charset=utf-8"),
            "/styles.css": (CONSOLE_CSS, "text/css; charset=utf-8"),
            "/app.js": (CONSOLE_JS, "text/javascript; charset=utf-8"),
        }
        if path in static_routes:
            body, content_type = static_routes[path]
            self._send(200, body, content_type)
            return
        if path == "/api/catalog":
            self._send_json(200, catalog())
            return
        self.send_error(404)

    def do_POST(self) -> None:
        path = urlsplit(self.path).path
        try:
            length = int(self.headers.get("content-length", "0"))
            if not 0 < length <= 131_072:
                raise ValueError("request size must be between 1 byte and 128 KiB")
            raw = self.rfile.read(length).decode("utf-8")
            body = strict_json_loads(raw)
            if not isinstance(body, dict):
                raise TypeError("request body must be a JSON object")
            self._send_json(200, api_response(path, body))
        except KeyError:
            self._send_json(404, {"error": "unknown API route"})
        except (UnicodeDecodeError, ValueError, TypeError) as error:
            self._send_json(400, {"error": str(error)})

    def log_message(self, format: str, *args: object) -> None:
        return

    def _send_json(self, status: int, body: dict[str, Any]) -> None:
        self._send(status, strict_json_dumps(body), "application/json; charset=utf-8")

    def _send(self, status: int, body: str, content_type: str) -> None:
        payload = body.encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", content_type)
        self.send_header("content-length", str(len(payload)))
        self.send_header("cache-control", "no-store")
        self.send_header(
            "content-security-policy",
            "default-src 'none'; style-src 'self'; script-src 'self'; "
            "connect-src 'self'; img-src 'self' data:; base-uri 'none'; "
            "form-action 'none'; frame-ancestors 'none'",
        )
        self.send_header("x-content-type-options", "nosniff")
        self.send_header("referrer-policy", "no-referrer")
        self.send_header("cross-origin-opener-policy", "same-origin")
        self.end_headers()
        self.wfile.write(payload)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local SystemBench interaction workbench")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    if not 1 <= args.port <= 65_535:
        parser.error("port must be between 1 and 65535")
    server = ThreadingHTTPServer(("127.0.0.1", args.port), ConsoleHandler)
    print(f"SystemBench workbench: http://127.0.0.1:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
