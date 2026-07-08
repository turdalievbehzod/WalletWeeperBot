import client from './client'

// Auth
export const authTelegram = (initData, timezone) =>
  client.post('/auth/', { initData, timezone }).then(r => r.data)

// Carousel
export const getSummary = () =>
  client.get('/summary/').then(r => r.data)

// Main history (today / last week / last month)
export const getHistoryMain = () =>
  client.get('/history/main/').then(r => r.data)

// Detail views
export const getWeekDetails = () =>
  client.get('/history/week-details/').then(r => r.data)

export const getMonthDetails = () =>
  client.get('/history/month-details/').then(r => r.data)

// Categories CRUD
export const getCategories = () =>
  client.get('/categories/').then(r => r.data)

export const createCategory = (name, icon = '📌') =>
  client.post('/categories/', { name, icon }).then(r => r.data)

export const deleteCategory = id =>
  client.delete(`/categories/${id}/`)

// Templates CRUD
export const getTemplates = () =>
  client.get('/templates/').then(r => r.data)

export const createTemplate = (title, amount, categoryId) =>
  client.post('/templates/', {
    title,
    amount,
    category: categoryId || null,
    template_type: 'fixed',
  }).then(r => r.data)

export const deleteTemplate = id =>
  client.delete(`/templates/${id}/`)

// Transactions
export const createTransaction = (amount, categoryId, description = '') =>
  client.post('/expenses/', {
    amount,
    category: categoryId || null,
    description,
  }).then(r => r.data)

export const deleteTransaction = id =>
  client.delete(`/expenses/${id}/`)

// User profile
export const getExchangeRates = () =>
  client.get('/exchange-rates/').then(r => r.data)

export const updateProfile = (data) =>
  client.patch('/auth/me/', data).then(r => r.data)
