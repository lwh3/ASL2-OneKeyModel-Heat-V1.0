import axios from 'axios'

// API基础URL配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

// 创建axios实例
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证token等
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default {
  // 系统状态
  getStatus() {
    return api.get('/status')
  },

  // 任务管理
  getTasks(params = {}) {
    return api.get('/tasks', { params })
  },

  // 历史数据
  getHistory(params = {}) {
    return api.get('/history', { params })
  },

  // 配置管理
  getConfig() {
    return api.get('/config')
  },

  updateConfig(data) {
    return api.post('/config', data)
  },

  // 算法
  getAlgorithms() {
    return api.get('/algorithms')
  },

  // 日志
  getLogs(params = {}) {
    return api.get('/logs', { params })
  },

  // 统计数据
  getStatistics(params = {}) {
    return api.get('/statistics', { params })
  },
}
