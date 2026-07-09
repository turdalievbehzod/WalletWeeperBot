import { motion, AnimatePresence } from 'framer-motion'
import { useLanguage } from '../i18n/LanguageContext'

const LANGUAGES = [
  { code: 'ru', flag: '🇷🇺' },
  { code: 'en', flag: '🇬🇧' },
]

export default function LanguageModal({ onClose }) {
  const { language, setLanguage, t } = useLanguage()

  const handleSelect = (code) => {
    if (code !== language) setLanguage(code)
    onClose()
  }

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 z-50 flex items-end justify-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
      >
        {/* Backdrop */}
        <div className="absolute inset-0 bg-black/40" onClick={onClose} />

        {/* Sheet */}
        <motion.div
          className="relative w-full max-w-sm bg-white rounded-t-3xl p-6 pb-10 z-10"
          initial={{ y: '100%' }}
          animate={{ y: 0 }}
          exit={{ y: '100%' }}
          transition={{ type: 'spring', stiffness: 320, damping: 32 }}
        >
          <div className="w-10 h-1 bg-gray-200 rounded-full mx-auto mb-5" />
          <h2 className="text-lg font-bold text-gray-800 mb-1">{t('languageModal.title')}</h2>
          <p className="text-sm text-gray-500 mb-4">{t('languageModal.description')}</p>

          <div className="space-y-2">
            {LANGUAGES.map(l => {
              const isActive = language === l.code
              return (
                <button
                  key={l.code}
                  onClick={() => handleSelect(l.code)}
                  className={`w-full flex items-center justify-between px-4 py-3 rounded-2xl border-2 transition-all ${
                    isActive
                      ? 'border-orange-400 bg-orange-50'
                      : 'border-gray-100 bg-gray-50'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{l.flag}</span>
                    <p className={`font-semibold text-sm ${isActive ? 'text-orange-600' : 'text-gray-800'}`}>
                      {t(`languageModal.names.${l.code}`)}
                    </p>
                  </div>
                  {isActive && (
                    <span className="text-orange-500 text-xs font-bold">✓</span>
                  )}
                </button>
              )
            })}
          </div>

          <button
            onClick={onClose}
            className="w-full mt-5 py-3.5 rounded-2xl bg-orange-500 text-white font-bold text-base"
          >
            {t('languageModal.close')}
          </button>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}
