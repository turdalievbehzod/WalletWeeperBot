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

  // ── Form state ────────────────────────────────────────────────────────────
  const [amount,   setAmount]   = useState('')
  const [category, setCategory] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  // ── Data ──────────────────────────────────────────────────────────────────
  const [summary,      setSummary]      = useState(null)
  const [history,      setHistory]      = useState(null)
  const [weekDays,     setWeekDays]     = useState([])
  const [monthWeeks,   setMonthWeeks]   = useState([])
  const [categories,   setCategories]   = useState([])
  const [templates,    setTemplates]    = useState([])

  // ── Auth on mount ─────────────────────────────────────────────────────────
  useEffect(() => {
    if (authed) {
      getProfile().then(setUser).catch(err => console.error('[Profile] Failed:', err))
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
      setUser(data.user)
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

  // ── Submit expense ─────────────────────────────────────────────────────────
  const handleSubmit = async () => {
    if (!amount || parseFloat(amount) <= 0) return
    setSubmitting(true)
    try {
      await createTransaction(
        parseFloat(amount),
        category?.id ?? null,
      )
      setAmount('')
      setCategory(null)
      await loadAll()
    } catch (err) {
      console.error('[Submit] Failed:', err)
    } finally {
      setSubmitting(false)
    }
  }

  // ── Apply template ─────────────────────────────────────────────────────────
  const handleApplyTemplate = (tpl) => {
    if (tpl.amount) setAmount(String(tpl.amount))
    if (tpl.category) setCategory({ id: tpl.category, name: tpl.category_name, icon: tpl.category_icon })
  }

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-cream">
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
            <WeekDetails days={weekDays} onBack={() => setView('home')} />
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
            <MonthDetails weeks={monthWeeks} onBack={() => setView('home')} />
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Main screen ── */}
      <div className="max-w-sm mx-auto pb-10">

        {/* Карусель сумм */}
        <Carousel summary={summary} onCurrencyTap={() => setCurrModalOpen(true)} />

        <SectionDivider />

        {/* Форма добавления расхода */}
        <ExpenseForm
          amount={amount}
          setAmount={setAmount}
          selectedCategory={category}
          onOpenCategory={() => setCatModalOpen(true)}
          onOpenTemplates={() => setTmplModalOpen(true)}
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
          onRefresh={loadAll}
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
              setUser(updatedUser)
              loadAll()
            }}
          />
        )}
      </AnimatePresence>
    </div>
  )
}
