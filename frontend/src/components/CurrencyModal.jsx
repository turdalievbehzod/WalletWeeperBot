import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { getExchangeRates, updateProfile } from '../api/expenses'
import { fmtAmount } from '../utils/format'
import { useLanguage } from '../i18n/LanguageContext'

const CURRENCY_CODES = ['UZS', 'USD', 'EUR', 'RUB']
const FLAGS = { UZS: '🇺🇿', USD: '🇺🇸', EUR: '🇪🇺', RUB: '🇷🇺' }

export default function CurrencyModal({ currentCurrency, onClose, onChanged }) {
  const { t } = useLanguage()
  const [rates, setRates]       = useState(null)
  const [selected, setSelected] = useState(currentCurrency)
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState(null)

  useEffect(() => {
    getExchangeRates()
      .then(d => setRates(d.rates))
      .catch(() => setError(t('currencyModal.loadError')))
  }, [])  // eslint-disable-line react-hooks/exhaustive-deps

  const getRate = (from, to) => {
    if (!rates || !rates[from] || !rates[to]) return null
    return rates[to] / rates[from]
  }

  const handleApply = async () => {
    if (selected === currentCurrency) { onClose(); return }
    setLoading(true)
    try {
      const user = await updateProfile({ currency: selected })
      onChanged(user)
      onClose()
    } catch {
      setError(t('currencyModal.changeError'))
    } finally {
      setLoading(false)
    }
  }

  const previewRate = selected !== currentCurrency ? getRate(currentCurrency, selected) : null

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 z-50 flex items-end justify-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
      >
        {/* Backdrop */}
        <div className="absolute inset-0 bg-black/40" onClick={onClose} />

        {/* Sheet */}
        <motion.div
          className="relative w-full max-w-sm bg-white rounded-t-3xl p-6 pb-10 z-10"
          initial={{ y: '100%' }}
          animate={{ y: 0 }}
          exit={{ y: '100%' }}
          transition={{ type: 'spring', stiffness: 320, damping: 32 }}
        >
          <div className="w-10 h-1 bg-gray-200 rounded-full mx-auto mb-5" />
          <h2 className="text-lg font-bold text-gray-800 mb-1">{t('currencyModal.title')}</h2>
          <p className="text-sm text-gray-500 mb-4">{t('currencyModal.description')}</p>

          {error && (
            <p className="text-red-500 text-sm mb-3">{error}</p>
          )}

          {/* Currency list */}
          <div className="space-y-2 mb-5">
            {CURRENCY_CODES.map(code => {
              const rate = rates ? getRate('USD', code) : null
              const isActive = selected === code
              return (
                <button
                  key={code}
                  onClick={() => setSelected(code)}
                  className={`w-full flex items-center justify-between px-4 py-3 rounded-2xl border-2 transition-all ${
                    isActive
                      ? 'border-orange-400 bg-orange-50'
                      : 'border-gray-100 bg-gray-50'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{FLAGS[code]}</span>
                    <div className="text-left">
                      <p className={`font-semibold text-sm ${isActive ? 'text-orange-600' : 'text-gray-800'}`}>
                        {code}
                      </p>
                      <p className="text-xs text-gray-500">{t(`currencyModal.names.${code}`)}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    {rate ? (
                      <p className="text-xs text-gray-500">
                        {t('currencyModal.rateLabel', { rate: fmtAmount(rate), code })}
                      </p>
                    ) : (
                      <p className="text-xs text-gray-400">...</p>
                    )}
                    {isActive && (
                      <span className="text-orange-500 text-xs font-bold">✓</span>
                    )}
                  </div>
                </button>
              )
            })}
          </div>

          {/* Conversion preview */}
          {previewRate && (
            <div className="bg-blue-50 rounded-2xl px-4 py-3 mb-4 text-center">
              <p className="text-xs text-blue-500 mb-1">
                {t('currencyModal.previewLabel', { currency: currentCurrency })}
              </p>
              <p className="text-base font-bold text-blue-700">
                {fmtAmount(1000 * previewRate)} {selected}
              </p>
            </div>
          )}

          <button
            onClick={handleApply}
            disabled={loading}
            className="w-full py-3.5 rounded-2xl bg-orange-500 text-white font-bold text-base disabled:opacity-60"
          >
            {loading
              ? t('currencyModal.applying')
              : selected === currentCurrency
                ? t('currencyModal.close')
                : t('currencyModal.switchTo', { code: selected })}
          </button>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}
