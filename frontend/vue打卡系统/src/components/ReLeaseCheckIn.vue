<template>
  <div class="publish-checkin-container">
    <el-card shadow="hover" class="form-card">
      <template #header>
        <div class="card-header">
          <span>发布新打卡</span>
        </div>
      </template>

      <el-form :model="form" label-width="120px" label-position="left">
        <!-- 打卡方式选择 -->
        <el-form-item label="打卡方式">
          <el-radio-group v-model="form.checkinType">
            <el-radio label="mixed">混合模式</el-radio>
            <el-radio label="face">人脸识别</el-radio>
            <el-radio label="location">地理位置</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 地理位置设置 -->
        <div v-if="form.checkinType === 'location'">
          <el-form-item label="选择地点">
            <el-button type="primary" @click="openMapDialog">选择地理位置</el-button>
            <el-button @click="getCurrentLocation" :loading="locating">
            <el-icon :component="Location" />
              使用当前位置
            </el-button>
            <div v-if="form.location" class="location-info">
              <p>经度: {{ form.location.longitude.toFixed(6) }}</p>
              <p>纬度: {{ form.location.latitude.toFixed(6) }}</p>
              <p v-if="form.location.address">地址: {{ form.location.address }}</p>
            </div>
          </el-form-item>

          <el-form-item label="打卡范围(米)">
            <el-input-number 
              v-model="form.radius" 
              :min="50" 
              :max="1000" 
              :step="50"
            />
          </el-form-item>
        </div>

        <!-- 打卡时间设置 -->
        <el-form-item label="打卡时间">
          <el-date-picker
            v-model="form.timeRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="submitForm">发布打卡</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 地图选择对话框 -->
    <el-dialog
      v-model="mapDialogVisible"
      title="选择打卡位置"
      width="80%"
      :fullscreen="false"
      :destroy-on-close="false"
      :close-on-click-modal="false"
      :before-close="handleDialogClose"
      class="map-dialog"
      :append-to-body="true"
    >
      <div class="map-dialog-content">
        <div class="map-container-wrapper">
          <div 
            ref="mapContainerRef"
            id="baidu-map-container" 
            class="map-container"
          />
          <div v-if="mapLoading" class="map-loading">
            <el-icon :component="Loading" class="is-loading" />
            <span>地图加载中...</span>
          </div>
        </div>
        <div class="map-controls">
          <div class="search-box">
            <el-input
              v-model="searchQuery"
              placeholder="搜索地点"
              clearable
              @keyup.enter="handleSearch"
            >
              <template #append>
                <el-button @click="handleSearch">
                   <el-icon :component="Search" />
                </el-button>
              </template>
            </el-input>
          </div>
          <div class="control-buttons">
            <el-button @click="locateCurrentPosition" :loading="locating" type="primary" plain>
              <el-icon :component="Location" />
              定位当前位置
            </el-button>
            <el-button @click="centerToSelected" :disabled="!selectedLocation" plain>
              <el-icon :component="Aim" />
              居中显示
            </el-button>
          </div>
          <div class="selected-info" v-if="selectedLocation">
            <h4>已选位置信息</h4>
            <el-divider />
            <div class="info-item">
              <span class="label">经度:</span>
              <span class="value">{{ selectedLocation.longitude.toFixed(6) }}</span>
            </div>
            <div class="info-item">
              <span class="label">纬度:</span>
              <span class="value">{{ selectedLocation.latitude.toFixed(6) }}</span>
            </div>
            <div class="info-item" v-if="selectedLocation.address">
              <span class="label">地址:</span>
              <span class="value">{{ selectedLocation.address }}</span>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="closeMapDialog">取消</el-button>
          <el-button 
            type="primary" 
            @click="confirmLocation" 
            :disabled="!selectedLocation"
          >
            确定
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
/* eslint-disable */
/* global BMap, BMAP_ANCHOR_TOP_LEFT, BMAP_NAVIGATION_CONTROL_SMALL, BMAP_ANCHOR_BOTTOM_LEFT, BMAP_STATUS_SUCCESS */

import { ref, nextTick, onBeforeUnmount, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Location, Aim, Loading, Search } from '@element-plus/icons-vue'
import request from '@/utils/request'

// 百度地图API密钥 - 请替换成您自己的AK
const BAIDU_MAP_AK = 'nFnPIgtDZWDFiV1V4G8bZZ8AAMp5xAmb'

// 表单数据
const form = ref({
  checkinType: 'mixed', // mixed/face/location
  timeRange: [],
  location: null, // { longitude, latitude, address? }
  radius: 100 // 打卡范围(米)
})

// 地图相关状态
const mapDialogVisible = ref(false)
const selectedLocation = ref(null)
const locating = ref(false)
const mapLoading = ref(true)
const searchQuery = ref('')
const isMapApiLoaded = ref(false)
const mapInitialized = ref(false)

let map = null
let marker = null
let circle = null
let geocoder = null
let localSearch = null

// 添加容器引用
const mapContainerRef = ref(null)

// 安全DOM操作辅助函数
const safeDOMOperation = async (selector, operation) => {
  await nextTick()
  const el = document.querySelector(selector)
  if (el && el.offsetParent) {
    return operation(el)
  }
  throw new Error(`元素 ${selector} 不可用或未渲染`)
}

// 组件卸载前清理地图
onBeforeUnmount(() => {
  // 清理地图实例
  if (map) {
    try {
      map.clearOverlays()
      map.destroy()
    } catch (e) {
      console.warn('地图实例清理失败:', e)
    }
    map = null
  }
  
  // 清理全局回调
  delete window.initBaiduMap
  delete window.BMap
  
  // 强制移除可能残留的脚本
  const scripts = document.querySelectorAll('script[src*="api.map.baidu.com"]')
  scripts.forEach(script => script.remove())
})

// 监听对话框显示状态
watch(mapDialogVisible, async (visible) => {
  console.log('对话框可见性变化:', visible)
  
  if (!visible) {
    console.log('对话框关闭，清理资源')
    cleanMap()
  }
})
// 添加关闭对话框方法
const closeMapDialog = () => {
  mapDialogVisible.value = false
}
// 加载百度地图API
const loadBaiduMap = () => {
  return new Promise((resolve, reject) => {
    try {
      console.log('开始检查百度地图状态...')
      
      // 如果已加载，直接返回
      if (window.BMap && window.BMap.Map) {
        console.log('检测到有效的 BMap 对象，无需重新加载')
        isMapApiLoaded.value = true
        resolve()
        return
      }

      // 使用新的 Promise 处理加载过程
      const loadPromise = new Promise((res, rej) => {
        const callbackName = `initBaiduMap_${Date.now()}`
        
        window[callbackName] = () => {
          console.log('百度地图回调函数执行')
          if (!window.BMap) {
            const error = new Error('BMap 对象未正确加载')
            console.error(error)
            rej(error)
            return
          }
          console.log('百度地图 API 加载成功')
          isMapApiLoaded.value = true
          res()
          delete window[callbackName]
        }

        const script = document.createElement('script')
        script.type = 'text/javascript'
        script.src = `https://api.map.baidu.com/api?v=3.0&ak=${BAIDU_MAP_AK}&callback=${callbackName}`
        
        script.onerror = (e) => {
          console.error('百度地图脚本加载失败:', e)
          rej(new Error('地图加载失败'))
        }

        document.body.appendChild(script)
        console.log('地图脚本已插入到页面')
      })

      // 设置超时处理
      const timeoutPromise = new Promise((_, rej) => {
        setTimeout(() => {
          rej(new Error('百度地图加载超时'))
        }, 10000)
      })

      // 使用 Promise.race 处理超时
      Promise.race([loadPromise, timeoutPromise])
        .then(() => {
          console.log('百度地图 API 加载完成')
          resolve()
        })
        .catch((error) => {
          console.error('百度地图加载失败:', error)
          reject(error)
        })

    } catch (error) {
      console.error('加载百度地图时发生错误:', error)
      reject(error)
    }
  })
}

// 初始化地图
const initMap = async () => {
  try {
    console.log('===== 开始初始化地图 =====')
    
    if (!window.BMap) {
      throw new Error('BMap 对象不存在')
    }

    const container = mapContainerRef.value
    if (!container) {
      throw new Error('地图容器未找到')
    }

    // 等待 DOM 完全渲染
    await nextTick()
    
    // 确保容器可见且有尺寸
    if (!container.offsetParent || container.offsetWidth === 0) {
      throw new Error('地图容器未正确渲染')
    }

    // 清理旧实例
    if (map) {
      try {
        map.clearOverlays()
        map.destroy()
      } catch (e) {
        console.warn('清理旧地图实例失败:', e)
      }
      map = null
    }

    // 创建新实例
    map = new window.BMap.Map(container, {
      enableMapClick: true,
      minZoom: 10,
      maxZoom: 19,
      enableHighResolution: true,
      enableAutoResize: true,
    })

    if (!map) {
      throw new Error('地图实例创建失败')
    }

    // 设置中心点和控件
    const point = new window.BMap.Point(116.404, 39.915)
    map.centerAndZoom(point, 15)
    
    // 添加基本控件
    map.enableScrollWheelZoom()
    map.enableDragging()
    map.addControl(new window.BMap.NavigationControl())
    map.addControl(new window.BMap.ScaleControl())

    // 初始化服务
    localSearch = new window.BMap.LocalSearch(map, {
      onSearchComplete: handleSearchComplete
    })
    geocoder = new window.BMap.Geocoder()

    // 添加事件监听
    map.addEventListener('click', handleMapClick)
    map.addEventListener('tilesloaded', () => {
      console.log('地图瓦片加载完成')
      mapLoading.value = false
    })

    mapInitialized.value = true
    console.log('地图初始化完成')

  } catch (error) {
    console.error('地图初始化失败:', error)
    mapLoading.value = false
    throw error
  }
}

// 搜索完成处理
const handleSearchComplete = (results) => {
  if (localSearch.getStatus() !== BMAP_STATUS_SUCCESS) {
    ElMessage.warning('未找到搜索结果')
    return
  }
  
  if (results.getNumPois() > 0) {
    const firstResult = results.getPoi(0)
    updateSelectedLocation(firstResult.point.lng, firstResult.point.lat)
    ElMessage.success(`已定位到: ${firstResult.title}`)
  }
}

// 地图点击处理
const handleMapClick = async (e) => {
  try {
    await updateSelectedLocation(e.point.lng, e.point.lat)
  } catch (error) {
    console.error('位置选择失败:', error)
    ElMessage.error('位置选择失败')
  }
}

// 更新选中位置
const updateSelectedLocation = async (lng, lat) => {
  try {
    const point = new BMap.Point(lng, lat)
    
    // 清除旧覆盖物
    if (marker) map.removeOverlay(marker)
    if (circle) map.removeOverlay(circle)
    
    // 添加新标记
    marker = new BMap.Marker(point, { 
      enableDragging: true,
      raiseOnDrag: true
    })
    marker.addEventListener('dragend', (e) => {
      updateSelectedLocation(e.point.lng, e.point.lat)
    })
    map.addOverlay(marker)
    
    // 添加范围圈
    circle = new BMap.Circle(point, form.value.radius, {
      strokeColor: "#1890ff",
      strokeWeight: 2,
      strokeOpacity: 0.8,
      fillColor: "#1890ff",
      fillOpacity: 0.2
    })
    map.addOverlay(circle)
    
    // 获取地址信息
    const address = await new Promise((resolve) => {
      geocoder.getLocation(point, (result) => {
        resolve(result ? formatAddress(result.addressComponents) : '未知地址')
      })
    })
    
    selectedLocation.value = {
      longitude: lng,
      latitude: lat,
      address: address
    }
    
    // 居中显示
    map.panTo(point)
    
  } catch (error) {
    console.error('更新位置失败:', error)
    throw error
  }
}

// 格式化地址
const formatAddress = (addComp) => {
  const { province, city, district, street, streetNumber } = addComp
  return `${province || ''}${city || ''}${district || ''}${street || ''}${streetNumber || ''}`
}

// 清理地图资源
const cleanMap = () => {
  try {
    if (map) {
      // 移除事件监听
      map.removeEventListener('click', handleMapClick)
      
      // 清除覆盖物
      map.clearOverlays()
      
      try {
        map.destroy()
      } catch (e) {
        console.warn('地图实例销毁失败:', e)
      }
      map = null
    }

    // 清理其他实例
    if (marker) {
      marker.removeEventListener('dragend')
      marker = null
    }
    circle = null
    localSearch = null
    geocoder = null

    // 重置状态
    selectedLocation.value = null
    mapLoading.value = true
    searchQuery.value = ''
    mapInitialized.value = false

  } catch (e) {
    console.error('清理地图资源时出错:', e)
  }
}
// 修改对话框关闭处理函数
const handleDialogClose = (done) => {
  try {
    cleanMap()
  } finally {
    done()
  }
}

// 打开地图对话框
const openMapDialog = async () => {
  try {
    console.log('开始打开地图对话框...')
    mapLoading.value = true
    mapDialogVisible.value = true
    
    // 等待对话框渲染完成
    await nextTick()
    await new Promise(resolve => setTimeout(resolve, 300))

    // 确保容器已准备好
    const container = mapContainerRef.value
    if (!container) {
      throw new Error('地图容器未找到')
    }

    // 加载地图API
    if (!window.BMap || !isMapApiLoaded.value) {
      await loadBaiduMap()
    }

    // 等待 DOM 更新
    await nextTick()
    
    // 初始化地图
    await initMap()

  } catch (error) {
    console.error('打开地图对话框失败:', error)
    ElMessage.error(error.message || '地图加载失败')
    mapDialogVisible.value = false
  } finally {
    if (!mapInitialized.value) {
      mapLoading.value = false
    }
  }
}
// 搜索处理
const handleSearch = () => {
  if (!searchQuery.value.trim()) {
    ElMessage.warning('请输入搜索关键词')
    return
  }
  
  if (!localSearch) {
    ElMessage.error('搜索功能未初始化')
    return
  }
  
  localSearch.search(searchQuery.value)
}

// 居中显示已选位置
const centerToSelected = () => {
  if (selectedLocation.value && map) {
    const point = new BMap.Point(
      selectedLocation.value.longitude,
      selectedLocation.value.latitude
    )
    map.panTo(point)
    map.setZoom(17)
  }
}

// 定位当前位置（地图对话框内）
const locateCurrentPosition = async () => {
  if (!navigator.geolocation) {
    ElMessage.warning('您的浏览器不支持地理位置功能')
    return
  }

  // 确保百度地图API已加载
  if (!isMapApiLoaded.value) {
    try {
      await loadBaiduMap()
    } catch (e) {
      ElMessage.error('百度地图API加载失败，无法定位')
      return
    }
  }

  locating.value = true
  navigator.geolocation.getCurrentPosition(
    async (position) => {
      try {
        const { lat, lng } = await convertWGS84ToBD09(
          position.coords.latitude,
          position.coords.longitude
        )
        await updateSelectedLocation(lng, lat)
        ElMessage.success('定位成功')
      } catch (error) {
        console.error('坐标转换失败:', error)
        ElMessage.error('定位失败')
      } finally {
        locating.value = false
      }
    },
    (error) => {
      locating.value = false
      console.error('获取位置失败:', error)
      ElMessage.error(`获取位置失败: ${error.message}`)
    },
    {
      enableHighAccuracy: true,
      timeout: 10000
    }
  )
}

// 获取当前位置(直接设置表单)
const getCurrentLocation = async () => {
  if (!navigator.geolocation) {
    ElMessage.warning('您的浏览器不支持地理位置功能')
    return
  }

  // 确保百度地图API已加载
  if (!isMapApiLoaded.value) {
    try {
      await loadBaiduMap()
    } catch (e) {
      ElMessage.error('百度地图API加载失败，无法定位')
      return
    }
  }

  locating.value = true
  navigator.geolocation.getCurrentPosition(
    async (position) => {
      try {
        const { lat, lng } = await convertWGS84ToBD09(
          position.coords.latitude,
          position.coords.longitude
        )
        let address = ''
        try {
          address = await getAddressByCoordinate(lng, lat)
        } catch (error) {
          address = '未知地址'
        }
        form.value.location = {
          longitude: lng,
          latitude: lat,
          address: address
        }
        ElMessage.success('当前位置已设置')
      } catch (error) {
        console.error('坐标转换失败:', error)
        ElMessage.error('定位失败')
      } finally {
        locating.value = false
      }
    },
    (error) => {
      locating.value = false
      console.error('获取位置失败:', error)
      ElMessage.error(`获取位置失败: ${error.message}`)
    },
    {
      enableHighAccuracy: true,
      timeout: 10000
    }
  )
}

// WGS84坐标转百度坐标(BD09)
const convertWGS84ToBD09 = async (lat, lng) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      // 简化的坐标转换算法
      resolve({
        lat: lat + 0.0060,
        lng: lng + 0.0065
      })
    }, 300)
  })
}

// 根据坐标获取地址
const getAddressByCoordinate = (lng, lat) => {
  return new Promise((resolve, reject) => {
    if (!window.BMap) {
      reject(new Error('百度地图API未加载'))
      return
    }
    if (!geocoder) geocoder = new BMap.Geocoder()
    const point = new BMap.Point(lng, lat)
    geocoder.getLocation(point, (result) => {
      if (result) {
        const addComp = result.addressComponents
        resolve(`${addComp.province}${addComp.city}${addComp.district}${addComp.street}${addComp.streetNumber}`)
      } else {
        resolve(null)
      }
    })
  })
}

// 确认位置选择
const confirmLocation = () => {
  if (selectedLocation.value) {
    form.value.location = { ...selectedLocation.value }
    closeMapDialog()
    ElMessage.success('位置选择成功')
  }
}

// 提交表单
const submitForm = () => {
  if (!form.value.timeRange || form.value.timeRange.length !== 2) {
    ElMessage.error('请选择打卡时间范围')
    return
  }

  if (form.value.checkinType === 'location' && !form.value.location) {
    ElMessage.error('请选择打卡位置')
    return
  }

  const payload = {
    checkinType: form.value.checkinType,
    startTime: form.value.timeRange[0],
    endTime: form.value.timeRange[1],
    ...(form.value.checkinType === 'location' ? {
      location: form.value.location,
      radius: form.value.radius
    } : {})
  }

  request({
    method: 'post',
    url: '/releasecheckin',
    data: payload
  }).then((response) => {
    if (response.data.code === 0) {
      ElMessage.success('打卡发布成功')
      resetForm()
    } else {
      ElMessage.error(response.data.message || '打卡发布失败')
    }
  }).catch((error) => {
    console.error(error)
    ElMessage.error('打卡发布失败')
  })
}

// 重置表单
const resetForm = () => {
  form.value = {
    checkinType: 'mixed',
    timeRange: [],
    location: null,
    radius: 100
  }
  ElMessage.success('表单已重置')
}
</script>

<style scoped>
.publish-checkin-container {
  max-width: 800px;
  margin: 20px auto;
  padding: 20px;
}

.form-card {
  border-radius: 8px;
}

.card-header {
  font-size: 18px;
  font-weight: bold;
}

.location-info {
  margin-top: 10px;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
  font-size: 14px;
}

.location-info p {
  margin: 5px 0;
}

.map-dialog :deep(.el-dialog__body) {
  padding: 0;
  height: 70vh;
  min-height: 500px;
}

.map-dialog-content {
  display: flex;
  width: 100%;
  height: 100%;
  gap: 16px;
  padding: 16px;
}

.map-container-wrapper {
  flex: 1;
  position: relative;
  min-height: 500px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

.map-container {
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

.map-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: rgba(255, 255, 255, 0.9);
  z-index: 100;
}

.search-box {
  margin-bottom: 16px;
}

@keyframes rotating {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.map-controls {
  width: 280px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.control-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.selected-info {
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.selected-info h4 {
  margin: 0 0 8px 0;
  color: #303133;
}

.info-item {
  display: flex;
  margin: 8px 0;
  line-height: 1.5;
}

.info-item .label {
  color: #606266;
  min-width: 40px;
  margin-right: 8px;
}

.info-item .value {
  color: #303133;
  word-break: break-all;
}

/* 添加输入框样式 */
input,
select,
textarea,
button {
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
}

input[type="number"] {
  -webkit-appearance: none;
  -moz-appearance: textfield;
  appearance: textfield;
}

input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  appearance: none;
  margin: 0;
}
</style>