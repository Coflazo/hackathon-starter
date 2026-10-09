"use client";

import { useState } from "react";

type Result = { output?: string; source?: "live" | "fixture"; error?: string };

export default function DemoPath() {
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<Result | null>(null);

  async function run(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setResult(null);
    try {
      const res = await fetch("/api/demo", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input }),
      });
      setResult(await res.json());
    } catch {
      setResult({ error: "Network error. The demo fixture still works with DEMO_MODE=1." });
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="page">
      <h1>Demo path</h1>
      <p className="muted">Replace this page with the one flow the judges will see.</p>
      <form onSubmit={run} className="form">
        <label htmlFor="input">Input</label>
        <textarea
          id="input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          rows={3}
          required
          aria-describedby={result?.error ? "input-error" : undefined}
        />
        <button type="submit" disabled={busy}>
          {busy ? "Running..." : "Run"}
        </button>
      </form>
      {result?.error && (
        <p id="input-error" role="alert" className="error">
          {result.error}
        </p>
      )}
      {result?.output && (
        <section className="output" aria-live="polite">
          {result.source === "fixture" && <span className="badge">Sample data</span>}
          <p data-testid="output">{result.output}</p>
        </section>
      )}
    </main>
  );
}
