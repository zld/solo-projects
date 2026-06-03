<template>
  <div class="items-page">
    <div class="page-header">
      <h2>物品管理</h2>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        新增物品
      </el-button>
    </div>

    <div class="card">
      <div style="margin-bottom: 15px; display: flex; gap: 10px">
        <el-input v-model="searchName" placeholder="搜索物品名称" style="width: 200px" clearable @input="fetchItems" />
        <el-select v-model="filterLowStock" placeholder="库存状态" style="width: 150px" clearable @change="fetchItems">
          <el-option label="库存不足" :value="true" />
        </el-select>
      </div>

      <el-table :data="items" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="sku" label="SKU" width="120" />
        <el-table-column prop="category" label="分类" width="100" />
        <el-table-column prop="total_quantity" label="总库存" width="100" />
        <el-table-column prop="available_quantity" label="可用库存" width="100">
          <template #default="{ row }">
            <span :class="{ 'low-stock': row.available_quantity < row.min_threshold }">
              {{ row.available_quantity }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="borrowed_quantity" label="已借出" width="100" />
        <el-table-column prop="min_threshold" label="预警阈值" width="100" />
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="editItem(row)">编辑</el-button>
            <el-button size="small" type="success" link @click="stockInItem(row)">入库</el-button>
            <el-button size="small" type="warning" link @click="borrowItem(row)">借出</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="showCreateDialog" title="新增物品" width="500px">
      <el-form :model="formData" label-width="100px">
        <el-form-item label="物品名称">
          <el-input v-model="formData.name" />
        </el-form-item>
        <el-form-item label="SKU">
          <el-input v-model="formData.sku" />
        </el-form-item>
        <el-form-item label="分类">
          <el-input v-model="formData.category" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="formData.description" type="textarea" />
        </el-form-item>
        <el-form-item label="预警阈值">
          <el-input-number v-model="formData.min_threshold" :min="0" />
        </el-form-item>
        <el-form-item label="单位">
          <el-input v-model="formData.unit" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createItem">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showStockInDialog" title="快速入库" width="400px">
      <el-form label-width="80px">
        <el-form-item label="物品">
          <span>{{ selectedItem?.name }}</span>
        </el-form-item>
        <el-form-item label="入库数量">
          <el-input-number v-model="stockInQuantity" :min="1" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="stockInRemark" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showStockInDialog = false">取消</el-button>
        <el-button type="primary" @click="quickStockIn">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showBorrowDialog" title="快速借出" width="400px">
      <el-form label-width="80px">
        <el-form-item label="物品">
          <span>{{ selectedItem?.name }} (可用: {{ selectedItem?.available_quantity }})</span>
        </el-form-item>
        <el-form-item label="借出数量">
          <el-input-number v-model="borrowQuantity" :min="1" :max="selectedItem?.available_quantity || 1" />
        </el-form-item>
        <el-form-item label="用途">
          <el-input v-model="borrowPurpose" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showBorrowDialog = false">取消</el-button>
        <el-button type="primary" @click="quickBorrow">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { itemsAPI, stockAPI, borrowAPI } from '../api'

const items = ref([])
const searchName = ref('')
const filterLowStock = ref(null)
const showCreateDialog = ref(false)
const showStockInDialog = ref(false)
const showBorrowDialog = ref(false)
const selectedItem = ref(null)
const stockInQuantity = ref(1)
const stockInRemark = ref('')
const borrowQuantity = ref(1)
const borrowPurpose = ref('')

const formData = ref({
  name: '',
  sku: '',
  category: '',
  description: '',
  min_threshold: 5,
  unit: '个'
})

const fetchItems = async () => {
  try {
    const res = await itemsAPI.list({ low_stock: filterLowStock.value })
    if (searchName.value) {
      items.value = res.data.filter(item => 
        item.name.includes(searchName.value)
      )
    } else {
      items.value = res.data
    }
  } catch (e) {
    ElMessage.error('获取物品列表失败')
  }
}

const createItem = async () => {
  try {
    await itemsAPI.create(formData.value)
    ElMessage.success('创建成功')
    showCreateDialog.value = false
    formData.value = { name: '', sku: '', category: '', description: '', min_threshold: 5, unit: '个' }
    fetchItems()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '创建失败')
  }
}

const editItem = (row) => {
  ElMessage.info('编辑功能可进一步扩展')
}

const stockInItem = (row) => {
  selectedItem.value = row
  stockInQuantity.value = 1
  stockInRemark.value = ''
  showStockInDialog.value = true
}

const quickStockIn = async () => {
  try {
    await stockAPI.stockIn({
      item_id: selectedItem.value.id,
      quantity: stockInQuantity.value,
      operator_id: 1,
      remark: stockInRemark.value,
      need_approval: false
    })
    ElMessage.success('入库成功')
    showStockInDialog.value = false
    fetchItems()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '入库失败')
  }
}

const borrowItem = (row) => {
  if (row.available_quantity <= 0) {
    ElMessage.warning('库存不足')
    return
  }
  selectedItem.value = row
  borrowQuantity.value = 1
  borrowPurpose.value = ''
  showBorrowDialog.value = true
}

const quickBorrow = async () => {
  try {
    await borrowAPI.borrow({
      item_id: selectedItem.value.id,
      quantity: borrowQuantity.value,
      borrower_id: 1,
      purpose: borrowPurpose.value,
      need_approval: false
    })
    ElMessage.success('借出成功')
    showBorrowDialog.value = false
    fetchItems()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '借出失败')
  }
}

onMounted(() => {
  fetchItems()
})
</script>
