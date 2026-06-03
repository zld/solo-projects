<template>
  <div class="borrow-page">
    <div class="page-header">
      <h2>借出/归还管理</h2>
    </div>

    <el-tabs v-model="activeTab">
      <el-tab-pane label="借出物品" name="borrow">
        <div class="card">
          <el-form :model="borrowForm" label-width="100px" style="max-width: 500px">
            <el-form-item label="选择物品">
              <el-select v-model="borrowForm.item_id" placeholder="请选择物品" style="width: 100%">
                <el-option v-for="item in items" :key="item.id" :label="`${item.name} (可用: ${item.available_quantity})`" :value="item.id" :disabled="item.available_quantity <= 0" />
              </el-select>
            </el-form-item>
            <el-form-item label="借出数量">
              <el-input-number v-model="borrowForm.quantity" :min="1" :max="maxQuantity" style="width: 100%" />
            </el-form-item>
            <el-form-item label="借用人">
              <el-select v-model="borrowForm.borrower_id" placeholder="请选择借用人" style="width: 100%" :disabled="!canSelectOtherUser">
                <el-option v-for="user in borrowableUsers" :key="user.id" :label="user.name" :value="user.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="需要审批">
              <el-switch v-model="borrowForm.need_approval" :disabled="!canSkipApproval" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="submitBorrow">提交借出</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>

      <el-tab-pane label="归还物品" name="return">
        <div class="card">
          <h3 style="margin-bottom: 15px">待归还列表</h3>
          <el-table :data="borrowedRecords" style="width: 100%">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="item_id" label="物品ID" width="100" />
            <el-table-column prop="quantity" label="借出数量" width="100" />
            <el-table-column prop="purpose" label="用途" show-overflow-tooltip />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <span :class="['status-tag', `status-${row.status}`]">
                  {{ row.status === 'borrowed' ? '借出中' : row.status }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="借出时间" width="180">
              <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button v-if="row.status === 'borrowed' && canReturn(row)" size="small" type="success" link @click="returnItem(row)">归还</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <el-tab-pane label="借出记录" name="records">
        <div class="card">
          <el-table :data="allRecords" style="width: 100%">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="item_id" label="物品ID" width="100" />
            <el-table-column prop="quantity" label="数量" width="100" />
            <el-table-column prop="purpose" label="用途" show-overflow-tooltip />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <span :class="['status-tag', `status-${row.status}`]">
                  {{ row.status === 'borrowed' ? '借出中' : row.status === 'returned' ? '已归还' : row.status }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="借出时间" width="180">
              <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
            </el-table-column>
            <el-table-column prop="actual_return_date" label="归还时间" width="180">
              <template #default="{ row }">{{ formatTime(row.actual_return_date) }}</template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, inject } from 'vue'
import { ElMessage } from 'element-plus'
import { itemsAPI, borrowAPI, usersAPI } from '../api'
import { hasPermission } from '../utils/permissions'

const refreshAlerts = inject('refreshAlerts')
const currentUserId = inject('currentUserId')
const currentUserRole = inject('currentUserRole')
const hasPerm = inject('hasPermission', hasPermission)

const isAdmin = computed(() => currentUserRole.value === 'admin')
const isApprover = computed(() => ['admin', 'approver'].includes(currentUserRole.value))
const canSelectOtherUser = computed(() => isApprover.value)
const canSkipApproval = computed(() => isApprover.value)

const borrowableUsers = computed(() => {
  if (isApprover.value) {
    return users.value
  }
  const me = users.value.find(u => u.id === currentUserId.value)
  return me ? [me] : []
})

const canReturn = (row) => {
  if (isApprover.value) return true
  return row.borrower_id === currentUserId.value
}

const activeTab = ref('borrow')
const items = ref([])
const users = ref([])
const borrowedRecords = ref([])
const allRecords = ref([])
const borrowForm = ref({
  item_id: null,
  quantity: 1,
  borrower_id: null,
  purpose: '',
  need_approval: true
})

const maxQuantity = computed(() => {
  const item = items.value.find(i => i.id === borrowForm.value.item_id)
  return item ? item.available_quantity : 1
})

const formatTime = (time) => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

const fetchItems = async () => {
  try {
    const res = await itemsAPI.list()
    items.value = res.data
  } catch (e) {
    ElMessage.error('获取物品列表失败')
  }
}

const fetchUsers = async () => {
  try {
    if (isApprover.value) {
      const res = await usersAPI.list()
      users.value = res.data
    } else {
      const res = await usersAPI.switchable()
      users.value = res.data
      if (!borrowForm.value.borrower_id) {
        borrowForm.value.borrower_id = currentUserId.value
      }
    }
  } catch (e) {
    ElMessage.error('获取用户列表失败')
  }
}

const fetchRecords = async () => {
  try {
    const params = {}
    if (!isApprover.value) {
      params.borrower_id = currentUserId.value
    }
    const [borrowedRes, allRes] = await Promise.all([
      borrowAPI.records({ status: 'borrowed', ...params }),
      borrowAPI.records(params)
    ])
    borrowedRecords.value = borrowedRes.data
    allRecords.value = allRes.data
  } catch (e) {
    ElMessage.error('获取记录失败')
  }
}

const submitBorrow = async () => {
  if (!borrowForm.value.item_id) {
    ElMessage.warning('请选择物品')
    return
  }
  if (!borrowForm.value.borrower_id) {
    ElMessage.warning('请选择借用人')
    return
  }
  try {
    const res = await borrowAPI.borrow(borrowForm.value)
    ElMessage.success(res.data.message)
    borrowForm.value = { item_id: null, quantity: 1, borrower_id: null, purpose: '', need_approval: true }
    fetchItems()
    fetchRecords()
    if (refreshAlerts) {
      refreshAlerts()
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '提交失败')
  }
}

const returnItem = async (row) => {
  try {
    await borrowAPI.returnItem({
      record_id: row.id,
      operator_id: currentUserId ? currentUserId.value : 1
    })
    ElMessage.success('归还成功')
    fetchItems()
    fetchRecords()
    if (refreshAlerts) {
      refreshAlerts()
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '归还失败')
  }
}

watch(activeTab, (val) => {
  if (val === 'return' || val === 'records') {
    fetchRecords()
  }
})

onMounted(() => {
  fetchItems()
  fetchUsers()
  fetchRecords()
})
</script>
