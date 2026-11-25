
import { useRef, useState } from "react";
import Editor, { loader } from "@monaco-editor/react";
import { invoke } from "@tauri-apps/api/core";

import {
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  ChamferCard,
  ChamferCardContent,
  ChamferCardHeader,
  ChamferCardTitle,
  ChamferCardDescription,
} from "@siberui/react";

import styles from "./App.module.css";

const INITIAL_SOURCE = `def calculate_total(prices):
    total = 0

    for price in prices:
        total += price

    return total

print(calculate_total([12, 18, 20]))
`;
function configureMonaco(monaco) {
  monaco.editor.defineTheme("siber-dark", {
    base: "vs-dark",
    inherit: true,
    rules: [],
    colors: {
      "editor.background": "#07090f",
      "editorGutter.background": "#07090f",
      "editor.lineHighlightBackground": "#0F172A",
      "editor.lineHighlightBorder": "#00000000",
      "editor.selectionBackground": "#22D3EE30",
      "editorCursor.foreground": "#22D3EE",
      "editorLineNumber.foreground": "#475569",
      "editorLineNumber.activeForeground": "#CBD5E1",
    },
  });
}
function displayLexeme(lexeme) {
  return lexeme.length === 0 ? "∅" : JSON.stringify(lexeme);
}

function displayError(error) {
  if (typeof error === "string") return error;
  if (error instanceof Error) return error.message;
  return "An unexpected error occurred during analysis.";
}

export default function App() {
  const [source, setSource] = useState(INITIAL_SOURCE);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);


  const revision = useRef(0);

  function handleSourceChange(value) {
    revision.current += 1;
    setSource(value);
    setResult(null);
    setError(null);
  }

  async function handleAnalyze() {
    if (loading || !source.trim()) return;

    const requestedRevision = revision.current;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await invoke("analyze_python", {
        source,
      });

      if (revision.current === requestedRevision) {
        setResult(response);
      }
    } catch (err) {
      if (revision.current === requestedRevision) {
        setError(displayError(err));
      }
    } finally {
      setLoading(false);
    }
  }

  return (
      <main className={styles.mainContentContainer}>
        <header className={styles.titleContainer}>
          <div>
            <p className={styles.eyebrow}>
              Lou Parra / Luis Adrian Diaz / Ana Flores / Joselyn Espinoza
            </p>

            <h1 className={styles.pageTitle}>
              Python Code Analyzer
            </h1>

            <p className={styles.pageSubtitle}>

            </p>

          </div>
          <Button
              variant="primary"
              size="lg"
              disabled={loading || !source.trim()}
              onClick={handleAnalyze}
          >
            {loading ? "Analyzing..." : "LEX & PARSE"}
          </Button>

        </header>

        <section className={styles.editorContainer}>

          <ChamferCard
              signal="cyan"
              glow
              tag="SOURCE.01 // PY"
              statusDot="cyan"
              className={styles.workspaceCard}
          >
            <ChamferCardHeader className={styles.panelHeader}>
              <div className={styles.panelHeading}>
                <ChamferCardTitle>
                  Source Code
                </ChamferCardTitle>

                <ChamferCardDescription>
                  Python source input
                </ChamferCardDescription>
              </div>
            </ChamferCardHeader>

            <ChamferCardContent className={styles.editorContent}>
              <div className={styles.monacoContainer}>
                <Editor
                    height="100%"
                    language="python"
                    theme="siber-dark"
                    beforeMount={configureMonaco}
                    value={source}
                    onChange={(value) => handleSourceChange(value ?? "")}
                    options={{
                      automaticLayout: true,
                      minimap: { enabled: false },
                      fontSize: 14,
                      lineNumbers: "on",
                      scrollBeyondLastLine: false,
                      wordWrap: "on",
                      padding: { top: 16, bottom: 16 },
                      bracketPairColorization: {
                        enabled: true,
                      },
                    }}
                />              </div>
            </ChamferCardContent>
          </ChamferCard>


          <Card className={styles.workspaceCard}>
            <CardHeader className={styles.panelHeader}>
              <div className={styles.panelHeading}>
                <CardTitle>
                  Token Output
                </CardTitle>

                <p className={styles.panelDescription}>
                  Lexical analysis results
                </p>
              </div>

              <span className={styles.panelMeta}>
              {result
                  ? `${result.tokens.length} TOKENS`
                  : "NO RESULT"}
            </span>
            </CardHeader>

            <CardContent className={styles.outputContent}>
              {error && (
                  <div
                      className={styles.errorMessage}
                      role="alert"
                  >
                    {error}
                  </div>
              )}

              {!result && !error && (
                  <div className={styles.emptyState}>
                    <div className={styles.emptySymbol}>
                      {"{ }"}
                    </div>

                    <strong>
                      No tokens generated
                    </strong>

                    <p>
                      Enter Python code and run the analyzer
                      to inspect its lexical structure.
                    </p>
                  </div>
              )}

              {result && (
                  <div className={styles.outputResults}>
                    {result.diagnostics.length > 0 && (
                        <div
                            className={styles.diagnostics}
                            role="status"
                        >
                          <strong>
                            {result.diagnostics.length} diagnostic(s)
                          </strong>

                          {result.diagnostics.map(
                              (diagnostic, index) => (
                                  <p key={index}>
                                    {diagnostic.message}
                                    {" — "}
                                    bytes {diagnostic.start}–
                                    {diagnostic.end}
                                  </p>
                              )
                          )}
                        </div>
                    )}

                    <div className={styles.tokenTableContainer}>
                      <table className={styles.tokenTable}>
                        <thead>
                        <tr>
                          <th>#</th>
                          <th>Type</th>
                          <th>Lexeme</th>
                          <th>Range</th>
                        </tr>
                        </thead>

                        <tbody>
                        {result.tokens.map(
                            (token, index) => (
                                <tr key={index}>
                                  <td className={styles.tokenIndex}>
                                    {index + 1}
                                  </td>

                                  <td>
                              <span className={styles.tokenKind}>
                                {token.kind}
                              </span>

                                    <small className={styles.tokenCategory}>
                                      {token.category}
                                    </small>
                                  </td>

                                  <td className={styles.tokenLexeme}>
                                    {displayLexeme(token.lexeme)}
                                  </td>

                                  <td className={styles.tokenRange}>
                                    {token.start}:{token.end}
                                  </td>
                                </tr>
                            )
                        )}
                        </tbody>
                      </table>
                    </div>
                  </div>
              )}
            </CardContent>
          </Card>
        </section>


      </main>
  );
}
