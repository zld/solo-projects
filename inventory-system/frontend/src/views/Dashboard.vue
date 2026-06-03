<template>
  <div class="dashboard">
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="6">
        <div class="stat-card stat-blue">
          <div class="stat-value">{{ alerts.low_stock_count || 0 }}</div>
          <div class="stat-label">库存预警物品</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card stat-orange">
          <div class="stat-value">{{ alerts.overdue_count || 0 }}</div>
          <div class="stat-label">超期未还</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card stat-green">
          <div class="stat-value">{{ alerts.pending_approvals || 0 }}</div>
          <div class="stat-label">待审批</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card stat-purple">
          <div class="stat-value">{{ totalItems }}</div>
          <div class="stat-label">物品种类</div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="12">
        <div class="card">
          <h3 style="margin-bottom: 15px">库存预警</h3>
          <el-table :data="alerts.low_stock_items || []" style="width: 100%" size="small">
            <el-table-column prop="name" label="物品名称" />
            <el-table-column prop="available" label="可用库存" />
            <el-table-column prop="min" label="最低阈值" />
            <el-table-column label="状态">
              <template #default>
                <span class="status-tag status-rejected">库存不足</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="card">
          <h3 style="margin-bottom: 15px">最近操作记录</h3>
          <el-table :data="recentLogs" style="width: 100%" size="small">
            <el-table-column prop="action" label="操作" width="100" />
            <el-table-column prop="target_type" label="类型" width="100" />
            <el-table-column prop="detail" label="详情" show-overflow-tooltip />
            <el-table-column prop="created_at" label="时间" width="180">
              <template #default="{ row }">
                {{ formatTime(row.created_at) }}
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { alertsAPI, logsAPI, itemsAPI } from '../api'

const alerts = ref({})
const recentLogs = ref([])
const totalItems = ref(0)

const formatTime = (time) => {
  if (!time) return ''
  return new Date(time).toLocaleString('zh-CN')
}

const fetchData = async () => {
  try {
    const [alertsRes, logsRes, itemsRes] = await Promise.all([
      alertsAPI.get(),
      logsAPI.list(),
      itemsAPI.list()
    ])
    alerts.value = alertsRes.data
    recentLogs.value = logsRes.data.slice(0, 10)
    totalItems.value = itemsRes.data.length
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.stat-card {
  padding: 20px;
  border-radius: 8px;
  color: white;
  text-align: center;
}

.stat-blue { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.stat-orange { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
.stat-green { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
.stat-purple { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }

.stat-value {
  font-size: 36px;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}
</style>
