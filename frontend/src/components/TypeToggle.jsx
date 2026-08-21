import { motion } from 'framer-motion'
import { useLanguage } from '../i18n/LanguageContext'

/**
 * Segmented Доход/Расход switch — shared by ExpenseForm (which type is being
 * added) and WeekDetails/MonthDetails (which type's items are shown).
 */
export default function TypeToggle({ value, onChange, className = '' }) {
  const { t } = useLanguage()
  const isIncome = value === 'income'

  return (
    <div className={`relative flex bg-gray-100 rounded-2xl p-1 ${className}`}>
      <motion.div
        className="absolute top-1 bottom-1 w-[calc(50%-4px)] rounded-xl shadow-sm"
        style={{ background: isIncome ? '#5C7EFF' : '#FF9F43' }}
        animate={{ x: isIncome ? 0 : '100%' }}
        transition={{ type: 'spring', stiffness: 400, damping: 32 }}
      />
      <button
        onClick={() => onChange('income')}
        className={`relative z-10 flex-1 h-10 rounded-xl text-sm font-semibold transition-colors ${
          isIncome ? 'text-white' : 'text-gray-500'
        }`}
      >
        {t('typeToggle.income')}
      </button>
      <button
        onClick={() => onChange('expense')}
        className={`relative z-10 flex-1 h-10 rounded-xl text-sm font-semibold transition-colors ${
          !isIncome ? 'text-white' : 'text-gray-500'
        }`}
      >
        {t('typeToggle.expense')}
      </button>
    </div>
  )
}
