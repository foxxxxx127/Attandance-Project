 
<template> 
    <!-- 主容器 --> 
    <div class="attendance-setting-form"> 
      <!-- 表单标题 --> 
      <h3 class="form-title">打卡方式设置</h3> 
       
      <!-- 使用Element Plus的Form组件 --> 
      <el-form  
        ref="formRef"              
        :model="form"               
        label-position="top"        
        class="setting-form" 
      > 
        <!-- 部门选择 --> 
        <el-form-item label="选择部门" prop="department"> 
          <!-- 部门选择器 --> 
          <el-select 
            v-model="form.department" 
            placeholder="请选择部门"  
            clearable                
            class="full-width-select" 
          > 
            <!-- 部门选项 --> 
            <el-option 
              v-for="dept in departments" 
              :key="dept.value" 
              :label="dept.label" 
              :value="dept.value" 
            /> 
            <!-- 右侧选择图标（Element Select自带图标） --> 
          </el-select> 
        </el-form-item> 
         
        <!-- 日期范围选择 --> 
        <el-form-item label="日期区间" prop="dateRange"> 
          <!-- 日期范围选择器 --> 
          <el-date-picker 
            v-model="form.dateRange" 
            type="daterange"         
            range-separator="至"      
            start-placeholder="开始日期" 
            end-placeholder="结束日期"   
            class="full-width-date-picker" 
          > 
            <!-- 右侧日历图标 --> 
            <template #suffix> 
              <el-icon><Calendar /></el-icon> 
            </template> 
          </el-date-picker> 
        </el-form-item> 
         
        <!-- 打卡时间选择 --> 
        <el-form-item label="打卡时间" prop="timeRange"> 
          <div class="time-range-container"> 
            <!-- 开始时间选择 --> 
            <el-time-picker 
              v-model="form.startTime" 
              placeholder="选择开始时间" 
              class="time-picker" 
            /> 
            <span class="time-separator">至</span> 
            <!-- 结束时间选择 --> 
            <el-time-picker 
              v-model="form.endTime"    
              placeholder="选择结束时间" 
              class="time-picker" 
            /> 
          </div> 
        </el-form-item> 
         
        <!-- 打卡方式选择 --> 
        <el-form-item label="打卡方式" prop="attendanceType"> 
          <!-- 单选组 --> 
          <el-radio-group  
            v-model="form.attendanceType"
            class="attendance-type-group" 
          > 
            <!-- 混合式选项 --> 
            <el-radio label="mixed" border> 
              <el-icon><Connection /></el-icon> 
              混合式 
            </el-radio> 
            <!-- 人脸识别选项 --> 
            <el-radio label="face" border> 
              <el-icon><User /></el-icon> 
              人脸识别 
            </el-radio> 
            <!-- 定位选项 --> 
            <el-radio label="location" border> 
              <el-icon><Location /></el-icon> 
              定位 
            </el-radio> 
          </el-radio-group> 
        </el-form-item> 
         
        <!-- 定位地点选择（当选择定位打卡方式时显示） --> 
        <el-form-item  
          v-if="form.attendanceType === 'location'"  
          label="定位地点"  
          prop="location" 
        > 
          <!-- 地点选择输入框 --> 
          <el-input 
            v-model="form.location"    
            placeholder="请选择定位地点"
     
            class="location-input" 
            @click="openLocationPicker" 
          > 
            <!-- 右侧地点图标 --> 
            <template #suffix> 
              <el-icon><LocationFilled /></el-icon> 
            </template> 
          </el-input> 
        </el-form-item> 
         
        <!-- 提交按钮 --> 
        <el-form-item> 
          <el-button 
            type="primary"           
            class="submit-btn"       
            @click="submitForm"      
          > 
            <el-icon><Check /></el-icon> 
            确定设置 
          </el-button> 
        </el-form-item> 
      </el-form> 
       
      <!-- 地点选择对话框（模拟） --> 
      <el-dialog 
        v-model="locationDialogVisible" 
        title="选择定位地点" 
        width="50%" 
      > 
        <!-- 这里应该是实际的地图选择组件 --> 
        <div class="map-placeholder"> 
          <p>地图组件占位区域</p> 
          <p>请在此选择打卡地点</p> 
        </div> 
        <template #footer> 
          <el-button @click="locationDialogVisible = false">取消</el-button> 
          <el-button type="primary" @click="confirmLocation">确定</el-button> 
        </template> 
      </el-dialog> 
    </div> 
  </template> 
   
  <script setup> 
  // 导入Vue的响应式API 
  import { ref } from 'vue' 
  // 导入Element Plus图标 
  import {  
    Calendar,          // 日历图标 
    Connection,        // 混合式图标 
    User,              // 人脸识别图标 
    Location,          // 定位图标 
    LocationFilled,    // 定位填充图标 
    Check              // 确认图标 
  } from '@element-plus/icons-vue' 
   
  // 表单引用 
  const formRef = ref(null) 
  // 控制地点选择对话框显示 
  const locationDialogVisible = ref(false) 
   
  // 表单数据对象 
  const form = ref({ 
    department: '',      // 部门 
    dateRange: [],       // 日期范围 
    startTime: '',       // 开始时间 
    endTime: '',         // 结束时间 
    attendanceType: 'mixed', // 打卡方式，默认混合式 
    location: ''         // 定位地点 
  }) 
   
  // 部门选项数据 
  const departments = ref([ 
    { value: 'dept1', label: '技术部' }, 
    { value: 'dept2', label: '产品部' }, 
    { value: 'dept3', label: '市场部' }, 
    { value: 'dept4', label: '人力资源部' }, 
    { value: 'dept5', label: '财务部' } 
  ]) 
   
  // 打开地点选择器 
  const openLocationPicker = () => { 
    locationDialogVisible.value = true 
  } 
   
  // 确认选择地点 
  const confirmLocation = () => { 
    // 这里应该是从地图选择组件获取的地点 
    // 模拟选择了一个地点 
    form.value.location = '北京市海淀区中关村软件园二期' 
    locationDialogVisible.value = false 
  } 
   
  // 提交表单 
  const submitForm = () => { 
    formRef.value.validate((valid) => { 
      if (valid) { 
        // 表单验证通过，处理提交逻辑 
        console.log('提交表单数据:', form.value) 
         
        // 这里应该是实际的API调用 
        // axios.post('/api/attendance/settings', form.value) 
         
        // 显示成功消息 
        // ElMessage.success('打卡方式设置成功') !!!!这里待定
      } 
    }) 
  } 
  </script> 
   
  <style scoped> 
  /* 主容器样式 */ 
  .attendance-setting-form { 
    max-width: 800px; 
    margin: 0 auto; 
    padding: 20px; 
    background-color: #fff; 
    border-radius: 8px; 
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1); 
  } 
   
  /* 表单标题样式 */ 
  .form-title { 
    text-align: center; 
    margin-bottom: 24px; 
    color: #303133; 
  } 
   
  /* 表单容器样式 */ 
  .setting-form { 
    padding: 0 20px; 
  } 
   
  /* 全宽选择器样式 */ 
  .full-width-select, 
  .full-width-date-picker { 
    width: 100%; 
  } 
   
  /* 时间范围容器样式 */ 
  .time-range-container { 
    display: flex; 
    align-items: center; 
    width: 100%; 
  } 
   
  /* 时间选择器样式 */ 
  .time-picker { 
    flex: 1; 
  } 
   
  /* 时间分隔符样式 */ 
  .time-separator { 
    padding: 0 10px; 
    color: #909399; 
  } 
   
  /* 打卡方式单选组样式 */ 
  .attendance-type-group { 
    display: flex; 
    justify-content: space-between; 
    width: 100%; 
  } 
   
  /* 单选按钮样式 */ 
  .attendance-type-group .el-radio { 
    flex: 1; 
    margin-right: 10px; 
  } 
   
  .attendance-type-group .el-radio:last-child { 
    margin-right: 0; 
  } 
   
  /* 地点输入框样式 */ 
  .location-input { 
    width: 100%; 
  } 
   
  /* 提交按钮样式 */ 
  .submit-btn { 
    width: 100%; 
    padding: 12px 24px; 
    font-size: 16px; 
    border-radius: 6px; 
    transition: all 0.3s; 
  } 
   
  /* 按钮悬停效果 */ 
  .submit-btn:hover { 
    transform: translateY(-2px); 
    box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3); 
  } 
   
  /* 地图占位区域样式 */ 
  .map-placeholder { 
    height: 300px; 
    display: flex; 
    flex-direction: column; 
    justify-content: center; 
    align-items: center; 
    background-color: #f5f7fa; 
    border-radius: 4px; 
    color: #909399; 
  } 
   
  /* 表单项样式 */ 
  .el-form-item { 
    margin-bottom: 22px; 
  } 
   
  /* 表单项标签样式 */ 
  .el-form-item__label { 
    font-weight: 500; 
    color: #606266; 
  } 
  </style> 