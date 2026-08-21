import { useState, useEffect, useCallback } from 'react'
import { AnimatePresence, motion } from 'framer-motion'

import {
  authTelegram,
  getProfile,
  getSummary,
  getHistoryMain,
  getWeekDetails,
  getMonthDetails,
  getCategories,
  getTemplates,
  createTransaction,
} from './api/expenses'

import Carousel        from './components/Carousel'
import ExpenseForm     from './components/ExpenseForm'
import CategoryModal   from './components/CategoryModal'
import TemplateModal   from './components/TemplateModal'
import HistorySection  from './components/HistorySection'
import WeekDetails     from './components/WeekDetails'
import MonthDetails    from './components/MonthDetails'
import CurrencyModal   from './components/CurrencyModal'
import LanguageModal   from './components/LanguageModal'
import { useLanguage } from './i18n/LanguageContext'

// ──────────────────────────────────────────────────────────────────────────────
// Helpers
// ──────────────────────────────────────────────────────────────────────────────

// Декоративный разделитель «линия + точка»
function SectionDivider() {
  return (
    <div className="flex items-center gap-2 mx-4 my-2">
      <div className="flex-1 h-px bg-blue-100" />
      <div className="w-2 h-2 rounded-full bg-blue-300 flex-shrink-0" />
      <div className="flex-1 h-px bg-blue-100" />
    </div>
  )
}

// ──────────────────────────────────────────────────────────────────────────────
// App
// ──────────────────────────────────────────────────────────────────────────────

export default function App() {
  const { syncLanguage } = useLanguage()

  // ── Auth ──────────────────────────────────────────────────────────────────
  const [authed,  setAuthed]  = useState(!!localStorage.getItem('access_token'))
  const [loading, setLoading] = useState(true)

  // ── View ──────────────────────────────────────────────────────────────────
  // 'home' | 'week-details' | 'month-details'
  const [view, setView] = useState('home')

  // ── User ──────────────────────────────────────────────────────────────────
  const [user, setUser] = useState(null)

  // ── Modals ────────────────────────────────────────────────────────────────
  const [catModalOpen,  setCatModalOpen]  = useState(false)
  const [tmplModalOpen, setTmplModalOpen] = useState(false)
  const [currModalOpen, setCurrModalOpen] = useState(false)
  const [langModalOpen, setLangModalOpen] = useState(false)

  // ── Form state ────────────────────────────────────────────────────────────
  const [amount,   setAmount]   = useState('')
  const [category, setCategory] = useState(null)
  const [transactionType, setTransactionType] = useState('expense')
  const [submitting, setSubmitting] = useState(false)

  // ── Data ──────────────────────────────────────────────────────────────────
  const [summary,      setSummary]      = useState(null)
  const [history,      setHistory]      = useState(null)
  const [weekDays,     setWeekDays]     = useState([])
  const [monthWeeks,   setMonthWeeks]   = useState([])
  const [categories,   setCategories]   = useState([])
  const [templates,    setTemplates]    = useState([])

  const applyUser = useCallback((u) => {
    setUser(u)
    syncLanguage(u.language)
  }, [syncLanguage])

  // ── Auth on mount ─────────────────────────────────────────────────────────
  useEffect(() => {
    if (authed) {
      getProfile().then(applyUser).catch(err => console.error('[Profile] Failed:', err))
      loadAll()
    } else {
      authenticate()
    }
  }, [])  // eslint-disable-line react-hooks/exhaustive-deps

  const authenticate = async () => {
    setLoading(true)
    try {
      const tg       = window.Telegram?.WebApp
      const initData = tg?.initData || ''
      const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone

      // In dev without Telegram context, skip auth and rely on localStorage token.
      if (!initData) {
        console.warn('[Auth] No Telegram initData — running in dev mode without auth.')
        setLoading(false)
        return
      }

      const data = await authTelegram(initData, timezone)
      localStorage.setItem('access_token',  data.access)
      localStorage.setItem('refresh_token', data.refresh)
      applyUser(data.user)
      setAuthed(true)
      await loadAll()
    } catch (err) {
      console.error('[Auth] Failed:', err)
      setLoading(false)
    }
  }

  const loadAll = useCallback(async () => {
    setLoading(true)
    try {
      const [sum, hist, cats, tmpls] = await Promise.all([
        getSummary(),
        getHistoryMain(),
        getCategories(),
        getTemplates(),
      ])
      setSummary(sum)
      setHistory(hist)
      setCategories(cats.results ?? cats)
      setTemplates(tmpls.results ?? tmpls)
    } catch (err) {
      console.error('[Load] Failed:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  const loadDetails = async (type) => {
    if (type === 'week') {
      const data = await getWeekDetails()
      setWeekDays(data)
      setView('week-details')
    } else {
      const data = await getMonthDetails()
      setMonthWeeks(data)
      setView('month-details')
    }
  }

  // ── Submit transaction (income or expense) ──────────────────────────────────
  const handleSubmit = async () => {
    if (!amount || parseFloat(amount) <= 0) return
    setSubmitting(true)
    try {
      await createTransaction(
        parseFloat(amount),
        category?.id ?? null,
        '',
        transactionType,
      )
      setAmount('')
      setCategory(null)
      setTransactionType('expense')
      await loadAll()
    } catch (err) {
      console.error('[Submit] Failed:', err)
    } finally {
      setSubmitting(false)
    }
  }

  // ── Apply template (templates are expense-only) ─────────────────────────────
  const handleApplyTemplate = (tpl) => {
    if (tpl.amount) setAmount(String(tpl.amount))
    if (tpl.category) setCategory({ id: tpl.category, name: tpl.category_name, icon: tpl.category_icon })
    setTransactionType('expense')
  }

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-cream">
      {/* ── Currency / language — fixed top-right corner ── */}
      <div className="fixed top-3 right-3 z-40 flex items-center gap-2">
        <button
          onClick={() => setCurrModalOpen(true)}
          className="flex items-center gap-1.5 pl-3.5 pr-3 h-10 rounded-full bg-white shadow-md active:scale-95 transition-transform text-blue-500 text-sm font-semibold"
        >
          <span>{user?.currency ?? 'UZS'}</span>
          <span className="text-xs opacity-70">⇄</span>
        </button>
        <button
          onClick={() => setLangModalOpen(true)}
          className="flex items-center justify-center w-10 h-10 rounded-full bg-white shadow-md active:scale-95 transition-transform text-lg"
        >
          {user?.language === 'en' ? '🇬🇧' : '🇷🇺'}
        </button>
      </div>

      {/* ── Detail views (slide over main screen) ── */}
      <AnimatePresence mode="wait">
        {view === 'week-details' && (
          <motion.div
            key="week"
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', stiffness: 300, damping: 32 }}
            className="fixed inset-0 z-30 overflow-y-auto"
          >
            <WeekDetails days={weekDays} onBack={() => setView('home')} onRefresh={() => loadDetails('week')} />
          </motion.div>
        )}

        {view === 'month-details' && (
          <motion.div
            key="month"
            initial={{ x: '-100%' }}
            animate={{ x: 0 }}
            exit={{ x: '-100%' }}
            transition={{ type: 'spring', stiffness: 300, damping: 32 }}
            className="fixed inset-0 z-30 overflow-y-auto"
          >
            <MonthDetails weeks={monthWeeks} onBack={() => setView('home')} onRefresh={() => loadDetails('month')} />
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Main screen ── */}
      <div className="max-w-sm mx-auto pb-10">

        {/* Карусель сумм */}
        <Carousel summary={summary} />

        <SectionDivider />

        {/* Форма добавления дохода/расхода */}
        <ExpenseForm
          amount={amount}
          setAmount={setAmount}
          selectedCategory={category}
          onOpenCategory={() => setCatModalOpen(true)}
          onOpenTemplates={() => setTmplModalOpen(true)}
          transactionType={transactionType}
          onTransactionTypeChange={setTransactionType}
          onSubmit={handleSubmit}
          submitting={submitting}
        />

        {/* Декоративный разделитель перед историей */}
        <SectionDivider />

        {/* История расходов — рендерится всегда, даже при пустых данных */}
        <HistorySection
          history={history}
          loading={loading}
          onWeekDetails={() => loadDetails('week')}
          onMonthDetails={() => loadDetails('month')}
        />
      </div>

      {/* ── Modals ── */}
      <AnimatePresence>
        {catModalOpen && (
          <CategoryModal
            key="cat-modal"
            categories={categories}
            selectedId={category?.id}
            onSelect={setCategory}
            onClose={() => setCatModalOpen(false)}
            onRefresh={() => getCategories().then(d => setCategories(d.results ?? d))}
          />
        )}
      </AnimatePresence>

      <AnimatePresence>
        {tmplModalOpen && (
          <TemplateModal
            key="tmpl-modal"
            templates={templates}
            categories={categories}
            onApply={handleApplyTemplate}
            onClose={() => setTmplModalOpen(false)}
            onRefresh={() => getTemplates().then(d => setTemplates(d.results ?? d))}
          />
        )}
      </AnimatePresence>

      <AnimatePresence>
        {currModalOpen && user && (
          <CurrencyModal
            key="curr-modal"
            currentCurrency={user.currency}
            onClose={() => setCurrModalOpen(false)}
            onChanged={updatedUser => {
              applyUser(updatedUser)
              loadAll()
            }}
          />
        )}
      </AnimatePresence>

      <AnimatePresence>
        {langModalOpen && (
          <LanguageModal
            key="lang-modal"
            onClose={() => setLangModalOpen(false)}
          />
        )}
      </AnimatePresence>
    </div>
  )
}
