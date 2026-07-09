import { createContext, useContext, useState, useCallback, useMemo } from 'react'
import { translations } from './translations'
import { updateProfile } from '../api/expenses'

const LanguageContext = createContext(null)

function detectInitialLanguage() {
  const tgLang = window.Telegram?.WebApp?.initDataUnsafe?.user?.language_code
  return tgLang === 'en' ? 'en' : 'ru'
}

function resolve(dict, path) {
  return path.split('.').reduce((acc, key) => acc?.[key], dict)
}

function interpolate(str, vars) {
  if (!vars) return str
  return str.replace(/\{(\w+)\}/g, (_, key) => vars[key] ?? `{${key}}`)
}

export function LanguageProvider({ children }) {
  const [language, setLanguageState] = useState(detectInitialLanguage)

  const t = useCallback((key, vars) => {
    const str = resolve(translations[language], key) ?? resolve(translations.ru, key) ?? key
    return interpolate(str, vars)
  }, [language])

  // Changes language locally and persists it to the profile (user-initiated switch).
  const setLanguage = useCallback((lang) => {
    setLanguageState(lang)
    updateProfile({ language: lang }).catch(err => console.error('[Language] Failed to persist:', err))
  }, [])

  // Adopts the language from a freshly-loaded profile without re-PATCHing it.
  const syncLanguage = useCallback((lang) => {
    if (lang === 'en' || lang === 'ru') setLanguageState(lang)
  }, [])

  const value = useMemo(
    () => ({ language, setLanguage, syncLanguage, t }),
    [language, setLanguage, syncLanguage, t],
  )

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>
}

export function useLanguage() {
  const ctx = useContext(LanguageContext)
  if (!ctx) throw new Error('useLanguage must be used within a LanguageProvider')
  return ctx
}
