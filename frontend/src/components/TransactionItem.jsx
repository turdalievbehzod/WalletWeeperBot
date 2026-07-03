import { fmtAmount } from '../utils/format'

export default function TransactionItem({ description, amount, onDelete }) {
  return (
    <div className="flex items-center gap-2 py-1">
      <div className="flex-1 bg-white rounded-full px-3 py-1.5 text-sm text-gray-700 truncate shadow-sm">
        {description}
      </div>
      <div className="bg-blue-500 rounded-full px-3 py-1.5 text-sm text-white font-medium whitespace-nowrap shadow-sm">
        {fmtAmount(amount)}
      </div>
      {onDelete && (
        <button
          onClick={onDelete}
          className="text-gray-300 hover:text-red-400 text-lg leading-none transition-colors flex-shrink-0"
        >
          ×
        </button>
      )}
    </div>
  )
}
