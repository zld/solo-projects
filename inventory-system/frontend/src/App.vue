<template>
  <el-container style="height: 100vh">
    <el-aside width="200px" style="background-color: #2f4050">
      <div style="padding: 20px; color: white; font-size: 18px; font-weight: bold; text-align: center; border-bottom: 1px solid #3d5166">
        仓库管理系统
      </div>
      <el-menu
        :default-active="activeMenu"
        background-color="#2f4050"
        text-color="#a7b1c2"
        active-text-color="#fff"
        router
      >
        <el-menu-item index="/">
          <el-icon><DataLine /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/items">
          <el-icon><Box /></el-icon>
          <span>物品管理</span>
        </el-menu-item>
        <el-menu-item index="/stock-in">
          <el-icon><Upload /></el-icon>
          <span>入库管理</span>
        </el-menu-item>
        <el-menu-item index="/borrow">
          <el-icon><Tickets /></el-icon>
          <span>借出/归还</span>
        </el-menu-item>
        <el-menu-item index="/approvals">
          <el-icon><CircleCheck />
            <el-badge v-if="pendingApprovals > 0" :value="pendingApprovals" class="badge" />
          </el-icon>
          <span>审批管理</span>
        </el-menu-item>
        <el-menu-item index="/records">
          <el-icon><Document /></el-icon>
          <span>操作记录</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="background-color: #fff; border-bottom: 1px solid #e6e6e6; display: flex; justify-content: space-between; align-items: center">
        <span style="font-size: 16px">{{ pageTitle }}</span>
        <span>当前用户: 管理员</span>
      </el-header>
      <el-main style="background-color: #f5f7fa; overflow-y: auto">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { DataLine, Box, Upload, Tickets, CircleCheck, Document } from '@element-plus/icons-vue'
import { alertsAPI } from './api'

const route = useRoute()
const pendingApprovals = ref(0)

const activeMenu = computed(() => route.path)
const pageTitle = computed(() => {
  const titles = {
    '/': '仪表盘',
    '/items': '物品管理',
    '/stock-in': '入库管理',
    '/borrow': '借出/归还管理',
    '/approvals': '审批管理',
    '/records': '操作记录'
  }
  return titles[route.path] || '仓库管理系统'
})

const fetchAlerts = async () => {
  try {
    const res = await alertsAPI.get()
    pendingApprovals.value = res.data.pending_approvals
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  fetchAlerts()
  setInterval(fetchAlerts, 30000)
})
</script>

<style scoped>
.badge :deep(.el-badge__content) {
  background-color: #f56c6c;
}
</style>
