<template>
  <div class="algorithms-page">
    <el-card>
      <template #header>
        <span>算法管理</span>
      </template>

      <el-descriptions :column="1" border v-loading="loading">
        <el-descriptions-item label="默认算法">
          <el-tag type="primary">{{ algorithms.default }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="启用算法">
          <el-space wrap>
            <el-tag v-for="alg in algorithms.enabled" :key="alg">{{ alg }}</el-tag>
          </el-space>
        </el-descriptions-item>
      </el-descriptions>

      <el-divider />

      <h3>算法1 - 历史数据预测</h3>
      <el-descriptions :column="2" border v-if="algorithms.algorithm1">
        <el-descriptions-item label="名称">{{ algorithms.algorithm1.name }}</el-descriptions-item>
        <el-descriptions-item label="精度">{{ algorithms.algorithm1.precision }}</el-descriptions-item>
        <el-descriptions-item label="最小历史记录" :span="2">
          {{ algorithms.algorithm1.min_historical_records }}
        </el-descriptions-item>
      </el-descriptions>

      <el-divider />

      <h3>算法2 - 公式计算</h3>
      <el-descriptions :column="2" border v-if="algorithms.algorithm2">
        <el-descriptions-item label="名称">{{ algorithms.algorithm2.name }}</el-descriptions-item>
        <el-descriptions-item label="精度">{{ algorithms.algorithm2.precision }}</el-descriptions-item>
        <el-descriptions-item label="基础系数" :span="2">
          {{ algorithms.algorithm2.formula_params?.base_coefficient }}
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const loading = ref(false)
const algorithms = ref({
  default: '',
  enabled: [],
  algorithm1: null,
  algorithm2: null
})

const loadAlgorithms = async () => {
  loading.value = true
  try {
    const data = await api.getAlgorithms()
    algorithms.value = data.algorithms || {}
  } catch (error) {
    console.error('Failed to load algorithms:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadAlgorithms()
})
</script>

<style scoped>
.algorithms-page {
  width: 100%;
}
</style>
