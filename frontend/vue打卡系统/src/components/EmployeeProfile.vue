<template>
  <div class="employee-profile-container">
    <!-- 顶部个人信息区域 -->
    <div class="profile-header">
      <!-- 员工头像 -->
      <el-avatar
        :size="100"
        :src="employeeData.photo ? 'http://127.0.0.1:5000' + employeeData.photo : 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'"
        class="profile-avatar"
      />
      <!-- 员工基本信息 -->
      <div class="profile-info">
        <h2 class="employee-name">{{ employeeData.name }}</h2>
        <p class="employee-department">
          <el-icon><OfficeBuilding /></el-icon>
          {{ employeeData.department }}
        </p>
        <p class="employee-position">
          <el-icon><Briefcase /></el-icon>
          {{ employeeData.position }}
        </p>
      </div>

      <!-- 设置按钮 -->
      <el-button 
        type="primary" 
        class="settings-button" 
        @click="openEditDialog"
      >
        设置
      </el-button>
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
          <span class="item-label">入职日期：</span>
          <span class="item-value">{{ employeeData.joinDate }}</span>
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
          <span class="item-label">职位：</span>
          <span class="item-value">{{ employeeData.role }}</span>
        </div>
      </el-card>
    </div>

    <!-- 编辑信息对话框 -->
    <el-dialog
      title="编辑个人信息"
      v-model="editDialogVisible"
      width="500px"
    >
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="姓名">
          <el-input v-model="editForm.name" />
        </el-form-item>
        <el-form-item label="性别">
          <el-select v-model="editForm.gender" placeholder="请选择性别">
            <el-option label="男" value="男" />
            <el-option label="女" value="女" />
          </el-select>
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="editForm.email" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="editForm.phone" />
        </el-form-item>
        <el-form-item label="岗位">
          <el-input v-model="editForm.position" />
        </el-form-item>
        <el-form-item label="部门">
          <el-input v-model="editForm.department" />
        </el-form-item>
        <el-form-item label="上传照片">
          <el-upload
            action="http://127.0.0.1:5000/upload_photo"
            list-type="text"
            :on-success="handlePhotoUpload"
            :on-error="handleUploadError"
            :before-upload="beforeUpload"
            :show-file-list="false"
          >
            <el-button type="primary">点击上传</el-button>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="updateProfile">保存</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { OfficeBuilding, Briefcase } from '@element-plus/icons-vue'

// 员工数据对象
const employeeData = ref({
  name: '', // 姓名
  employeeId: '', // 工号
  position: '', // 岗位
  department: '', // 部门
  gender: '', // 性别
  email: '', // 邮箱
  phone: '', // 手机号
  role: '', // 职位
  joinDate: '' // 入职日期
})

// 编辑表单数据
const editForm = reactive({
  name: '',
  gender: '',
  email: '',
  phone: '',
  position: '',
  department: '',
  photo: '' // 新增字段
})

// 编辑对话框的显示状态
const editDialogVisible = ref(false)

// 获取员工数据
const fetchEmployeeData = async () => {
  try {
    const employeeId = localStorage.getItem('employee_id') // 从 localStorage 获取员工编号
    if (!employeeId) {
      ElMessage.error('未找到用户信息，请重新登录')
      return
    }

    const response = await axios.get('http://127.0.0.1:5000/get_profile', {
      params: { employee_id: employeeId }
    })

    if (response.status === 200) {
      const data = response.data
      employeeData.value = {
        name: data.name,
        employeeId: data.employee_id, // 映射字段名
        position: data.position,
        department: data.department,
        gender: data.gender,
        email: data.email,
        phone: data.phone,
        role: data.role,
        joinDate: data.join_date
      }
    } else {
      ElMessage.error(response.data.error || '获取员工数据失败')
    }
  } catch (error) {
    console.error('获取员工数据失败:', error)
    ElMessage.error('获取员工数据失败')
  }
}
const handlePhotoUpload = (response) => {
  if (response.url) {
    editForm.photo = response.url; // 假设后端返回上传后的照片 URL
    ElMessage.success('照片上传成功');
  } else {
    ElMessage.error('照片上传失败');
  }
};

const beforeUpload = (file) => {
  console.log(file); // 打印文件对象，确保是 File 类型
  const isImage = file.type.startsWith('image/');
  if (!isImage) {
    ElMessage.error('只能上传图片文件');
    return false;
  }
  return true;
};
// 打开编辑对话框
const openEditDialog = () => {
  editForm.name = employeeData.value.name
  editForm.gender = employeeData.value.gender
  editForm.email = employeeData.value.email
  editForm.phone = employeeData.value.phone
  editForm.position = employeeData.value.position
  editForm.department = employeeData.value.department
  editDialogVisible.value = true
}

// 更新个人信息
const updateProfile = async () => {
  try {
    const employeeId = localStorage.getItem('employee_id') // 从 localStorage 获取员工编号
    if (!employeeId) {
      ElMessage.error('未找到用户信息，请重新登录')
      return
    }

    const response = await axios.post('http://127.0.0.1:5000/update_profile', {
      employee_id: employeeId,
      name: editForm.name,
      gender: editForm.gender,
      email: editForm.email,
      phone: editForm.phone,
      position: editForm.position,
      department: editForm.department,
      photo: editForm.photo // 提交照片 URL
    })

    if (response.status === 200) {
      ElMessage.success('个人信息更新成功')
      fetchEmployeeData() // 重新获取员工数据
      editDialogVisible.value = false
    } else {
      ElMessage.error(response.data.error || '更新失败')
    }
  } catch (error) {
    console.error('更新失败:', error)
    ElMessage.error('更新失败')
  }
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
  grid-template-columns: repeat(2, 1fr);
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


/* 设置按钮样式 */
.settings-button {
  margin-left: auto;
  border-radius: 20px;
  padding: 6px 20px;
  font-size: 14px;
  font-weight: bold;
  background-color: #409eff;
  color: #fff;
  border: none;
  cursor: pointer;
  transition: background-color 0.3s;
}

.settings-button:hover {
  background-color: #66b1ff;
}
</style>