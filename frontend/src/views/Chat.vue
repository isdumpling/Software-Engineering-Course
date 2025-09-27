<template>
  <div class="chat-layout">
    <!-- 历史对话侧边栏 -->
    <div class="history-sidebar" :class="{ 'is-visible': showHistory }">
      <div class="sidebar-header">
        <h4><i class="el-icon-time"></i> 历史对话</h4>
        <el-button 
          icon="el-icon-close" 
          @click="showHistory = false"
          circle
          size="mini"
          class="close-sidebar-btn"
        ></el-button>
      </div>
      <div class="new-chat-button-container">
        <el-button icon="el-icon-plus" @click="clearChat" class="new-chat-btn">
          新的对话
        </el-button>
      </div>
      <div class="history-list">
        <div 
          v-for="chat in courseHistories" 
          :key="chat.id"
          class="history-item"
          :class="{ active: currentChatId === chat.id }"
          @click="loadChat(chat)"
        >
          <i class="el-icon-chat-dot-round history-icon"></i>
          <div class="history-info">
            <div class="history-title">{{ chat.title }}</div>
            <div class="history-time">{{ formatTime(chat.createdAt) }}</div>
          </div>
        </div>
        <div v-if="courseHistories.length === 0" class="no-history">
          <i class="el-icon-info"></i>
          <p>暂无历史对话</p>
        </div>
      </div>
    </div>

    <div class="chat-container">
      <!-- 聊天头部 -->
      <div class="chat-header">
        <div class="header-left">
          <el-button 
            icon="el-icon-arrow-left" 
            @click="goBack"
            circle
            class="back-button"
          ></el-button>
          <div class="course-info">
            <h3>{{ courseName }}</h3>
            <span>智能助教在线</span>
          </div>
        </div>
        <div class="header-right">
          <el-tooltip content="历史对话" placement="bottom">
            <el-button 
              icon="el-icon-s-fold" 
              @click="showHistory = !showHistory"
              circle
              class="history-button"
            ></el-button>
          </el-tooltip>
        </div>
      </div>

      <!-- 聊天主区域 -->
      <div class="chat-main">
        <!-- 消息列表 -->
        <div class="messages-container" ref="messagesContainer">
          <div v-if="messages.length === 0" class="welcome-message">
            <div class="welcome-content">
              <div class="brand-logo">
                <svg width="60" height="60" viewBox="0 0 64 64">
                  <path fill="none" stroke="#5A8DFF" stroke-width="3" stroke-miterlimit="10" d="M1 20L32 6l31 14-31 14z"/>
                  <path fill="none" stroke="#5A8DFF" stroke-width="3" stroke-miterlimit="10" d="M11 26v18c0 4.418 9.399 8 21 8s21-3.582 21-8V26"/>
                  <path fill="none" stroke="#5A8DFF" stroke-width="3" stroke-miterlimit="10" d="M57 40V28"/>
                </svg>
              </div>
              <h2>{{ courseName }} 智能助教</h2>
              <p>你好！有什么可以帮助你的吗？</p>
              <div class="quick-questions">
                <el-button 
                  v-for="question in quickQuestions" 
                  :key="question"
                  @click="sendQuickQuestion(question)"
                  class="quick-question-btn"
                  size="small"
                >
                  {{ question }}
                </el-button>
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
              <i :class="message.role === 'user' ? 'el-icon-user' : 'el-icon-cpu'"></i>
            </div>
            <div class="message-content">
              <div class="message-text" v-html="formatMarkdown(message.content)"></div>
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
              :autosize="{ minRows: 1, maxRows: 5 }"
              placeholder="请在此输入您的问题...(Ctrl+Enter换行)"
              @keyup.enter.native="handleEnter"
              ref="messageInput"
              resize="none"
            ></el-input>
            <el-button 
              type="primary" 
              icon="el-icon-s-promotion"
              @click="sendMessage"
              :loading="isLoading"
              :disabled="!currentMessage.trim()"
              circle
              class="send-button"
            ></el-button>
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
    },
    
    formatMarkdown(text) {
      if (!text) return ''
      
      // 转义HTML特殊字符（安全性考虑）
      let html = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;')
      
      // 处理markdown语法
      html = html
        // 标题处理 (必须在其他处理之前)
        .replace(/^### (.+)$/gm, '<h3 class="md-h3">$1</h3>')
        .replace(/^## (.+)$/gm, '<h2 class="md-h2">$1</h2>')
        .replace(/^# (.+)$/gm, '<h1 class="md-h1">$1</h1>')
        // 粗体 **text** -> <strong>text</strong>
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        // 斜体 *text* -> <em>text</em>
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        // 行内代码 `code` -> <code>code</code>
        .replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')
        // 代码块 ```code``` -> <pre><code>code</code></pre>
        .replace(/```([\s\S]*?)```/g, '<pre class="code-block"><code>$1</code></pre>')
        // 换行符处理
        .replace(/\n/g, '<br>')
        // 链接 [text](url) -> <a href="url">text</a>
        .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>')
        // 列表项 - item -> <li>item</li>（简单处理）
        .replace(/^- (.+)$/gm, '<li>$1</li>')
        // 包装连续的列表项
        .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
      
      return html
    }
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap');

.chat-layout {
  display: flex;
  height: calc(100vh - 65px); /* Full height minus the app header */
  font-family: 'Noto Sans SC', sans-serif;
  background-color: #f7f8fc;
}

.history-sidebar {
  width: 280px;
  background: #ffffff;
  border-right: 1px solid #eef0f3;
  display: flex;
  flex-direction: column;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  flex-shrink: 0;
}

.sidebar-header {
  padding: 15px;
  border-bottom: 1px solid #eef0f3;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  display: flex;
  align-items: center;
  gap: 8px;
}

.new-chat-button-container {
  padding: 15px;
  border-bottom: 1px solid #eef0f3;
}

.new-chat-btn {
  width: 100%;
  background-color: #f7f8fc;
  border-color: #e0e4eb;
  color: #5A8DFF;
  font-weight: 500;
}
.new-chat-btn:hover {
  background-color: #eef1f8;
  border-color: #cdd3e0;
}

.history-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.history-item {
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 5px;
}

.history-item:hover {
  background: #f7f8fc;
}

.history-item.active {
  background: #5A8DFF;
  color: white;
}
.history-item.active .history-time {
  color: #e0eaff;
}
.history-item.active .history-icon {
  color: white;
}


.history-icon {
  font-size: 16px;
  color: #888;
}

.history-info {
  overflow: hidden;
}

.history-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.history-time {
  font-size: 12px;
  color: #999;
}

.no-history {
  padding: 30px 15px;
  text-align: center;
  color: #aaa;
}
.no-history i {
  font-size: 24px;
  margin-bottom: 10px;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-header {
  background: white;
  padding: 10px 20px;
  border-bottom: 1px solid #eef0f3;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
  height: 65px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.course-info h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.course-info span {
  font-size: 13px;
  color: #888;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
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
  color: #777;
}

.brand-logo {
  margin-bottom: 20px;
}

.welcome-content h2 {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin: 0 0 10px 0;
}
.welcome-content p {
  margin: 0 0 30px 0;
  font-size: 15px;
}

.quick-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
  max-width: 500px;
}

.quick-question-btn {
  background-color: #f7f8fc;
  border: 1px solid #eef0f3;
  color: #555;
  transition: all 0.2s;
}
.quick-question-btn:hover {
  background: #eef1f8;
  color: #5A8DFF;
  border-color: #cdd3e0;
}

.message-item {
  display: flex;
  margin-bottom: 25px;
  gap: 12px;
}

.message-item.user-message {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 18px;
}

.user-message .message-avatar {
  background: #5A8DFF;
  color: white;
}

.ai-message .message-avatar {
  background: #eef1f8;
  color: #5A8DFF;
}

.message-content {
  max-width: 75%;
}

.user-message .message-content {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.message-text {
  padding: 12px 18px;
  border-radius: 18px;
  word-wrap: break-word;
  line-height: 1.6;
  font-size: 15px;
}

.ai-message .message-text {
  background: #fff;
  border: 1px solid #eef0f3;
  border-top-left-radius: 4px;
}

.user-message .message-text {
  background: #5A8DFF;
  color: white;
  border-top-right-radius: 4px;
}

.message-time {
  font-size: 12px;
  color: #aaa;
  margin-top: 8px;
  padding: 0 5px;
}

.message-loading {
  background: #fff;
  border: 1px solid #eef0f3;
  padding: 15px 18px;
  border-radius: 18px;
  border-top-left-radius: 4px;
  display: flex;
  gap: 5px;
  align-items: center;
}

.message-loading span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ccc;
  animation: loading 1.4s infinite;
}

.message-loading span:nth-child(2) { animation-delay: 0.2s; }
.message-loading span:nth-child(3) { animation-delay: 0.4s; }

@keyframes loading {
  0%, 80%, 100% { transform: scale(0.5); opacity: 0.5; }
  40% { transform: scale(1); opacity: 1; }
}

.input-area {
  padding: 15px 20px;
  border-top: 1px solid #eef0f3;
  background: #fff;
}

.input-container {
  display: flex;
  gap: 10px;
  align-items: flex-end;
  background-color: #f7f8fc;
  border-radius: 25px;
  padding: 5px 10px 5px 20px;
}

.input-container .el-textarea {
  flex: 1;
}

.input-container >>> .el-textarea__inner {
  background: transparent;
  border: none;
  padding: 10px 0;
  font-size: 15px;
}

.send-button {
  width: 40px;
  height: 40px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .history-sidebar {
    position: fixed;
    top: 0;
    left: 0;
    height: 100%;
    z-index: 1001;
    transform: translateX(-100%);
    box-shadow: 2px 0 15px rgba(0,0,0,0.1);
  }
  .history-sidebar.is-visible {
    transform: translateX(0);
  }
  .close-sidebar-btn { display: block; }
  .history-button { display: block; }

  .back-button { display: none; }
  .course-info h3 { font-size: 16px; }
  .message-content { max-width: 85%; }
}
@media (min-width: 769px) {
  .close-sidebar-btn { display: none; }
  .history-button { display: none; }
}

/* Markdown 样式 */
.message-text >>> h1, .message-text >>> h2, .message-text >>> h3 {
  font-weight: 600;
  color: #333;
  margin-top: 1em;
  margin-bottom: 0.5em;
}
.user-message .message-text >>> h1, .user-message .message-text >>> h2, .user-message .message-text >>> h3 {
  color: #fff;
}
.message-text >>> h1 { font-size: 1.4em; }
.message-text >>> h2 { font-size: 1.2em; }
.message-text >>> h3 { font-size: 1.1em; }

.message-text >>> p {
  margin: 0.8em 0;
}

.message-text >>> strong {
  font-weight: 600;
}

.message-text >>> em {
  font-style: italic;
}

.message-text >>> .inline-code {
  background: #f0f2f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
  font-size: 0.9em;
  color: #e74c3c;
}
.user-message .message-text >>> .inline-code {
  background: rgba(0,0,0,0.15);
  color: #fff;
}

.message-text >>> .code-block {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 12px;
  margin: 1em 0;
  overflow-x: auto;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
  font-size: 0.9em;
  color: #333;
}
.message-text >>> .code-block code {
  white-space: pre-wrap;
  word-wrap: break-word;
}

.message-text >>> ul, .message-text >>> ol {
  margin: 0.8em 0;
  padding-left: 25px;
}
.message-text >>> li {
  margin: 0.4em 0;
}

.message-text >>> a {
  color: #5A8DFF;
  text-decoration: none;
  font-weight: 500;
}
.message-text >>> a:hover {
  text-decoration: underline;
}
.user-message .message-text >>> a {
  color: #fff;
  text-decoration: underline;
}
</style>