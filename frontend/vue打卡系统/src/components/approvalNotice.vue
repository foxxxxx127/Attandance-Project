<template>
  <div class="approval-notifications">
    <!-- 标题 -->
    <h2 class="notification-title">我的审批通知</h2>

    <!-- 筛选区域 -->
    <div class="filter-area">
      <el-select
        v-model="filter.type"
        placeholder="全部类型"
        clearable
        class="filter-item"
        @change="fetchNotifications"
      >
        <el-option
          v-for="type in notificationTypes"
          :key="type.value"
          :label="type.label"
          :value="type.value"
        />
      </el-select>

      <el-button
        type="primary"
        @click="fetchNotifications"
        :loading="loading"
      >
        刷新
      </el-button>
    </div>

    <!-- 表格 -->
    <el-table
      :data="notifications"
      style="width: 100%"
      border
      v-loading="loading"
      :header-cell-style="{ background: '#f5f7fa', color: '#606266' }"
    >
      <el-table-column prop="applyTime" label="申请时间" width="300" align="center">
        <template #default="{ row }">
          {{ row.applyTime || '-' }}
        </template>
      </el-table-column>

      <el-table-column prop="type" label="事件类型" width="300" align="center">
        <template #default="{ row }">
          <el-tag :type="getTypeTagType(row.type)">
            {{ formatType(row.type || '-') }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="reason" label="申请原因" width="300" align="center">
        <template #default="{ row }">
          {{ row.reason || '无' }}
        </template>
      </el-table-column>

      <el-table-column prop="result" label="审批结果" width="300" align="center">
        <template #default="{ row }">
          <el-tag :type="getResultTagType(row.result)" effect="dark">
            {{ formatResult(row.result || '-') }}
          </el-tag>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="pagination.currentPage"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="fetchNotifications"
        @current-change="fetchNotifications"
      />
    </div>
  </div>
</template>

<script setup>
import axios from 'axios'
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserInfo } from '@/stores/userInfo'

const userInfo = useUserInfo()
const userId = userInfo.userId

// 响应式数据
const notifications = ref([])
const loading = ref(false)

// 筛选条件
const filter = ref({
  type: '' // 仅保留事件类型筛选
})

// 分页信息
const pagination = ref({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

// 通知类型选项
const notificationTypes = ref([
  { value: 'leave', label: '请假审批' },
  { value: 'card', label: '补卡审批' },
  { value: 'field', label: '外勤审批' }
])

// 组件挂载时获取数据
onMounted(() => {
  fetchNotifications()
})

// 获取审批通知数据
const fetchNotifications = async () => {
  try {
    loading.value = true

    // 构造请求参数
    const params = {
      type: filter.value.type || '', // 筛选类型
      page: pagination.value.currentPage, // 当前页码
      size: pagination.value.pageSize // 每页大小
    }

    // 调用后端接口
    const response = await axios.get(`http://localhost:5000/employee/approval_records/${userId}`, { params })

    if (response.data.code === 0) {
      // 映射后端返回的数据到前端字段
      notifications.value = response.data.data.records.map(record => ({
        applyTime: record.application_time, // 申请时间范围
        type: record.event_type, // 事件类型
        reason: record.reason, // 申请原因
        result: record.status // 审批结果
      }))
      pagination.value.total = response.data.data.total // 更新总记录数
      ElMessage.success('审批记录加载成功')
    } else {
      ElMessage.error(response.data.message || '获取审批记录失败')
    }
  } catch (error) {
    console.error('获取审批记录失败:', error)
    ElMessage.error('获取审批记录失败')
  } finally {
    loading.value = false
  }
}

// 格式化类型显示
const formatType = (type) => {
  const typeMap = {
    leave: '请假审批',
    card: '补卡审批',
    field: '外勤审批'
  }
  return typeMap[type] || type
}

// 格式化结果显示
const formatResult = (result) => {
  const resultMap = {
    approved: '已通过',
    rejected: '已拒绝',
    pending: '待审批'
  }
  return resultMap[result] || result
}

// 获取类型标签样式
const getTypeTagType = (type) => {
  const typeMap = {
    leave: '',
    card: 'info',
    field: 'warning'
  }
  return typeMap[type] || ''
}

// 获取结果标签样式
const getResultTagType = (result) => {
  const resultMap = {
    approved: 'success',
    rejected: 'danger',
    pending: 'warning'
  }
  return resultMap[result] || ''
}
</script>

<style scoped>
.approval-notifications {
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.notification-title {
  margin-bottom: 20px;
  color: #303133;
  text-align: center;
  font-size: 1.5em;
}

.filter-area {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.filter-item {
  width: 200px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>