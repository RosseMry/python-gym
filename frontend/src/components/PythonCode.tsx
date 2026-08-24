import type { ReactNode } from "react";

// Minimal, dependency-free Python syntax highlighter - just enough
// token classes (comment/string/keyword/number/decorator) for a
// static code block to read like a real editor, without pulling in
// Prism/highlight.js for a handful of Learning Notes code samples.
const TOKEN_RE =
  /(#.*$)|("""[\s\S]*?"""|'''[\s\S]*?'''|"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')|(@\w+)|\b(def|class|for|while|if|elif|else|try|except|finally|with|as|import|from|return|yield|break|continue|pass|lambda|and|or|not|in|is|None|True|False|raise|global|nonlocal|assert|del|async|await)\b|\b(\d+\.?\d*)\b/gm;

export function PythonCode({ code }: { code: string }) {
  const parts: ReactNode[] = [];
  let lastIndex = 0;
  let match: RegExpExecArray | null;
  let key = 0;
  TOKEN_RE.lastIndex = 0;

  while ((match = TOKEN_RE.exec(code))) {
    if (match.index > lastIndex) {
      parts.push(code.slice(lastIndex, match.index));
    }
    const [full, comment, string, decorator, keyword, number] = match;
    let className: string | null = null;
    if (comment) className = "py-tok py-tok--comment";
    else if (string) className = "py-tok py-tok--string";
    else if (decorator) className = "py-tok py-tok--decorator";
    else if (keyword) className = "py-tok py-tok--keyword";
    else if (number) className = "py-tok py-tok--number";

    parts.push(
      className ? (
        <span key={key++} className={className}>
          {full}
        </span>
      ) : (
        full
      ),
    );
    lastIndex = match.index + full.length;
  }
  if (lastIndex < code.length) {
    parts.push(code.slice(lastIndex));
  }

  return <>{parts}</>;
}
