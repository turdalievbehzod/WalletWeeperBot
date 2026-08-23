import { useState } from 'react'
import { motion } from 'framer-motion'
import PageHeader from './PageHeader'
import TransactionItem from './TransactionItem'
import TypeToggle from './TypeToggle'
import { fmtAmount } from '../utils/format'
import { deleteTransaction } from '../api/expenses'
import { useLanguage } from '../i18n/LanguageContext'

export default function MonthDetails({ weeks, onBack, onRefresh, onMenu }) {
  const { t } = useLanguage()
  const [filterType, setFilterType] = useState('expense')

  const handleDelete = async (id) => {
    await deleteTransaction(id)
    onRefresh?.()
  }

  return (
    <div className="min-h-screen" style={{ background: '#FFF5C4' }}>
      <PageHeader title={t('monthDetails.title')} onBack={onBack} onMenu={onMenu} bg="#FFF5C4" />

      <div className="px-4 pb-3">
        <TypeToggle value={filterType} onChange={setFilterType} />
      </div>

      <div className="px-4 pb-8 space-y-5">
        {weeks.length === 0 && (
          <p className="text-center text-gray-400 py-12 text-sm">
            {t('monthDetails.empty')}
          </p>
        )}

        {weeks.map((week, i) => {
          const items = week.transactions.filter(tx => tx.type === filterType)
          const typeTotal = filterType === 'income' ? week.income_total : week.expense_total

          return (
            <motion.div
              key={week.week_num}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
            >
              {/* Week header */}
              <div className="flex items-center justify-between mb-2.5">
                <span className="bg-blue-500 text-white rounded-full px-3 py-1 text-xs font-semibold">
                  {week.week_label}
                </span>
                <span className="bg-orange-500 text-white rounded-full px-3 py-1 text-xs font-semibold">
                  {t('historySection.total', { amount: fmtAmount(typeTotal) })}
                </span>
              </div>

              {/* Transactions of the selected type */}
              <div className="space-y-1.5">
                {items.length > 0 ? (
                  items.map(tx => (
                    <TransactionItem
                      key={tx.id}
                      description={tx.description}
                      amount={tx.amount}
                      onDelete={() => handleDelete(tx.id)}
                    />
                  ))
                ) : (
                  <p className="text-xs text-gray-400 text-center py-2">{t('historySection.empty')}</p>
                )}
              </div>

              {/* Остаток за неделю — доход минус расход, вне зависимости от переключателя */}
              <div className="bg-blue-500 rounded-2xl px-3 py-2 text-center shadow-sm mt-2.5">
                <div className="text-white/80 text-xs font-medium">{t('historySection.balanceLabel')}</div>
                <div className="text-white text-sm font-bold">{fmtAmount(week.balance)}</div>
              </div>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
