<template>
  <div class="history-page">
    <el-card>
      <template #header>
        <div class="header">
          <span>历史数据</span>
          <el-space>
            <el-input v-model="steelGradeFilter" placeholder="钢种筛选" clearable style="width: 150px;" />
            <el-button type="primary" :icon="Search" @click="loadHistory">查询</el-button>
          </el-space>
        </div>
      </template>

      <el-table :data="history" v-loading="loading" stripe>
        <el-table-column prop="task_id" label="任务ID" width="180" />
        <el-table-column prop="steel_grade" label="钢种" width="100" />
        <el-table-column prop="heat_stage" label="加热阶段" width="120" />
        <el-table-column label="温度" width="180">
          <template #default="scope">
            {{ scope.row.start_temp }}°C → {{ scope.row.end_temp }}°C
          </template>
        </el-table-column>
        <el-table-column prop="heat_level" label="档位" width="80" />
        <el-table-column label="时长" width="120">
          <template #default="scope">
            {{ scope.row.heat_duration }}分钟
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.success ? 'success' : 'danger'" size="small">
              {{ scope.row.success ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="timestamp" label="时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.timestamp) }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import api from '../api'
import dayjs from 'dayjs'

const loading = ref(false)
const history = ref([])
const steelGradeFilter = ref('')

const formatDate = (date) => {
  return date ? dayjs(date).format('YYYY-MM-DD HH:mm:ss') : '-'
}

const loadHistory = async () => {
  loading.value = true
  try {
    const params = { limit: 100 }
    if (steelGradeFilter.value) {
      params.steel_grade = steelGradeFilter.value
    }
    const data = await api.getHistory(params)
    history.value = data.history || []
  } catch (error) {
    console.error('Failed to load history:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.history-page {
  width: 100%;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
