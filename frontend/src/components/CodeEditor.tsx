import { useRef } from "react";
import "./CodeEditor.css";

interface CodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

/**
 * A deliberately simple code editor for the MVP: a monospace textarea
 * with Tab-to-indent support. No syntax highlighting yet - the goal
 * is writing Python from scratch, not a full IDE experience.
 */
export function CodeEditor({ value, onChange, disabled }: CodeEditorProps) {
  const ref = useRef<HTMLTextAreaElement>(null);

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key !== "Tab") return;
    e.preventDefault();
    const textarea = ref.current;
    if (!textarea) return;
    const { selectionStart, selectionEnd } = textarea;
    const next =
      value.slice(0, selectionStart) + "    " + value.slice(selectionEnd);
    onChange(next);
    requestAnimationFrame(() => {
      textarea.selectionStart = textarea.selectionEnd = selectionStart + 4;
    });
  }

  const lineCount = value.split("\n").length;

  return (
    <div className="code-editor">
      <div className="code-editor__gutter" aria-hidden="true">
        {Array.from({ length: lineCount }, (_, i) => (
          <div key={i}>{i + 1}</div>
        ))}
      </div>
      <textarea
        ref={ref}
        className="code-editor__textarea code-editor"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        spellCheck={false}
        autoCapitalize="off"
        autoCorrect="off"
        aria-label="Python code editor"
      />
    </div>
  );
}
