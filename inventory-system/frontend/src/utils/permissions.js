export const ROLE_PERMISSIONS = {
  admin: ['dashboard', 'items_view', 'items_edit', 'stock_in', 'borrow', 'approval', 'user_manage', 'logs_view'],
  approver: ['dashboard', 'items_view', 'items_edit', 'stock_in', 'borrow', 'approval', 'logs_view'],
  user: ['dashboard', 'items_view', 'borrow', 'logs_view']
}

export const PAGE_ROUTE_PERMISSIONS = {
  '/': 'dashboard',
  '/items': 'items_view',
  '/stock-in': 'stock_in',
  '/borrow': 'borrow',
  '/approvals': 'approval',
  '/users': 'user_manage',
  '/records': 'logs_view'
}

export function hasPermission(role, permission) {
  if (!role) return false
  const perms = ROLE_PERMISSIONS[role] || []
  return perms.includes(permission)
}

export function canAccessRoute(role, path) {
  const requiredPermission = PAGE_ROUTE_PERMISSIONS[path]
  if (!requiredPermission) return true
  return hasPermission(role, requiredPermission)
}

export function getAccessibleMenus(role) {
  const menus = [
    { path: '/', label: '仪表盘', icon: 'DataLine' },
    { path: '/items', label: '物品管理', icon: 'Box' },
    { path: '/stock-in', label: '入库管理', icon: 'Upload', permission: 'stock_in' },
    { path: '/borrow', label: '借出/归还', icon: 'Tickets', permission: 'borrow' },
    { path: '/approvals', label: '审批管理', icon: 'CircleCheck', permission: 'approval' },
    { path: '/users', label: '用户管理', icon: 'User', permission: 'user_manage' },
    { path: '/records', label: '操作记录', icon: 'Document', permission: 'logs_view' }
  ]
  return menus.filter(m => !m.permission || hasPermission(role, m.permission))
}
