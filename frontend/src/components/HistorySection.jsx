import { motion } from 'framer-motion'
import TransactionItem from './TransactionItem'
import { fmtAmount } from '../utils/format'
import { deleteTransaction } from '../api/expenses'

// ─── Скелетон одной строки транзакции ────────────────────────────────────────
function SkeletonRow() {
  return (
    <div className="flex items-center gap-2 py-1 animate-pulse">
      <div className="flex-1 h-8 bg-gray-200 rounded-full" />
      <div className="w-20 h-8 bg-gray-200 rounded-full" />
    </div>
  )
}

// ─── Один период (Сегодня / За прошлую неделю / За прошлый месяц) ────────────
function HistoryBlock({ label, block, loading, onDetails, onRefresh }) {
  const transactions = block?.transactions ?? []
  const totalSum     = block?.total_sum    ?? 0

  const handleDelete = async (id) => {
    await deleteTransaction(id)
    onRefresh?.()
  }

  return (
    <div className="mb-5">
      {/* Заголовок периода */}
      <div className="flex items-center justify-between mb-2.5">
        <span className="bg-orange-500 text-white rounded-full px-3 py-1 text-xs font-semibold shadow-sm">
          {label}
        </span>
        <span className="bg-orange-500 text-white rounded-full px-3 py-1 text-xs font-semibold shadow-sm">
          {loading ? '...' : `Итого: ${fmtAmount(totalSum)}`}
        </span>
      </div>

      {/* Список транзакций */}
      <div className="space-y-1.5">
        {loading ? (
          <>
            <SkeletonRow />
            <SkeletonRow />
            <SkeletonRow />
          </>
        ) : transactions.length > 0 ? (
          transactions.slice(0, 4).map(tx => (
            <TransactionItem
              key={tx.id}
              description={tx.description}
              amount={tx.amount}
              onDelete={() => handleDelete(tx.id)}
            />
          ))
        ) : (
          <p className="text-sm text-gray-400 text-center py-3">Нет записей</p>
        )}
      </div>

      {/* Кнопка «Подробнее» — только если есть данные и колбэк */}
      {onDetails && transactions.length > 0 && (
        <div className="flex justify-center mt-3">
          <motion.button
            whileTap={{ scale: 0.95 }}
            onClick={onDetails}
            className="bg-blue-500 text-white rounded-full px-6 py-1.5 text-xs font-semibold
                       hover:bg-blue-600 transition-colors shadow-sm"
          >
            Подробнее
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
export default function HistorySection({ history, loading, onWeekDetails, onMonthDetails, onRefresh }) {
  // Блок всегда рендерится — скелетон показывается при loading=true
  return (
    <div className="px-4 py-2">

      {/* Заголовок секции */}
      <div className="flex justify-center mb-4">
        <span className="bg-blue-500 text-white rounded-full px-5 py-1.5 text-sm font-semibold shadow-sm">
          История расходов
        </span>
      </div>

      <Divider />

      <HistoryBlock
        label="Сегодня"
        block={history?.today}
        loading={loading}
        onRefresh={onRefresh}
      />

      <Divider />

      <HistoryBlock
        label="За прошлую неделю"
        block={history?.last_week}
        loading={loading}
        onDetails={onWeekDetails}
        onRefresh={onRefresh}
      />

      <Divider />

      <HistoryBlock
        label="За прошлый месяц"
        block={history?.last_month}
        loading={loading}
        onDetails={onMonthDetails}
        onRefresh={onRefresh}
      />
    </div>
  )
}
