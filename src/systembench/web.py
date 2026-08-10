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

CONSOLE_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light">
  <title>SystemBench · Local reliability lab</title>
  <style>
    :root{--ink:#18231f;--muted:#58645e;--line:#d7ded9;--paper:#f7f8f5;--panel:#fff;--accent:#245e4b;--accent-dark:#174535;--soft:#e9f1ed;--warn:#765b16;--focus:#b65c00}
    *{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
    a{color:var(--accent-dark)}a:focus-visible,button:focus-visible,input:focus-visible,summary:focus-visible{outline:3px solid var(--focus);outline-offset:3px}
    header{border-bottom:1px solid var(--line);background:rgba(255,255,255,.94)}.bar,main,footer{width:min(1040px,calc(100% - 2rem));margin:auto}.bar{min-height:68px;display:flex;align-items:center;justify-content:space-between;gap:1.5rem}.brand{display:flex;align-items:center;gap:.7rem;text-decoration:none;color:var(--ink);font-weight:720}.mark{width:30px;height:30px;border:2px solid var(--accent);border-radius:50%;position:relative}.mark:before,.mark:after{content:"";position:absolute;border:1px solid var(--accent);border-radius:50%;inset:5px}.mark:after{inset:10px;background:var(--accent)}nav{display:flex;gap:1rem;align-items:center}.status{font-size:.78rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--accent-dark)}
    main{padding:3.5rem 0 4.5rem}.eyebrow{color:var(--accent-dark);font-size:.78rem;font-weight:750;letter-spacing:.1em;text-transform:uppercase}h1{font-size:clamp(2rem,5vw,3.6rem);line-height:1.05;letter-spacing:-.035em;max-width:820px;margin:.55rem 0 1rem}h2{font-size:1.35rem;margin:0 0 .8rem}p{max-width:72ch}.lede{font-size:1.12rem;color:var(--muted);margin-bottom:2rem}.boundary{border-left:4px solid var(--warn);background:#f5f0df;padding:.9rem 1rem;margin:0 0 2rem;color:#4c421e}.grid{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(260px,.65fr);gap:1rem}.panel{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:1.35rem;box-shadow:0 1px 2px rgba(20,40,30,.04)}
    label{display:block;font-weight:680;margin-bottom:.45rem}input{width:100%;max-width:180px;border:1px solid #9ba8a1;border-radius:7px;padding:.68rem;background:#fff;color:var(--ink);font:inherit}.help{font-size:.9rem;color:var(--muted);margin:.4rem 0 1.2rem}.primary{border:0;border-radius:7px;background:var(--accent);color:#fff;padding:.75rem 1.15rem;font:inherit;font-weight:730;cursor:pointer}.primary:hover{background:var(--accent-dark)}button:disabled{opacity:.55;cursor:not-allowed}.secondary{border:1px solid var(--accent);border-radius:7px;background:#fff;color:var(--accent-dark);padding:.6rem .85rem;font:inherit;font-weight:680;cursor:pointer}.actions{display:flex;flex-wrap:wrap;gap:.65rem;margin-top:1rem}
    .method{margin-top:1rem}.method summary{cursor:pointer;font-weight:720;color:var(--accent-dark)}.method ul{padding-left:1.2rem;color:var(--muted)}.signals{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.65rem;margin-top:1rem}.signal{padding:.85rem;background:var(--soft);border-radius:8px}.signal strong{display:block;font-size:1.35rem}.signal span{font-size:.82rem;color:var(--muted)}pre{min-height:160px;margin:1rem 0 0;background:#17201c;color:#e7eee9;padding:1rem;border-radius:8px;overflow:auto;white-space:pre-wrap;word-break:break-word;font:13px/1.5 ui-monospace,SFMono-Regular,Consolas,monospace}.empty{color:var(--muted);font-size:.95rem}.trust{list-style:none;padding:0;margin:0}.trust li{padding:.55rem 0;border-bottom:1px solid var(--line)}.trust li:last-child{border:0}.trust strong{display:block}footer{border-top:1px solid var(--line);padding:1.5rem 0 2.5rem;color:var(--muted);font-size:.9rem;display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap}
    @media(max-width:720px){main{padding-top:2.3rem}.bar{align-items:flex-start;padding:.9rem 0;flex-direction:column;gap:.5rem}nav{width:100%;justify-content:space-between}.grid{grid-template-columns:1fr}.signals{grid-template-columns:1fr 1fr}h1{font-size:2.25rem}}
    @media(max-width:390px){.signals{grid-template-columns:1fr}.actions button{width:100%}}
    @media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
  </style>
</head>
<body>
  <header><div class="bar">
    <a class="brand" href="#top"><span class="mark" aria-hidden="true"></span><span>SystemBench</span></a>
    <nav aria-label="Project"><a href="#method">Method</a><a href="https://github.com/manufaujdar/systembench">Source</a><span class="status">Local only</span></nav>
  </div></header>
  <main id="top">
    <div class="eyebrow">Offline reliability lab</div>
    <h1>Evaluate the system around the model.</h1>
    <p class="lede">Run a small, deterministic suite to see how SystemBench preserves outcomes, failures, resource use, repeated-trial reliability, and uncertainty.</p>
    <p class="boundary"><strong>Research demonstration.</strong> A pass here validates only this synthetic protocol and bundled demo system. It does not certify an AI model or prove safety, fairness, compliance, or production readiness.</p>
    <div class="grid">
      <section class="panel" aria-labelledby="run-title">
        <h2 id="run-title">Run the demonstration</h2>
        <label for="trials">Trials per scenario</label>
        <input id="trials" type="number" min="1" max="10" step="1" value="2" inputmode="numeric" aria-describedby="trial-help">
        <p class="help" id="trial-help">Two synthetic scenarios are repeated 1–10 times. More trials show repeatability; they do not add scenario diversity.</p>
        <button class="primary" id="run" type="button">Run benchmark</button>
        <div class="signals" aria-label="Latest result summary">
          <div class="signal"><strong id="pass-rate">—</strong><span>Pass rate</span></div>
          <div class="signal"><strong id="reliability">—</strong><span>Reliability@N</span></div>
          <div class="signal"><strong id="errors">—</strong><span>Error rate</span></div>
          <div class="signal"><strong id="latency">—</strong><span>Mean latency</span></div>
        </div>
        <pre id="result" aria-live="polite">Ready. No result is stored.</pre>
        <div class="actions">
          <button class="secondary" id="download" type="button" disabled>Download result</button>
          <button class="secondary" id="copy" type="button" disabled>Copy review brief</button>
        </div>
      </section>
      <aside class="panel" aria-labelledby="boundary-title">
        <h2 id="boundary-title">What this lab does</h2>
        <ul class="trust">
          <li><strong>Local execution</strong>No model, account, API key, or database is used.</li>
          <li><strong>Observable evidence</strong>Results include failures, traces, evaluator evidence, latency, and cost.</li>
          <li><strong>Declared uncertainty</strong>Confidence intervals resample scenarios as clusters.</li>
          <li><strong>No persistence</strong>Refresh the page and the displayed result is gone.</li>
        </ul>
        <details class="method" id="method">
          <summary>Method and limitations</summary>
          <ul>
            <li>One arithmetic task checks the normal route.</li>
            <li>One task injects a synthetic retrieval failure and checks fallback evidence.</li>
            <li>The suite is too small and artificial for model or product claims.</li>
            <li>Use the CLI with a frozen, representative suite for real system evaluation.</li>
          </ul>
        </details>
      </aside>
    </div>
  </main>
  <footer><span>SystemBench 0.1.1 · Research software · Apache-2.0</span><span>Provider-neutral · Synthetic demo · Reviewable evidence</span></footer>
  <script>
    const byId=id=>document.getElementById(id);let latest=null;
    const percent=value=>`${(Number(value)*100).toFixed(1)}%`;
    function brief(data){const s=data.summary;return `# SystemBench review brief\n\n- Run: ${data.run_id}\n- Protocol: bundled synthetic offline demo\n- Pass rate: ${percent(s.pass_rate)}\n- Reliability@N: ${percent(s.reliability_at_n)}\n- Error rate: ${percent(s.error_rate)}\n- Mean latency: ${Number(s.mean_latency_ms).toFixed(2)} ms\n- Trials: ${s.trial_count}\n\nBoundary: This result does not certify a model or prove safety, fairness, compliance, equivalence, or production readiness. Review the frozen protocol, trial evidence, uncertainty, slices, failures, budgets, and manifests before drawing conclusions.\n`;}
    byId('run').addEventListener('click',async()=>{const button=byId('run'),out=byId('result');button.disabled=true;button.textContent='Running…';out.textContent='Running the local synthetic suite…';try{const response=await fetch('/api/run',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({trials:Number(byId('trials').value)})});const data=await response.json();if(!response.ok)throw new Error(data.error||'Benchmark request failed');latest=data;const s=data.summary;byId('pass-rate').textContent=percent(s.pass_rate);byId('reliability').textContent=percent(s.reliability_at_n);byId('errors').textContent=percent(s.error_rate);byId('latency').textContent=`${Number(s.mean_latency_ms).toFixed(2)} ms`;out.textContent=JSON.stringify(data,null,2);byId('download').disabled=false;byId('copy').disabled=false}catch(error){latest=null;out.textContent=`Unable to run: ${error.message||String(error)}`}finally{button.disabled=false;button.textContent='Run benchmark'}});
    byId('download').addEventListener('click',()=>{if(!latest)return;const blob=new Blob([JSON.stringify(latest,null,2)+'\\n'],{type:'application/json'}),link=document.createElement('a');link.href=URL.createObjectURL(blob);link.download=`${latest.run_id}-summary.json`;link.click();URL.revokeObjectURL(link.href)});
    byId('copy').addEventListener('click',async()=>{if(!latest)return;const button=byId('copy');try{await navigator.clipboard.writeText(brief(latest));button.textContent='Copied';setTimeout(()=>button.textContent='Copy review brief',1400)}catch(error){byId('result').textContent+=`\n\nCopy unavailable: ${error.message||String(error)}`}});
  </script>
</body>
</html>"""


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
        self.send_header("content-security-policy", "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")
        self.send_header("x-content-type-options", "nosniff")
        self.send_header("referrer-policy", "no-referrer")
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
