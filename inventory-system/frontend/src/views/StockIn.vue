<template>
  <div class="stock-in-page">
    <div class="page-header">
      <h2>入库管理</h2>
    </div>

    <el-row :gutter="20">
      <el-col :span="10">
        <div class="card">
          <h3 style="margin-bottom: 15px">新增入库</h3>
          <el-form :model="formData" label-width="100px">
            <el-form-item label="选择物品">
              <el-select v-model="formData.item_id" placeholder="请选择物品" style="width: 100%">
                <el-option v-for="item in items" :key="item.id" :label="item.name" :value="item.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="入库数量">
              <el-input-number v-model="formData.quantity" :min="1" style="width: 100%" />
            </el-form-item>
            <el-form-item label="备注">
              <el-input v-model="formData.remark" type="textarea" />
            </el-form-item>
            <el-form-item label="需要审批">
              <el-switch v-model="formData.need_approval" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="submitStockIn" style="width: 100%">提交入库</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-col>
      <el-col :span="14">
        <div class="card">
          <h3 style="margin-bottom: 15px">入库记录</h3>
          <el-table :data="records" style="width: 100%">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="item_id" label="物品ID" width="100" />
            <el-table-column prop="quantity" label="数量" width="100" />
            <el-table-column prop="type" label="类型" width="80">
              <template #default="{ row }">
                <el-tag type="success" size="small">{{ row.type === 'in' ? '入库' : row.type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="remark" label="备注" show-overflow-tooltip />
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
import { ElMessage } from 'element-plus'
import { itemsAPI, stockAPI } from '../api'

const items = ref([])
const records = ref([])
const formData = ref({
  item_id: null,
  quantity: 1,
  remark: '',
  need_approval: false
})

const formatTime = (time) => {
  if (!time) return ''
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

const fetchRecords = async () => {
  try {
    const res = await stockAPI.records()
    records.value = res.data
  } catch (e) {
    ElMessage.error('获取记录失败')
  }
}

const submitStockIn = async () => {
  if (!formData.value.item_id) {
    ElMessage.warning('请选择物品')
    return
  }
  try {
    const res = await stockAPI.stockIn({
      ...formData.value,
      operator_id: 1
    })
    ElMessage.success(res.data.message)
    formData.value = { item_id: null, quantity: 1, remark: '', need_approval: false }
    fetchRecords()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '提交失败')
  }
}

onMounted(() => {
  fetchItems()
  fetchRecords()
})
</script>
