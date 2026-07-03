import { motion } from 'framer-motion'
import TransactionItem from './TransactionItem'
import { fmtAmount } from '../utils/format'

export default function MonthDetails({ weeks, onBack }) {
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
          За прошлый месяц
        </h2>
      </div>

      <div className="px-4 pb-8 space-y-5">
        {weeks.length === 0 && (
          <p className="text-center text-gray-400 py-12 text-sm">
            Расходов за прошлый месяц нет
          </p>
        )}

        {weeks.map((week, i) => (
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
                Итого: {fmtAmount(week.total_sum)}
              </span>
            </div>

            {/* Transactions */}
            <div className="space-y-1.5">
              {week.transactions.map(tx => (
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
