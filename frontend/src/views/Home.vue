<template>
  <div class="home-container">
    <div class="home-header">
      <div class="header-left">
        <h1>欢迎回来，{{ username }}!</h1>
        <p>今天想学习哪一门课程？</p>
      </div>
      <div class="header-right">
        <el-button type="primary" icon="el-icon-time" @click="$router.push('/history')">
          查看历史记录
        </el-button>
      </div>
    </div>
    
    <div class="courses-section">
      <div class="section-header">
        <h2>我的课程</h2>
        <p>选择一门课程开始您的智能学习之旅</p>
      </div>
      <div class="courses-grid">
        <div 
          v-for="course in courses" 
          :key="course.id"
          class="course-card"
          @click="enterCourse(course)"
          :style="{'--course-color': course.color}"
        >
          <div class="card-content">
            <div class="course-icon">
              <i :class="course.icon"></i>
            </div>
            <div class="course-info">
              <h3>{{ course.name }}</h3>
              <p>{{ course.description }}</p>
            </div>
          </div>
          <div class="card-footer">
            <span class="chat-count">
              <i class="el-icon-chat-dot-round"></i>
              {{ getChatCountForCourse(course.id) }} 次对话
            </span>
            <div class="course-enter">
              <span>开始学习</span>
              <i class="el-icon-arrow-right"></i>
            </div>
          </div>
        </div>
      </div>
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
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap');

.home-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px;
  font-family: 'Noto Sans SC', sans-serif;
}

.home-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  padding: 25px 30px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  margin-bottom: 40px;
}

.header-left h1 {
  font-size: 24px;
  color: #333;
  margin: 0 0 5px 0;
  font-weight: 700;
}

.header-left p {
  font-size: 14px;
  color: #999;
  margin: 0;
}

/* Courses Section */
.courses-section {
  margin-bottom: 40px;
}

.section-header {
  margin-bottom: 25px;
}

.section-header h2 {
  font-size: 22px;
  color: #333;
  font-weight: 700;
  margin: 0 0 5px 0;
}

.section-header p {
  font-size: 14px;
  color: #999;
}

.courses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 25px;
}

.course-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  border-left: 5px solid var(--course-color, #409EFF);
  overflow: hidden;
}

.course-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
}

.card-content {
  padding: 25px;
  display: flex;
  align-items: flex-start;
  gap: 20px;
  flex-grow: 1;
}

.course-icon {
  width: 50px;
  height: 50px;
  border-radius: 10px;
  background-color: var(--course-color, #409EFF);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.course-icon i {
  font-size: 24px;
  color: white;
}

.course-info h3 {
  font-size: 18px;
  color: #333;
  margin: 0 0 8px 0;
  font-weight: 700;
}

.course-info p {
  font-size: 14px;
  color: #777;
  margin: 0;
  line-height: 1.5;
}

.card-footer {
  padding: 15px 25px;
  background-color: #f9fafb;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-count {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #888;
}

.chat-count i {
  font-size: 15px;
}

.course-enter {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 13px;
  font-weight: 500;
  color: var(--course-color, #409EFF);
  transition: all 0.3s ease;
}

.course-card:hover .course-enter {
  gap: 8px;
}

.course-enter i {
  transition: transform 0.3s ease;
}
.course-card:hover .course-enter i {
  transform: translateX(3px);
}


/* 响应式设计 */
@media (max-width: 768px) {
  .home-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .courses-grid {
    grid-template-columns: 1fr;
  }
}
</style>