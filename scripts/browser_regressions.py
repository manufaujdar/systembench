"""Synthetic Chromium regressions; all API traffic is intercepted and local."""

import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def fixture(browser, assets, blocked_storage=False):
    page = browser.new_page(viewport={"width": 1280, "height": 800}, reduced_motion="reduce")
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    if blocked_storage:
        page.add_init_script(
            "Object.defineProperty(window, 'localStorage', {get(){throw new DOMException('Synthetic denied storage', 'SecurityError')}})"
        )

    def route(request):
        from urllib.parse import urlparse

        url = urlparse(request.request.url)
        if url.hostname != "synthetic.test":
            request.abort()
        elif url.path in assets:
            kind = (
                "text/css"
                if url.path.endswith(".css")
                else "text/javascript"
                if url.path.endswith(".js")
                else "text/html"
            )
            body = assets[url.path] + (
                ";window.__syntheticAppReady=true;" if url.path.endswith(".js") else ""
            )
            request.fulfill(body=body, content_type=kind)
        elif url.path.startswith("/v1/"):
            request.fulfill(json={"execution_mode": "mock", "runtime_credentials_allowed": False})
        else:
            request.abort()

    page.route("**/*", route)
    page.goto("https://synthetic.test/")
    page.wait_for_function("window.__syntheticAppReady === true")
    return page, errors


def run(browser):
    base = ROOT / "src/systembench/static"
    page, errors = fixture(
        browser,
        {
            "/": (base / "index.html").read_text(),
            "/styles.css": (base / "styles.css").read_text(),
            "/app.js": (base / "app.js").read_text(),
        },
    )
    calls = page.evaluate(
        "()=>{window.motionCalls=[]; HTMLElement.prototype.scrollIntoView=function(options){motionCalls.push(options)};renderAnalysis({realism_score:0,readiness:'Synthetic',claim_boundary:'Synthetic fixture only',construct_coverage:[],gaps:[],recommended_probes:[],comparison_baseline:'Synthetic',statistical_plan:'Synthetic',protocol_fingerprint:'synthetic'});return motionCalls}"
    )
    assert calls and calls[-1].get("behavior") != "smooth"
    assert not errors, errors
    page.close()


if __name__ == "__main__":
    with sync_playwright() as playwright:
        options = {"headless": True}
        if os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH"):
            options["executable_path"] = os.environ["PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH"]
        browser = playwright.chromium.launch(**options)
        try:
            run(browser)
            print("Synthetic browser regressions passed")
        finally:
            browser.close()
