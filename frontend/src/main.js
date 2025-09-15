import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import './assets/styles/global.css'
import api, { authAPI, chatAPI, commonAPI } from './api'

Vue.config.productionTip = false

// 配置API
Vue.prototype.$api = { authAPI, chatAPI, commonAPI }
Vue.prototype.$http = api

// 使用Element UI
Vue.use(ElementUI)

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')