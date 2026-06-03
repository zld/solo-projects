import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

export const itemsAPI = {
  list: (params) => api.get('/items', { params }),
  get: (id) => api.get(`/items/${id}`),
  create: (data) => api.post('/items', data),
  update: (id, data) => api.put(`/items/${id}`, data)
}

export const stockAPI = {
  stockIn: (data) => api.post('/stock/in', data),
  records: (params) => api.get('/stock-records', { params })
}

export const borrowAPI = {
  borrow: (data) => api.post('/borrow', data),
  returnItem: (data) => api.post('/return', data),
  records: (params) => api.get('/borrow-records', { params })
}

export const approvalAPI = {
  list: (params) => api.get('/approvals', { params }),
  process: (id, data) => api.post(`/approvals/${id}/process`, data)
}

export const logsAPI = {
  list: (params) => api.get('/operation-logs', { params })
}

export const alertsAPI = {
  get: () => api.get('/alerts')
}

export const usersAPI = {
  list: () => api.get('/users')
}

export default api
