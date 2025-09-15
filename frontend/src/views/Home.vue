<template>
  <div class="home-container">
    <div class="welcome-section">
      <h1>欢迎，{{ username }}！</h1>
      <p>选择一门课程开始学习吧</p>
    </div>
    
    <div class="courses-section">
      <div class="courses-grid">
        <div 
          v-for="course in courses" 
          :key="course.id"
          class="course-card"
          @click="enterCourse(course)"
        >
          <div class="course-icon">
            <i :class="course.icon"></i>
          </div>
          <div class="course-info">
            <h3>{{ course.name }}</h3>
            <p>{{ course.description }}</p>
            <div class="course-stats">
              <span class="chat-count">
                <i class="el-icon-chat-dot-round"></i>
                {{ getChatCountForCourse(course.id) }} 次对话
              </span>
            </div>
          </div>
          <div class="course-enter">
            <i class="el-icon-arrow-right"></i>
          </div>
        </div>
      </div>
    </div>
    
    <div class="quick-actions">
      <el-card class="action-card">
        <div class="action-content">
          <i class="el-icon-time action-icon"></i>
          <div class="action-info">
            <h4>历史记录</h4>
            <p>查看所有对话记录</p>
          </div>
          <el-button type="text" @click="$router.push('/history')">查看</el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Home',
  data() {
    return {
      courses: [
        {
          id: 'software-engineering',
          name: '软件工程',
          description: '学习软件开发的系统化方法、工具和技术',
          icon: 'el-icon-cpu',
          color: '#409EFF'
        },
        {
          id: 'operating-system',
          name: '操作系统',
          description: '深入了解计算机操作系统的原理和实现',
          icon: 'el-icon-monitor',
          color: '#67C23A'
        },
        {
          id: 'computer-network',
          name: '计算机网络',
          description: '掌握网络通信协议和网络系统设计',
          icon: 'el-icon-connection',
          color: '#E6A23C'
        },
        {
          id: 'data-structure',
          name: '数据结构',
          description: '学习各种数据结构和算法的设计与实现',
          icon: 'el-icon-s-data',
          color: '#F56C6C'
        },
        {
          id: 'database',
          name: '数据库系统',
          description: '理解数据库设计、查询优化和事务处理',
          icon: 'el-icon-coin',
          color: '#909399'
        },
        {
          id: 'compiler',
          name: '编译原理',
          description: '学习程序语言翻译器的设计和实现',
          icon: 'el-icon-document',
          color: '#9C27B0'
        }
      ],
      chatStats: {} // 存储从服务器获取的统计数据
    }
  },
  computed: {
    username() {
      return this.$store.getters.username
    },
    chatHistories() {
      return this.$store.getters.chatHistories
    }
  },
  async created() {
    // 加载聊天统计数据
    await this.loadChatStats()
  },
  methods: {
    enterCourse(course) {
      this.$router.push({
        name: 'Chat',
        params: { courseId: course.id },
        query: { courseName: course.name }
      })
    },
    
    async loadChatStats() {
      try {
        // 从服务器获取聊天统计数据
        this.chatStats = await this.$api.chatAPI.getChatStats()
      } catch (error) {
        console.error('加载聊天统计失败:', error)
        // 如果API调用失败，继续使用本地数据
      }
    },
    
    getChatCountForCourse(courseId) {
      // 优先使用服务器数据，如果没有则使用本地数据
      if (this.chatStats[courseId]) {
        return this.chatStats[courseId].session_count
      }
      return this.chatHistories.filter(chat => chat.courseId === courseId).length
    }
  }
}
</script>

<style scoped>
.home-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.welcome-section {
  text-align: center;
  margin-bottom: 50px;
}

.welcome-section h1 {
  font-size: 36px;
  color: #333;
  margin: 0 0 10px 0;
  font-weight: 600;
}

.welcome-section p {
  font-size: 18px;
  color: #666;
  margin: 0;
}

.courses-section {
  margin-bottom: 50px;
}

.courses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 20px;
}

.course-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 20px;
  border: 2px solid transparent;
}

.course-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  border-color: #409EFF;
}

.course-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  background: linear-gradient(135deg, #409EFF, #66b1ff);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.course-icon i {
  font-size: 28px;
  color: white;
}

.course-info {
  flex: 1;
}

.course-info h3 {
  font-size: 20px;
  color: #333;
  margin: 0 0 8px 0;
  font-weight: 600;
}

.course-info p {
  font-size: 14px;
  color: #666;
  margin: 0 0 12px 0;
  line-height: 1.4;
}

.course-stats {
  display: flex;
  gap: 15px;
}

.chat-count {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #999;
}

.chat-count i {
  font-size: 14px;
}

.course-enter {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  transition: all 0.3s ease;
}

.course-card:hover .course-enter {
  color: #409EFF;
  transform: translateX(4px);
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.action-card {
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.action-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.action-icon {
  font-size: 32px;
  color: #409EFF;
}

.action-info {
  flex: 1;
}

.action-info h4 {
  font-size: 16px;
  color: #333;
  margin: 0 0 4px 0;
  font-weight: 600;
}

.action-info p {
  font-size: 14px;
  color: #666;
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .courses-grid {
    grid-template-columns: 1fr;
  }
  
  .course-card {
    padding: 20px;
  }
  
  .welcome-section h1 {
    font-size: 28px;
  }
  
  .welcome-section p {
    font-size: 16px;
  }
}
</style>