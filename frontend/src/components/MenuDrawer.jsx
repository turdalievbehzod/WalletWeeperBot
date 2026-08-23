import { motion } from 'framer-motion'
import { useLanguage } from '../i18n/LanguageContext'

const HISTORY_VIEWS = ['history', 'today-details', 'week-details', 'month-details']

/**
 * Right-side slide-in menu — replaces the old fixed top-right currency/
 * language buttons (which overlapped page titles on narrow phones).
 * Holds page navigation (Главная / История) plus the currency and
 * language pickers, both moved in here.
 */
export default function MenuDrawer({ currentView, onNavigate, onCurrency, onLanguage, user, onClose }) {
  const { t, language } = useLanguage()

  const navClass = active =>
    `flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-semibold text-left transition-colors ${
      active ? 'bg-blue-500 text-white' : 'text-gray-700 hover:bg-gray-100'
    }`

  return (
    <motion.div
      className="fixed inset-0 z-50 flex justify-end"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <div className="absolute inset-0 bg-black/40" onClick={onClose} />

      <motion.div
        className="relative w-64 max-w-[80%] h-full bg-white shadow-xl flex flex-col py-6 px-3 gap-1"
        initial={{ x: '100%' }}
        animate={{ x: 0 }}
        exit={{ x: '100%' }}
        transition={{ type: 'spring', stiffness: 320, damping: 34 }}
      >
        <span className="text-xs font-semibold text-gray-400 uppercase tracking-wide px-3 mb-1">
          {t('menu.navigation')}
        </span>
        <button onClick={() => onNavigate('home')} className={navClass(currentView === 'home')}>
          🏠 {t('menu.home')}
        </button>
        <button onClick={() => onNavigate('history')} className={navClass(HISTORY_VIEWS.includes(currentView))}>
          📜 {t('menu.history')}
        </button>

        <div className="h-px bg-gray-100 my-3" />

        <span className="text-xs font-semibold text-gray-400 uppercase tracking-wide px-3 mb-1">
          {t('menu.settings')}
        </span>
        <button
          onClick={onCurrency}
          className="flex items-center justify-between rounded-xl px-3 py-3 text-sm font-semibold text-gray-700 hover:bg-gray-100 transition-colors"
        >
          <span>{t('menu.currency')}</span>
          <span className="text-blue-500">{user?.currency ?? 'UZS'} ⇄</span>
        </button>
        <button
          onClick={onLanguage}
          className="flex items-center justify-between rounded-xl px-3 py-3 text-sm font-semibold text-gray-700 hover:bg-gray-100 transition-colors"
        >
          <span>{t('menu.language')}</span>
          <span>{language === 'en' ? '🇬🇧 EN' : '🇷🇺 RU'}</span>
        </button>
      </motion.div>
    </motion.div>
  )
}
