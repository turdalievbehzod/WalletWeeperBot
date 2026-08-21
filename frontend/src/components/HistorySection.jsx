import { motion } from 'framer-motion'
import { fmtAmount } from '../utils/format'
import { useLanguage } from '../i18n/LanguageContext'

// ─── Скелетон одного блока периода ────────────────────────────────────────────
function SkeletonBlock() {
  return (
    <div className="space-y-2 animate-pulse">
      <div className="flex gap-3">
        <div className="flex-1 h-16 bg-gray-200 rounded-2xl" />
        <div className="flex-1 h-16 bg-gray-200 rounded-2xl" />
      </div>
      <div className="h-12 bg-gray-200 rounded-2xl" />
    </div>
  )
}

// ─── Один период (Сегодня / За прошлую неделю / За прошлый месяц) ────────────
function HistoryBlock({ label, block, loading, onDetails }) {
  const { t } = useLanguage()
  const income   = block?.income   ?? 0
  const expense  = block?.expense  ?? 0
  const balance  = block?.balance  ?? 0
  const hasData  = (block?.transactions?.length ?? 0) > 0

  return (
    <div className="mb-5">
      {/* Заголовок периода */}
      <div className="flex justify-center mb-2.5">
        <span className="bg-orange-500 text-white rounded-full px-4 py-1 text-xs font-semibold shadow-sm">
          {label}
        </span>
      </div>

      {loading ? (
        <SkeletonBlock />
      ) : (
        <>
          {/* Доход / Расход */}
          <div className="flex gap-3">
            <div className="flex-1 bg-blue-500 rounded-2xl px-3 py-2.5 text-center shadow-sm">
              <div className="text-white/80 text-xs font-medium">{t('historySection.incomeLabel')}</div>
              <div className="text-white text-base font-bold mt-0.5">{fmtAmount(income)}</div>
            </div>
            <div className="flex-1 bg-blue-500 rounded-2xl px-3 py-2.5 text-center shadow-sm">
              <div className="text-white/80 text-xs font-medium">{t('historySection.expenseLabel')}</div>
              <div className="text-white text-base font-bold mt-0.5">{fmtAmount(expense)}</div>
            </div>
          </div>

          {/* Остаток */}
          <div className="bg-blue-500 rounded-2xl px-3 py-2.5 text-center shadow-sm mt-2">
            <div className="text-white/80 text-xs font-medium">{t('historySection.balanceLabel')}</div>
            <div className="text-white text-base font-bold mt-0.5">{fmtAmount(balance)}</div>
          </div>

          {!hasData && (
            <p className="text-sm text-gray-400 text-center py-3">{t('historySection.empty')}</p>
          )}
        </>
      )}

      {/* Кнопка «Подробнее» — только если есть данные и колбэк */}
      {onDetails && hasData && !loading && (
        <div className="flex justify-center mt-3">
          <motion.button
            whileTap={{ scale: 0.95 }}
            onClick={onDetails}
            className="bg-blue-500 text-white rounded-full px-6 py-1.5 text-xs font-semibold
                       hover:bg-blue-600 transition-colors shadow-sm"
          >
            {t('historySection.more')}
          </motion.button>
        </div>
      )}
    </div>
  )
}

// ─── Декоративный разделитель (линия + точка) ─────────────────────────────────
function Divider() {
  return (
    <div className="flex items-center gap-2 my-4">
      <div className="flex-1 h-px bg-blue-100" />
      <div className="w-2 h-2 rounded-full bg-blue-300 flex-shrink-0" />
      <div className="flex-1 h-px bg-blue-100" />
    </div>
  )
}

// ─── Основной компонент ────────────────────────────────────────────────────────
export default function HistorySection({ history, loading, onWeekDetails, onMonthDetails }) {
  const { t } = useLanguage()
  // Блок всегда рендерится — скелетон показывается при loading=true
  return (
    <div className="px-4 py-2">

      {/* Заголовок секции */}
      <div className="flex justify-center mb-4">
        <span className="bg-blue-500 text-white rounded-full px-5 py-1.5 text-sm font-semibold shadow-sm">
          {t('historySection.title')}
        </span>
      </div>

      <Divider />

      <HistoryBlock
        label={t('historySection.today')}
        block={history?.today}
        loading={loading}
      />

      <Divider />

      <HistoryBlock
        label={t('historySection.lastWeek')}
        block={history?.last_week}
        loading={loading}
        onDetails={onWeekDetails}
      />

      <Divider />

      <HistoryBlock
        label={t('historySection.lastMonth')}
        block={history?.last_month}
        loading={loading}
        onDetails={onMonthDetails}
      />
    </div>
  )
}
