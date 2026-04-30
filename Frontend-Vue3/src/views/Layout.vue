<template>
  <el-container class="layout-container">
    <el-aside width="200px" class="sidebar">
      <div class="logo">
        <h2>LF加热模型</h2>
      </div>
      <el-menu
        :default-active="currentRoute"
        class="el-menu-vertical"
        :router="true"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item
          v-for="route in menuRoutes"
          :key="route.path"
          :index="route.path"
        >
          <el-icon><component :is="route.meta.icon" /></el-icon>
          <template #title>{{ route.meta.title }}</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-content">
          <h3>{{ currentTitle }}</h3>
          <div class="header-right">
            <el-tag :type="connected ? 'success' : 'danger'" size="small">
              {{ connected ? '已连接' : '未连接' }}
            </el-tag>
            <span class="time">{{ currentTime }}</span>
          </div>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSystemStore } from '../store/system'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()
const systemStore = useSystemStore()

const currentTime = ref(dayjs().format('YYYY-MM-DD HH:mm:ss'))
const timer = ref(null)

const currentRoute = computed(() => route.path)
const connected = computed(() => systemStore.connected)

const menuRoutes = computed(() => {
  return router.options.routes[0].children || []
})

const currentTitle = computed(() => {
  const matched = menuRoutes.value.find(r => r.path === route.path.substring(1))
  return matched?.meta?.title || 'LF精炼炉加热模型监控系统'
})

onMounted(() => {
  systemStore.initWebSocket()
  timer.value = setInterval(() => {
    currentTime.value = dayjs().format('YYYY-MM-DD HH:mm:ss')
  }, 1000)
})

onUnmounted(() => {
  if (timer.value) {
    clearInterval(timer.value)
  }
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.sidebar {
  background-color: #304156;
  overflow: auto;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  border-bottom: 1px solid #1f2d3d;
}

.logo h2 {
  font-size: 18px;
  margin: 0;
}

.el-menu-vertical {
  border-right: none;
}

.header {
  background: white;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.time {
  color: #666;
  font-size: 14px;
}

.main-content {
  background: #f0f2f5;
  padding: 20px;
  overflow: auto;
}
</style>
