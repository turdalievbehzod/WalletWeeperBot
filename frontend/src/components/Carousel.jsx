import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { fmtAmount } from '../utils/format'
import { useLanguage } from '../i18n/LanguageContext'

const PERIOD_KEYS = ['this_week', 'this_month', 'this_year']

const CIRCLE_SIZE = 160   // px, active circle diameter
const SIDE_SCALE  = 0.72  // side circles are 72% of active size

export default function Carousel({ summary, onCurrencyTap, onLanguageTap }) {
  const { t, language } = useLanguage()
  const [activeIdx, setActiveIdx] = useState(1)   // start on "month"
  const [dragDir, setDragDir]     = useState(0)    // -1 left, +1 right

  const total = summary?.[PERIOD_KEYS[activeIdx]] ?? 0
  const currency = summary?.currency === 'UZS' ? t('carousel.uzsLabel') : summary?.currency ?? t('carousel.uzsLabel')

  const goTo = idx => {
    if (idx < 0 || idx > 2) return
    setDragDir(idx > activeIdx ? -1 : 1)
    setActiveIdx(idx)
  }

  const handleDragEnd = (_, info) => {
    if (info.offset.x < -60) goTo(activeIdx + 1)
    else if (info.offset.x > 60) goTo(activeIdx - 1)
  }

  return (
    <div className="flex flex-col items-center py-6 select-none">
      {/* Title */}
      <h2 className="text-sm font-medium text-gray-500 mb-4 tracking-wide uppercase">
        {t('carousel.title')}
      </h2>

      {/* Circles track */}
      <motion.div
        className="relative flex items-center justify-center w-full overflow-hidden"
        style={{ height: CIRCLE_SIZE + 24 }}
        drag="x"
        dragConstraints={{ left: 0, right: 0 }}
        dragElastic={0.15}
        onDragEnd={handleDragEnd}
      >
        {PERIOD_KEYS.map((periodKey, idx) => {
          const offset = idx - activeIdx
          const isActive = offset === 0
          const scale = isActive ? 1 : SIDE_SCALE
          const x = offset * (CIRCLE_SIZE * 0.9 + 16)
          const opacity = Math.abs(offset) > 1 ? 0 : isActive ? 1 : 0.65

          return (
            <motion.div
              key={periodKey}
              className="absolute flex flex-col items-center justify-center rounded-full cursor-pointer"
              style={{
                width:  CIRCLE_SIZE,
                height: CIRCLE_SIZE,
                background: isActive
                  ? 'linear-gradient(145deg, #FF9F43, #FF7B1E)'
                  : 'linear-gradient(145deg, #7B9FF5, #5C7EFF)',
                boxShadow: isActive
                  ? '0 8px 32px rgba(255,159,67,0.45)'
                  : '0 4px 16px rgba(92,126,255,0.30)',
              }}
              animate={{ x, scale, opacity }}
              transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              onClick={() => !isActive && goTo(idx)}
            >
              {isActive ? (
                <AnimatePresence mode="wait">
                  <motion.div
                    key={periodKey}
                    className="flex flex-col items-center text-white text-center px-3"
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -8 }}
                    transition={{ duration: 0.2 }}
                  >
                    <span className="text-xs font-medium opacity-90 leading-tight">
                      {t(`carousel.periods.${periodKey}`)}
                    </span>
                    <span className="text-2xl font-bold mt-1 leading-tight">
                      {fmtAmount(total)}
                    </span>
                    <div className="mt-1.5 flex items-center gap-1">
                      <button
                        onClick={e => { e.stopPropagation(); onCurrencyTap?.() }}
                        className="flex items-center gap-1 pl-2.5 pr-2 py-1 rounded-full bg-white/25 active:bg-white/40 text-white text-xs font-semibold leading-none"
                      >
                        <span>{currency}</span>
                        <span className="text-[10px] opacity-90">⇄</span>
                      </button>
                      <button
                        onClick={e => { e.stopPropagation(); onLanguageTap?.() }}
                        className="flex items-center justify-center w-6 h-6 rounded-full bg-white/25 active:bg-white/40 text-white text-xs leading-none"
                      >
                        {language === 'en' ? '🇬🇧' : '🇷🇺'}
                      </button>
                    </div>
                  </motion.div>
                </AnimatePresence>
              ) : (
                <span className="text-white text-xs font-medium text-center px-2 opacity-90 leading-tight">
                  {t(`carousel.periods.${periodKey}`)}
                </span>
              )}
            </motion.div>
          )
        })}
      </motion.div>

      {/* Dot indicators */}
      <div className="flex gap-2 mt-3">
        {PERIOD_KEYS.map((_, idx) => (
          <button
            key={idx}
            onClick={() => goTo(idx)}
            className={`rounded-full transition-all duration-200 ${
              idx === activeIdx
                ? 'w-5 h-2 bg-orange-500'
                : 'w-2 h-2 bg-gray-300'
            }`}
          />
        ))}
      </div>
    </div>
  )
}
