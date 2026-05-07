<template>
  <div class="admin-page">
    <div class="page-title">
      <div>
        <h3>系统状态</h3>
        <p>查看后端、数据库、AI 服务和向量库加载状态。</p>
      </div>
      <div>
        <el-button @click="loadHealth">刷新</el-button>
        <el-button type="primary" :loading="reloading" @click="reloadAI">重新加载 AI 服务</el-button>
      </div>
    </div>

    <el-card class="section-card">
      <div v-loading="loading">
        <el-descriptions :column="2" border>
        <el-descriptions-item label="API 状态">
          <el-tag type="success">{{ health.api_status || '-' }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="数据库状态">
          <el-tag :type="dbTagType">{{ health.database_status || '-' }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="AI 服务">
          <el-tag :type="health.ai_status === 'initialized' ? 'success' : 'warning'">
            {{ health.ai_status || '-' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="豆包模型">{{ health.model_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="API Key">
          <el-tag :type="health.api_key_configured ? 'success' : 'danger'">
            {{ health.api_key_configured ? '已配置' : '未配置' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="嵌入模型">{{ health.embedding_model || '-' }}</el-descriptions-item>
      </el-descriptions>
      </div>
    </el-card>

    <el-card class="section-card">
      <div slot="header">已加载课程</div>
      <el-table v-if="loadedRows.length" :data="loadedRows" border>
        <el-table-column prop="course_id" label="课程 ID" />
        <el-table-column prop="course_name" label="课程名称" />
      </el-table>
      <el-empty v-else description="暂无已加载课程" />
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'AdminSystem',
  data() {
    return {
      loading: false,
      reloading: false,
      health: {}
    }
  },
  computed: {
    dbTagType() {
      return String(this.health.database_status || '').startsWith('connected') ? 'success' : 'danger'
    },
    loadedRows() {
      const loaded = this.health.loaded_courses || {}
      return Object.keys(loaded).map(cid => ({ course_id: cid, course_name: loaded[cid] }))
    }
  },
  created() {
    this.loadHealth()
  },
  methods: {
    async loadHealth() {
      this.loading = true
      try {
        this.health = await this.$api.adminAPI.getSystemHealth()
      } catch (error) {
        this.$message.error('加载系统状态失败')
      } finally {
        this.loading = false
      }
    },
    async reloadAI() {
      this.reloading = true
      try {
        await this.$api.adminAPI.reloadAI()
        this.$message.success('AI 服务已重新加载')
        this.loadHealth()
      } catch (error) {
        this.$message.error(error.response?.data?.detail || '重载失败')
      } finally {
        this.reloading = false
      }
    }
  }
}
</script>

<style scoped>
.admin-page { display: flex; flex-direction: column; gap: 18px; }
.page-title { display: flex; justify-content: space-between; align-items: flex-end; }
.page-title h3 { margin: 0 0 6px; font-size: 22px; color: #1f2d3d; }
.page-title p { margin: 0; color: #7a869a; }
.section-card { border-radius: 16px; }
</style>
