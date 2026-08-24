import { useEffect, useState } from "react";
import { api } from "../services/api";
import type { FunctionReferenceDetail } from "../types/exercise";
import { useLocale, useLocalized } from "../i18n/LocaleContext";
import "../pages/LearningNote.css";
import "./FunctionReferencePanel.css";

interface FunctionReferencePanelProps {
  functionId: string;
  onClose: () => void;
}

/**
 * "Learn: x()" popover (Sprint 3 finalization spec section 6-7): a
 * reusable explanation a hint can point to instead of duplicating the
 * same content in every exercise. The student closes this and tries
 * the exercise independently - it never shows the exercise's solution.
 */
export function FunctionReferencePanel({
  functionId,
  onClose,
}: FunctionReferencePanelProps) {
  const [fn, setFn] = useState<FunctionReferenceDetail | null>(null);
  const { t } = useLocale();
  const localize = useLocalized();

  useEffect(() => {
    setFn(null);
    api.getFunction(functionId).then(setFn);
  }, [functionId]);

  return (
    <div className="fn-ref-overlay" role="dialog" aria-modal="true" onClick={onClose}>
      <div className="fn-ref-panel" onClick={(e) => e.stopPropagation()}>
        {!fn ? (
          <p>{t("notes.loading")}</p>
        ) : (
          <>
            <div className="fn-ref-panel__header">
              <p className="fn-ref-panel__eyebrow">{t("functionRef.learn")}</p>
              <h2>{localize(fn.name, fn.name_fr)}</h2>
              <button className="fn-ref-panel__close" onClick={onClose} aria-label="Close">
                ✕
              </button>
            </div>

            <p className="fn-ref-panel__what">
              {localize(fn.what_it_does, fn.what_it_does_fr)}
            </p>

            <pre className="solution-block">{fn.syntax}</pre>

            <dl className="fn-ref-panel__meta">
              <dt>{t("functionRef.parameters")}</dt>
              <dd>{localize(fn.parameters, fn.parameters_fr)}</dd>
              <dt>{t("functionRef.returns")}</dt>
              <dd>{localize(fn.return_value, fn.return_value_fr)}</dd>
            </dl>

            <p className="fn-ref-panel__section-title">{t("functionRef.example")}</p>
            <pre className="examples-block">{fn.example}</pre>
            <p className="fn-ref-panel__section-title">{t("functionRef.output")}</p>
            <pre className="examples-block">{fn.example_output}</pre>

            <div className="fn-ref-panel__card fn-ref-panel__card--warning">
              <p className="learning-note__card-label">
                ⚠️ {t("notes.commonMistakes")}
              </p>
              <p className="learning-note__card-text">
                {localize(fn.common_mistakes, fn.common_mistakes_fr)}
              </p>
            </div>

            <div className="fn-ref-panel__card fn-ref-panel__card--tip">
              <p className="learning-note__card-label">{t("functionRef.whenToUse")}</p>
              <p className="learning-note__card-text">
                {localize(fn.when_to_use, fn.when_to_use_fr)}
              </p>
            </div>

            <button className="btn btn--primary fn-ref-panel__back" onClick={onClose}>
              {t("functionRef.backToExercise")}
            </button>
          </>
        )}
      </div>
    </div>
  );
}
