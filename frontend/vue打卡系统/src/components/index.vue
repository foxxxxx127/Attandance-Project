<template>
  <div class="attendance-system">
    <header>
      <img src="@/assets/logo.png" alt="Logo" class="logo">
      <h1 class="site-title">企业混合考勤打卡系统</h1>
      <div class="auth-buttons">
        <el-button class="login-btn" @click="showLogin">登录</el-button>
        <el-button  class="register-btn" @click="showRegister">注册</el-button>
      </div>
    </header>
    
    <div class="additional-buttons">
      <el-button class="login-btn" @click="showLogin">登录</el-button>
      <el-button  class="register-btn" @click="showRegister">注册</el-button>
    </div>
    
    <img src="@/assets/首界面.svg" alt="主图" class="main-image">
    
    <main>
      <div class="login-container">
        <div class="login-tabs">
          <div 
            class="tab" 
            :class="{ active: (activeTab === 'login'||activeTab === 'register') && loginType === 'user' }"
            @click="switchLoginType('user')"
          >
            用户{{ isLoginForm ? '登录' : '注册' }}
          </div>
          <div 
            class="tab" 
            :class="{ active: (activeTab === 'login'||activeTab === 'register') && loginType === 'admin' }"
            @click="switchLoginType('admin')"
          >
            管理员{{ isLoginForm ? '登录' : '注册' }}
          </div>
        </div>
        
        <!-- 登录表单 -->
        <el-form 
          v-if="isLoginForm"
          :model="loginForm" 
          :rules="loginRules" 
          ref="loginFormRef"
          label-position="top"
          class="login-form"
          :class="{ active: activeTab === 'login' }"
          @submit.prevent="handleLogin"
        >
          <el-form-item label="账号" prop="employeeId">
            <el-input 
              v-model="loginForm.employeeId" 
              placeholder="请输入账号"
            />
          </el-form-item>
          
          <el-form-item label="密码" prop="password">
            <el-input 
              v-model="loginForm.password" 
              type="password" 
              show-password
              placeholder="请输入密码"
            />
          </el-form-item>
          
          <el-button 
            native-type="submit" 
            class="submit-btn"
            :loading="loading"
          >
            {{ loginType.value === 'user' ? '登录' : '登录' }}
          </el-button>
        </el-form>
        
      <el-form 
        :model="registerForm" 
        :rules="registerRules" 
        ref="registerFormRef"
        label-position="top"
        class="register-form"
        :class="{ active: activeTab === 'register' }"
        @submit.prevent="handleRegister"
      >
        <el-form-item label="姓名" prop="name">
          <el-input v-model="registerForm.name" placeholder="请输入姓名" />
        </el-form-item>
        
        <el-form-item label="员工编号" prop="employeeId" v-if="loginType === 'user'">
          <el-input v-model="registerForm.employeeId" placeholder="请输入员工编号" />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="registerForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="registerForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input 
            v-model="registerForm.password" 
            type="password" 
            show-password
            placeholder="请输入密码"
          />
        </el-form-item>
        
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input 
            v-model="registerForm.confirmPassword" 
            type="password" 
            show-password
            placeholder="请再次输入密码"
          />
        </el-form-item>
        
        <el-form-item label="部门" prop="department" v-if="loginType === 'user'">
          <el-select v-model="registerForm.department" placeholder="请选择部门" style="width: 100%">
            <el-option label="技术部" value="技术部" />
            <el-option label="市场部" value="市场部" />
            <el-option label="人事部" value="人事部" />
            <el-option label="财务部" value="财务部" />
          </el-select>
        </el-form-item>
        
      <el-button 
        native-type="submit" 
        class="submit-btn"
        :loading="loading"
      >
        {{ loginType === 'user' ? '员工注册' : '管理员注册' }}
      </el-button>
        
        <div class="login-link">
          已有账号？<el-link  @click="showLogin">立即登录</el-link>
        </div>
      </el-form>
      </div>
    </main>
    <footer></footer>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import axios from 'axios' // 引入 axios

const router = useRouter()
const activeTab = ref('login') // login or register
const loginType = ref('user') // user or admin
const isLoginForm = ref(true)
const loading = ref(false)

// 登录表单
const loginForm = reactive({
  employeeId: '', // 改为 employeeId
  password: ''
})

// 注册表单
const registerForm = reactive({
  name: '', // 姓名
  employeeId: '', // 员工编号
  email: '', // 邮箱
  phone: '', // 手机号
  password: '', // 密码
  confirmPassword: '', // 确认密码
  department: '' // 部门
})

// 登录表单验证规则
const loginRules = reactive({
  employeeId: [ // 改为 employeeId
    { required: true, message: '请输入员工编号', trigger: 'blur' },
    { min: 3, max: 16, message: '长度在 3 到 16 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' }
  ]
})

// 注册表单验证规则
const validatePass = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入密码不一致!'))
  } else {
    callback()
  }
}

const validatePhone = (rule, value, callback) => {
  const reg = /^1[3-9]\d{9}$/
  if (!reg.test(value)) {
    callback(new Error('请输入正确的手机号码'))
  } else {
    callback()
  }
}

const validateEmail = (rule, value, callback) => {
  const reg = /^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$/
  if (!reg.test(value)) {
    callback(new Error('请输入正确的邮箱地址'))
  } else {
    callback()
  }
}

const registerRules = reactive({
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, max: 16, message: '长度在 2 到 16 个字符', trigger: 'blur' }
  ],
  employeeId: [
    { required: loginType.value === 'user', message: '请输入员工编号', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { validator: validateEmail, trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { validator: validatePhone, trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validatePass, trigger: 'blur' }
  ],
  department: [
    { required: loginType.value === 'user', message: '请选择部门', trigger: 'change' }
  ]
})
const loginFormRef = ref(null)
const registerFormRef = ref(null)

// 切换登录类型 (用户/管理员)
const switchLoginType = (type) => {
  loginType.value = type
}

// 显示登录表单
const showLogin = () => {
  isLoginForm.value = true
  activeTab.value = 'login'
}

// 显示注册表单
const showRegister = () => {
  isLoginForm.value = false
  activeTab.value = 'register'
}

const handleLogin = async () => {
  try {
        // 管理员登录（前端写死账号密码）
    if (loginType.value === 'admin') {
      if (
        loginForm.employeeId === 'admin123' &&
        loginForm.password === 'admin123'
      ) {
        localStorage.setItem('admin_id', loginForm.employeeId)
        ElMessage.success('管理员登录成功')
        router.push('/managermainmenu/releasecheckin')
        return
      } else {
        ElMessage.error('管理员账号或密码错误')
        return
      }
    }
    const response = await axios.post('http://127.0.0.1:5000/login', {
      employee_id: loginForm.employeeId, // 改为 employeeId
      password: loginForm.password
    })

    if (response.status === 200) {
      // 登录成功，存储 employee_id
      localStorage.setItem('employee_id', loginForm.employeeId) // 改为 employeeId
      ElMessage.success('登录成功')
      router.push('/mainmenu/attendance') // 修改跳转路径
    } else {
      ElMessage.error(response.data.message || '登录失败')
    }
  } catch (error) {
    console.error('登录失败:', error)
    ElMessage.error(error.response?.data?.message || '登录失败')
  }
}

// 处理注册
const handleRegister = async () => {
  try {
    // 验证表单
    await registerFormRef.value.validate()

    loading.value = true // 开始加载

    // 调用后端注册接口
    const response = await axios.post('http://127.0.0.1:5000/register', {
      employee_id: registerForm.employeeId,
      name: registerForm.name,
      email: registerForm.email,
      phone: registerForm.phone,
      password: registerForm.password,
      department: registerForm.department,
      role: loginType.value === 'user' ? '员工' : '管理员',
      join_date: new Date().toISOString().split('T')[0] // 默认当前日期
    })

    // 处理后端响应
    if (response.status === 201 && response.data.message === '注册成功') {
      ElMessage.success(`${loginType.value === 'user' ? '用户' : '管理员'}注册成功`)
      showLogin() // 注册成功后切换到登录界面
    } else {
      ElMessage.error(response.data.message || response.data.error || '注册失败')
    }
  } catch (error) {
    console.error('注册失败:', error)
    ElMessage.error(error.response?.data?.message || '注册请求失败')
  } finally {
    loading.value = false // 结束加载
  }
}
</script>

<style scoped>
*{
  margin: 0;
  padding: 0;
}
.attendance-system {
  background-color: #ffffff;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
}

header {
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.site-title {
  position: absolute;
  left: 230px;
  top: 210px;
  font-size: 38px;
  font-weight: bold;
  color: #333;
}

.logo {
  position: absolute;
  left: 20.5px;
  top: 16.5px;
  width: 239px;
  height: 67px;
}

.main-image {
  position: absolute;
  left: 174px;
  top: 290px;
  width: 465px;
  height: 333px;
}

.auth-buttons {
  display: flex;
  gap: 20px;
}

.auth-buttons .el-button {
  padding: 12px 30px;
  border-radius: 25px;
  font-weight: bold;
  font-size: 16px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.auth-buttons .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.login-btn {
  background-color: #f8f9fa;
  color: #333;
}

.register-btn {
  background-color: #215476;
  color: white;
}

.additional-buttons {
  position: absolute;
  right: 30px;
  top: 30px;
  display: flex;
  gap: 20px;
}

.additional-buttons .el-button {
  padding: 12px 30px;
  border-radius: 25px;
  font-weight: bold;
  font-size: 16px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.additional-buttons .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

main {
  flex: 1;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding-right: 10%;
}

.login-container {
  width:50%; 
  max-width: 400px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  padding: 30px;
}

.login-tabs {
  display: flex;
  margin-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.tab {
  padding: 12px 24px;
  cursor: pointer;
  font-weight: bold;
  color: #666;
  transition: all 0.3s ease;
}

.tab.active {
  color: #215476;
  border-bottom: 2px solid #215476;
}

.tab:hover {
  background-color: #f8f9fa;
  border-radius: 6px;
}

.login-form, .register-form {
  display: none;
}

.login-form.active, .register-form.active {
  display: block;
}

.submit-btn {
  color:#eee;
  background-color: #215476;
  width: 100%;
  padding: 14px;
  border-radius: 6px;
  font-weight: bold;
  font-size: 16px;
  margin-top: 15px;
  transition: all 0.3s ease;
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.captcha-container {
  display: flex;
  gap: 10px;
}

.captcha-btn {
  width: 120px;
  flex-shrink: 0;
}

.login-link {
  margin-top: 15px;
  text-align: center;
  color: #666;
}

footer {
  height: 107px;
  background-color: #215476;
}

/* 调整Element Plus表单样式 */
:deep(.el-form-item__label) {
  font-weight: bold;
  color: #1c1b20cd;
  padding: 0 !important;
  margin-bottom: 8px;
}

:deep(.el-input__inner) {
  padding: 12px;
  border-radius: 6px;
}
</style>