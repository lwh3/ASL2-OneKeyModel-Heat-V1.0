import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export const useTaskStore = defineStore('task', () => {
  const tasks = ref([])
  const loading = ref(false)
  const error = ref(null)

  const fetchTasks = async (params = {}) => {
    loading.value = true
    error.value = null
    try {
      const data = await api.getTasks(params)
      tasks.value = data.tasks || []
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    tasks,
    loading,
    error,
    fetchTasks
  }
})
