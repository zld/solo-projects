import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'
import { canAccessRoute } from '../utils/permissions'

export const authState = {
  role: null,
  initialized: false
}

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue')
  },
  {
    path: '/items',
    name: 'Items',
    component: () => import('../views/Items.vue')
  },
  {
    path: '/stock-in',
    name: 'StockIn',
    component: () => import('../views/StockIn.vue')
  },
  {
    path: '/borrow',
    name: 'Borrow',
    component: () => import('../views/Borrow.vue')
  },
  {
    path: '/approvals',
    name: 'Approvals',
    component: () => import('../views/Approvals.vue')
  },
  {
    path: '/users',
    name: 'Users',
    component: () => import('../views/Users.vue')
  },
  {
    path: '/records',
    name: 'Records',
    component: () => import('../views/Records.vue')
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  if (to.path === '/') {
    next()
    return
  }
  if (!authState.initialized) {
    next()
    return
  }
  if (!canAccessRoute(authState.role, to.path)) {
    ElMessage.warning(`当前角色【${authState.role === 'admin' ? '管理员' : authState.role === 'approver' ? '审批员' : '普通用户'}】无权限访问此页面`)
    next('/')
    return
  }
  next()
})

export default router
