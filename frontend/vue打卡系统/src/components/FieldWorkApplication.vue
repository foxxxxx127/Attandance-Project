//外勤申请页面
<template> 
  <div class="field-work-application"> 
    <h3 class="form-title">外勤申请</h3> 
     
    <el-form  
      ref="formRef"  
      :model="form"  
      label-position="top"  
      class="application-form" 
      :rules="rules"
    > 
      <!-- 申请原因 --> 
      <el-form-item label="申请原因" prop="reason"> 
        <el-input 
          v-model="form.reason" 
          placeholder="请输入申请原因" 
          clearable 
          class="form-input large-input" 
        /> 
      </el-form-item> 
       
      <!-- 外勤地点 --> 
      <el-form-item label="外勤地点" prop="location"> 
        <el-input 
          v-model="form.location" 
          placeholder="请输入外勤地点" 
          clearable 
          class="form-input large-input" 
        /> 
      </el-form-item> 
       
      <!-- 时间范围 -->
      <el-form-item label="外勤时间" prop="dateRange">
        <el-date-picker
          v-model="form.dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          class="time-range-picker small-input"
        >
          <template #suffix>
            <el-icon><Calendar /></el-icon>
          </template>
        </el-date-picker>
      </el-form-item>
       
      <!-- 提交按钮 --> 
      <el-form-item> 
        <el-button 
          type="primary" 
          :loading="isSubmitting" 
          class="submit-btn" 
          @click="handleSubmit" 
        > 
          <template v-if="!isSubmitted"> 
            <el-icon class="el-icon--left"><DocumentAdd /></el-icon> 
            提交申请 
          </template> 
          <template v-else> 
            <el-icon class="el-icon--left"><SuccessFilled /></el-icon> 
            申请已提交，等待审核 
          </template> 
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
import { submitFieldWorkApplication } from '@/api/fieldWorkApplication'

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
    ElMessage.warning('请输入外勤原因')
    return
  }
  if (!form.value.location) {
    ElMessage.warning('请输入外勤地点')
    return
  }
  if (form.value.dateRange.length !== 2) {
    ElMessage.warning('请选择外勤时间范围')
    return
  }
  try {
    const data = {
      employee_id: form.value.userId,
      reason: form.value.reason,
      location: form.value.location,
      start_date: form.value.dateRange[0].toISOString().split('T')[0],
      end_date: form.value.dateRange[1].toISOString().split('T')[0]
    }
    const response = await submitFieldWorkApplication(data)
    if (response.data && response.data.message === '外勤申请已提交') {
      ElMessage.success('外勤申请提交成功')
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
.field-work-application { 
  max-width: 600px; 
  margin: 0 auto; 
  padding: 20px; 
  background-color: #fff; 
  border-radius: 8px; 
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1); 
} 

.form-title { 
  text-align: center; 
  margin-bottom: 24px; 
  color: #303133; 
} 

.application-form { 
  padding: 0 20px; 
} 

.form-input { 
  width: 100%; 
} 

.large-input {
  height: 48px;
  
}

.large-input :deep(.el-input__inner) {
  height: 48px;
  line-height: 48px;
  font-size: 16px;
}

.time-range-picker {
  width: 100%;
}

.small-input {
  height: 40px;
}

.small-input :deep(.el-range__inner) {
  height: 40px;
}

.small-input :deep(.el-range-input) {
  height: 38px;
  font-size: 14px;
}

.small-input :deep(.el-range-separator) {
  line-height: 38px;
  font-size: 14px;
}

.small-input :deep(.el-range__close-icon) {
  line-height: 38px;
}

.submit-btn { 
  width: 100%; 
  padding: 12px 24px; 
  font-size: 16px; 
  border-radius: 6px; 
  transition: all 0.3s; 
  align-items: center;
} 

.submit-btn:hover { 
  transform: translateY(-2px); 
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3); 
} 

.el-form-item { 
  margin-bottom: 22px; 
} 

.el-form-item__label { 
  font-weight: 500; 
  color: #606266; 
} 
</style>