<template>
  <div class="history-container">
    <div class="history-header">
      <h1>对话历史</h1>
      <div class="header-actions">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索对话内容..."
          prefix-icon="el-icon-search"
          size="medium"
          class="search-input"
          clearable
        ></el-input>
        <el-select 
          v-model="selectedCourse" 
          placeholder="选择课程" 
          size="medium"
          clearable
        >
          <el-option label="全部课程" value=""></el-option>
          <el-option 
            v-for="course in courseOptions" 
            :key="course.id"
            :label="course.name" 
            :value="course.id"
          ></el-option>
        </el-select>
      </div>
    </div>

    <div class="history-content">
      <div v-if="filteredHistories.length === 0" class="empty-state">
        <div class="empty-content">
          <i class="el-icon-chat-dot-square"></i>
          <h3>暂无对话记录</h3>
          <p>开始与AI助教对话，创建您的第一个学习记录吧！</p>
          <el-button type="primary" @click="$router.push('/home')">
            选择课程开始对话
          </el-button>
        </div>
      </div>

      <div v-else class="history-list">
        <div 
          v-for="chat in paginatedHistories" 
          :key="chat.id"
          class="history-card"
          @click="continueChat(chat)"
        >
          <div class="card-header">
            <div class="course-tag">
              <i class="el-icon-collection-tag"></i>
              {{ chat.courseName }}
            </div>
            <div class="card-actions" @click.stop>
              <el-dropdown @command="handleCommand">
                <span class="el-dropdown-link">
                  <i class="el-icon-more"></i>
                </span>
                <el-dropdown-menu slot="dropdown">
                  <el-dropdown-item :command="{action: 'continue', chat}">继续对话</el-dropdown-item>
                  <el-dropdown-item :command="{action: 'delete', chat}" class="danger">删除记录</el-dropdown-item>
                </el-dropdown-menu>
              </el-dropdown>
            </div>
          </div>

          <div class="card-body">
            <h3 class="chat-title">{{ chat.title }}</h3>
            <div class="chat-preview">
              <div class="message-preview">
                <span class="message-role">我:</span>
                <span class="message-text">{{ getFirstUserMessage(chat) }}</span>
              </div>
              <div v-if="getFirstAIMessage(chat)" class="message-preview ai-message">
                <span class="message-role">AI:</span>
                <span class="message-text">{{ getFirstAIMessage(chat) }}</span>
              </div>
            </div>
          </div>

          <div class="card-footer">
            <div class="chat-stats">
              <span class="stat-item">
                <i class="el-icon-chat-dot-round"></i>
                {{ chat.messages.length }} 条消息
              </span>
              <span class="stat-item">
                <i class="el-icon-time"></i>
                {{ formatDate(chat.updatedAt) }}
              </span>
            </div>
            <div class="continue-hint">
              <i class="el-icon-arrow-right"></i>
            </div>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div v-if="filteredHistories.length > pageSize" class="pagination-container">
        <el-pagination
          @current-change="handlePageChange"
          :current-page="currentPage"
          :page-size="pageSize"
          :total="filteredHistories.length"
          layout="prev, pager, next"
        ></el-pagination>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'History',
  data() {
    return {
      searchKeyword: '',
      selectedCourse: '',
      currentPage: 1,
      pageSize: 10,
      courseOptions: [
        { id: 'software-engineering', name: '软件工程' },
        { id: 'operating-system', name: '操作系统' },
        { id: 'computer-network', name: '计算机网络' },
        { id: 'data-structure', name: '数据结构' },
        { id: 'database', name: '数据库系统' },
        { id: 'compiler', name: '编译原理' }
      ]
    }
  },
  data() {
    return {
      serverHistories: [] // 存储从服务器获取的历史记录
    }
  },
  computed: {
    chatHistories() {
      // 合并服务器数据和本地数据
      const localHistories = this.$store.getters.chatHistories
      const combined = [...this.serverHistories]
      
      // 添加本地独有的记录
      localHistories.forEach(local => {
        if (!combined.find(server => server.id === local.id)) {
          combined.push(local)
        }
      })
      
      return combined
    },
    filteredHistories() {
      let filtered = this.chatHistories
      
      // 课程过滤
      if (this.selectedCourse) {
        filtered = filtered.filter(chat => chat.courseId === this.selectedCourse)
      }
      
      // 关键词搜索
      if (this.searchKeyword.trim()) {
        const keyword = this.searchKeyword.toLowerCase()
        filtered = filtered.filter(chat => {
          return chat.title.toLowerCase().includes(keyword) ||
                 chat.courseName.toLowerCase().includes(keyword) ||
                 chat.messages.some(msg => msg.content.toLowerCase().includes(keyword))
        })
      }
      
      // 按更新时间排序
      return filtered.sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt))
    },
    paginatedHistories() {
      const start = (this.currentPage - 1) * this.pageSize
      const end = start + this.pageSize
      return this.filteredHistories.slice(start, end)
    }
  },
  async created() {
    // 加载服务器的聊天历史
    await this.loadServerHistories()
  },
  methods: {
    async loadServerHistories() {
      try {
        // 获取所有聊天历史
        const histories = await this.$api.chatAPI.getChatHistory()
        
        // 转换数据格式
        this.serverHistories = histories.map(history => ({
          id: history.id,
          courseId: history.course_id,
          courseName: history.course_name,
          title: history.title,
          messages: [], // 消息需要单独加载
          createdAt: history.created_at,
          updatedAt: history.updated_at
        }))
        
      } catch (error) {
        console.error('加载服务器历史记录失败:', error)
        // 如果失败，使用本地数据
      }
    },
    
    continueChat(chat) {
      this.$store.commit('SET_CURRENT_CHAT', chat)
      this.$router.push({
        name: 'Chat',
        params: { courseId: chat.courseId },
        query: { courseName: chat.courseName }
      })
    },
    
    handleCommand(command) {
      if (command.action === 'continue') {
        this.continueChat(command.chat)
      } else if (command.action === 'delete') {
        this.deleteChat(command.chat)
      }
    },
    
    async deleteChat(chat) {
      this.$confirm('确定要删除这条对话记录吗？', '确认删除', {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          // 调用API删除
          await this.$api.chatAPI.deleteChatHistory(chat.id)
          
          // 从本地数据中删除
          this.$store.dispatch('deleteChatHistory', chat.id)
          
          // 从服务器历史记录中删除
          this.serverHistories = this.serverHistories.filter(h => h.id !== chat.id)
          
          this.$message.success('删除成功')
          
        } catch (error) {
          console.error('删除聊天记录失败:', error)
          this.$message.error('删除失败，请稍后重试')
        }
      }).catch(() => {})
    },
    
    getFirstUserMessage(chat) {
      const userMsg = chat.messages.find(msg => msg.role === 'user')
      return userMsg ? this.truncateText(userMsg.content, 50) : '无消息'
    },
    
    getFirstAIMessage(chat) {
      const aiMsg = chat.messages.find(msg => msg.role === 'assistant')
      return aiMsg ? this.truncateText(aiMsg.content, 80) : ''
    },
    
    truncateText(text, maxLength) {
      if (text.length <= maxLength) return text
      return text.substring(0, maxLength) + '...'
    },
    
    formatDate(dateString) {
      const date = new Date(dateString)
      const now = new Date()
      const diff = now - date
      
      if (diff < 60000) return '刚刚'
      if (diff < 3600000) return Math.floor(diff / 60000) + '分钟前'
      if (diff < 86400000) return Math.floor(diff / 3600000) + '小时前'
      if (diff < 604800000) return Math.floor(diff / 86400000) + '天前'
      
      return date.toLocaleDateString()
    },
    
    handlePageChange(page) {
      this.currentPage = page
    }
  }
}
</script>

<style scoped>
.history-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px 20px;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 20px;
}

.history-header h1 {
  font-size: 32px;
  color: #333;
  margin: 0;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 15px;
  align-items: center;
}

.search-input {
  width: 250px;
}

.empty-state {
  height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-content {
  text-align: center;
  color: #999;
}

.empty-content i {
  font-size: 64px;
  color: #ddd;
  margin-bottom: 20px;
}

.empty-content h3 {
  font-size: 20px;
  color: #333;
  margin: 0 0 10px 0;
}

.empty-content p {
  font-size: 14px;
  margin: 0 0 20px 0;
}

.history-list {
  display: grid;
  gap: 20px;
}

.history-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.history-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  border-color: #409EFF;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.course-tag {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: #f0f9ff;
  color: #409EFF;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
}

.card-actions {
  color: #999;
  cursor: pointer;
}

.card-actions:hover {
  color: #409EFF;
}

.el-dropdown-link {
  cursor: pointer;
  padding: 5px;
}

.card-body {
  margin-bottom: 20px;
}

.chat-title {
  font-size: 18px;
  color: #333;
  margin: 0 0 15px 0;
  font-weight: 600;
  line-height: 1.4;
}

.chat-preview {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.message-preview {
  display: flex;
  gap: 8px;
  font-size: 14px;
  line-height: 1.5;
}

.message-role {
  color: #666;
  font-weight: 500;
  flex-shrink: 0;
  min-width: 30px;
}

.message-text {
  color: #333;
  flex: 1;
}

.ai-message .message-role {
  color: #409EFF;
}

.ai-message .message-text {
  color: #666;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
}

.chat-stats {
  display: flex;
  gap: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #999;
}

.continue-hint {
  color: #999;
  transition: all 0.3s ease;
}

.history-card:hover .continue-hint {
  color: #409EFF;
  transform: translateX(4px);
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 30px;
}

/* 下拉菜单危险项样式 */
::v-deep .danger {
  color: #f56c6c;
}

::v-deep .danger:hover {
  background-color: #fef0f0;
  color: #f56c6c;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .history-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .header-actions {
    flex-direction: column;
    gap: 10px;
  }
  
  .search-input {
    width: 100%;
  }
  
  .history-card {
    padding: 20px;
  }
  
  .chat-stats {
    flex-direction: column;
    gap: 8px;
  }
  
  .card-footer {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
}
</style>