import Editor, { loader } from "@monaco-editor/react";
import * as monaco from "monaco-editor/esm/vs/editor/editor.api.js";
import "monaco-editor/esm/vs/editor/editor.all.js";
import "monaco-editor/esm/vs/basic-languages/python/python.contribution.js";
import EditorWorker from "monaco-editor/esm/vs/editor/editor.worker?worker";
self.MonacoEnvironment = {
    getWorker() {
        return new EditorWorker();
    },
};
loader.config({ monaco });
monaco.editor.defineTheme("aivora-light", {
    base: "vs",
    inherit: true,
    rules: [
        { token: "keyword", foreground: "BF0046", fontStyle: "bold" },
        { token: "string", foreground: "7A1C54" },
        { token: "comment", foreground: "656570", fontStyle: "italic" },
        { token: "number", foreground: "9B0050" },
        { token: "operator", foreground: "111111" },
    ],
    colors: {
        "editor.background": "#FFFFFF",
        "editor.foreground": "#111111",
        "editorGutter.background": "#F8F8FA",
        "editor.lineHighlightBackground": "#F9EDF2",
        "editor.lineHighlightBorder": "#00000000",
        "editor.selectionBackground": "#FE0A6230",
        "editor.inactiveSelectionBackground": "#FE0A6218",
        "editorCursor.foreground": "#FE0A62",
        "editorLineNumber.foreground": "#656570",
        "editorLineNumber.activeForeground": "#BF0046",
        "editorBracketMatch.background": "#FE0A6222",
        "editorBracketMatch.border": "#FE0A62",
        "editorIndentGuide.background1": "#D9DCE3",
        "editorIndentGuide.activeBackground1": "#FE0A62",
        focusBorder: "#FE0A62",
        "editorWidget.background": "#F8F8FA",
        "editorWidget.border": "#D9DCE3",
    },
});
export default function MonacoInput({ id, label, value, onChange, onReady }) {
    return (
        <Editor
            height="100%"
            path={`${id}.py`}
            language="python"
            theme="aivora-light"
            value={value}
            onChange={(v) => onChange(v ?? "")}
            onMount={() => onReady(id)}
            loading={<span>Cargando editor local…</span>}
            options={{
                ariaLabel: label,
                automaticLayout: true,
                minimap: { enabled: false },
                fontFamily: "'IBM Plex Mono', monospace",
                fontSize: 14,
                lineNumbers: "on",
                scrollBeyondLastLine: false,
                wordWrap: "on",
                tabSize: 4,
                insertSpaces: true,
                autoIndent: "full",
                bracketPairColorization: { enabled: true },
                padding: { top: 14, bottom: 14 },
                renderWhitespace: "selection",
                accessibilitySupport: "auto",
                quickSuggestions: false,
                overviewRulerLanes: 0,
            }}
        />
    );
}
