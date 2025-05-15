<template> 
  <!-- 主容器 --> 
  <div class="attendance-statistics"> 
    <!-- 标题 --> 
    <h3 class="statistics-title">打卡统计</h3> 
     
    <!-- 筛选条件区域 --> 
    <div class="filter-area"> 
      <!-- 日期选择 --> 
      <el-date-picker 
        v-model="filter.date"          
        type="date"                    
        placeholder="选择日期"          
        class="filter-item" 
        @change="validateForm"
      /> 
       
      <!-- 部门选择 --> 
      <el-select 
        v-model="filter.department"     
        placeholder="选择部门"          
        clearable                       
        class="filter-item" 
        @change="validateForm"
      > 
        <!-- 部门选项 --> 
        <el-option 
          v-for="dept in departments" 
          :key="dept.value" 
          :label="dept.label" 
          :value="dept.value" 
        /> 
      </el-select> 
       
      <!-- 员工工号输入 --> 
      <el-input 
        v-model="filter.employeeId"    
        placeholder="输入8位员工工号"       
        clearable                       
        class="filter-item" 
        @input="validateForm"
        maxlength="8"
      > 
        <template #prefix> 
          <el-icon><User /></el-icon>   
        </template> 
      </el-input>

      <!-- 查询按钮 -->
      <el-button 
        type="primary" 
        @click="fetchAttendanceData"
        :disabled="!isFormValid"
        class="search-button"
      >
        查询
      </el-button>
    </div> 
     
    <!-- 打卡数据表格 --> 
    <el-table 
      :data="attendanceData"           
      style="width: 100%"             
      border                           
      :header-cell-style="{ background: '#f5f7fa', color: '#606266' }" 
      class="attendance-table" 
      v-loading="loading"
    > 
      <!-- 姓名列 --> 
      <el-table-column 
        prop="name"                   
        label="姓名"                   
        width="120"                    
      /> 
       
      <!-- 部门列 --> 
      <el-table-column 
        prop="department"             
        label="部门"                    
        width="150"                    
      /> 
       
      <!-- 日期列 --> 
      <el-table-column 
        prop="date"                   
        label="日期"                   
        width="120"                   
      /> 
       
      <!-- 打卡状态列 --> 
      <el-table-column 
        prop="status"                  
        label="打卡状态"                
        width="120"                   
      > 
        <!-- 自定义状态显示 --> 
        <template #default="{ row }"> 
          <el-tag  
            :type="getStatusTagType(row.status)" 
            size="small"                        
          > 
            {{ row.status }} 
          </el-tag> 
        </template> 
      </el-table-column> 
       
      <!-- 打卡方式列 --> 
      <el-table-column 
        prop="method"                  
        label="打卡方式"               
        > 
        <template #default="{ row }"> 
          <div class="method-cell"> 
            <el-icon v-if="row.method === '人脸识别'"><User /></el-icon> 
            <el-icon v-else-if="row.method === '定位'"><Location /></el-icon> 
            <el-icon v-else><Connection /></el-icon> 
            <span>{{ row.method }}</span> 
          </div> 
        </template> 
      </el-table-column> 
    </el-table> 
  </div> 
</template> 
 
<script setup> 
import { ElMessage } from 'element-plus'
// 导入Vue相关API 
import { ref, onMounted } from 'vue' 
// 导入Element Plus图标 
import {  
  User,          // 用户图标 
  Location,      // 定位图标 
  Connection,    // 连接图标 
} from '@element-plus/icons-vue' 
// 导入axios用于API调用
import axios from 'axios'
 
// 筛选条件 
const filter = ref({ 
  date: '',        // 日期 
  department: '',  // 部门 
  employeeId: ''   // 员工工号 
}) 

// 表单验证状态
const isFormValid = ref(false)

// 加载状态
const loading = ref(false)

// 部门选项 
const departments = ref([ 
  { value: 'dept1', label: '技术部' }, 
  { value: 'dept2', label: '产品部' }, 
  { value: 'dept3', label: '市场部' }, 
  { value: 'dept4', label: '人力资源部' }, 
  { value: 'dept5', label: '财务部' } 
]) 
 
// 打卡数据 
const attendanceData = ref([]) 
 
// 验证表单
const validateForm = () => {
  isFormValid.value = (
    filter.value.date !== '' && 
    filter.value.department !== '' && 
    filter.value.employeeId !== '' && 
    /^\d{8}$/.test(filter.value.employeeId)
  )
}
 
// 组件挂载时获取初始数据 
onMounted(() => { 
  // 初始加载可以不要数据，或者加载全部数据
  // fetchAttendanceData() 
}) 
 
// 获取打卡数据 
const fetchAttendanceData = async () => { 
  try {
    loading.value = true
    
    // 实际API调用
    const response = await axios.get('/getcarddata', { 
      params: {
        date: filter.value.date,
        department: filter.value.department,
        employeeId: filter.value.employeeId
      }
    })
    
    // 更新表格数据
    attendanceData.value = response.data
  } catch (error) {
    console.error('获取打卡数据失败:', error)
    // 可以添加错误提示
    ElMessage.error('获取打卡数据失败')
    
    // 模拟数据用于演示
    attendanceData.value = [
      { name: '张三', department: '技术部', date: filter.value.date, status: '正常', method: '人脸识别' },
      { name: '李四', department: '产品部', date: filter.value.date, status: '迟到', method: '定位' }
    ]
  } finally {
    loading.value = false
  }
}
 
// 根据打卡状态获取标签类型 
const getStatusTagType = (status) => { 
  switch (status) { 
    case '正常': return 'success' 
    case '迟到': return 'warning' 
    case '早退': return 'warning' 
    case '缺卡': return 'danger' 
    default: return 'info' 
  } 
} 
</script> 
 
<style scoped> 
/* 主容器样式 */ 
.attendance-statistics { 
  max-width: 1200px; 
  margin: 0 auto; 
  padding: 20px; 
  background-color: #fff; 
  border-radius: 8px; 
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1); 
} 
 
/* 标题样式 */ 
.statistics-title { 
  text-align: center; 
  margin-bottom: 24px; 
  color: #303133; 
} 
 
/* 筛选区域样式 */ 
.filter-area { 
  display: flex; 
  gap: 15px; 
  margin-bottom: 20px; 
  align-items: center;
} 
 
/* 筛选项样式 */ 
.filter-item { 
  flex: 1; 
} 

/* 查询按钮样式 */
.search-button {
  height: 40px;
}
 
/* 表格样式 */ 
.attendance-table { 
  margin-top: 20px; 
  border: none; 
} 
 
/* 表格单元格样式 */ 
:deep(.el-table__cell) { 
  border: none; 
} 
 
/* 打卡方式单元格样式 */ 
.method-cell { 
  display: flex; 
  align-items: center; 
  gap: 8px; 
} 
</style>