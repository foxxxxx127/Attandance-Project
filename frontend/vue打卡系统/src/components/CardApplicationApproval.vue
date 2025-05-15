<template>
    <div class="leave-approval-form">
      <!-- 日期范围选择 -->
      <div class="date-range-selector">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          :size="'small'"
          @change="fetchLeaveData"
        >
          <template #prefix>
            <el-icon><calendar /></el-icon>
          </template>
        </el-date-picker>
      </div>
  
      <!-- 请假申请表格 -->
      <div class="leave-table-container">
        <el-table
          :data="leaveData"
          style="width: 100%"
          :border="false"
          :header-cell-style="{ background: '#f5f7fa' }"
        >
          <el-table-column prop="applyDate" label="申请日期" width="150" />
          <el-table-column prop="reason" label="申请原因" width="250" />
          <el-table-column prop="leaveDate" label="请假日期" width="200">
            <template #default="{ row }">
              {{ row.startDate }} 至 {{ row.endDate }}
            </template>
          </el-table-column>
          <el-table-column prop="applicant" label="申请人" width="120" />
          <el-table-column label="审批意见" width="180">
            <template #default="{ row }">
              <div v-if="row.status === 'pending'">
                <el-button 
                  type="success" 
                  size="small" 
                  @click="approveLeave(row, 'approved')"
                >
                  通过
                </el-button>
                <el-button 
                  type="danger" 
                  size="small" 
                  @click="approveLeave(row, 'rejected')"
                  
                >
                  不通过
                </el-button>
              </div>
              <div v-else>
                <el-tag 
                  :type="row.status === 'approved' ? 'success' : 'danger'" 
                  size="medium"
                >
                  {{ row.status === 'approved' ? '已通过' : '未通过' }}
                </el-tag>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  import { Calendar } from '@element-plus/icons-vue';
  import axios from 'axios';
  
  // 日期范围
  const dateRange = ref([]);
  
  // 请假数据
  const leaveData = ref([
    {
      id: 1,
      applyDate: '2023-06-01',
      reason: '身体不适需要休息',
      startDate: '2023-06-02',
      endDate: '2023-06-03',
      applicant: '张三',
      status: 'pending'
    },
    {
      id: 2,
      applyDate: '2023-06-03',
      reason: '家庭事务处理',
      startDate: '2023-06-05',
      endDate: '2023-06-07',
      applicant: '李四',
      status: 'pending'
    }
  ]);
  
  // 获取请假数据
  const fetchLeaveData = async () => {
    if (dateRange.value && dateRange.value.length === 2) {
      try {
        const [startDate, endDate] = dateRange.value;
        const response = await axios.get('/api/leave-applications', {
          params: {
            startDate: formatDate(startDate),
            endDate: formatDate(endDate)
          }
        });
        leaveData.value = response.data.map(item => ({
          ...item,
          status: item.status || 'pending'
        }));
      } catch (error) {
        console.error('获取请假数据失败:', error);
        // ElMessage.error('获取数据失败');
      }
    }
  };
  
  // 审批请假申请
  const approveLeave = async (row, status) => {
    try {
      await axios.put(`/api/leave-applications/${row.id}/approve`, { status });
      row.status = status;
    //   ElMessage.success(`已${status === 'approved' ? '通过' : '拒绝'}该申请`);
    } catch (error) {
      console.error('审批操作失败:', error);
    //   ElMessage.error('操作失败');
    }
  };
  
  // 格式化日期
  const formatDate = (date) => {
    return date.toISOString().split('T')[0];
  };
  </script>
  
  <style scoped>
  .leave-approval-form {
    padding: 20px;
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  }
  
  .date-range-selector {
    margin-bottom: 20px;
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
  
  :deep(.el-date-editor--daterange.el-input__wrapper) {
    width: 380px;
  }
  </style>