import { io } from 'socket.io-client'

class WebSocketService {
  constructor() {
    this.socket = null
    this.connected = false
    this.listeners = new Map()
  }

  connect(url = '') {
    if (this.connected) return

    this.socket = io(url || window.location.origin, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: 5,
    })

    this.socket.on('connect', () => {
      console.log('WebSocket connected')
      this.connected = true
      this.emit('connected', true)
    })

    this.socket.on('disconnect', () => {
      console.log('WebSocket disconnected')
      this.connected = false
      this.emit('connected', false)
    })

    this.socket.on('error', (error) => {
      console.error('WebSocket error:', error)
      this.emit('error', error)
    })

    // 订阅更新
    this.socket.emit('subscribe_updates')
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
      this.connected = false
    }
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event).push(callback)

    if (this.socket) {
      this.socket.on(event, callback)
    }
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event)
      const index = callbacks.indexOf(callback)
      if (index > -1) {
        callbacks.splice(index, 1)
      }
    }

    if (this.socket) {
      this.socket.off(event, callback)
    }
  }

  emit(event, data) {
    const callbacks = this.listeners.get(event) || []
    callbacks.forEach(callback => callback(data))
  }

  send(event, data) {
    if (this.socket && this.connected) {
      this.socket.emit(event, data)
    }
  }
}

export default new WebSocketService()
