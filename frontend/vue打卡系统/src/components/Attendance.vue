//考勤打卡界面
<template>
  <div class="attendance-container">
    <!-- 初始界面 -->
    <div v-if="currentView === 'initial'" class="initial-view">
      <!-- 左侧打卡部分 -->
      <div class="left-section">
        <div class="user-info">
          <el-avatar :size="100" :src="user.avatar" />
          <div class="user-details">
            <h3>{{ user.name }}</h3>
            <p>{{ user.position }}</p>
          </div>
        </div>
        
        <div class="checkin-info">
          <el-tag :type="checkinStatus.type">{{ checkinStatus.text }}</el-tag>
          <p class="checkin-time" v-if="lastCheckin.time">上次打卡: {{ lastCheckin.time }}</p>
        </div>
        
        <el-button 
          type="success" 
          class="check-btn" 
          @click="startCheckin"
          :disabled="!checkinAvailable"
        >
          <el-icon><AlarmClock /></el-icon>
          <span>{{ checkinAvailable ? '打卡' : '今日无需打卡' }}</span>
        </el-button>
        <div class="current-time">{{ currentTime }}</div>
        <div class="map-placeholder">
          <div id="map-container" style="height: 350px; width: 100%;"></div>
          <div class="location-info">
          </div>
        </div>
      </div>
      
      <!-- 右侧部分 -->
      <div class="right-section">
        <!-- 工作日历 -->
        <div class="work-calendar">
          <div class="calendar-header">
            <span>工作日历</span>
            <span class="click-hint">点击查看</span>
          </div>
          <el-calendar v-model="calendarDate" class="mini-calendar">
            <template #date-cell="{ data }">
              <div :class="getDateCellClass(data)">
                {{ data.day.split('-').slice(2).join('-') }}
              </div>
            </template>
          </el-calendar>
        </div>
        
        <!-- 打卡规则 -->
        <div class="checkin-rules">
          <div class="rules-header">
            <span>今日打卡规则</span>
          </div>
          <div class="rules-content">
            <p v-if="checkinRules.method === 'face'">方式: 人脸识别</p>
            <p v-if="checkinRules.method === 'location'">方式: 地理位置</p>
            <p v-if="checkinRules.method === 'mixed'">方式: 人脸识别+地理位置</p>
            <p>时间: {{ checkinRules.startTime }} - {{ checkinRules.endTime }}</p>
            <p v-if="checkinRules.method !== 'face'">允许误差: {{ checkinRules.radius }}米</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 人脸识别界面 -->
    <div v-if="currentView === 'faceRecognition'" class="recognition-view">
      <div class="recognition-box">
        <h3 class="recognition-title">请将脸部正对蓝色显示框内，并保持光线充足</h3>
        <div class="camera-container">
          <video ref="video" autoplay playsinline class="camera-feed"></video>
          <canvas ref="canvas" class="camera-canvas"></canvas>
        </div>
        <div class="action-buttons">
          <el-button @click="cancelRecognition">取消</el-button>
          <el-button type="primary" @click="captureImage" :loading="isProcessing">
            拍照识别
          </el-button>
        </div>
      </div>
    </div>
    
    <!-- 地理位置打卡界面 -->
    <div v-if="currentView === 'locationCheckin'" class="location-view">
      <div class="location-box">
        <h3 class="location-title">请确保已开启定位权限，并在指定范围内打卡</h3>
        <div id="location-map" class="map-container"></div>
        <div class="location-info">
          <p>当前位置: {{ currentLocation.address || '获取中...' }}</p>
          <p>距离: {{ currentLocation.distance !== null ? currentLocation.distance + '米' : '计算中...' }}</p>
          <p>状态: 
            <el-tag :type="locationStatus.type" size="small">
              {{ locationStatus.text }}
            </el-tag>
          </p>
        </div>
        <div class="action-buttons">
          <el-button @click="cancelLocationCheck">取消</el-button>
          <el-button 
            type="primary" 
            @click="checkLocation" 
            :loading="isProcessing"
            :disabled="!locationReady"
          >
            确认打卡
          </el-button>
        </div>
      </div>
    </div>
    
    <!-- 打卡成功界面 -->
    <div v-if="currentView === 'success'" class="success-view">
      <div class="success-box">
        <div class="user-info">
          <el-avatar :size="80" :src="user.avatar" />
          <div class="user-details">
            <h3>{{ user.name }}</h3>
            <p>{{ user.position }}</p>
          </div>
        </div>
        <div class="success-message">
          <el-icon color="#67C23A" :size="60"><CircleCheck /></el-icon>
          <span>打卡成功</span>
        </div>
        <div class="check-time">{{ checkinResult.time }}</div>
        <div class="check-method">方式: {{ checkinResult.method }}</div>
        <div class="check-location" v-if="checkinResult.location">地点: {{ checkinResult.location }}</div>
        <el-button type="primary" class="back-btn" @click="backToInitial">返回</el-button>
      </div>
    </div>
    
    <!-- 打卡失败界面 -->
    <div v-if="currentView === 'failed'" class="failed-view">
      <div class="failed-box">
        <div class="failed-message">
          <el-icon color="#F56C6C" :size="60"><CircleClose /></el-icon>
          <span>打卡失败</span>
        </div>
        <div class="failed-reason">{{ failedReason }}</div>
        <el-button type="primary" class="retry-btn" @click="retryCheckin">重试</el-button>
        <el-button class="back-btn" @click="backToInitial">返回</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
// import {request} from '@/utils/request.js'
import FormData from 'form-data'
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { AlarmClock, CircleCheck, CircleClose } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const locationStatus = ref({
  type: 'info',
  text: '获取位置中...'
})
// 模拟从服务器获取的打卡规则
const checkinRules = ref({
  method: 'mixed', // 'face' | 'location' | 'mixed'
  startTime: '09:00',
  endTime: '18:00',
  radius: 1000, // 允许的误差范围(米)
  location: { // 目标位置坐标
    lat:  23.054521,    // 广东省广州市番禺区东苑一横路 的百度地图坐标
    lng: 113.406689,
    address: '广东省广州市番禺区东苑一横路'
  }
})

// 用户信息
const user = ref({
  avatar: 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png',
  name: '',
  position: ''
})

// 当前时间
const currentTime = ref('')
// 日历日期
const calendarDate = ref(new Date())
// 上次打卡信息
const lastCheckin = ref({
  time: '',
  location: '',
  method: ''
})

// 获取用户信息
const fetchUserInfo = async () => {
  try {
    const employeeId = localStorage.getItem('employee_id') // 假设员工编号存储在 localStorage 中
    if (!employeeId) {
      ElMessage.error('未找到用户信息，请重新登录')
      return
    }

    const response = await axios.get('http://127.0.0.1:5000/get_profile', {
      params: { employee_id: employeeId }
    })

    if (response.status === 200) {
      const data = response.data
      user.value = {
        avatar: user.value.avatar, // 保留默认头像
        name: data.name,
        position: data.position || '未设置职位'
      }
    } else {
      ElMessage.error(response.data.error || '获取用户信息失败')
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
    ElMessage.error(error.response?.data?.error || '获取用户信息失败')
  }
}
// 视图状态
const currentView = ref('initial') // 'initial' | 'faceRecognition' | 'locationCheckin' | 'success' | 'failed'
const isProcessing = ref(false)
const failedReason = ref('')
const checkinAvailable = ref(true)

// 打卡状态
const checkinStatus = ref({
  type: 'info',
  text: '待打卡'
})

// 人脸识别相关
const video = ref(null)
const canvas = ref(null)
let stream = null

// 地理位置相关
const currentLocation = ref({
  lat: null,
  lng: null,
  address: '',
  distance: null
})
const locationReady = ref(false)
let map = null
// let marker = null
// let circle = null
let watchId = null

// 打卡结果
const checkinResult = ref({
  time: '',
  location: '',
  method: ''
})



// 开始打卡
const startCheckin = () => {
  if (!checkinAvailable.value) {
    ElMessage.warning('今日无需打卡')
    return
  }

  // 根据打卡规则进入不同的打卡界面
  if (checkinRules.value.method === 'face') {
    startFaceRecognition()
  } else if (checkinRules.value.method === 'location') {
    startLocationCheck()
  } else {
    // 混合模式默认先进行人脸识别
    startFaceRecognition()
  }
}

// 开始人脸识别
const startFaceRecognition = async () => {
  currentView.value = 'faceRecognition'
  
  try {
    // 请求摄像头权限
    stream = await navigator.mediaDevices.getUserMedia({ 
      video: { 
        facingMode: 'user',
        width: { ideal: 1280 },
        height: { ideal: 720 }
      },
      audio: false
    })
    
    video.value.srcObject = stream
    video.value.play()
  } catch (error) {
    console.error('摄像头访问失败:', error)
    ElMessage.error('无法访问摄像头: ' + error.message)
    backToInitial()
  }
}

// 拍照识别
const captureImage = () => {
  isProcessing.value = true

  // 设置canvas尺寸与视频一致
  canvas.value.width = video.value.videoWidth
  canvas.value.height = video.value.videoHeight

  // 在canvas上绘制当前视频帧
  const ctx = canvas.value.getContext('2d')
  ctx.drawImage(video.value, 0, 0, canvas.value.width, canvas.value.height)

  canvas.value.toBlob(async (blob) => {
    try {
      isProcessing.value = true

      // 创建 FormData 并添加 blob
      const formData = new FormData()
      formData.append('face_image', blob, 'face.jpg')
      // 假设还需要员工ID
      formData.append('employee_id', localStorage.getItem('employee_id') || '')

      // 调用后端人脸识别接口
      const response = await axios.post('http://127.0.0.1:5000/api/face_recognition', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      if (response.data.code === 0 && response.data.result === true) {
        // 识别成功
        if (checkinRules.value.method === 'mixed') {
          startLocationCheck()
        } else {
          completeCheckin('face')
        }
      } else {
        failedReason.value = response.data.msg || '人脸识别失败，请重试'
        currentView.value = 'failed'
      }
    } catch (error) {
      console.error('人脸识别失败:', error)
      failedReason.value = error.response?.data?.msg || '人脸识别服务异常: ' + error.message
      currentView.value = 'failed'
    } finally {
      isProcessing.value = false
      stopCamera()
    }
  }, 'image/jpeg', 0.9)
}
// 停止摄像头
const stopCamera = () => {
  if (stream) {
    stream.getTracks().forEach(track => track.stop())
    stream = null
  }
  if (video.value) {
    video.value.srcObject = null
  }
}

// 开始地理位置打卡
const startLocationCheck = () => {
  currentView.value = 'locationCheckin'
  
  // 初始化地图
  initMap().then(() => {
    // 开始监听位置变化
    watchPosition()
  }).catch(error => {
    console.error('地图初始化失败:', error)
    ElMessage.error('地图加载失败: ' + error.message)
    backToInitial()
  })
}

const initMap = () => {
  return new Promise((resolve, reject) => {
    loadBaiduMap().then(() => {
      const target = checkinRules.value.location
      const container = document.getElementById('location-map')
      if (!container) return reject(new Error('找不到地图容器'))
      map = new BMap.Map(container)
      const targetPoint = new BMap.Point(target.lng, target.lat)
      map.centerAndZoom(targetPoint, 16)
      // 目标点标记
      const targetMarker = new BMap.Marker(targetPoint)
      map.addOverlay(targetMarker)
      // 允许范围圆
      const circle = new BMap.Circle(targetPoint, checkinRules.value.radius, {
        strokeColor: "#409eff",
        fillColor: "#80d8ff88",
        strokeWeight: 2,
        fillOpacity: 0.3
      })
      map.addOverlay(circle)
      resolve()
    }).catch(e => {
      reject(e)
    })
  })
}

const watchPosition = () => {
  if (watchId) {
    navigator.geolocation.clearWatch(watchId)
  }
  watchId = navigator.geolocation.watchPosition(
    (position) => {
      const { latitude, longitude } = position.coords
      currentLocation.value.lat = latitude
      currentLocation.value.lng = longitude

      // 计算距离
      calculateDistance(latitude, longitude)

      // 更新地图显示
      updateMap(latitude, longitude)

      // 新增：用百度地图逆地理编码获取地址
      if (window.BMap && map) {
        const userPoint = new BMap.Point(longitude, latitude)
        const geocoder = new BMap.Geocoder()
        geocoder.getLocation(userPoint, (result) => {
          currentLocation.value.address = result?.address || '未知地址'
        })
      }

      locationReady.value = true
    },
    (error) => {
      console.error('获取位置失败:', error)
      ElMessage.error('获取位置失败: ' + error.message)
      locationReady.value = false
    },
    {
      enableHighAccuracy: true,
      timeout: 5000,
      maximumAge: 0
    }
  )
}

const calculateDistance = (lat, lng) => {
  const target = checkinRules.value.location
  const userPoint = new BMap.Point(lng, lat)
  const targetPoint = new BMap.Point(target.lng, target.lat)
  // 使用百度地图API计算距离
  const distance = baiduMap.getDistance(userPoint, targetPoint)
  currentLocation.value.distance = Math.round(distance)
  // 更新状态
  updateLocationStatus(distance)
}

// 更新位置状态
const updateLocationStatus = (distance) => {
  if (distance <= checkinRules.value.radius) {
    locationStatus.value = {
      type: 'success',
      text: '在允许范围内'
    }
  } else {
    locationStatus.value = {
      type: 'danger',
      text: '超出允许范围'
    }
  }
}

const updateMap = (lat, lng) => {
  if (map) {
    const userPoint = new BMap.Point(lng, lat)
    // 移动地图中心
    map.panTo(userPoint)
    // 用户位置标记
    if (!map._userMarker) {
      map._userMarker = new BMap.Marker(userPoint, { icon: new BMap.Icon("https://api.map.baidu.com/images/marker_red.png", new BMap.Size(23, 25)) })
      map.addOverlay(map._userMarker)
    } else {
      map._userMarker.setPosition(userPoint)
    }
  }
}

// 检查位置并打卡
const checkLocation = () => {
  isProcessing.value = true
  
  // 检查是否在允许范围内
  if (currentLocation.value.distance <= checkinRules.value.radius) {
    completeCheckin('location')
  } else {
    failedReason.value = '您不在允许的打卡范围内'
    currentView.value = 'failed'
  }
  
  isProcessing.value = false
}

// 完成打卡
const completeCheckin = (method) => {
  // 记录打卡结果
  const now = new Date()
  checkinResult.value = {
    time: `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`,
    location: currentLocation.value.address || checkinRules.value.location.address,
    method: method === 'face' ? '人脸识别' : '地理位置'
  }
  
  // 更新上次打卡信息
  lastCheckin.value = {
    time: checkinResult.value.time,
    location: checkinResult.value.location,
    method: checkinResult.value.method
  }
  
  // 更新打卡状态
  checkinStatus.value = {
    type: 'success',
    text: '已打卡'
  }
  
  // 进入成功界面
  currentView.value = 'success'
  
  // 清理资源
  stopLocationWatch()
  stopCamera()
}

// 停止位置监听
const stopLocationWatch = () => {
  if (watchId) {
    navigator.geolocation.clearWatch(watchId)
    watchId = null
  }
}

// 取消人脸识别
const cancelRecognition = () => {
  stopCamera()
  backToInitial()
}

// 取消地理位置打卡
const cancelLocationCheck = () => {
  stopLocationWatch()
  backToInitial()
}

// 返回初始界面
const backToInitial = () => {
  currentView.value = 'initial'
}

// 重试打卡
const retryCheckin = () => {
  if (failedReason.value.includes('人脸识别')) {
    startFaceRecognition()
  } else if (failedReason.value.includes('位置') || failedReason.value.includes('范围')) {
    startLocationCheck()
  } else {
    backToInitial()
  }
}

// 日历日期样式
const getDateCellClass = (data) => {
  const day = data.day
  // 模拟工作日/周末样式
  const date = new Date(day)
  const isWeekend = date.getDay() === 0 || date.getDay() === 6
  return {
    'is-weekend': isWeekend,
    'is-today': day === new Date().toISOString().split('T')[0],
    'is-checked': lastCheckin.value.time && day === new Date().toISOString().split('T')[0]
  }
}

// 定时更新时间
let timer = null
onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
  stopCamera()
  stopLocationWatch()
})
// 在组件挂载时获取用户信息
onMounted(() => {
  fetchUserInfo()
})
/* global BMap */
// 地图相关
const BAIDU_MAP_AK = 'nFnPIgtDZWDFiV1V4G8bZZ8AAMp5xAmb'
const baiduLocation = ref({
  longitude: null,
  latitude: null,
  address: ''
})
let baiduMap = null
let baiduMarker = null
let baiduGeocoder = null

const loadBaiduMap = () => {
  return new Promise((resolve, reject) => {
    if (window.BMap && window.BMap.Map) {
      resolve()
      return
    }
    const callbackName = `onBaiduMapLoaded_${Date.now()}`
    window[callbackName] = () => {
      resolve()
      delete window[callbackName]
    }
    const script = document.createElement('script')
    script.src = `https://api.map.baidu.com/api?v=3.0&ak=${BAIDU_MAP_AK}&callback=${callbackName}`
    script.onerror = () => reject(new Error('百度地图加载失败'))
    document.body.appendChild(script)
  })
}

const initBaiduMap = async () => {
  await loadBaiduMap()
  const container = document.getElementById('map-container')
  if (!container) return
  baiduMap = new BMap.Map(container)
  baiduGeocoder = new BMap.Geocoder()
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const lng = pos.coords.longitude
        const lat = pos.coords.latitude
        baiduLocation.value.longitude = lng
        baiduLocation.value.latitude = lat
        const point = new BMap.Point(lng, lat)
        baiduMap.centerAndZoom(point, 16)
        baiduMarker = new BMap.Marker(point)
        baiduMap.addOverlay(baiduMarker)
        baiduGeocoder.getLocation(point, (result) => {
          baiduLocation.value.address = result?.address || '未知地址'
        })
      },
      (err) => {
        console.error('定位失败:', err)
        ElMessage.error('定位失败，显示默认位置')
        const point = new BMap.Point(116.404, 39.915)
        baiduMap.centerAndZoom(point, 15)
      }
    )
  } else {
    ElMessage.warning('浏览器不支持定位')
    const point = new BMap.Point(116.404, 39.915)
    baiduMap.centerAndZoom(point, 15)
  }
}

onMounted(() => {
  initBaiduMap()
})
onBeforeUnmount(() => {
  if (baiduMap) {
    baiduMap.clearOverlays()
    baiduMap = null
  }
})
</script>

<style scoped>
.attendance-container {
  display: flex;
  height: 100vh;
  padding: 20px;
  background-color: #f5f7fa;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
}

.initial-view {
  display: flex;
  width: 100%;
  gap: 20px;
}

.left-section {
  flex: 2;
  display: flex;
  flex-direction: column;
  background-color: #2f5373;
  border-radius: 12px;      /* 圆角更大一点 */
  padding: 30px 20px;      /* 上下左右内边距更大或更小都可以 */
  margin: 30px 0 40px 0;   /* 上下外边距，左右可根据需要调整 */
  box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.1);
  min-width: 400px;        /* 最小宽度，防止太窄 */
  max-width: 700px;        /* 最大宽度，防止太宽 */
}

.right-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.user-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;
  margin-top: 30px; /* 新增：整体往下移30px，可根据需要调整 */
}
.user-details {
  text-align: center;
  margin-top: 10px;
}

.user-details h3 {
  margin: 5px 0;
  font-size: 20px;
  color: #fff; 
}

.user-details p {
  margin: 0;
  color:#fff; 
  font-size: 16px;
}

.checkin-info {
  text-align: center;
  margin-bottom: 15px;
  color:#909399;
}

.checkin-time {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.check-btn {
  margin: 0 auto 20px;
  padding: 0;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  font-size: 24px;
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  justify-content: center;
  background-color: #4ba38b !important;
  border: none;
  color: #fff;
}

.current-time {
  text-align: center;
  font-size: 15px;
  color:#fff;
  margin-bottom: 20px;
}

.map-placeholder {
  height: 350px;
  background-color: #f0f2f5;
  border-radius: 4px;
  margin-top: 20px;
  overflow: hidden;
}
#map-container {
  height: 100%;
  width: 100%;
}

.work-calendar, .checkin-rules, .approval-notice {
  background-color: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.calendar-header, .rules-header, .notice-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.click-hint {
  font-size: 12px;
  color: #409eff;
  cursor: pointer;
}

.mini-calendar {
  --el-calendar-cell-width: 30px;
  --el-calendar-cell-height: 30px;
}

.mini-calendar :deep(.el-calendar__body) {
  padding: 0;
}

.mini-calendar :deep(.el-calendar-table .el-calendar-day) {
  height: 30px;
  padding: 0;
  display: flex;
  justify-content: center;
  align-items: center;
}

.is-weekend {
  color: #F56C6C;
}

.is-today {
  background-color: #f0f9eb;
  border-radius: 50%;
}

.is-checked {
  position: relative;
}

.is-checked::after {
  content: '';
  position: absolute;
  bottom: 2px;
  left: 50%;
  transform: translateX(-50%);
  width: 4px;
  height: 4px;
  background-color: #67C23A;
  border-radius: 50%;
}

.rules-content {
  font-size: 14px;
  color: #606266;
}

.rules-content p {
  margin: 8px 0;
}

/* 识别界面 */
.recognition-view, .location-view {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
}

.recognition-box, .location-box {
  width: 80%;
  max-width: 600px;
  background-color: white;
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.recognition-title, .location-title {
  text-align: center;
  margin-bottom: 30px;
  color: #606266;
}

.camera-container {
  position: relative;
  width: 600px;      /* 调整摄像头宽度 */
  height: 360px;     /* 调整摄像头高度 */
  margin: 40px auto 30px auto;
  display: flex;
  justify-content: center;
  align-items: center;
}

.camera-feed {
  width: 100%;
  height: 100%;
  border-radius: 8px;
  display: block;
}

.camera-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: none;
}

.camera-circle {
  width: 200px;
  height: 200px;
  border-radius: 50%;
  border: 2px dashed #409eff;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 30px;
  color: #409eff;
}

.action-buttons {
  display: flex;
  gap: 15px;
  width: 100%;
  max-width: 400px;
}

.action-buttons .el-button {
  flex: 1;
  padding: 12px;
}

.location-info {
  width: 100%;
  max-width: 400px;
  margin: 15px 0;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.location-info p {
  margin: 8px 0;
  font-size: 14px;
}

/* 打卡成功界面 */
.success-view, .failed-view {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
}

.success-box, .failed-box {
  width: 80%;
  max-width: 500px;
  background-color: white;
  border-radius: 8px;
  padding: 40px 30px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.success-message, .failed-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 20px 0;
}

.success-message span, .failed-message span {
  font-size: 24px;
  font-weight: bold;
  margin-top: 10px;
}

.check-time, .check-method, .check-location {
  font-size: 14px;
  color: #606266;
  margin: 8px 0;
}

.check-location {
  margin-bottom: 20px;
}

.failed-reason {
  color: #F56C6C;
  margin: 15px 0;
  font-size: 16px;
}

.back-btn, .retry-btn {
  width: 100%;
  max-width: 200px;
  margin-top: 20px;
}

.retry-btn {
  margin-bottom: 10px;
}

</style>