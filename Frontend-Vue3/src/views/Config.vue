<template>
  <div class="config-page">
    <el-card>
      <template #header>
        <span>系统配置</span>
      </template>

      <el-table :data="configs" v-loading="loading" stripe>
        <el-table-column prop="key" label="配置键" width="300" />
        <el-table-column prop="value" label="配置值" min-width="200">
          <template #default="scope">
            <el-input v-model="scope.row.value" size="small" />
          </template>
        </el-table-column>
        <el-table-column prop="description" label="说明" min-width="200" />
        <el-table-column label="操作" width="120">
          <template #default="scope">
            <el-button type="primary" size="small" @click="updateConfig(scope.row)">
              保存
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const loading = ref(false)
const configs = ref([])

const loadConfigs = async () => {
  loading.value = true
  try {
    const data = await api.getConfig()
    configs.value = data.configs || []
  } catch (error) {
    console.error('Failed to load configs:', error)
  } finally {
    loading.value = false
  }
}

const updateConfig = async (config) => {
  try {
    await api.updateConfig({
      key: config.key,
      value: config.value
    })
    ElMessage.success('配置更新成功')
  } catch (error) {
    ElMessage.error('配置更新失败')
    console.error('Failed to update config:', error)
  }
}

onMounted(() => {
  loadConfigs()
})
</script>

<style scoped>
.config-page {
  width: 100%;
}
</style>
