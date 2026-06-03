import { createRouter, createWebHistory } from 'vue-router'

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
    path: '/records',
    name: 'Records',
    component: () => import('../views/Records.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
