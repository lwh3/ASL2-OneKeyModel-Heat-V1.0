<template>
  <div class="logs-page">
    <el-card>
      <template #header>
        <div class="header">
          <span>系统日志</span>
          <el-space>
            <el-input-number v-model="lines" :min="10" :max="1000" :step="10" size="small" />
            <el-button type="primary" :icon="Refresh" @click="loadLogs">刷新</el-button>
          </el-space>
        </div>
      </template>

      <div class="logs-container" v-loading="loading">
        <pre class="logs-content">{{ logsText }}</pre>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import api from '../api'

const loading = ref(false)
const logs = ref([])
const lines = ref(100)

const logsText = computed(() => {
  return logs.value.join('')
})

const loadLogs = async () => {
  loading.value = true
  try {
    const data = await api.getLogs({ lines: lines.value })
    logs.value = data.logs || []
  } catch (error) {
    console.error('Failed to load logs:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadLogs()
  setInterval(loadLogs, 10000) // 自动刷新
})
</script>

<style scoped>
.logs-page {
  width: 100%;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logs-container {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 15px;
  border-radius: 4px;
  max-height: 600px;
  overflow: auto;
}

.logs-content {
  margin: 0;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 12px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
