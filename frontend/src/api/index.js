import axios from 'axios'
import router from '../router'
import { Message } from 'element-ui'

const API_BASE = 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 180000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// ---- fetch 封装（绕过 XHR + CORS 预检缓存问题） ----
async function fetchApi(method, path, body) {
  const headers = {}
  const token = localStorage.getItem('token')
  if (token) headers.Authorization = `Bearer ${token}`
  // GET/HEAD 不加 Content-Type，避免触发不必要的 CORS 预检
  if (method !== 'GET' && method !== 'HEAD') {
    headers['Content-Type'] = 'application/json'
  }

  const opts = { method, headers }
  if (body) opts.body = JSON.stringify(body)

  const resp = await fetch(API_BASE + path, opts)
  const data = await resp.json()

  if (!resp.ok) {
    const err = new Error(data.detail || data.error || `HTTP ${resp.status}`)
    err.response = { status: resp.status, data }
    throw err
  }
  return data
}

api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API Error:', error)
    
    if (error.response) {
      const { status, data } = error.response
      
      if (status === 401) {
        localStorage.removeItem('token')
        localStorage.removeItem('username')
        
        // 避免重复导航
        if (router.currentRoute.path !== '/login') {
          router.replace('/login').catch(err => {
            // 忽略导航重复错误
            if (err.name !== 'NavigationDuplicated') {
              console.error('Navigation error:', err)
            }
          })
        }
        Message.error('登录已过期，请重新登录')
      } else if (status === 403) {
        Message.error('没有权限访问此资源')
      } else if (status === 404) {
        Message.error('请求的资源不存在')
      } else if (status === 500) {
        Message.error('服务器内部错误')
      } else {
        Message.error(data?.error || data?.detail || '请求失败')
      }
    } else if (error.code === 'ECONNABORTED') {
      Message.error('请求超时，请检查网络连接')
    } else {
      Message.error('网络错误，请检查网络连接')
    }
    
    return Promise.reject(error)
  }
)

export const authAPI = {
  register(userData) {
    return api.post('/auth/register', userData)
  },
  
  login(credentials) {
    return api.post('/auth/login', credentials)
  },
  
  getCurrentUser() {
    return api.get('/auth/me')
  },
  
  forgotPassword(email) {
    return api.post('/auth/forgot-password', { email })
  },
  
  resetPassword(token, password) {
    return api.post('/auth/reset-password', { token, password })
  },
  
  validateResetToken(token) {
    return api.post('/auth/validate-reset-token', null, {
      params: { token }
    })
  },
  
  getSecurityQuestion(email) {
    return api.post('/auth/security-question', { email })
  },
  
  verifySecurityAnswer(email, securityAnswer) {
    return api.post('/auth/verify-security-answer', { 
      email, 
      security_answer: securityAnswer 
    })
  }
}

export const chatAPI = {
  sendMessage(messageData) {
    return api.post('/chat/', messageData)
  },
  
  getChatHistory(courseId = null) {
    const params = courseId ? { course_id: courseId } : {}
    return api.get('/chat/history', { params })
  },
  
  getChatDetail(sessionId) {
    return api.get(`/chat/history/${sessionId}`)
  },
  
  deleteChatHistory(sessionId) {
    return api.delete(`/chat/history/${sessionId}`)
  },
  
  getChatStats() {
    return api.get('/chat/stats')
  }
}

export const adminAPI = {
  getDashboard() {
    return fetchApi('GET', '/admin/dashboard')
  },

  getCourses() {
    return fetchApi('GET', '/admin/courses')
  },

  async uploadMaterial(courseId, formData) {
    // formData 由调用方构造（含原始 File 对象），直接发送，不要再包装
    const headers = {}
    const token = localStorage.getItem('token')
    if (token) headers.Authorization = `Bearer ${token}`
    const resp = await fetch(API_BASE + `/admin/courses/${courseId}/material`, {
      method: 'POST', headers, body: formData
    })
    const data = await resp.json()
    if (!resp.ok) throw new Error(data.detail || '上传失败')
    return data
  },

  buildKnowledge(courseId) {
    return fetchApi('POST', `/admin/courses/${courseId}/knowledge/build`)
  },

  getBuildTask(taskId) {
    return fetchApi('GET', `/admin/knowledge/tasks/${taskId}`)
  },

  getBuildTasks() {
    return fetchApi('GET', '/admin/knowledge/tasks')
  },

  testRetrieval(data) {
    return fetchApi('POST', '/admin/retrieval-test', data)
  },

  getSystemHealth() {
    return fetchApi('GET', '/admin/system/health')
  },

  reloadAI() {
    return fetchApi('POST', '/admin/ai/reload')
  },

  reloadCourse(courseId) {
    return fetchApi('POST', `/admin/ai/reload/${courseId}`)
  }
}

export const commonAPI = {
  healthCheck() {
    return api.get('/health')
  }
}

export default api