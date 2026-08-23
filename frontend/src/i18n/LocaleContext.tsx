import { createContext, useContext, useMemo, useState } from "react";
import type { ReactNode } from "react";
import en from "./en.json";
import fr from "./fr.json";

export type Locale = "en" | "fr";

const DICTIONARIES: Record<Locale, Record<string, string>> = { en, fr };
const STORAGE_KEY = "python-gym-locale";

interface LocaleContextValue {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: (key: string) => string;
}

const LocaleContext = createContext<LocaleContextValue | null>(null);

function readStoredLocale(): Locale {
  const stored = window.localStorage.getItem(STORAGE_KEY);
  return stored === "fr" ? "fr" : "en";
}

export function LocaleProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>(readStoredLocale);

  function setLocale(next: Locale) {
    setLocaleState(next);
    window.localStorage.setItem(STORAGE_KEY, next);
  }

  const value = useMemo<LocaleContextValue>(
    () => ({
      locale,
      setLocale,
      t: (key: string) => DICTIONARIES[locale][key] ?? DICTIONARIES.en[key] ?? key,
    }),
    [locale],
  );

  return <LocaleContext.Provider value={value}>{children}</LocaleContext.Provider>;
}

export function useLocale(): LocaleContextValue {
  const ctx = useContext(LocaleContext);
  if (!ctx) {
    throw new Error("useLocale must be used within a LocaleProvider");
  }
  return ctx;
}

/** Picks a French field if the current locale is fr and it's translated, else English. */
export function useLocalized(): (en: string, fr: string | null | undefined) => string {
  const { locale } = useLocale();
  return (enValue, frValue) => (locale === "fr" && frValue ? frValue : enValue);
}
