<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :xs="24" :sm="12" :md="6" v-for="stat in statistics" :key="stat.key">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" :style="{ backgroundColor: stat.color }">
              <el-icon :size="30"><component :is="stat.icon" /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :xs="24" :md="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>任务处理趋势</span>
            </div>
          </template>
          <v-chart :option="taskTrendOption" style="height: 300px;" />
        </el-card>
      </el-col>

      <el-col :xs="24" :md="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>钢种分布</span>
            </div>
          </template>
          <v-chart :option="steelGradeOption" style="height: 300px;" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最近任务</span>
              <el-button type="primary" size="small" @click="refreshTasks">刷新</el-button>
            </div>
          </template>
          <el-table :data="recentTasks" stripe v-loading="loading">
            <el-table-column prop="task_id" label="任务ID" width="150" />
            <el-table-column prop="steel_grade" label="钢种" width="120" />
            <el-table-column prop="heat_stage" label="阶段" width="120" />
            <el-table-column prop="current_temp" label="当前温度" width="120">
              <template #default="scope">{{ scope.row.current_temp }}°C</template>
            </el-table-column>
            <el-table-column prop="target_temp" label="目标温度" width="120">
              <template #default="scope">{{ scope.row.target_temp }}°C</template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="scope">
                <el-tag v-if="scope.row.output && scope.row.output.finish_flag" type="success" size="small">
                  已完成
                </el-tag>
                <el-tag v-else type="warning" size="small">处理中</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="结果" min-width="200">
              <template #default="scope">
                <span v-if="scope.row.output && scope.row.output.finish_flag">
                  档位: {{ scope.row.output.heat_level }},
                  时长: {{ scope.row.output.heat_duration }}分钟
                </span>
                <span v-else>-</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useSystemStore } from '../store/system'
import { useTaskStore } from '../store/task'
import api from '../api'

const systemStore = useSystemStore()
const taskStore = useTaskStore()

const loading = ref(false)
const recentTasks = ref([])

const statistics = computed(() => {
  const stats = systemStore.status?.statistics || {}
  return [
    {
      key: 'total',
      label: '总任务数',
      value: stats.total_tasks || 0,
      icon: 'DataLine',
      color: '#409EFF'
    },
    {
      key: 'pending',
      label: '待处理',
      value: stats.pending_tasks || 0,
      icon: 'Clock',
      color: '#E6A23C'
    },
    {
      key: 'completed',
      label: '已完成',
      value: stats.completed_tasks || 0,
      icon: 'CircleCheck',
      color: '#67C23A'
    },
    {
      key: 'error',
      label: '错误任务',
      value: stats.error_tasks || 0,
      icon: 'CircleClose',
      color: '#F56C6C'
    }
  ]
})

const taskTrendOption = reactive({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'] },
  yAxis: { type: 'value' },
  series: [{ data: [120, 200, 150, 80, 70, 110, 130], type: 'line', smooth: true }]
})

const steelGradeOption = reactive({
  tooltip: { trigger: 'item' },
  legend: { top: '5%', left: 'center' },
  series: [{
    name: '钢种',
    type: 'pie',
    radius: ['40%', '70%'],
    avoidLabelOverlap: false,
    itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
    label: { show: false, position: 'center' },
    emphasis: { label: { show: true, fontSize: 20, fontWeight: 'bold' } },
    labelLine: { show: false },
    data: [
      { value: 1048, name: '碳钢' },
      { value: 735, name: '合金钢' },
      { value: 580, name: '不锈钢' },
      { value: 484, name: '高温合金' }
    ]
  }]
})

const refreshTasks = async () => {
  loading.value = true
  try {
    await systemStore.fetchStatus()
    const data = await api.getTasks({ limit: 10 })
    recentTasks.value = data.tasks || []
  } catch (error) {
    console.error('Failed to refresh:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  refreshTasks()
  // 自动刷新
  setInterval(refreshTasks, 10000)
})
</script>

<style scoped>
.dashboard {
  width: 100%;
}

.stat-card {
  margin-bottom: 20px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
