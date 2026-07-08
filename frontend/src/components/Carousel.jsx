import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { fmtAmount } from '../utils/format'

const PERIODS = [
  { key: 'this_week',  label: 'За эту неделю' },
  { key: 'this_month', label: 'За этот месяц' },
  { key: 'this_year',  label: 'За этот год' },
]

const CIRCLE_SIZE = 160   // px, active circle diameter
const SIDE_SCALE  = 0.72  // side circles are 72% of active size

export default function Carousel({ summary, onCurrencyTap }) {
  const [activeIdx, setActiveIdx] = useState(1)   // start on "month"
  const [dragDir, setDragDir]     = useState(0)    // -1 left, +1 right

  const total = summary?.[PERIODS[activeIdx].key] ?? 0
  const currency = summary?.currency === 'UZS' ? 'сум' : summary?.currency ?? 'сум'

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
        Общие расходы
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
        {PERIODS.map((period, idx) => {
          const offset = idx - activeIdx
          const isActive = offset === 0
          const scale = isActive ? 1 : SIDE_SCALE
          const x = offset * (CIRCLE_SIZE * 0.9 + 16)
          const opacity = Math.abs(offset) > 1 ? 0 : isActive ? 1 : 0.65

          return (
            <motion.div
              key={period.key}
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
                    key={period.key}
                    className="flex flex-col items-center text-white text-center px-3"
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -8 }}
                    transition={{ duration: 0.2 }}
                  >
                    <span className="text-xs font-medium opacity-90 leading-tight">
                      {period.label}
                    </span>
                    <span className="text-2xl font-bold mt-1 leading-tight">
                      {fmtAmount(total)}
                    </span>
                    <button
                      onClick={e => { e.stopPropagation(); onCurrencyTap?.() }}
                      className="text-xs opacity-85 underline decoration-dotted underline-offset-2"
                    >
                      {currency}
                    </button>
                  </motion.div>
                </AnimatePresence>
              ) : (
                <span className="text-white text-xs font-medium text-center px-2 opacity-90 leading-tight">
                  {period.label}
                </span>
              )}
            </motion.div>
          )
        })}
      </motion.div>

      {/* Dot indicators */}
      <div className="flex gap-2 mt-3">
        {PERIODS.map((_, idx) => (
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
