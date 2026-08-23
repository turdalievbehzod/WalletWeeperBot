import { useState } from 'react'
import { motion } from 'framer-motion'
import PageHeader from './PageHeader'
import TransactionItem from './TransactionItem'
import TypeToggle from './TypeToggle'
import { fmtAmount } from '../utils/format'
import { deleteTransaction } from '../api/expenses'
import { useLanguage } from '../i18n/LanguageContext'

/**
 * "Подробнее" for the Today block — unlike WeekDetails/MonthDetails there's
 * no grouping (it's a single day), just the itemized list filtered by the
 * Доход/Расход toggle, with a running Остаток unaffected by the toggle.
 */
export default function TodayDetails({ block, onBack, onRefresh, onMenu }) {
  const { t } = useLanguage()
  const [filterType, setFilterType] = useState('expense')

  const transactions = block?.transactions ?? []
  const items = transactions.filter(tx => tx.type === filterType)
  const typeTotal = filterType === 'income' ? (block?.income ?? 0) : (block?.expense ?? 0)
  const balance = block?.balance ?? 0

  const handleDelete = async (id) => {
    await deleteTransaction(id)
    onRefresh?.()
  }

  return (
    <div className="min-h-screen" style={{ background: '#FFF5C4' }}>
      <PageHeader title={t('historySection.today')} onBack={onBack} onMenu={onMenu} bg="#FFF5C4" />

      <div className="px-4 pb-3">
        <TypeToggle value={filterType} onChange={setFilterType} />
      </div>

      <div className="px-4 pb-8">
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex justify-end mb-2.5">
            <span className="bg-orange-500 text-white rounded-full px-3 py-1 text-xs font-semibold">
              {t('historySection.total', { amount: fmtAmount(typeTotal) })}
            </span>
          </div>

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
              <p className="text-sm text-gray-400 text-center py-3">{t('historySection.empty')}</p>
            )}
          </div>

          <div className="bg-blue-500 rounded-2xl px-3 py-2.5 text-center shadow-sm mt-3">
            <div className="text-white/80 text-xs font-medium">{t('historySection.balanceLabel')}</div>
            <div className="text-white text-base font-bold">{fmtAmount(balance)}</div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
