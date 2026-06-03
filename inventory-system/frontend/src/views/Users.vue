<template>
  <div class="users-page">
    <div class="page-header">
      <h2>用户管理</h2>
      <el-button type="primary" @click="openCreateDialog">
        <el-icon><Plus /></el-icon>
        新增用户
      </el-button>
    </div>

    <div class="card">
      <div style="margin-bottom: 15px; display: flex; gap: 10px">
        <el-input v-model="searchKeyword" placeholder="搜索用户名/姓名" style="width: 200px" clearable @input="filterUsers" />
        <el-select v-model="filterRole" placeholder="角色筛选" style="width: 140px" clearable @change="filterUsers">
          <el-option label="管理员" value="admin" />
          <el-option label="审批员" value="approver" />
          <el-option label="普通用户" value="user" />
        </el-select>
        <el-select v-model="filterActive" placeholder="状态筛选" style="width: 140px" clearable @change="fetchUsers">
          <el-option label="启用" :value="true" />
          <el-option label="禁用" :value="false" />
        </el-select>
      </div>

      <el-table :data="displayUsers" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="140" />
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="role" label="角色" width="120">
          <template #default="{ row }">
            <el-tag :type="roleTagType(row.role)" size="small">{{ roleLabel(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-switch
              :model-value="row.is_active"
              @change="(val) => toggleActive(row, val)"
              :disabled="row.role === 'admin'"
              active-text="启用"
              inactive-text="禁用"
              inline-prompt
            />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="openEditDialog(row)">编辑</el-button>
            <el-button size="small" type="warning" link @click="openResetRoleDialog(row)">修改角色</el-button>
            <el-button size="small" type="danger" link @click="confirmDelete(row)" :disabled="row.role === 'admin'">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="showCreateDialog" title="新增用户" width="460px" @close="resetForm">
      <el-form :model="createForm" :rules="createRules" ref="createFormRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="createForm.username" placeholder="登录用户名" />
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input v-model="createForm.name" placeholder="真实姓名" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="createForm.role" style="width: 100%">
            <el-option label="管理员" value="admin" />
            <el-option label="审批员" value="approver" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="submitCreate" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showEditDialog" title="编辑用户" width="460px" @close="resetForm">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="用户名">
          <el-input :model-value="editForm.username" disabled />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="editForm.name" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="submitEdit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showRoleDialog" title="修改角色" width="400px">
      <el-form label-width="80px">
        <el-form-item label="用户">
          <span>{{ currentUser?.name }} ({{ currentUser?.username }})</span>
        </el-form-item>
        <el-form-item label="当前角色">
          <el-tag :type="roleTagType(currentUser?.role)" size="small">{{ roleLabel(currentUser?.role) }}</el-tag>
        </el-form-item>
        <el-form-item label="新角色">
          <el-select v-model="newRole" style="width: 100%">
            <el-option label="管理员" value="admin" />
            <el-option label="审批员" value="approver" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRoleDialog = false">取消</el-button>
        <el-button type="primary" @click="submitRoleChange" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { usersAPI } from '../api'

const users = ref([])
const searchKeyword = ref('')
const filterRole = ref(null)
const filterActive = ref(null)
const submitting = ref(false)

const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const showRoleDialog = ref(false)
const currentUser = ref(null)
const newRole = ref('')

const createFormRef = ref(null)

const createForm = ref({
  username: '',
  name: '',
  role: 'user'
})

const createRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }]
}

const editForm = ref({
  id: null,
  username: '',
  name: ''
})

const roleLabel = (role) => {
  const map = { admin: '管理员', approver: '审批员', user: '普通用户' }
  return map[role] || role
}

const roleTagType = (role) => {
  const map = { admin: 'danger', approver: 'warning', user: 'info' }
  return map[role] || 'info'
}

const formatTime = (time) => {
  if (!time) return ''
  return new Date(time).toLocaleString('zh-CN')
}

const displayUsers = computed(() => {
  let result = users.value
  if (searchKeyword.value) {
    const kw = searchKeyword.value.toLowerCase()
    result = result.filter(u =>
      u.username.toLowerCase().includes(kw) || u.name.toLowerCase().includes(kw)
    )
  }
  if (filterRole.value) {
    result = result.filter(u => u.role === filterRole.value)
  }
  return result
})

const filterUsers = () => {}

const fetchUsers = async () => {
  try {
    const res = await usersAPI.list({
      role: filterRole.value || undefined,
      is_active: filterActive.value !== null && filterActive.value !== '' ? filterActive.value : undefined
    })
    users.value = res.data
  } catch (e) {
    ElMessage.error('获取用户列表失败')
  }
}

const resetForm = () => {
  createForm.value = { username: '', name: '', role: 'user' }
  editForm.value = { id: null, username: '', name: '' }
}

const openCreateDialog = () => {
  resetForm()
  showCreateDialog.value = true
}

const submitCreate = async () => {
  if (!createForm.value.username || !createForm.value.name) {
    ElMessage.warning('请填写完整信息')
    return
  }
  submitting.value = true
  try {
    await usersAPI.create(createForm.value)
    ElMessage.success('用户创建成功')
    showCreateDialog.value = false
    fetchUsers()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '创建失败')
  } finally {
    submitting.value = false
  }
}

const openEditDialog = (row) => {
  currentUser.value = row
  editForm.value = { id: row.id, username: row.username, name: row.name }
  showEditDialog.value = true
}

const submitEdit = async () => {
  submitting.value = true
  try {
    await usersAPI.update(editForm.value.id, { name: editForm.value.name })
    ElMessage.success('用户信息已更新')
    showEditDialog.value = false
    fetchUsers()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '更新失败')
  } finally {
    submitting.value = false
  }
}

const openResetRoleDialog = (row) => {
  currentUser.value = row
  newRole.value = row.role
  showRoleDialog.value = true
}

const submitRoleChange = async () => {
  if (newRole.value === currentUser.value.role) {
    ElMessage.info('角色未变更')
    showRoleDialog.value = false
    return
  }
  submitting.value = true
  try {
    await usersAPI.update(currentUser.value.id, { role: newRole.value })
    ElMessage.success('角色已更新')
    showRoleDialog.value = false
    fetchUsers()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '更新失败')
  } finally {
    submitting.value = false
  }
}

const toggleActive = async (row, val) => {
  if (row.role === 'admin') {
    ElMessage.warning('不能禁用管理员账户')
    return
  }
  const action = val ? '启用' : '禁用'
  try {
    await ElMessageBox.confirm(`确定要${action}用户 "${row.name}" 吗？`, `${action}用户`, {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await usersAPI.update(row.id, { is_active: val })
    ElMessage.success(`已${action}`)
    fetchUsers()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(e.response?.data?.detail || '操作失败')
    }
  }
}

const confirmDelete = async (row) => {
  if (row.role === 'admin') {
    ElMessage.warning('不能删除管理员账户')
    return
  }
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${row.name}" 吗？此操作不可恢复。`,
      '删除确认',
      { confirmButtonText: '确定删除', cancelButtonText: '取消', type: 'error' }
    )
    await usersAPI.delete(row.id)
    ElMessage.success('用户已删除')
    fetchUsers()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(e.response?.data?.detail || '删除失败')
    }
  }
}

onMounted(() => {
  fetchUsers()
})
</script>
