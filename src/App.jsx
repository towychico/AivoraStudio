import { lazy, Suspense, useEffect, useRef, useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import {
 Button,
 Card,
 CardHeader,
 CardTitle,
 CardContent,
} from "@siberui/react";
import styles from "./App.module.css";
const baseline = import.meta.env.MODE === "textarea";
const MonacoInput = baseline ? null : lazy(() => import("./MonacoInput.jsx"));
const A = "def square(x):\n    return x * x",
    B = "def calculate(n):\n    return n ** 2";
const pct = (x) => `${(x * 100).toFixed(2)}%`;
function PlainInput({ id, label, value, onChange, onReady }) {
 useEffect(() => {
  onReady(id);
 }, [id, onReady]);
 return (
     <textarea
         className={styles.input}
         aria-label={label}
         spellCheck={false}
         value={value}
         onChange={(e) => onChange(e.target.value)}
     />
 );
}
export default function App() {
 const [original, setOriginal] = useState(A),
     [comparison, setComparison] = useState(B),
     [result, setResult] = useState(null),
     [loading, setLoading] = useState(false),
     [error, setError] = useState(null);
 const revision = useRef(0),
     ready = useRef(new Set()),
     marked = useRef(false),
     busy = useRef(false);
 function onReady(id) {
  ready.current.add(id);
  if (ready.current.size === 2 && !marked.current) {
   marked.current = true;
   Promise.resolve(document.fonts?.ready).then(() =>
       requestAnimationFrame(() =>
           requestAnimationFrame(() =>
               invoke("benchmark_ready", {
                variant: baseline ? "textarea" : "monaco",
               }).catch(() => {})
           )
       )
   );
  }
 }
 function change(set, value) {
  revision.current++;
  set(value);
  setResult(null);
  setError(null);
 }
 async function compare() {
  if (busy.current || !original.trim() || !comparison.trim()) return;
  const r = revision.current;
  busy.current = true;
  setLoading(true);
  setResult(null);
  setError(null);
  try {
   const data = await invoke("compare_python", { original, comparison });
   if (r === revision.current) setResult(data);
  } catch (e) {
   if (r === revision.current)
    setError(
        typeof e === "string" ? e : e?.message || "No fue posible comparar."
    );
  } finally {
   busy.current = false;
   setLoading(false);
  }
 }
 const Input = baseline ? PlainInput : MonacoInput;
 return (
     <main className={styles.shell}>
      <nav className={styles.topbar}>
       <div className={styles.brand}>
        <img src="/brand/aivora-pink.svg" alt="Aivora AI" />
        <span>
            Aivora<span className={styles.brandAI}> AI.</span>
            <small>STUDIO / 01</small>
          </span>
       </div>
       <div className={styles.local}>
        <span className={styles.dot} /> LOCAL INFERENCE{" "}
        <span className={styles.divider}>//</span> PYTHON
       </div>
      </nav>
      <div className={styles.workspace}>
       <header className={styles.titleContainer}>
        <div>
         <p className={styles.eyebrow}>
          01 / WORKSPACE — SOURCE INTELLIGENCE
         </p>
         <h1>
          Similarity analysis<span>.</span>
         </h1>
         <p className={styles.subtitle}>
          Compare Python source code. Your intelligence stays on your
          device.
         </p>
        </div>
        <div className={styles.index}>
         01<span>↘</span>
        </div>
       </header>
       <section
           className={styles.editorContainer}
           aria-label="Código a comparar"
       >
        {[
         {
          id: "original",
          n: "01",
          label: "Original Text",
          value: original,
          set: setOriginal,
         },
         {
          id: "comparison",
          n: "02",
          label: "Text to Compare",
          value: comparison,
          set: setComparison,
         },
        ].map((e) => (
            <Card key={e.id} className={styles.workspaceCard}>
             <CardHeader className={styles.panelHeader}>
              <div>
               <p className={styles.panelMeta}>{e.n} / SOURCE</p>
               <CardTitle className={styles.panelTitle}>{e.label}</CardTitle>
              </div>
              <span className={styles.file}>{e.id}.py</span>
             </CardHeader>
             <CardContent className={styles.editorContent}>
              <Suspense
                  fallback={
                   <div className={styles.loading}>
                    INITIALIZING LOCAL EDITOR…
                   </div>
                  }
              >
               <Input
                   id={e.id}
                   label={e.label}
                   value={e.value}
                   onChange={(v) => change(e.set, v)}
                   onReady={onReady}
               />
              </Suspense>
             </CardContent>
             <div className={styles.editorFooter}>
              PYTHON / UTF-8{" "}
              <span>{new TextEncoder().encode(e.value).length} B</span>
             </div>
            </Card>
        ))}
       </section>
       <div className={styles.actions}>
          <span>
            ENGINE_01 / {baseline ? "TEXTAREA BASELINE" : "MONACO LOCAL"} / NO
            CODE EXECUTION
          </span>
        <Button
            className={styles.run}
            variant="primary"
            size="lg"
            disabled={loading || !original.trim() || !comparison.trim()}
            onClick={compare}
        >
         {loading ? "Analyzing…" : "Run analysis"}{" "}
         <span aria-hidden="true">↗</span>
        </Button>
       </div>
       <section
           className={styles.results}
           aria-live="polite"
           aria-busy={loading}
       >
        <div className={styles.score}>
         <span>01 / LEXICAL SIMILARITY</span>
         <strong>{result ? pct(result.similarity) : "—"}</strong>
         <small>Normalized token overlap</small>
         {result && (
             <div className={styles.meter}>
              <i style={{ width: pct(result.similarity) }} />
             </div>
         )}
        </div>
        <div className={styles.confidence}>
         <span>02 / MODEL CONFIDENCE</span>
         <strong>{result ? pct(result.confidence) : "—"}</strong>
         <small>
          {result
              ? `${
                  result.predictedSimilar ? "Similar" : "Different"
              } · threshold ${pct(
                  result.threshold
              )} · ${result.elapsedMs.toFixed(2)} ms`
              : "Estimated probability of similar class"}
         </small>
         {result && (
             <div className={styles.meter}>
              <i style={{ width: pct(result.confidence) }} />
             </div>
         )}
        </div>
       </section>
       {error && (
           <p role="alert" className={styles.error}>
            {error}
           </p>
       )}
       <p className={styles.hint}>
        {loading
            ? "Evaluating locally…"
            : result
                ? "Similarity and model confidence are distinct metrics. Not a plagiarism verdict."
                : "Paste two Python blocks and run analysis. Maximum 64 KiB UTF-8 per input."}
       </p>
      </div>
      <footer className={styles.footer}>
        <span>
          <b>▰</b> SOVEREIGN ENGINE / EMBEDDED ML
        </span>
       <span>
          104 B / PARAMETER ESTIMATE <b>//</b> NO REMOTE API
        </span>
      </footer>
     </main>
 );
}
