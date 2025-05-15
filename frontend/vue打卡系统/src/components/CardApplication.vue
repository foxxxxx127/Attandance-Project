//补卡申请页面
<template> 
    <div class="card-application"> 
      <!-- 标题 --> 
      <h2 class="title">补卡申请</h2> 
       
      <!-- 表单区域 --> 
      <el-form  
        :model="form"  
        label-position="top"  
        class="application-form" 
        @submit.prevent="handleSubmit" 
      > 
        <!-- 申请原因输入框 --> 
        <el-form-item label="申请原因"> 
          <el-input 
            v-model="form.reason" 
            placeholder="申请原因：******" 
            clearable 
          /> 
        </el-form-item> 
         
        <!-- 日期选择器 --> 
        <el-form-item label="选择时间"> 
          <el-date-picker 
            v-model="form.dateRange" 
            type="daterange" 
            range-separator="至" 
            start-placeholder="请选择日期" 
            end-placeholder="请选择日期" 
            :prefix-icon="Calendar" 
          /> 
        </el-form-item> 
         
        <!-- 提交按钮 --> 
        <el-form-item> 
          <el-button 
            class="submit-btn" 
            type="primary" 
            :icon="isSubmitted ? SuccessFilled : ''" 
            :disabled="isSubmitted" 
            @click="handleSubmit" 
          > 
            {{ isSubmitted ? '申请已提交，等待审核' : '提交' }} 
          </el-button> 
        </el-form-item> 
      </el-form> 
    </div> 
</template> 
   
  <script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Calendar, SuccessFilled } from '@element-plus/icons-vue'
import { useUserInfo } from '@/stores/userInfo'
import { cardApplicationService } from '@/api/cardApplication'

const userInfo = useUserInfo()
const userId = userInfo.userId

const form = ref({
  reason: '',
  dateRange: [],
  userId: userId
})

const isSubmitted = ref(false)
const resetForm = () => {
  form.value.reason = ''
  form.value.dateRange = []
  isSubmitted.value = false
}

const handleSubmit = async () => {
  if (!form.value.reason) {
    ElMessage.warning('请输入补卡原因')
    return
  }
  if (form.value.dateRange.length !== 2) {
    ElMessage.warning('请选择补卡时间范围')
    return
  }
  try {
    const data = {
      employee_id: form.value.userId,
      reason: form.value.reason,
      start_date: form.value.dateRange[0].toISOString().split('T')[0],
      end_date: form.value.dateRange[1].toISOString().split('T')[0]
    }
    const response = await cardApplicationService(data)
    if (response.data && response.data.message === '补卡申请已提交') {
      ElMessage.success('补卡申请提交成功')
      isSubmitted.value = true

      // 2秒后重置表单
      setTimeout(() => {
        resetForm()
        ElMessage.info('表单已重置，可继续申请')
      }, 2000)
    } else {
      ElMessage.error(response.data.message || '提交失败')
    }
  } catch (error) {
    ElMessage.error('提交失败')
    console.error(error)
  }
}
</script>
   
  <style scoped> 
  .card-application { 
    max-width: 500px; 
    margin: 0 auto; 
    padding: 20px; 
    background-color: #fff; 
    border-radius: 8px; 
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1); 
  } 
   
  .title { 
    text-align: center; 
    margin-bottom: 24px; 
    color: #303133; 
  } 
   
  .application-form { 
    padding: 0 20px; 
  } 
   
  /* 提交按钮样式 */ 
  .submit-btn { 
    width: 100%; 
    border-radius: 20px; /* 圆角矩形 */ 
    padding: 12px 0; 
    font-size: 16px; 
    margin-top: 10px; 
  } 
   
  /* 日期选择器图标样式 */ 
  :deep(.el-date-editor .el-input__prefix) { 
    display: flex; 
    align-items: center; 
  } 
  </style> 
 
 
 
 
 
 
 

 
 
 
 

 
 
 
 

 
 
 
 

 
 
 
 
