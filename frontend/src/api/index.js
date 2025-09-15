import axios from 'axios'
import router from '../router'
import { Message } from 'element-ui'

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 60000, // 增加到60秒以支持AI调用
  headers: {
    'Content-Type': 'application/json'
  }
})

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

export const commonAPI = {
  healthCheck() {
    return api.get('/health')
  }
}

export default api