<template> 
    <!-- 主容器 --> 
    <div class="employee-profile-container"> 
      <!-- 顶部个人信息区域 --> 
      <div class="profile-header"> 
        <!-- 员工头像 --> 
        <el-avatar  
          :size="100"  
          :src="employeeData.avatar"  
          class="profile-avatar" 
        /> 
         
        <!-- 员工基本信息 --> 
        <div class="profile-info"> 
          <!-- 员工姓名 --> 
          <h2 class="employee-name">{{ employeeData.name }}</h2> 
          <!-- 部门信息 --> 
          <p class="employee-department"> 
            <el-icon><OfficeBuilding /></el-icon> 
            {{ employeeData.department }} 
          </p> 
          <!-- 职位信息 --> 
          <p class="employee-position"> 
            <el-icon><Briefcase /></el-icon> 
            {{ employeeData.position }} 
          </p> 
        </div> 
      </div> 
   
      <!-- 详细信息卡片区域 --> 
      <div class="detail-cards"> 
        <!-- 第一张卡片：基本信息 --> 
        <el-card class="detail-card"> 
          <div class="card-item"> 
            <span class="item-label">姓名：</span> 
            <span class="item-value">{{ employeeData.name }}</span> 
          </div> 
          <div class="card-item"> 
            <span class="item-label">工号：</span> 
            <span class="item-value">{{ employeeData.employeeId }}</span> 
          </div> 
          <div class="card-item"> 
            <span class="item-label">岗位：</span> 
            <span class="item-value">{{ employeeData.position }}</span> 
          </div> 
          <div class="card-item"> 
            <span class="item-label">出生日期：</span> 
            <span class="item-value">{{ employeeData.birthDate }}</span> 
          </div> 
        </el-card> 
   
        <!-- 第二张卡片：联系信息 --> 
        <el-card class="detail-card"> 
          <div class="card-item"> 
            <span class="item-label">性别：</span> 
            <span class="item-value">{{ employeeData.gender }}</span> 
          </div> 
          <div class="card-item"> 
            <span class="item-label">邮箱：</span> 
            <span class="item-value">{{ employeeData.email }}</span> 
          </div> 
          <div class="card-item"> 
            <span class="item-label">手机号：</span> 
            <span class="item-value">{{ employeeData.phone }}</span> 
          </div> 
          <div class="card-item"> 
            <span class="item-label">身份证号：</span> 
            <span class="item-value">{{ employeeData.idNumber }}</span> 
          </div> 
        </el-card> 
   
        <!-- 第三张卡片：工作信息 --> 
        <el-card class="detail-card"> 
          <div class="card-item"> 
            <span class="item-label">工龄：</span> 
            <span class="item-value">{{ employeeData.workYears }}</span> 
          </div> 
          <div class="card-item"> 
            <span class="item-label">入职日期：</span> 
            <span class="item-value">{{ employeeData.joinDate }}</span> 
          </div> 
          <div class="card-item"> 
            <span class="item-label">户籍：</span> 
            <span class="item-value">{{ employeeData.hometown }}</span> 
          </div> 
          <div class="card-item"> 
            <span class="item-label">住址：</span> 
            <span class="item-value">{{ employeeData.address }}</span> 
          </div> 
        </el-card> 
   
        <!-- 第四张卡片：其他信息 --> 
        <el-card class="detail-card"> 
          <div class="card-item"> 
            <span class="item-label">学历：</span> 
            <span class="item-value">{{ employeeData.education }}</span> 
          </div> 
          <div class="card-item"> 
            <span class="item-label">政治面貌：</span> 
            <span class="item-value">{{ employeeData.politicalStatus }}</span> 
          </div> 
          <div class="card-item"> 
            <span class="item-label">民族：</span> 
            <span class="item-value">{{ employeeData.ethnicity }}</span> 
          </div> 
          <div class="card-item"> 
            <span class="item-label">婚姻状态：</span> 
            <span class="item-value">{{ employeeData.maritalStatus }}</span> 
          </div> 
        </el-card> 
      </div> 
   
      <!-- 退出按钮 --> 
      <div class="logout-container"> 
        <el-button  
          type="danger"  
          class="logout-btn" 
          @click="handleLogout" 
        > 
          <el-icon><SwitchButton /></el-icon> 
          退出登录 
        </el-button> 
      </div> 
    </div> 
  </template> 
   
  <script setup> 
  // import request from '@/utils/request'
  // 导入Vue相关API 
  import axios from 'axios'
  import { ref, onMounted } from 'vue' 
  // 导入Element Plus图标 
  import {  
    OfficeBuilding,  // 部门图标 
    Briefcase,       // 职位图标 
    SwitchButton     // 退出图标 
  } from '@element-plus/icons-vue' 
import { ElMessage } from 'element-plus'
   
  // 员工数据对象 
  const employeeData = ref({ 
    avatar: '',            // 头像URL 
    name: '',              // 姓名 
    department: '',        // 部门 
    position: '',          // 职位 
    employeeId: '',        // 工号 
    birthDate: '',         // 出生日期 
    gender: '',            // 性别 
    email: '',             // 邮箱 
    phone: '',             // 手机号 
    idNumber: '',          // 身份证号 
    workYears: '',         // 工龄 
    joinDate: '',          // 入职日期 
    hometown: '',          // 户籍 
    address: '',           // 住址 
    education: '',         // 学历 
    politicalStatus: '',   // 政治面貌 
    ethnicity: '',         // 民族 
    maritalStatus: ''      // 婚姻状态 
  }) 
   
  // 模拟从服务器获取员工数据 
  const fetchEmployeeData = async () => { 
    // 这里应该是实际的API调用 
    // 例如: const response = await axios.get('/api/employee/profile') 
    // let result=await request.get('/managerinfo',) 
    // 模拟API返回数据 
    const response = await axios.get('http://localhost:8080/managerinfo')
    if(response.data.code===0){
      ElMessage.success('服务器响应成功')
    }
    const mockData = { 
      avatar: 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png', 
      name: '张三', 
      department: '技术研发部', 
      position: '高级前端工程师', 
      employeeId: 'EMP20230001', 
      birthDate: '1990-05-15', 
      gender: '男', 
      email: 'zhangsan@company.com', 
      phone: '13800138000', 
      idNumber: '110***********1234', 
      workYears: '5年', 
      joinDate: '2018-06-10', 
      hometown: '北京市朝阳区', 
      address: '北京市海淀区中关村大街1号', 
      education: '硕士研究生', 
      politicalStatus: '中共党员', 
      ethnicity: '汉族', 
      maritalStatus: '已婚' 
    } 
     
    // 将模拟数据赋值给响应式对象 
    Object.assign(employeeData.value, mockData) 
  } 
   
  // 处理退出登录 
  const handleLogout = () => { 
    // 这里应该调用退出登录的API 
    // 例如: await axios.post('/api/logout') 
     
    // 模拟退出操作 
    console.log('执行退出登录操作') 
    // 实际项目中可能需要跳转到登录页 
    // router.push('/login') 
  } 
   
  // 组件挂载时获取员工数据 
  onMounted(() => { 
    fetchEmployeeData() 
  }) 
  </script> 
   
  <style scoped> 
  /* 主容器样式 */ 
  .employee-profile-container { 
    max-width: 1200px; 
    margin: 0 auto; 
    padding: 20px; 
    position: relative; 
    min-height: 100vh; 
  } 
   
  /* 顶部个人信息区域样式 */ 
  .profile-header { 
    display: flex; 
    align-items: center; 
    margin-bottom: 40px; 
    padding: 20px; 
    background-color: #f5f7fa; 
    border-radius: 8px; 
  } 
   
  /* 头像样式 */ 
  .profile-avatar { 
    margin-right: 30px; 
    border: 3px solid #fff; 
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1); 
  } 
   
  /* 个人信息区域样式 */ 
  .profile-info { 
    flex: 1; 
  } 
   
  /* 员工姓名样式 */ 
  .employee-name { 
    margin: 0 0 10px 0; 
    font-size: 24px; 
    color: #303133; 
  } 
   
  /* 部门和职位信息样式 */ 
  .employee-department, 
  .employee-position { 
    margin: 8px 0; 
    font-size: 16px; 
    color: #606266; 
    display: flex; 
    align-items: center; 
  } 
   
  /* 部门、职位图标样式 */ 
  .employee-department .el-icon, 
  .employee-position .el-icon { 
    margin-right: 8px; 
    font-size: 18px; 
  } 
   
  /* 详细信息卡片区域样式 */ 
  .detail-cards { 
    display: grid; 
    grid-template-columns: repeat(4, 1fr); 
    gap: 20px; 
    margin-bottom: 60px; 
  } 
   
  /* 单个卡片样式 */ 
  .detail-card { 
    border-radius: 8px; 
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1); 
  } 
   
  /* 卡片项样式 */ 
  .card-item { 
    padding: 12px 0; 
    border-bottom: 1px solid #ebeef5; 
    display: flex; 
  } 
   
  /* 最后一项不需要下边框 */ 
  .card-item:last-child { 
    border-bottom: none; 
  } 
   
  /* 标签样式 */ 
  .item-label { 
    font-weight: bold; 
    color: #909399; 
    min-width: 80px; 
    display: inline-block; 
  } 
   
  /* 值样式 */ 
  .item-value { 
    color: #606266; 
    flex: 1; 
  } 
   
  /* 退出按钮容器样式 */ 
  .logout-container { 
    position: fixed; 
    right: 40px; 
    bottom: 40px; 
  } 
   
  /* 退出按钮样式 */ 
  .logout-btn { 
    padding: 12px 24px; 
    font-size: 16px; 
    border-radius: 6px; 
    box-shadow: 0 2px 12px rgba(245, 108, 108, 0.3); 
    transition: all 0.3s; 
  } 
   
  /* 退出按钮悬停效果 */ 
  .logout-btn:hover { 
    transform: translateY(-2px); 
    box-shadow: 0 4px 16px rgba(245, 108, 108, 0.4); 
  } 
  </style> 