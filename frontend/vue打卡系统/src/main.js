import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from '@/utils/request.js'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import '@/mock'
import { createPersistedState } from 'pinia-persistedstate-plugin'
import { createPinia } from 'pinia'
const pinia=createPinia()
const persist = createPersistedState()



// 创建应用实例
const app = createApp(App)
// 创建 pinia 实例（推荐单独创建）


// 全局配置
app.config.globalProperties.routerAppend = (path, pathToAppend) => {
  return path + (path.endsWith('/') ? '' : '/') + pathToAppend
}
pinia.use(persist)
// 使用 provide/inject 更规范
app.provide("$axios", axios)

// 按顺序安装插件（router -> pinia -> UI库）
app.use(router)

app.use(pinia)

app.use(ElementPlus)

// 挂载应用
app.mount('#app')

// 除非有特殊需求，否则不建议暴露到 window
// window.$vueApp = app