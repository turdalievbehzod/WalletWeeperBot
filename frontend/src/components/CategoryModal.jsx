import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { createCategory, deleteCategory } from '../api/expenses'

export default function CategoryModal({ categories, selectedId, onSelect, onClose, onRefresh }) {
  const [showForm, setShowForm] = useState(false)
  const [newName, setNewName]   = useState('')
  const [saving, setSaving]     = useState(false)

  const handleAdd = async () => {
    const name = newName.trim()
    if (!name) return
    setSaving(true)
    try {
      await createCategory(name)
      setNewName('')
      setShowForm(false)
      onRefresh()
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (e, id) => {
    e.stopPropagation()
    await deleteCategory(id)
    onRefresh()
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
          style={{ background: 'linear-gradient(160deg, #6B8FFF, #4A6EEF)' }}
          initial={{ y: '100%' }}
          animate={{ y: 0 }}
          exit={{ y: '100%' }}
          transition={{ type: 'spring', stiffness: 320, damping: 34 }}
        >
          {/* Header */}
          <div className="flex items-center justify-between px-5 pt-5 pb-3">
            <span className="text-white font-semibold text-base">Категории</span>
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
                    value={newName}
                    onChange={e => setNewName(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && handleAdd()}
                    placeholder="Название категории"
                    className="flex-1 bg-white/20 text-white placeholder-white/60 rounded-xl px-4 py-2 text-sm"
                  />
                  <button
                    onClick={handleAdd}
                    disabled={saving || !newName.trim()}
                    className="bg-white/30 text-white rounded-xl px-4 py-2 text-sm font-semibold disabled:opacity-50 hover:bg-white/40 transition-colors"
                  >
                    {saving ? '...' : 'OK'}
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Category list */}
          <div className="px-4 pb-6 max-h-64 overflow-y-auto modal-scroll space-y-2">
            {categories.map(cat => (
              <motion.div
                key={cat.id}
                layout
                className={`flex items-center rounded-xl px-4 py-2.5 cursor-pointer transition-colors ${
                  cat.id === selectedId
                    ? 'bg-white/30'
                    : 'bg-white/15 hover:bg-white/22'
                }`}
                onClick={() => { onSelect(cat); onClose() }}
              >
                <span className="mr-2 text-base">{cat.icon}</span>
                <span className="flex-1 text-white text-sm font-medium">{cat.name}</span>
                {cat.id === selectedId && (
                  <span className="text-green-300 font-bold mr-2">✓</span>
                )}
                {!cat.is_system && (
                  <button
                    onClick={e => handleDelete(e, cat.id)}
                    className="text-white/60 hover:text-red-300 text-lg leading-none ml-1 transition-colors"
                  >
                    ×
                  </button>
                )}
              </motion.div>
            ))}

            {categories.length === 0 && (
              <p className="text-white/60 text-sm text-center py-4">
                Нет категорий. Нажмите + чтобы добавить.
              </p>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}
