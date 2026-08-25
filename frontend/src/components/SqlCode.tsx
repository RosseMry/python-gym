import type { ReactNode } from "react";

// SQL variant of PythonCode: same minimal, dependency-free approach
// and the same `py-tok--*` color tokens (defined once in
// LearningNote.css, not Python-specific despite the class prefix),
// just SQL's own keywords/comment/string syntax instead of Python's.
const SQL_KEYWORDS =
  "SELECT|FROM|WHERE|JOIN|INNER|LEFT|RIGHT|FULL|OUTER|CROSS|ON|GROUP|BY|ORDER|HAVING|LIMIT|" +
  "OFFSET|INSERT|INTO|VALUES|UPDATE|SET|DELETE|CREATE|ALTER|DROP|TABLE|VIEW|INDEX|TRIGGER|" +
  "FUNCTION|PROCEDURE|RETURNS|RETURN|CALL|BEGIN|END|AS|AND|OR|NOT|NULL|IS|IN|LIKE|BETWEEN|" +
  "DISTINCT|UNION|ALL|INTERSECT|EXCEPT|WITH|CASE|WHEN|THEN|ELSE|IF|ELSIF|PRIMARY|KEY|FOREIGN|" +
  "REFERENCES|UNIQUE|CHECK|DEFAULT|CONSTRAINT|COLUMN|ADD|SAVEPOINT|ROLLBACK|COMMIT|TRANSACTION|" +
  "OVER|PARTITION|ASC|DESC|LANGUAGE|PLPGSQL|EXECUTE|RAISE|EXCEPTION|TRIGGER";

const TOKEN_RE = new RegExp(
  `(--.*$)|('(?:[^']|'')*')|\\b(${SQL_KEYWORDS})\\b|\\b(\\d+\\.?\\d*)\\b`,
  "gim",
);

export function SqlCode({ code }: { code: string }) {
  const parts: ReactNode[] = [];
  let lastIndex = 0;
  let match: RegExpExecArray | null;
  let key = 0;
  TOKEN_RE.lastIndex = 0;

  while ((match = TOKEN_RE.exec(code))) {
    if (match.index > lastIndex) {
      parts.push(code.slice(lastIndex, match.index));
    }
    const [full, comment, string, keyword, number] = match;
    let className: string | null = null;
    if (comment) className = "py-tok py-tok--comment";
    else if (string) className = "py-tok py-tok--string";
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
