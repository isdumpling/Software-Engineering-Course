<template>
  <div class="admin-page">
    <div class="page-title">
      <div>
        <h3>向量检索测试</h3>
        <p>输入课程问题，查看查询优化结果和向量库返回的教材片段。</p>
      </div>
    </div>

    <el-card class="section-card">
      <el-form :inline="true" :model="form">
        <el-form-item label="课程">
          <el-select v-model="form.course_id" placeholder="请选择课程" style="width: 220px">
            <el-option
              v-for="course in courses"
              :key="course.course_id"
              :label="course.course_name"
              :value="course.course_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Top K">
          <el-input-number v-model="form.top_k" :min="1" :max="10" />
        </el-form-item>
      </el-form>
      <el-input v-model="form.query" type="textarea" :rows="3" placeholder="请输入测试问题，例如：瀑布模型是什么？" />
      <div class="actions">
        <el-button type="primary" :loading="loading" @click="testRetrieval">开始检索</el-button>
      </div>
    </el-card>

    <el-card v-if="result" class="section-card">
      <div slot="header">检索结果</div>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="原始查询">{{ result.original_query }}</el-descriptions-item>
        <el-descriptions-item label="优化后查询">{{ result.optimized_query }}</el-descriptions-item>
      </el-descriptions>
      <div v-if="result.message && !result.results.length" class="result-message">
        <el-alert :title="result.message" type="warning" show-icon :closable="false" />
      </div>
      <div class="result-list">
        <el-card v-for="(item, index) in result.results" :key="index" class="result-card" shadow="never">
          <div class="result-title">片段 {{ index + 1 }}</div>
          <div class="result-content">{{ item.content }}</div>
          <pre class="metadata">{{ JSON.stringify(item.metadata, null, 2) }}</pre>
        </el-card>
      </div>
      <el-empty v-if="!result.results || result.results.length === 0" description="没有检索到结果" />
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'AdminRetrievalTest',
  data() {
    return {
      loading: false,
      courses: [],
      form: {
        course_id: this.$route.query.course_id || '',
        query: '',
        top_k: 5
      },
      result: null
    }
  },
  created() {
    this.loadCourses()
  },
  methods: {
    async loadCourses() {
      try {
        this.courses = await this.$api.adminAPI.getCourses()
        if (!this.form.course_id && this.courses.length > 0) {
          this.form.course_id = this.courses[0].course_id
        }
      } catch (error) {
        this.$message.error('加载课程失败')
      }
    },
    async testRetrieval() {
      if (!this.form.course_id || !this.form.query.trim()) {
        this.$message.warning('请选择课程并输入测试问题')
        return
      }
      this.loading = true
      try {
        this.result = await this.$api.adminAPI.testRetrieval(this.form)
      } catch (error) {
        this.$message.error(error.response?.data?.detail || '检索测试失败')
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.admin-page { display: flex; flex-direction: column; gap: 18px; }
.page-title h3 { margin: 0 0 6px; font-size: 22px; color: #1f2d3d; }
.page-title p { margin: 0; color: #7a869a; }
.section-card { border-radius: 16px; }
.actions { margin-top: 16px; text-align: right; }
.result-message { margin-top: 12px; }
.result-list { margin-top: 18px; display: flex; flex-direction: column; gap: 14px; }
.result-card { border-radius: 12px; background: #fbfcff; }
.result-title { font-weight: 600; color: #4f6bed; margin-bottom: 10px; }
.result-content { color: #1f2d3d; line-height: 1.7; white-space: pre-wrap; }
.metadata { margin-top: 12px; padding: 12px; border-radius: 10px; background: #f2f5fa; color: #5e6c84; font-size: 12px; overflow: auto; }
</style>
