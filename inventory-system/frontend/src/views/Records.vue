<template>
  <div class="records-page">
    <div class="page-header">
      <h2>操作记录</h2>
    </div>

    <div class="card">
      <div style="margin-bottom: 15px; display: flex; gap: 10px">
        <el-select v-model="filterType" placeholder="操作类型" style="width: 150px" clearable @change="fetchLogs">
          <el-option label="物品" value="item" />
          <el-option label="审批" value="approval" />
        </el-select>
      </div>

      <el-table :data="logs" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="action" label="操作" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ row.action }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="target_type" label="类型" width="100" />
        <el-table-column prop="target_id" label="目标ID" width="100" />
        <el-table-column prop="detail" label="详情" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.detail">{{ parseDetail(row.detail) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="ip_address" label="IP地址" width="150" />
        <el-table-column prop="created_at" label="操作时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { logsAPI } from '../api'

const logs = ref([])
const filterType = ref('')

const formatTime = (time) => {
  if (!time) return ''
  return new Date(time).toLocaleString('zh-CN')
}

const parseDetail = (detail) => {
  try {
    if (typeof detail === 'string') {
      return JSON.stringify(JSON.parse(detail))
    }
    return JSON.stringify(detail)
  } catch {
    return detail
  }
}

const fetchLogs = async () => {
  try {
    const res = await logsAPI.list({ target_type: filterType.value || undefined })
    logs.value = res.data
  } catch (e) {
    ElMessage.error('获取操作记录失败')
  }
}

onMounted(() => {
  fetchLogs()
})
</script>
