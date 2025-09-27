<template>
  <div class="history-container">
    <div class="history-header">
      <div class="header-left">
        <i class="el-icon-time header-icon"></i>
        <div class="header-text">
          <h1>对话历史</h1>
          <p>在这里查看、搜索和管理您所有的学习对话</p>
        </div>
      </div>
      <div class="header-actions">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索标题、课程或内容..."
          prefix-icon="el-icon-search"
          size="medium"
          class="search-input"
          clearable
        ></el-input>
        <el-select 
          v-model="selectedCourse" 
          placeholder="筛选课程" 
          size="medium"
          clearable
          class="course-select"
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
          <i class="el-icon-chat-line-square"></i>
          <h3>{{ searchKeyword || selectedCourse ? '没有找到匹配的记录' : '暂无对话记录' }}</h3>
          <p v-if="!searchKeyword && !selectedCourse">开始一段对话来创建您的第一条历史记录吧！</p>
          <el-button v-if="!searchKeyword && !selectedCourse" type="primary" plain @click="$router.push('/home')">
            <i class="el-icon-plus"></i>
            开始新的学习
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
            <div class="course-tag" :style="getCourseColor(chat.courseId)">
              {{ chat.courseName }}
            </div>
            <div class="card-actions" @click.stop>
              <el-dropdown @command="handleCommand" trigger="click">
                <span class="el-dropdown-link">
                  <i class="el-icon-more"></i>
                </span>
                <el-dropdown-menu slot="dropdown">
                  <el-dropdown-item :command="{action: 'continue', chat}" icon="el-icon-chat-dot-round">继续对话</el-dropdown-item>
                  <el-dropdown-item :command="{action: 'delete', chat}" icon="el-icon-delete" class="danger">删除记录</el-dropdown-item>
                </el-dropdown-menu>
              </el-dropdown>
            </div>
          </div>

          <div class="card-body">
            <h3 class="chat-title">{{ chat.title }}</h3>
            <div class="chat-preview">
              <p v-if="getLastMessage(chat)">
                <span class="message-role" :class="getLastMessage(chat).role">
                  {{ getLastMessage(chat).role === 'user' ? '你' : 'AI' }}:
                </span>
                <span class="message-text">{{ getLastMessage(chat).content }}</span>
              </p>
               <p v-else class="no-message-preview">
                点击查看对话详情
              </p>
            </div>
          </div>

          <div class="card-footer">
            <div class="chat-stats">
              <span class="stat-item">
                <i class="el-icon-chat-dot-round"></i>
                {{ chat.message_count || chat.messages?.length || 0 }} 条消息
              </span>
              <span class="stat-item">
                <i class="el-icon-time"></i>
                更新于 {{ formatDate(chat.updatedAt) }}
              </span>
            </div>
            <div class="continue-hint">
              <span>查看</span>
              <i class="el-icon-arrow-right"></i>
            </div>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div v-if="filteredHistories.length > pageSize" class="pagination-container">
        <el-pagination
          background
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
      pageSize: 9,
      courseOptions: [
        { id: 'software-engineering', name: '软件工程', color: '#409EFF' },
        { id: 'operating-system', name: '操作系统', color: '#67C23A' },
        { id: 'computer-network', name: '计算机网络', color: '#E6A23C' },
        { id: 'data-structure', name: '数据结构', color: '#F56C6C' },
        { id: 'database', name: '数据库系统', color: '#909399' },
        { id: 'compiler', name: '编译原理', color: '#9C27B0' }
      ],
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
                 (chat.messages && chat.messages.some(msg => msg.content.toLowerCase().includes(keyword)))
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
        console.log('正在加载服务器历史记录...')
        // 获取所有聊天历史（不传course_id获取所有课程）
        const histories = await this.$api.chatAPI.getChatHistory()
        console.log('服务器返回的历史记录:', histories)
        
        // 转换数据格式
        this.serverHistories = histories.map(history => ({
          id: history.id,
          courseId: history.course_id,
          courseName: history.course_name,
          title: history.title,
          messages: [], // 消息需要单独加载
          message_count: history.message_count, // 添加消息数量
          createdAt: history.created_at,
          updatedAt: history.updated_at
        }))
        
        console.log('处理后的历史记录:', this.serverHistories)
        
      } catch (error) {
        console.error('加载服务器历史记录失败:', error)
        this.$message.error('加载历史记录失败，显示本地数据')
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
      this.$confirm('此操作将永久删除该对话记录, 是否继续?', '警告', {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        center: true
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
    
    getLastMessage(chat) {
      if (chat.messages && chat.messages.length > 0) {
        const lastMsg = chat.messages[chat.messages.length - 1];
        return {
          role: lastMsg.role,
          content: this.truncateText(lastMsg.content, 100)
        };
      }
      return null;
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
      window.scrollTo(0, 0);
    },

    getCourseColor(courseId) {
      const course = this.courseOptions.find(c => c.id === courseId);
      if (course) {
        return { 
          '--course-bg-color': `${course.color}1A`, 
          '--course-text-color': course.color 
        };
      }
      return {
        '--course-bg-color': '#f0f0f0',
        '--course-text-color': '#666'
      };
    }
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap');

.history-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px;
  font-family: 'Noto Sans SC', sans-serif;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 20px;
  background: #fff;
  padding: 25px 30px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-icon {
  font-size: 32px;
  color: #5A8DFF;
}

.header-text h1 {
  font-size: 24px;
  font-weight: 700;
  color: #333;
  margin: 0 0 5px 0;
}

.header-text p {
  font-size: 14px;
  color: #999;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 15px;
  align-items: center;
}

.search-input { width: 220px; }
.course-select { width: 150px; }

.empty-state {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  border-radius: 12px;
}

.empty-content {
  text-align: center;
  color: #aaa;
}

.empty-content i {
  font-size: 64px;
  margin-bottom: 20px;
}

.empty-content h3 {
  font-size: 18px;
  font-weight: 500;
  color: #555;
  margin: 0 0 10px 0;
}

.empty-content p {
  font-size: 14px;
  margin: 0 0 25px 0;
}

.history-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 25px;
}

.history-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
}

.history-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #f0f2f5;
}

.course-tag {
  background: var(--course-bg-color, #f0f9ff);
  color: var(--course-text-color, #409EFF);
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 13px;
  font-weight: 500;
}

.card-actions .el-dropdown-link {
  color: #999;
  cursor: pointer;
  padding: 5px;
  border-radius: 50%;
  transition: all 0.2s;
}
.card-actions .el-dropdown-link:hover {
  background-color: #f5f5f5;
  color: #5A8DFF;
}

.card-body {
  padding: 20px;
  flex-grow: 1;
}

.chat-title {
  font-size: 17px;
  font-weight: 600;
  color: #333;
  margin: 0 0 15px 0;
  line-height: 1.4;
  height: 48px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.chat-preview p {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin: 0;
  height: 44px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
.chat-preview .no-message-preview {
  color: #999;
  font-style: italic;
}
.chat-preview .message-role {
  font-weight: 500;
  margin-right: 5px;
}
.chat-preview .message-role.user { color: #5A8DFF; }
.chat-preview .message-role.assistant { color: #888; }


.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-top: 1px solid #f0f2f5;
  background-color: #fcfdfe;
}

.chat-stats {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #999;
}

.continue-hint {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 13px;
  font-weight: 500;
  color: #999;
  transition: all 0.3s ease;
}

.history-card:hover .continue-hint {
  color: #5A8DFF;
  gap: 8px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 40px;
}

.danger { color: #f56c6c; }
.danger:hover { color: #f56c6c; background-color: #fef0f0; }

@media (max-width: 768px) {
  .history-header { flex-direction: column; align-items: stretch; }
  .header-actions { flex-direction: column; align-items: stretch; }
  .search-input, .course-select { width: 100%; }
}
</style>