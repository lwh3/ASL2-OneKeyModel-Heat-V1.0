<template>
  <div class="tasks-page">
    <el-card>
      <template #header>
        <div class="header">
          <span>任务列表</span>
          <el-space>
            <el-select v-model="statusFilter" placeholder="状态筛选" @change="loadTasks">
              <el-option label="全部" value="all" />
              <el-option label="待处理" value="pending" />
              <el-option label="已完成" value="completed" />
            </el-select>
            <el-button type="primary" :icon="Refresh" @click="loadTasks">刷新</el-button>
          </el-space>
        </div>
      </template>

      <el-table :data="tasks" v-loading="loading" stripe>
        <el-table-column prop="task_id" label="任务ID" width="180" />
        <el-table-column prop="steel_grade" label="钢种" width="100" />
        <el-table-column prop="heat_stage" label="加热阶段" width="120" />
        <el-table-column label="温度范围" width="180">
          <template #default="scope">
            {{ scope.row.current_temp }}°C → {{ scope.row.target_temp }}°C
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag v-if="scope.row.start_flag === 0" type="info" size="small">未开始</el-tag>
            <el-tag v-else-if="!scope.row.output" type="warning" size="small">处理中</el-tag>
            <el-tag v-else-if="scope.row.output.finish_flag" type="success" size="small">已完成</el-tag>
            <el-tag v-else type="danger" size="small">错误</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="计算结果" min-width="200">
          <template #default="scope">
            <div v-if="scope.row.output">
              <div v-if="scope.row.output.error_code === 0">
                档位: <el-tag size="small">{{ scope.row.output.heat_level }}</el-tag>
                时长: <el-tag size="small">{{ scope.row.output.heat_duration }}分</el-tag>
                <br/>
                算法: {{ scope.row.output.algorithm_used }}
              </div>
              <el-text v-else type="danger">{{ scope.row.output.error_message }}</el-text>
            </div>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        @current-change="loadTasks"
        layout="total, prev, pager, next"
        style="margin-top: 20px; justify-content: center;"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import api from '../api'
import dayjs from 'dayjs'

const loading = ref(false)
const tasks = ref([])
const statusFilter = ref('all')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const formatDate = (date) => {
  return date ? dayjs(date).format('YYYY-MM-DD HH:mm:ss') : '-'
}

const loadTasks = async () => {
  loading.value = true
  try {
    const data = await api.getTasks({
      status: statusFilter.value,
      limit: pageSize.value
    })
    tasks.value = data.tasks || []
    total.value = data.count || 0
  } catch (error) {
    console.error('Failed to load tasks:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadTasks()
  setInterval(loadTasks, 5000) // 自动刷新
})
</script>

<style scoped>
.tasks-page {
  width: 100%;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
