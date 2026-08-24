import { useLocale } from "../i18n/LocaleContext";
import "./PrerequisiteWarningModal.css";

interface PrerequisiteWarningModalProps {
  onGoBack: () => void;
  onContinueAnyway: () => void;
}

/**
 * Soft block (Sprint 3 finalization spec section 4): shown when a
 * student opens an exercise with unfinished prerequisites. They can
 * still proceed - this warns, it doesn't lock them out.
 */
export function PrerequisiteWarningModal({
  onGoBack,
  onContinueAnyway,
}: PrerequisiteWarningModalProps) {
  const { t } = useLocale();

  return (
    <div className="prereq-modal-overlay" role="dialog" aria-modal="true">
      <div className="prereq-modal">
        <p className="prereq-modal__headline">⚠️ {t("prereq.headline")}</p>
        <p className="prereq-modal__body">{t("prereq.body")}</p>
        <p className="prereq-modal__question">{t("prereq.question")}</p>
        <div className="actions prereq-modal__actions">
          <button className="btn" onClick={onGoBack}>
            {t("prereq.goBack")}
          </button>
          <button className="btn btn--primary" onClick={onContinueAnyway}>
            {t("prereq.continueAnyway")}
          </button>
        </div>
      </div>
    </div>
  );
}
