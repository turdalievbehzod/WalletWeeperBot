import { motion } from 'framer-motion'

/**
 * Shared page header — optional back button + title on the left, optional
 * hamburger menu button on the right. Used by every top-level page and
 * detail screen so there's exactly one place that owns this layout —
 * the old design had the currency/language buttons fixed-positioned over
 * everything, which overlapped page titles on narrow phones.
 */
export default function PageHeader({ title, onBack, onMenu, bg = '#FAF5EC' }) {
  return (
    <div
      className="sticky top-0 z-20 flex items-center justify-between gap-2 px-4 py-4"
      style={{ background: bg }}
    >
      <div className="flex items-center gap-3 min-w-0">
        {onBack && (
          <motion.button
            whileTap={{ scale: 0.92 }}
            onClick={onBack}
            className="w-9 h-9 flex-shrink-0 flex items-center justify-center rounded-full bg-blue-500 text-white shadow-sm"
          >
            ←
          </motion.button>
        )}
        <h2 className="text-base font-semibold text-gray-800 truncate">{title}</h2>
      </div>

      {onMenu && (
        <motion.button
          whileTap={{ scale: 0.92 }}
          onClick={onMenu}
          className="w-10 h-10 flex-shrink-0 flex items-center justify-center rounded-full bg-white shadow-md"
        >
          <span className="text-lg leading-none text-gray-700">☰</span>
        </motion.button>
      )}
    </div>
  )
}
