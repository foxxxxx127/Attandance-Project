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
        <el-menu-item index="0" @click="EnterReleaseCheckIn">
          <template #title>
            <el-icon><Edit /></el-icon> <!-- 使用 Edit 图标 -->
            <span>发布新打卡</span>
          </template>
        </el-menu-item>
        <el-menu-item index="1" @click="EnterAttendanceStats">
          <template #title>
            <el-icon><DataAnalysis /></el-icon>
            <span>打卡统计</span>
          </template>
        </el-menu-item>
        <el-menu-item index="2" @click="EnterLeaveApproval">
          <template #title>
            <el-icon><DocumentChecked /></el-icon>
            <span>请假审批</span>
          </template>
        </el-menu-item>
        <el-menu-item index="3" @click="EnterReissueApproval">
          <template #title>
            <el-icon><Finished /></el-icon>
            <span>补卡审批</span>
          </template>
        </el-menu-item>
        <el-menu-item index="4" @click="EnterFieldApproval">
          <template #title>
            <el-icon><Location /></el-icon> <!-- 修改为Location图标 -->
            <span>外勤审批</span>
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
            <el-badge :value="unreadCount" class="badge" v-if="unreadCount > 0" />
          </el-button>
          <el-dropdown>
            <span class="topbar-item user-info">
              <el-avatar size="small" class="user-avatar">{{ userInitial }}</el-avatar>
              <span>{{ userName }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item divided @click="logout">退出登录</el-dropdown-item>
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
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  Search,
  Bell,
  Edit, // 新增 Edit 图标
  DataAnalysis,
  DocumentChecked,
  Finished,
  Location
} from '@element-plus/icons-vue'

// 响应式数据
const activeMenu = ref('')
const userName = ref('管理员')
const unreadCount = ref(3) // 未读通知数量

// 计算属性
const userInitial = computed(() => userName.value.charAt(0))

const router = useRouter()
const route = useRoute()

// 根据路由动态设置 activeMenu
watch(
  () => route.path,
  (newPath) => {
    switch (newPath) {
      case '/managermainmenu/releasecheckin':
        activeMenu.value = '0'
        break
      case '/managermainmenu/carddata':
        activeMenu.value = '1'
        break
      case '/managermainmenu/leaveabsenceapproval':
        activeMenu.value = '2'
        break
      case '/managermainmenu/cardapproval':
        activeMenu.value = '3'
        break
      case '/managermainmenu/fieldworkapproval':
        activeMenu.value = '4'
        break
      default:
        activeMenu.value = ''
    }
  },
  { immediate: true } // 立即执行以初始化 activeMenu
)


const EnterFieldApproval = async () => {
  router.push('/managermainmenu/fieldworkapproval')
}
const EnterReleaseCheckIn = async () => {
  router.push('/managermainmenu/releasecheckin')
}
const EnterAttendanceStats = async () => {
  router.push('/managermainmenu/carddata')
}
const EnterLeaveApproval = async () => {
  router.push('/managermainmenu/leaveabsenceapproval')
}
const EnterReissueApproval = async () => {
  router.push('/managermainmenu/cardapproval')
}
const logout = () => {
  localStorage.removeItem('admin_id')
  router.push('/')
}
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