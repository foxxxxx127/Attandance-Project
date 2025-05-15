<template>
  <div class="enterprise-management-system">
    <!-- 左侧边栏 -->
    <el-aside width="200px" class="sidebar">
      <el-menu
        :default-active="activeMenu"
        class="el-menu-vertical"
        background-color="#041528"
        text-color="#fff"
        active-text-color="#ffd04b"
      >
        <el-menu-item index="1" @click="EnterAttendance">
          <template #title>
            <el-icon><Check /></el-icon>
            <span>打卡</span>
          </template>
        </el-menu-item>
        <el-menu-item index="2" @click="EnterQingjia">
          <template #title>
            <el-icon><Calendar /></el-icon>
            <span>请假申请</span>
          </template>
        </el-menu-item>
        <el-menu-item index="3" @click="EnterCardApplication">
          <template #title>
            <el-icon><Clock /></el-icon>
            <span>补卡申请</span>
          </template>
        </el-menu-item>
        <el-menu-item index="4" @click="EnterField">
          <template #title>
            <el-icon><Location /></el-icon>
            <span>外勤申请</span>
          </template>
        </el-menu-item>
        <!-- 新增审批通知菜单项 -->
        <el-menu-item index="5" @click="EnterApprovalNotifications">
          <template #title>
            <el-icon><Bell /></el-icon>
            <span>审批通知</span>
          </template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 主布局 -->
    <el-container class="main-container">
      <!-- 顶部导航栏 -->
      <el-header class="topbar">
        <div class="topbar-right">
          <el-button type="text" class="topbar-item">
            <el-icon><Search /></el-icon>
          </el-button>
          <el-button type="text" class="topbar-item">
            <el-icon><Bell /></el-icon>
          </el-button>
          <el-dropdown>
            <span class="topbar-item user-info">
              <el-avatar size="small" class="user-avatar">{{ userInitial }}</el-avatar>
              <span>{{ userName }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="EnterPerInfoCenter">
                  个人中心
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 主内容区域 -->
      <el-main class="main-content">
        <router-view></router-view>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import {
  Check,
  Calendar,
  Clock,
  Location,
  Search,
  Bell,
} from '@element-plus/icons-vue'

// 响应式数据
const activeMenu = ref('1')
const userName = ref('') // 用户名从后端获取

// 计算属性
const userInitial = computed(() => userName.value.charAt(0))

const router = useRouter()

// 跳转到个人中心
const EnterPerInfoCenter = async () => {
  router.push('/mainmenu/personinfo')
}

// 跳转到外勤申请
const EnterField = async () => {
  router.push('/mainmenu/fieldworkapplication')
}

// 跳转到补卡申请
const EnterCardApplication = async () => {
  router.push('/mainmenu/cardapplication')
}

// 跳转到考勤页面
const EnterAttendance = async () => {
  router.push('/mainmenu/attendance')
}

// 跳转到请假申请
const EnterQingjia = async () => {
  router.push('/mainmenu/leaveapplication')
}

// 跳转到审批通知
const EnterApprovalNotifications = async () => {
  router.push('/mainmenu/approvalnotice')
}

// 退出登录
const handleLogout = () => {
  localStorage.removeItem('employee_id') // 清除用户信息
  router.push('/') // 跳转到登录页面
}

// 获取用户信息
const fetchUserInfo = async () => {
  try {
    const employeeId = localStorage.getItem('employee_id') // 从 localStorage 获取员工编号
    if (!employeeId) {
      console.error('未找到用户信息，请重新登录')
      return
    }

    const response = await axios.get('http://127.0.0.1:5000/get_profile', {
      params: { employee_id: employeeId }
    })

    if (response.status === 200) {
      const data = response.data
      userName.value = data.name // 更新用户名
    } else {
      console.error('获取用户信息失败:', response.data.error || '未知错误')
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
}

// 在组件挂载时获取用户信息
onMounted(() => {
  fetchUserInfo()
})
</script>

<style scoped>
.enterprise-management-system {
  display: flex;
  height: 100vh;
  background-color: #f5f5f5;
}

.sidebar {
  background-color: #041528;
  height: 100vh;
}

.el-menu-vertical {
  border-right: none;
  padding-top: 80px;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.topbar {
  background-color:#2f5373;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  height: 80px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.topbar-right {
  display: flex;
  align-items: center;
}

.topbar-item {
  color: white;
  margin-left: 20px;
  display: flex;
  align-items: center;
}

.user-info {
  cursor: pointer;
  display: flex;
  align-items: center;
}

.user-avatar {
  margin-right: 10px;
  background-color: #fff;
  color: #3d6392;
  font-weight: bold;
}

.main-content {
  padding: 20px;
  height: calc(100vh - 80px);
  overflow-y: auto;
}

.el-icon {
  margin-right: 10px;
}
</style>