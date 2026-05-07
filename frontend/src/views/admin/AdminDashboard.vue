<template>
  <div class="admin-page">
    <div class="page-title">
      <h3>系统概览</h3>
      <el-button type="primary" size="small" @click="loadDashboard">刷新</el-button>
    </div>

    <el-row :gutter="16" v-loading="loading">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-label">课程总数</div>
          <div class="stat-value">{{ dashboard.total_courses || 0 }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-label">已上传教材</div>
          <div class="stat-value">{{ dashboard.doc_ready_courses || 0 }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-label">已构建向量库</div>
          <div class="stat-value">{{ dashboard.vector_ready_courses || 0 }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-label">AI 已加载</div>
          <div class="stat-value">{{ dashboard.loaded_courses || 0 }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="section-card">
      <div slot="header">运行状态</div>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="API 状态">
          <el-tag type="success">{{ dashboard.api_status || '-' }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="AI 服务">
          <el-tag :type="dashboard.ai_status === 'initialized' ? 'success' : 'warning'">
            {{ dashboard.ai_status || '-' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="模型名称">
          {{ dashboard.model_name || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="API Key">
          <el-tag :type="dashboard.api_key_configured ? 'success' : 'danger'">
            {{ dashboard.api_key_configured ? '已配置' : '未配置' }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card class="section-card">
      <div slot="header">课程知识库概览</div>
      <el-table v-if="(dashboard.courses || []).length" :data="dashboard.courses" border>
        <el-table-column prop="course_name" label="课程" width="140" />
        <el-table-column prop="doc_file" label="教材文件" />
        <el-table-column label="教材" width="100">
          <template slot-scope="{ row }">
            <el-tag :type="row.doc_exists ? 'success' : 'info'">
              {{ row.doc_exists ? '已上传' : '未上传' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="向量库" width="100">
          <template slot-scope="{ row }">
            <el-tag :type="row.vector_db_exists ? 'success' : 'info'">
              {{ row.vector_db_exists ? '已构建' : '未构建' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="document_count" label="文档块" width="90" />
        <el-table-column label="AI 加载" width="100">
          <template slot-scope="{ row }">
            <el-tag :type="row.loaded ? 'success' : 'warning'">
              {{ row.loaded ? '已加载' : '未加载' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-else description="暂无数据" />
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'AdminDashboard',
  data() {
    return {
      loading: false,
      dashboard: {}
    }
  },
  created() {
    this.loadDashboard()
  },
  methods: {
    async loadDashboard() {
      this.loading = true
      try {
        this.dashboard = await this.$api.adminAPI.getDashboard()
      } catch (error) {
        this.$message.error('加载系统概览失败')
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.admin-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.page-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.page-title h3 {
  margin: 0;
  font-size: 22px;
  color: #1f2d3d;
}
.stat-card {
  border-radius: 16px;
}
.stat-label {
  color: #7a869a;
  font-size: 14px;
}
.stat-value {
  margin-top: 10px;
  font-size: 30px;
  font-weight: 700;
  color: #4f6bed;
}
.section-card {
  border-radius: 16px;
}
</style>
