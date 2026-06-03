import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

let getCurrentUserId = () => 1

export function setUserIdGetter(fn) {
  getCurrentUserId = fn
}

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 403) {
      ElMessage.error(error.response.data?.detail || '权限不足，无法执行此操作')
    }
    return Promise.reject(error)
  }
)

function appendOperatorId(params = {}) {
  return { ...params, operator_id: getCurrentUserId() }
}

export const itemsAPI = {
  list: (params) => api.get('/items', { params: appendOperatorId(params) }),
  get: (id) => api.get(`/items/${id}`, { params: { operator_id: getCurrentUserId() } }),
  create: (data) => api.post('/items', data, { params: { operator_id: getCurrentUserId() } }),
  update: (id, data) => api.put(`/items/${id}`, data, { params: { operator_id: getCurrentUserId() } })
}

export const stockAPI = {
  stockIn: (data) => api.post('/stock/in', data),
  records: (params) => api.get('/stock-records', { params: appendOperatorId(params) })
}

export const borrowAPI = {
  borrow: (data) => api.post('/borrow', data),
  returnItem: (data) => api.post('/return', data),
  records: (params) => api.get('/borrow-records', { params: appendOperatorId(params) })
}

export const approvalAPI = {
  list: (params) => api.get('/approvals', { params: appendOperatorId(params) }),
  process: (id, data) => api.post(`/approvals/${id}/process`, data)
}

export const logsAPI = {
  list: (params) => api.get('/operation-logs', { params: { ...appendOperatorId(params), viewer_id: getCurrentUserId() } })
}

export const alertsAPI = {
  get: () => api.get('/alerts', { params: { operator_id: getCurrentUserId() } })
}

export const usersAPI = {
  list: (params) => api.get('/users', { params: appendOperatorId(params) }),
  get: (id) => api.get(`/users/${id}`, { params: { operator_id: getCurrentUserId() } }),
  switchable: () => api.get('/users/switchable'),
  create: (data) => api.post('/users', data, { params: { operator_id: getCurrentUserId() } }),
  update: (id, data) => api.put(`/users/${id}`, data, { params: { operator_id: getCurrentUserId() } }),
  delete: (id) => api.delete(`/users/${id}`, { params: { operator_id: getCurrentUserId() } })
}

export default api
