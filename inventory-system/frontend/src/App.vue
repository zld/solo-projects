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
        <el-menu-item v-for="menu in accessibleMenus" :key="menu.path" :index="menu.path">
          <el-icon><component :is="menu.iconComp" /></el-icon>
          <span>{{ menu.label }}</span>
          <el-badge v-if="menu.path === '/approvals' && pendingApprovals > 0" :value="pendingApprovals" class="badge" style="margin-left: 5px" />
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="background-color: #fff; border-bottom: 1px solid #e6e6e6; display: flex; justify-content: space-between; align-items: center">
        <span style="font-size: 16px">{{ pageTitle }}</span>
        <div style="display: flex; align-items: center; gap: 12px">
          <el-dropdown @command="switchUser">
            <span style="cursor: pointer; display: flex; align-items: center; gap: 6px">
              <el-avatar :size="28" style="background-color: #409eff">{{ currentUserName.charAt(0) }}</el-avatar>
              <span style="font-size: 14px; color: #606266">{{ currentUserName }}</span>
              <el-tag size="small" :type="currentUserRole === 'admin' ? 'danger' : currentUserRole === 'approver' ? 'warning' : 'info'">{{ roleLabel }}</el-tag>
              <el-icon style="color: #909399"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item v-for="u in activeUsers" :key="u.id" :command="u.id" :disabled="u.id === currentUserId">
                  {{ u.name }} ({{ u.username }}) - {{ u.role === 'admin' ? '管理员' : u.role === 'approver' ? '审批员' : '普通用户' }}
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main style="background-color: #f5f7fa; overflow-y: auto">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted, provide, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { DataLine, Box, Upload, Tickets, CircleCheck, Document, User, ArrowDown } from '@element-plus/icons-vue'
import { alertsAPI, usersAPI, setUserIdGetter } from './api'
import { getAccessibleMenus, hasPermission, canAccessRoute } from './utils/permissions'
import { authState } from './router'

const route = useRoute()
const router = useRouter()
const pendingApprovals = ref(0)
const currentUserId = ref(1)
const currentUserObj = ref({ name: '管理员', role: 'admin', is_active: true })
const allUsers = ref([])

const iconMap = {
  DataLine, Box, Upload, Tickets, CircleCheck, User, Document
}

const currentUser = computed(() => currentUserObj.value)
const currentUserName = computed(() => currentUserObj.value.name)
const currentUserRole = computed(() => currentUserObj.value.role)
const roleLabel = computed(() => {
  const map = { admin: '管理员', approver: '审批员', user: '普通用户' }
  return map[currentUserRole.value] || '普通用户'
})
const activeUsers = computed(() => allUsers.value.filter(u => u.is_active !== false))

const accessibleMenus = computed(() => {
  const menus = getAccessibleMenus(currentUserRole.value)
  return menus.map(m => ({ ...m, iconComp: iconMap[m.icon] }))
})

const activeMenu = computed(() => route.path)
const pageTitle = computed(() => {
  const titles = {
    '/': '仪表盘',
    '/items': '物品管理',
    '/stock-in': '入库管理',
    '/borrow': '借出/归还管理',
    '/approvals': '审批管理',
    '/users': '用户管理',
    '/records': '操作记录'
  }
  return titles[route.path] || '仓库管理系统'
})

setUserIdGetter(() => currentUserId.value)

const fetchAlerts = async () => {
  try {
    const res = await alertsAPI.get()
    pendingApprovals.value = res.data.pending_approvals
  } catch (e) {
    console.error(e)
  }
}

const fetchCurrentUser = async () => {
  try {
    const res = await usersAPI.get(currentUserId.value)
    currentUserObj.value = res.data
    authState.role = res.data.role
  } catch (e) {
    console.error(e)
  }
}

const fetchSwitchableUsers = async () => {
  try {
    const res = await usersAPI.switchable()
    allUsers.value = res.data
  } catch (e) {
    console.error(e)
  }
}

const fetchUsers = async () => {
  try {
    if (currentUserRole.value === 'admin') {
      const res = await usersAPI.list()
      allUsers.value = res.data
    }
  } catch (e) {
    console.error(e)
  }
}

const switchUser = (userId) => {
  if (userId === currentUserId.value) return
  const selectedUser = allUsers.value.find(u => u.id === userId)
  if (selectedUser && !selectedUser.is_active) {
    return
  }
  currentUserId.value = userId
  currentUserObj.value = selectedUser || currentUserObj.value
  authState.role = currentUserObj.value.role
  if (!canAccessRoute(currentUserObj.value.role, route.path) && route.path !== '/') {
    ElMessage.warning(`当前角色【${roleLabel.value}】无权限访问此页面，已跳转至仪表盘`)
    router.push('/')
  }
}

provide('refreshAlerts', fetchAlerts)
provide('currentUserId', currentUserId)
provide('currentUserRole', currentUserRole)
provide('hasPermission', hasPermission)

watch(currentUserId, async (newId) => {
  await fetchCurrentUser()
  authState.role = currentUserRole.value
  authState.initialized = true
  if (!canAccessRoute(currentUserRole.value, route.path) && route.path !== '/') {
    ElMessage.warning(`当前角色【${roleLabel.value}】无权限访问此页面，已跳转至仪表盘`)
    router.push('/')
  }
  fetchAlerts()
}, { immediate: true })

onMounted(() => {
  fetchSwitchableUsers()
  fetchAlerts()
  setInterval(fetchAlerts, 30000)
})
</script>

<style scoped>
.badge :deep(.el-badge__content) {
  background-color: #f56c6c;
}
</style>
