import { motion } from 'framer-motion'
import TransactionItem from './TransactionItem'
import { fmtAmount } from '../utils/format'
import { useLanguage } from '../i18n/LanguageContext'

export default function WeekDetails({ days, onBack }) {
  const { t } = useLanguage()
  return (
    <div className="min-h-screen" style={{ background: '#FFF5C4' }}>
      {/* Back header */}
      <div className="sticky top-0 z-10 flex items-center gap-3 px-4 py-4"
           style={{ background: '#FFF5C4' }}>
        <motion.button
          whileTap={{ scale: 0.92 }}
          onClick={onBack}
          className="w-9 h-9 flex items-center justify-center rounded-full bg-blue-500 text-white shadow-sm"
        >
          ←
        </motion.button>
        <h2 className="text-base font-semibold text-gray-800">
          {t('weekDetails.title')}
        </h2>
      </div>

      <div className="px-4 pb-8 space-y-5">
        {days.length === 0 && (
          <p className="text-center text-gray-400 py-12 text-sm">
            {t('weekDetails.empty')}
          </p>
        )}

        {days.map((day, i) => (
          <motion.div
            key={day.date}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
          >
            {/* Day header */}
            <div className="flex items-center justify-between mb-2.5">
              <span className="bg-blue-500 text-white rounded-full px-3 py-1 text-xs font-semibold">
                {day.day_name}
              </span>
              <span className="bg-orange-500 text-white rounded-full px-3 py-1 text-xs font-semibold">
                {t('historySection.total', { amount: fmtAmount(day.total_sum) })}
              </span>
            </div>

            {/* Transactions */}
            <div className="space-y-1.5">
              {day.transactions.map(tx => (
                <TransactionItem
                  key={tx.id}
                  description={tx.description}
                  amount={tx.amount}
                />
              ))}
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
