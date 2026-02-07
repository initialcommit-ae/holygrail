"use client";

import {
  SandpackCodeEditor,
  SandpackLayout,
  SandpackPreview,
  SandpackProvider,
} from "@codesandbox/sandpack-react";
import { useMemo, useState } from "react";

type AnalyzeResponse =
  | {
      ok: true;
      tsx: string;
      data: unknown;
      model: string;
    }
  | {
      detail?: unknown;
    };

function getBackendUrl(): string {
  return process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
}

export default function AnalyticsPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tsx, setTsx] = useState<string | null>(null);
  const [data, setData] = useState<unknown>(null);

  const backendUrl = getBackendUrl();

  async function generate() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${backendUrl}/analyze`, { method: "GET" });
      const json = (await res.json()) as AnalyzeResponse;
      if (!res.ok || !("ok" in json) || json.ok !== true) {
        throw new Error(
          `Analyze failed: ${res.status} ${res.statusText}\n${JSON.stringify(
            json,
            null,
            2,
          )}`,
        );
      }

      setTsx(json.tsx);
      setData(json.data);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setTsx(null);
      setData(null);
    } finally {
      setLoading(false);
    }
  }

  const files = useMemo(() => {
    if (!tsx) return null;

    const safeDataJson = JSON.stringify(data ?? null, null, 2);

    return {
      "/Report.tsx": tsx,
      "/App.tsx": `import React from "react";
import Report from "./Report";

(globalThis as any).React = React;

const data = ${safeDataJson} as any;

export default function App() {
  return <Report data={data} />;
}
`,
      "/index.tsx": `import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";

const rootEl = document.getElementById("root");
if (!rootEl) throw new Error("Missing #root");
createRoot(rootEl).render(<App />);
`,
    };
  }, [tsx, data]);

  return (
    <div style={{ padding: 24, display: "grid", gap: 12 }}>
      <h1 style={{ fontSize: 20, fontWeight: 600 }}>Analytics report</h1>

      <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
        <button
          onClick={generate}
          disabled={loading}
          style={{
            padding: "10px 14px",
            borderRadius: 8,
            border: "1px solid #ccc",
            background: loading ? "#eee" : "white",
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "Generating…" : "Generate report"}
        </button>
        <div style={{ opacity: 0.8, fontSize: 13 }}>
          Backend: <code>{backendUrl}</code>
        </div>
      </div>

      <div style={{ opacity: 0.85, fontSize: 13 }}>
        Note: this executes AI-generated code inside an isolated preview. Treat it
        as untrusted.
      </div>

      {error ? (
        <pre
          style={{
            padding: 12,
            borderRadius: 8,
            background: "#fff5f5",
            border: "1px solid #f3c2c2",
            color: "#7a1a1a",
            whiteSpace: "pre-wrap",
          }}
        >
          {error}
        </pre>
      ) : null}

      {tsx ? (
        <details style={{ opacity: 0.9 }}>
          <summary style={{ cursor: "pointer" }}>Raw TSX (generated)</summary>
          <pre style={{ whiteSpace: "pre-wrap" }}>{tsx}</pre>
        </details>
      ) : null}

      {!files ? (
        <div style={{ opacity: 0.7 }}>No report yet. Click “Generate report”.</div>
      ) : (
        <SandpackProvider
          template="react-ts"
          files={files}
          options={{
            recompileMode: "immediate",
            recompileDelay: 200,
          }}
        >
          <SandpackLayout style={{ border: "1px solid #e5e5e5", borderRadius: 8 }}>
            <SandpackCodeEditor style={{ height: 520 }} showLineNumbers />
            <SandpackPreview style={{ height: 520 }} />
          </SandpackLayout>
        </SandpackProvider>
      )}
    </div>
  );
}

