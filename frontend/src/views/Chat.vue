<template>
  <div class="chat-container">
    <!-- 聊天头部 -->
    <div class="chat-header">
      <div class="header-left">
        <el-button 
          icon="el-icon-arrow-left" 
          @click="goBack"
          circle
          size="small"
        ></el-button>
        <div class="course-info">
          <h3>{{ courseName }}</h3>
          <span>智能助教为您服务</span>
        </div>
      </div>
      <div class="header-right">
        <el-button 
          icon="el-icon-refresh-left" 
          @click="clearChat"
          size="small"
          type="text"
        >
          新对话
        </el-button>
        <el-button 
          icon="el-icon-s-unfold" 
          @click="showHistory = !showHistory"
          size="small"
          type="text"
        >
          历史对话
        </el-button>
      </div>
    </div>

    <div class="chat-body">
      <!-- 历史对话侧边栏 -->
      <div v-if="showHistory" class="history-sidebar">
        <div class="sidebar-header">
          <h4>历史对话</h4>
          <el-button 
            icon="el-icon-close" 
            @click="showHistory = false"
            size="mini"
            type="text"
          ></el-button>
        </div>
        <div class="history-list">
          <div 
            v-for="chat in courseHistories" 
            :key="chat.id"
            class="history-item"
            :class="{ active: currentChatId === chat.id }"
            @click="loadChat(chat)"
          >
            <div class="history-title">{{ chat.title }}</div>
            <div class="history-time">{{ formatTime(chat.updatedAt) }}</div>
          </div>
          <div v-if="courseHistories.length === 0" class="no-history">
            暂无历史对话
          </div>
        </div>
      </div>

      <!-- 聊天主区域 -->
      <div class="chat-main">
        <!-- 消息列表 -->
        <div class="messages-container" ref="messagesContainer">
          <div v-if="messages.length === 0" class="welcome-message">
            <div class="welcome-content">
              <i class="el-icon-chat-dot-round"></i>
              <h4>开始对话</h4>
              <p>您可以询问关于{{ courseName }}的任何问题</p>
              <div class="quick-questions">
                <el-tag 
                  v-for="question in quickQuestions" 
                  :key="question"
                  @click="sendQuickQuestion(question)"
                  class="quick-tag"
                >
                  {{ question }}
                </el-tag>
              </div>
            </div>
          </div>
          
          <div 
            v-for="(message, index) in messages" 
            :key="index"
            class="message-item"
            :class="{ 'user-message': message.role === 'user', 'ai-message': message.role === 'assistant' }"
          >
            <div class="message-avatar">
              <i :class="message.role === 'user' ? 'el-icon-user-solid' : 'el-icon-cpu'"></i>
            </div>
            <div class="message-content">
              <div class="message-text">{{ message.content }}</div>
              <div class="message-time">{{ formatTime(message.timestamp) }}</div>
            </div>
          </div>
          
          <!-- 加载动画 -->
          <div v-if="isLoading" class="message-item ai-message">
            <div class="message-avatar">
              <i class="el-icon-cpu"></i>
            </div>
            <div class="message-content">
              <div class="message-loading">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 输入区域 -->
        <div class="input-area">
          <div class="input-container">
            <el-input
              v-model="currentMessage"
              type="textarea"
              :rows="1"
              placeholder="输入您的问题..."
              @keyup.enter.native="handleEnter"
              ref="messageInput"
              resize="none"
              maxlength="1000"
              show-word-limit
            ></el-input>
            <el-button 
              type="primary" 
              icon="el-icon-s-promotion"
              @click="sendMessage"
              :loading="isLoading"
              :disabled="!currentMessage.trim()"
              class="send-button"
            >
              发送
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Chat',
  props: ['courseId'],
  data() {
    return {
      courseName: this.$route.query.courseName || '课程',
      messages: [],
      currentMessage: '',
      isLoading: false,
      showHistory: false,
      currentChatId: null,
      quickQuestions: [
        '这门课程的主要内容是什么？',
        '有哪些重点知识点？',
        '推荐的学习资料有哪些？',
        '如何准备考试？'
      ]
    }
  },
  computed: {
    courseHistories() {
      return this.$store.getters.getChatHistoriesByCourse(this.courseId)
    }
  },
  async created() {
    // 加载服务器的聊天历史
    await this.loadChatHistories()
    
    // 如果有当前聊天记录，加载它
    const currentChat = this.$store.getters.currentChat
    if (currentChat && currentChat.courseId === this.courseId) {
      this.loadChat(currentChat)
    }
  },
  methods: {
    goBack() {
      this.$router.go(-1)
    },
    
    clearChat() {
      this.messages = []
      this.currentChatId = null
      this.$store.commit('SET_CURRENT_CHAT', null)
    },
    
    async sendMessage() {
      if (!this.currentMessage.trim() || this.isLoading) return
      
      const userMessage = {
        role: 'user',
        content: this.currentMessage.trim(),
        timestamp: new Date().toISOString()
      }
      
      this.messages.push(userMessage)
      const userInput = this.currentMessage
      this.currentMessage = ''
      this.isLoading = true
      
      // 滚动到底部
      this.$nextTick(() => {
        this.scrollToBottom()
      })
      
      try {
        // 确保有session ID
        if (!this.currentChatId) {
          this.currentChatId = 'chat_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
        }
        
        // 调用真实的聊天API
        const response = await this.$api.chatAPI.sendMessage({
          session_id: this.currentChatId,
          query: userInput,
          course_id: this.courseId,
          course_name: this.courseName
        })
        
        // 添加AI回答
        const aiMessage = {
          role: 'assistant',
          content: response.answer,
          timestamp: new Date().toISOString()
        }
        
        this.messages.push(aiMessage)
        
        // 更新本地存储的聊天记录
        this.updateLocalChatHistory()
        
      } catch (error) {
        console.error('发送消息失败:', error)
        this.$message.error('发送失败，请稍后重试')
      } finally {
        this.isLoading = false
        this.$nextTick(() => {
          this.scrollToBottom()
        })
      }
    },
    
    async simulateAIResponse(userInput) {
      // 模拟AI响应
      setTimeout(() => {
        const aiMessage = {
          role: 'assistant',
          content: this.generateMockResponse(userInput),
          timestamp: new Date().toISOString()
        }
        
        this.messages.push(aiMessage)
        this.isLoading = false
        
        // 保存聊天记录
        this.saveChatHistory()
        
        this.$nextTick(() => {
          this.scrollToBottom()
        })
      }, 1500)
    },
    
    generateMockResponse(userInput) {
      const responses = [
        `关于"${userInput}"这个问题，我来为您详细解答。根据课程资料，这是一个重要的知识点。`,
        `很好的问题！关于${userInput}，我建议您从以下几个方面来理解...`,
        `这个问题涉及到${this.courseName}的核心概念。让我为您详细说明一下...`,
        `根据教学大纲，${userInput}是必须掌握的内容。我来帮您梳理一下要点...`
      ]
      return responses[Math.floor(Math.random() * responses.length)]
    },
    
    sendQuickQuestion(question) {
      this.currentMessage = question
      this.sendMessage()
    },
    
    handleEnter(e) {
      if (e.ctrlKey || e.shiftKey) {
        return
      }
      e.preventDefault()
      this.sendMessage()
    },
    
    async loadChat(chat) {
      try {
        // 如果是从本地存储加载且有消息，直接使用
        if (chat.messages && chat.messages.length > 0) {
          this.messages = chat.messages
          this.currentChatId = chat.id
          this.$store.commit('SET_CURRENT_CHAT', chat)
          this.$nextTick(() => {
            this.scrollToBottom()
          })
          return
        }
        
        // 否则从服务器加载完整的聊天记录
        const chatDetail = await this.$api.chatAPI.getChatDetail(chat.id)
        
        this.messages = chatDetail.messages || []
        this.currentChatId = chat.id
        
        // 更新本地存储
        const updatedChat = {
          ...chat,
          messages: this.messages
        }
        this.$store.commit('SET_CURRENT_CHAT', updatedChat)
        this.$store.dispatch('saveChatHistory', updatedChat)
        
        this.$nextTick(() => {
          this.scrollToBottom()
        })
        
      } catch (error) {
        console.error('加载聊天记录失败:', error)
        this.$message.error('加载聊天记录失败')
      }
    },
    
    updateLocalChatHistory() {
      if (!this.currentChatId) return
      
      const chatData = {
        id: this.currentChatId,
        courseId: this.courseId,
        courseName: this.courseName,
        title: this.messages.length > 0 ? this.messages[0].content.substring(0, 20) + '...' : '新对话',
        messages: this.messages,
        createdAt: this.messages[0]?.timestamp || new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
      
      this.$store.dispatch('saveChatHistory', chatData)
    },
    
    async loadChatHistories() {
      try {
        // 从服务器加载聊天历史
        const histories = await this.$api.chatAPI.getChatHistory(this.courseId)
        
        // 更新本地存储
        histories.forEach(history => {
          this.$store.dispatch('saveChatHistory', {
            id: history.id,
            courseId: history.course_id,
            courseName: history.course_name,
            title: history.title,
            messages: [], // 具体消息需要单独加载
            createdAt: history.created_at,
            updatedAt: history.updated_at
          })
        })
        
      } catch (error) {
        console.error('加载聊天历史失败:', error)
      }
    },
    
    scrollToBottom() {
      const container = this.$refs.messagesContainer
      if (container) {
        container.scrollTop = container.scrollHeight
      }
    },
    
    formatTime(timestamp) {
      if (!timestamp) return ''
      const date = new Date(timestamp)
      const now = new Date()
      const diff = now - date
      
      if (diff < 60000) return '刚刚'
      if (diff < 3600000) return Math.floor(diff / 60000) + '分钟前'
      if (diff < 86400000) return Math.floor(diff / 3600000) + '小时前'
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString().slice(0, 5)
    }
  }
}
</script>

<style scoped>
.chat-container {
  height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

.chat-header {
  background: white;
  padding: 15px 20px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.course-info h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.course-info span {
  font-size: 12px;
  color: #999;
}

.chat-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.history-sidebar {
  width: 280px;
  background: white;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 15px 20px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-header h4 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.history-list {
  flex: 1;
  overflow-y: auto;
}

.history-item {
  padding: 15px 20px;
  border-bottom: 1px solid #f5f5f5;
  cursor: pointer;
  transition: background-color 0.2s;
}

.history-item:hover {
  background: #f5f5f5;
}

.history-item.active {
  background: #e6f7ff;
  border-right: 3px solid #409EFF;
}

.history-title {
  font-size: 14px;
  color: #333;
  margin-bottom: 5px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.history-time {
  font-size: 12px;
  color: #999;
}

.no-history {
  padding: 20px;
  text-align: center;
  color: #999;
  font-size: 14px;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.welcome-message {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.welcome-content {
  text-align: center;
  color: #999;
}

.welcome-content i {
  font-size: 48px;
  margin-bottom: 15px;
  color: #ddd;
}

.welcome-content h4 {
  margin: 0 0 10px 0;
  color: #333;
}

.welcome-content p {
  margin: 0 0 20px 0;
}

.quick-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}

.quick-tag {
  cursor: pointer;
  transition: all 0.2s;
}

.quick-tag:hover {
  background: #409EFF;
  color: white;
}

.message-item {
  display: flex;
  margin-bottom: 20px;
  gap: 12px;
}

.message-item.user-message {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 16px;
}

.user-message .message-avatar {
  background: #409EFF;
  color: white;
}

.ai-message .message-avatar {
  background: #f0f0f0;
  color: #666;
}

.message-content {
  max-width: 70%;
}

.user-message .message-content {
  text-align: right;
}

.message-text {
  background: white;
  padding: 12px 16px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  word-wrap: break-word;
  line-height: 1.5;
}

.user-message .message-text {
  background: #409EFF;
  color: white;
}

.message-time {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

.message-loading {
  background: white;
  padding: 12px 16px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  display: flex;
  gap: 4px;
}

.message-loading span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ddd;
  animation: loading 1.4s infinite;
}

.message-loading span:nth-child(2) {
  animation-delay: 0.2s;
}

.message-loading span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes loading {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.input-area {
  padding: 20px;
  border-top: 1px solid #e4e7ed;
  background: #fafafa;
}

.input-container {
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

.input-container .el-textarea {
  flex: 1;
}

.send-button {
  height: 40px;
  padding: 0 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .history-sidebar {
    position: absolute;
    top: 0;
    left: 0;
    height: 100%;
    z-index: 1000;
    box-shadow: 2px 0 8px rgba(0,0,0,0.1);
  }
  
  .message-content {
    max-width: 85%;
  }
  
  .quick-questions {
    flex-direction: column;
    align-items: center;
  }
}
</style>