<template>
  <el-table
    :data="leaveData"
    style="width: 100%"
    :border="false"
    :header-cell-style="{ background: '#f5f7fa' }"
    v-loading="loading"
  >
    <el-table-column prop="reason" label="申请原因" width="300" />
    <el-table-column prop="leaveDate" label="请假日期" width="300">
      <template #default="{ row }">
        {{ row.start_date }} 至 {{ row.end_date }}
      </template>
    </el-table-column>
    <el-table-column prop="applicant" label="申请人" width="300" />
    <el-table-column label="审批状态" width="300">
      <template #default="{ row }">
        <div v-if="row.status === '待审批'">
          <el-button 
            type="success" 
            size="small" 
            @click="handleApprove(row, '已批准')"
            :loading="row.loading"
            :disabled="row.loading"
          >
            通过
          </el-button>
          <el-button 
            type="danger" 
            size="small" 
            @click="handleApprove(row, '已拒绝')"
            :loading="row.loading"
            :disabled="row.loading"
          >
            不通过
          </el-button>
        </div>
        <div v-else>
          <el-tag 
            :type="row.status === '已批准' ? 'success' : 'danger'" 
            size="medium"
          >
            {{ row.status }}
          </el-tag>
        </div>
      </template>
    </el-table-column>
  </el-table>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { ElMessage } from 'element-plus';

// 加载状态
const loading = ref(false);

// 请假数据
const leaveData = ref([]);

// 获取请假记录
const fetchLeaveData = async () => {
  loading.value = true;
  try {
    const response = await axios.get('http://127.0.0.1:5000/admin/leave'); // 确保路径正确
    leaveData.value = response.data.map(item => ({
      ...item,
      status: item.status || '待审批',
      loading: false
    }));
  } catch (error) {
    console.error('获取请假数据失败:', error);
    ElMessage.error('获取请假数据失败，请检查网络或后端接口');
  } finally {
    loading.value = false;
  }
};

// 处理审批操作
const handleApprove = async (row, status) => {
  try {
    // 设置加载状态
    row.loading = true;

    // 发送审批请求到服务器
    const response = await axios.post(`http://127.0.0.1:5000/admin/leave/${row.id}`, { status });

    if (response.status === 200) {
      ElMessage.success(`已${status === '已批准' ? '通过' : '拒绝'}该申请`);
      // 更新本地数据状态
      row.status = status;
    } else {
      ElMessage.error(response.data.message || '审批失败');
    }
  } catch (error) {
    console.error('审批操作失败:', error);
    ElMessage.error('审批操作失败，请检查网络或后端接口');
  } finally {
    row.loading = false;
  }
};

// 页面加载时获取数据
onMounted(() => {
  fetchLeaveData();
});
</script>

<style scoped>
.leave-approval-form {
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.leave-table-container {
  margin-top: 20px;
}

:deep(.el-table) {
  --el-table-border-color: transparent;
  --el-table-border: none;
}

:deep(.el-table__header) {
  border-bottom: 1px solid #ebeef5;
}

:deep(.el-table__row) {
  border-bottom: 1px solid #f0f0f0;
}

:deep(.el-table__row:last-child) {
  border-bottom: none;
}
</style>