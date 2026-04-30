import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'
import wsService from '../api/websocket'

export const useSystemStore = defineStore('system', () => {
  const status = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const connected = ref(false)

  // 获取系统状态
  const fetchStatus = async () => {
    loading.value = true
    error.value = null
    try {
      const data = await api.getStatus()
      status.value = data
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // 初始化WebSocket
  const initWebSocket = () => {
    wsService.connect()
    wsService.on('connected', (isConnected) => {
      connected.value = isConnected
    })
  }

  return {
    status,
    loading,
    error,
    connected,
    fetchStatus,
    initWebSocket
  }
})
