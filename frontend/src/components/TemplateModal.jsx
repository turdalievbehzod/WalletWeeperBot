import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { createTemplate, deleteTemplate } from '../api/expenses'
import { fmtAmount } from '../utils/format'

export default function TemplateModal({ templates, onApply, onClose, onRefresh }) {
  const [showForm, setShowForm]   = useState(false)
  const [newTitle, setNewTitle]   = useState('')
  const [newAmount, setNewAmount] = useState('')
  const [saving, setSaving]       = useState(false)
  const [checkedId, setCheckedId] = useState(null)

  const handleAdd = async () => {
    const title  = newTitle.trim()
    const amount = parseFloat(newAmount)
    if (!title || !amount || amount <= 0) return
    setSaving(true)
    try {
      await createTemplate(title, amount, null)
      setNewTitle('')
      setNewAmount('')
      setShowForm(false)
      onRefresh()
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (e, id) => {
    e.stopPropagation()
    await deleteTemplate(id)
    if (checkedId === id) setCheckedId(null)
    onRefresh()
  }

  const handleCheck = (tpl) => {
    setCheckedId(prev => prev === tpl.id ? null : tpl.id)
  }

  const handleApply = () => {
    const tpl = templates.find(t => t.id === checkedId)
    if (tpl) {
      onApply(tpl)
      onClose()
    }
  }

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 z-40 flex items-end justify-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
      >
        {/* Backdrop */}
        <div
          className="absolute inset-0 bg-black/40 backdrop-blur-sm"
          onClick={onClose}
        />

        {/* Sheet */}
        <motion.div
          className="relative w-full max-w-sm rounded-t-3xl overflow-hidden"
          style={{ background: 'linear-gradient(160deg, #FFB84A, #FF8C20)' }}
          initial={{ y: '100%' }}
          animate={{ y: 0 }}
          exit={{ y: '100%' }}
          transition={{ type: 'spring', stiffness: 320, damping: 34 }}
        >
          {/* Header */}
          <div className="flex items-center justify-between px-5 pt-5 pb-3">
            <span className="text-white font-semibold text-base">Шаблоны</span>
            <button
              onClick={() => setShowForm(v => !v)}
              className="w-8 h-8 rounded-full bg-white/25 flex items-center justify-center text-white font-bold text-lg leading-none hover:bg-white/35 transition-colors"
            >
              +
            </button>
          </div>

          {/* Add-new form */}
          <AnimatePresence>
            {showForm && (
              <motion.div
                className="px-5 pb-3"
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.2 }}
              >
                <div className="flex gap-2">
                  <input
                    autoFocus
                    value={newTitle}
                    onChange={e => setNewTitle(e.target.value)}
                    placeholder="Введите товар"
                    className="flex-1 bg-white/20 text-white placeholder-white/60 rounded-xl px-3 py-2 text-sm min-w-0"
                  />
                  <input
                    type="number"
                    value={newAmount}
                    onChange={e => setNewAmount(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && handleAdd()}
                    placeholder="Цена"
                    className="w-24 bg-white/20 text-white placeholder-white/60 rounded-xl px-3 py-2 text-sm"
                  />
                  <button
                    onClick={handleAdd}
                    disabled={saving || !newTitle.trim() || !newAmount}
                    className="bg-white/30 text-white rounded-xl px-3 py-2 text-sm font-semibold disabled:opacity-50 hover:bg-white/40 transition-colors"
                  >
                    {saving ? '...' : 'OK'}
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Template list */}
          <div className="px-4 max-h-64 overflow-y-auto modal-scroll space-y-2">
            {templates.map(tpl => (
              <motion.div
                key={tpl.id}
                layout
                className={`flex items-center rounded-xl px-4 py-2.5 cursor-pointer transition-colors ${
                  tpl.id === checkedId
                    ? 'bg-white/30'
                    : 'bg-white/15 hover:bg-white/22'
                }`}
                onClick={() => handleCheck(tpl)}
              >
                <span className="flex-1 text-white text-sm font-medium truncate mr-2">
                  {tpl.title}
                </span>
                {tpl.amount && (
                  <span className="text-white/80 text-sm mr-3">
                    {fmtAmount(tpl.amount)}
                  </span>
                )}
                {tpl.id === checkedId && (
                  <span className="text-green-300 font-bold mr-2">✓</span>
                )}
                <button
                  onClick={e => handleDelete(e, tpl.id)}
                  className="text-white/60 hover:text-red-300 text-lg leading-none transition-colors"
                >
                  ×
                </button>
              </motion.div>
            ))}

            {templates.length === 0 && (
              <p className="text-white/70 text-sm text-center py-4">
                Нет шаблонов. Нажмите + чтобы создать.
              </p>
            )}
          </div>

          {/* Apply button */}
          {checkedId && (
            <motion.div
              className="px-5 pt-3 pb-6"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <button
                onClick={handleApply}
                className="w-full bg-white text-orange-500 font-semibold rounded-2xl py-3 text-sm hover:bg-orange-50 transition-colors"
              >
                Применить шаблон
              </button>
            </motion.div>
          )}

          {!checkedId && <div className="pb-6" />}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}
