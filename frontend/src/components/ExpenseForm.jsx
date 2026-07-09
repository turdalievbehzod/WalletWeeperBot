import { useState } from 'react'
import { motion } from 'framer-motion'
import { useLanguage } from '../i18n/LanguageContext'

export default function ExpenseForm({
  amount, setAmount,
  selectedCategory, onOpenCategory,
  onOpenTemplates,
  onSubmit,
  submitting,
}) {
  const { t } = useLanguage()
  const canSubmit = amount && parseFloat(amount) > 0

  return (
    <div className="px-4 py-3 space-y-3">
      {/* Amount + Category row */}
      <div className="flex gap-3">
        {/* Amount input */}
        <div className="flex-1 flex items-center bg-white rounded-2xl shadow-sm border border-gray-100 px-4 h-12">
          <input
            type="number"
            inputMode="numeric"
            value={amount}
            onChange={e => setAmount(e.target.value)}
            placeholder={t('expenseForm.amountPlaceholder')}
            className="flex-1 text-sm text-gray-800 bg-transparent min-w-0"
          />
          {amount && parseFloat(amount) > 0 && (
            <span className="text-green-500 font-bold text-base ml-2">✓</span>
          )}
        </div>

        {/* Category selector */}
        <button
          onClick={onOpenCategory}
          className={`flex-1 flex items-center justify-between rounded-2xl px-4 h-12 shadow-sm border transition-colors ${
            selectedCategory
              ? 'bg-blue-500 border-blue-500'
              : 'bg-white border-gray-100'
          }`}
        >
          <span className={`text-sm font-medium truncate ${selectedCategory ? 'text-white' : 'text-gray-400'}`}>
            {selectedCategory
              ? `${selectedCategory.icon} ${selectedCategory.name}`
              : t('expenseForm.category')}
          </span>
          {selectedCategory && (
            <span className="text-green-300 font-bold ml-2">✓</span>
          )}
        </button>
      </div>

      {/* Add button */}
      <motion.button
        onClick={onSubmit}
        disabled={!canSubmit || submitting}
        whileTap={{ scale: 0.97 }}
        className={`w-full h-12 rounded-2xl text-white font-semibold text-sm shadow-sm transition-all ${
          canSubmit && !submitting
            ? 'bg-blue-500 hover:bg-blue-600 shadow-blue-200'
            : 'bg-gray-200 text-gray-400 cursor-not-allowed'
        }`}
      >
        {submitting ? t('expenseForm.adding') : t('expenseForm.add')}
      </motion.button>

      {/* Templates button */}
      <motion.button
        onClick={onOpenTemplates}
        whileTap={{ scale: 0.97 }}
        className="w-full h-12 rounded-2xl bg-blue-50 text-blue-500 font-semibold text-sm border border-blue-100 hover:bg-blue-100 transition-colors"
      >
        {t('expenseForm.chooseFromList')}
      </motion.button>
    </div>
  )
}
