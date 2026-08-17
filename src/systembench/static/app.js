const byId = (id) => document.getElementById(id);
let latestAnalysis = null;
let currentSession = null;

async function request(path, payload) {
  const response = await fetch(path, {
    method: payload ? "POST" : "GET",
    headers: payload ? { "content-type": "application/json" } : {},
    body: payload ? JSON.stringify(payload) : undefined,
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Request failed");
  return data;
}

function designPayload() {
  const form = byId("design-form");
  return {
    target_type: form.target_type.value,
    name: form.name.value,
    description: form.description.value,
    decision: form.decision.value,
    users: form.users.value,
    environment: form.environment.value,
    methods: [...form.querySelectorAll('input[name="methods"]:checked')].map((item) => item.value),
  };
}

function setBusy(button, busy, busyText, idleText) {
  button.disabled = busy;
  button.textContent = busy ? busyText : idleText;
}

function renderCoverage(items) {
  const root = byId("coverage-list");
  root.replaceChildren(...items.map((item) => {
    const wrapper = document.createElement("div");
    wrapper.className = "coverage-item";
    const label = document.createElement("div");
    label.className = "coverage-label";
    const name = document.createElement("span");
    name.textContent = item.construct;
    const value = document.createElement("span");
    value.textContent = `${item.coverage}%`;
    label.append(name, value);
    const track = document.createElement("div");
    track.className = "coverage-track";
    const fill = document.createElement("i");
    fill.style.width = `${item.coverage}%`;
    track.append(fill);
    wrapper.append(label, track);
    return wrapper;
  }));
}

function renderGaps(gaps) {
  const root = byId("gap-list");
  root.replaceChildren(...gaps.slice(0, 6).map((gap) => {
    const item = document.createElement("div");
    item.className = "finding";
    const heading = document.createElement("div");
    const dot = document.createElement("i");
    dot.className = `severity ${gap.severity}`;
    const title = document.createElement("strong");
    title.textContent = gap.area;
    heading.append(dot, title);
    const detail = document.createElement("p");
    detail.textContent = gap.detail;
    item.append(heading, detail);
    return item;
  }));
  if (!gaps.length) {
    const note = document.createElement("p");
    note.textContent = "No checklist gaps detected. Independent validity review is still required.";
    root.replaceChildren(note);
  }
}

function renderProbes(probes) {
  const root = byId("probe-list");
  root.replaceChildren(...probes.map((probe, index) => {
    const item = document.createElement("div");
    item.className = "probe-summary";
    const button = document.createElement("button");
    button.type = "button";
    const detailId = `probe-detail-${index + 1}`;
    const buttonId = `probe-toggle-${index + 1}`;
    button.id = buttonId;
    button.setAttribute("aria-controls", detailId);
    button.setAttribute("aria-expanded", "false");
    const number = document.createElement("span");
    number.textContent = String(index + 1).padStart(2, "0");
    const title = document.createElement("strong");
    title.textContent = probe.title;
    const dimension = document.createElement("small");
    dimension.textContent = probe.dimension;
    button.append(number, title, dimension);
    const detail = document.createElement("div");
    detail.id = detailId;
    detail.setAttribute("role", "region");
    detail.setAttribute("aria-labelledby", buttonId);
    detail.className = "probe-detail";
    detail.hidden = true;
    const success = document.createElement("p");
    success.textContent = `Success: ${probe.observable_success}`;
    const failure = document.createElement("p");
    failure.textContent = `Failure: ${probe.failure_signal}`;
    detail.append(success, failure);
    button.addEventListener("click", () => {
      detail.hidden = !detail.hidden;
      button.setAttribute("aria-expanded", String(!detail.hidden));
    });
    item.append(button, detail);
    return item;
  }));
}

function renderAnalysis(analysis) {
  latestAnalysis = analysis;
  byId("realism-score").textContent = analysis.realism_score;
  byId("score-ring").style.setProperty("--score", analysis.realism_score);
  byId("readiness").textContent = analysis.readiness;
  byId("score-summary").textContent = analysis.claim_boundary;
  renderCoverage(analysis.construct_coverage);
  renderGaps(analysis.gaps);
  renderProbes(analysis.recommended_probes);
  byId("baseline-plan").textContent = analysis.comparison_baseline;
  byId("statistical-plan").textContent = analysis.statistical_plan;
  byId("protocol-fingerprint").textContent = analysis.protocol_fingerprint;
  byId("analysis-results").hidden = false;
  byId("analysis-results").scrollIntoView({ behavior: "smooth", block: "start" });
}

byId("design-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = byId("analyze-button");
  setBusy(button, true, "Analyzing…", "Analyze benchmark design");
  byId("form-status").textContent = "Checking constructs, human interaction, budgets, failure paths, and evidence…";
  try {
    const analysis = await request("/api/analyze", designPayload());
    renderAnalysis(analysis);
    byId("form-status").textContent = `Analysis complete · ${analysis.gaps.length} evidence gaps found.`;
  } catch (error) {
    byId("form-status").textContent = `Unable to analyze: ${error.message}`;
  } finally {
    setBusy(button, false, "Analyzing…", "Analyze benchmark design");
  }
});

byId("complete-example").addEventListener("click", () => {
  const form = byId("design-form");
  for (const input of form.querySelectorAll('input[name="methods"]')) input.checked = true;
  byId("form-status").textContent = "Loaded a broader evidence plan. Analyze to review construct coverage.";
});

function download(name, data) {
  const blob = new Blob([`${JSON.stringify(data, null, 2)}\n`], { type: "application/json" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = name;
  link.click();
  URL.revokeObjectURL(link.href);
}

function analysisBrief(analysis) {
  return `# SystemBench protocol review\n\nTarget: ${analysis.protocol.target.name} (${analysis.protocol.target.type})\nDecision: ${analysis.protocol.decision}\nProtocol realism coverage: ${analysis.realism_score}/100 (${analysis.readiness})\nFingerprint: ${analysis.protocol_fingerprint}\n\n## Highest-priority gaps\n${analysis.gaps.map((gap) => `- [${gap.severity}] ${gap.area}: ${gap.detail}`).join("\n") || "- No checklist gaps; independent review remains required."}\n\n## Recommended probes\n${analysis.recommended_probes.map((probe) => `- ${probe.title}: ${probe.human_goal}`).join("\n")}\n\n## Boundaries\n${analysis.claim_boundary} Freeze the protocol before comparison and retain trial-level failures, human effort, traces, budgets, and uncertainty.\n`;
}

byId("download-analysis").addEventListener("click", () => {
  if (latestAnalysis) download("systembench-protocol.json", latestAnalysis);
});

byId("copy-analysis").addEventListener("click", async () => {
  if (!latestAnalysis) return;
  const button = byId("copy-analysis");
  try {
    await navigator.clipboard.writeText(analysisBrief(latestAnalysis));
    button.textContent = "Copied";
    setTimeout(() => { button.textContent = "Copy review brief"; }, 1400);
  } catch (error) {
    byId("form-status").textContent = `Copy unavailable: ${error.message}`;
  }
});

function showProbe(probe) {
  if (!probe) {
    const title = document.createElement("h3");
    title.textContent = "Planned probes complete";
    const note = document.createElement("p");
    note.textContent = "Export the session and conduct an independent validity review before drawing a conclusion.";
    byId("current-probe").replaceChildren(title, note);
    byId("record-observation").disabled = true;
    return;
  }
  byId("probe-dimension").textContent = probe.dimension;
  byId("probe-id").textContent = probe.id;
  byId("probe-title").textContent = probe.title;
  byId("probe-goal").textContent = probe.human_goal;
  byId("probe-setup").textContent = probe.setup;
  byId("probe-perturbation").textContent = probe.perturbation;
  byId("probe-success").textContent = probe.observable_success;
  byId("probe-failure").textContent = probe.failure_signal;
  byId("probe-evidence").textContent = probe.evidence.join(" · ");
}

function renderSession(session) {
  currentSession = session;
  showProbe(session.current_probe);
  const metrics = session.metrics;
  byId("metric-observations").textContent = metrics.observations;
  byId("metric-success").textContent = metrics.observations ? `${Math.round(metrics.task_success * 100)}%` : "—";
  byId("metric-ease").textContent = metrics.observations ? `${Math.round(metrics.mean_human_ease * 100)}%` : "—";
  byId("metric-calibration").textContent = metrics.observations ? `${Math.round(metrics.mean_calibration_gap * 100)}%` : "—";
  byId("adaptation-note").textContent = session.last_adaptation || "The next probe will respond to the first observation.";
  const history = byId("history-list");
  history.replaceChildren(...session.history.map((record) => {
    const row = document.createElement("div");
    row.className = "history-record";
    const probe = document.createElement("strong"); probe.textContent = record.probe_id;
    const outcome = document.createElement("span"); outcome.textContent = record.outcome;
    const effort = document.createElement("span"); effort.textContent = `effort ${record.human_effort}/5`;
    const gap = document.createElement("span"); gap.textContent = `calibration gap ${Math.round(record.calibration_gap * 100)}%`;
    row.append(probe, outcome, effort, gap);
    return row;
  }));
}

byId("start-session").addEventListener("click", async () => {
  try {
    const session = await request("/api/session/start", designPayload());
    renderSession(session);
    byId("session").hidden = false;
    byId("session").scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    byId("form-status").textContent = `Unable to start session: ${error.message}`;
  }
});

byId("human-effort").addEventListener("input", (event) => { byId("effort-output").textContent = event.target.value; });
byId("confidence").addEventListener("input", (event) => { byId("confidence-output").textContent = `${event.target.value}%`; });

byId("observation-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!currentSession) return;
  const button = byId("record-observation");
  setBusy(button, true, "Adapting…", "Record and adapt");
  try {
    const session = await request("/api/session/observe", {
      session: currentSession,
      observation: {
        outcome: byId("outcome").value,
        human_effort: Number(byId("human-effort").value),
        confidence: Number(byId("confidence").value) / 100,
        notes: byId("notes").value,
      },
    });
    renderSession(session);
    byId("session-status").textContent = session.last_adaptation;
    byId("notes").value = "";
  } catch (error) {
    byId("session-status").textContent = `Unable to record: ${error.message}`;
  } finally {
    setBusy(button, false, "Adapting…", "Record and adapt");
  }
});

byId("run-demo").addEventListener("click", async () => {
  const button = byId("run-demo");
  const output = byId("demo-result");
  setBusy(button, true, "Running…", "Run synthetic suite");
  output.textContent = "Running local deterministic scenarios…";
  try {
    const result = await request("/api/run", { trials: Number(byId("trials").value) });
    output.textContent = JSON.stringify(result, null, 2);
  } catch (error) {
    output.textContent = `Unable to run: ${error.message}`;
  } finally {
    setBusy(button, false, "Running…", "Run synthetic suite");
  }
});
