<template>
  <div class="approvals-page">
    <div class="page-header">
      <h2>审批管理</h2>
    </div>

    <div class="card">
      <div style="margin-bottom: 15px">
        <el-radio-group v-model="filterStatus" @change="fetchApprovals">
          <el-radio-button value="">全部</el-radio-button>
          <el-radio-button value="pending">待审批</el-radio-button>
          <el-radio-button value="approved">已通过</el-radio-button>
          <el-radio-button value="rejected">已拒绝</el-radio-button>
        </el-radio-group>
      </div>

      <el-table :data="approvals" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="record_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.record_type === 'stock_in' ? 'success' : 'warning'" size="small">
              {{ row.record_type === 'stock_in' ? '入库' : '借出' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="item_id" label="物品ID" width="100" />
        <el-table-column prop="quantity" label="数量" width="100" />
        <el-table-column prop="remark" label="申请说明" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <span :class="['status-tag', `status-${row.status}`]">
              {{ row.status === 'pending' ? '待审批' : row.status === 'approved' ? '已通过' : '已拒绝' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="approval_remark" label="审批意见" show-overflow-tooltip />
        <el-table-column prop="created_at" label="申请时间" width="180">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200" v-if="filterStatus === '' || filterStatus === 'pending'">
          <template #default="{ row }">
            <div v-if="row.status === 'pending'" class="table-actions">
              <el-button size="small" type="success" @click="approve(row)">通过</el-button>
              <el-button size="small" type="danger" @click="reject(row)">拒绝</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="showProcessDialog" :title="processType === 'approve' ? '审批通过' : '审批拒绝'" width="400px">
      <el-form label-width="80px">
        <el-form-item label="审批意见">
          <el-input v-model="approvalRemark" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showProcessDialog = false">取消</el-button>
        <el-button :type="processType === 'approve' ? 'success' : 'danger'" @click="submitProcess">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { approvalAPI } from '../api'

const approvals = ref([])
const filterStatus = ref('')
const showProcessDialog = ref(false)
const processType = ref('')
const currentApproval = ref(null)
const approvalRemark = ref('')

const formatTime = (time) => {
  if (!time) return ''
  return new Date(time).toLocaleString('zh-CN')
}

const fetchApprovals = async () => {
  try {
    const res = await approvalAPI.list({ status: filterStatus.value || undefined })
    approvals.value = res.data
  } catch (e) {
    ElMessage.error('获取审批列表失败')
  }
}

const approve = (row) => {
  processType.value = 'approve'
  currentApproval.value = row
  approvalRemark.value = ''
  showProcessDialog.value = true
}

const reject = (row) => {
  processType.value = 'reject'
  currentApproval.value = row
  approvalRemark.value = ''
  showProcessDialog.value = true
}

const submitProcess = async () => {
  try {
    await approvalAPI.process(currentApproval.value.id, {
      status: processType.value === 'approve' ? 'approved' : 'rejected',
      approval_remark: approvalRemark.value,
      approver_id: 1
    })
    ElMessage.success(processType.value === 'approve' ? '已通过' : '已拒绝')
    showProcessDialog.value = false
    fetchApprovals()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  }
}

onMounted(() => {
  fetchApprovals()
})
</script>
