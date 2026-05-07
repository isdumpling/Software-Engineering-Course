<template>
  <div class="admin-page">
    <div class="page-title">
      <div>
        <h3>课程知识库</h3>
        <p>上传课程教材、构建向量数据库，并查看 AI 加载状态。</p>
      </div>
      <el-button type="primary" @click="loadCourses">刷新状态</el-button>
    </div>

    <el-card class="section-card">
      <div v-loading="loading">
        <el-table v-if="courses.length" :data="courses" border>
        <el-table-column prop="course_name" label="课程" width="130" />
        <el-table-column prop="course_id" label="课程 ID" width="180" />
        <el-table-column prop="doc_file" label="教材文件" min-width="180" />
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
        <el-table-column label="AI" width="100">
          <template slot-scope="{ row }">
            <el-tag :type="row.loaded ? 'success' : 'warning'">
              {{ row.loaded ? '已加载' : '未加载' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="330" fixed="right">
          <template slot-scope="{ row }">
            <el-button size="mini" @click="openUpload(row)">上传教材</el-button>
            <el-button size="mini" type="primary" :disabled="!row.doc_exists" @click="buildKnowledge(row)">构建</el-button>
            <el-button size="mini" type="success" :disabled="!row.vector_db_exists" @click="reloadCourse(row)">重载</el-button>
            <el-button size="mini" @click="goRetrieval(row)">检索</el-button>
          </template>
        </el-table-column>
      </el-table>
        <el-empty v-else description="暂无数据" />
      </div>
    </el-card>

    <el-dialog title="上传课程教材" :visible.sync="uploadDialogVisible" width="520px">
      <p v-if="currentCourse">当前课程：<strong>{{ currentCourse.course_name }}</strong></p>
      <el-alert
        title="仅支持 DOCX 文件。上传后需点击「构建」生成向量数据库。"
        type="info" show-icon :closable="false" class="mb-16"
      />
      <el-upload
        drag action="" :http-request="uploadMaterial" :show-file-list="false" accept=".docx"
      >
        <i class="el-icon-upload"></i>
        <div class="el-upload__text">将 DOCX 文件拖到此处，或 <em>点击上传</em></div>
      </el-upload>
    </el-dialog>

    <el-dialog title="知识库构建任务" :visible.sync="taskDialogVisible" width="720px">
      <div v-if="currentTask">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="任务 ID">{{ currentTask.id }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="taskTagType(currentTask.status)">{{ currentTask.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="课程">{{ currentTask.course_name }}</el-descriptions-item>
          <el-descriptions-item label="文档块数">{{ currentTask.document_count || 0 }}</el-descriptions-item>
        </el-descriptions>
        <div class="log-box">
          <pre>{{ currentTask.log || currentTask.error_message || '暂无日志' }}</pre>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'AdminCourses',
  data() {
    return {
      loading: false,
      courses: [],
      uploadDialogVisible: false,
      taskDialogVisible: false,
      currentCourse: null,
      currentTask: null,
      pollTimer: null
    }
  },
  created() {
    this.loadCourses()
  },
  beforeDestroy() {
    if (this.pollTimer) { clearInterval(this.pollTimer) }
  },
  methods: {
    async loadCourses() {
      this.loading = true
      try {
        this.courses = await this.$api.adminAPI.getCourses()
      } catch (error) {
        this.$message.error('加载课程状态失败')
      } finally {
        this.loading = false
      }
    },
    openUpload(row) {
      this.currentCourse = row
      this.uploadDialogVisible = true
    },
    async uploadMaterial({ file }) {
      if (!this.currentCourse) return
      const formData = new FormData()
      formData.append('file', file)
      try {
        await this.$api.adminAPI.uploadMaterial(this.currentCourse.course_id, formData)
        this.$message.success('教材上传成功')
        this.uploadDialogVisible = false
        this.loadCourses()
      } catch (error) {
        this.$message.error(error.response?.data?.detail || '上传失败')
      }
    },
    async buildKnowledge(row) {
      try {
        const confirmed = await this.$confirm(
          `确认构建「${row.course_name}」的向量知识库吗？`,
          '确认构建', { type: 'warning' }
        )
        if (!confirmed) return
        const task = await this.$api.adminAPI.buildKnowledge(row.course_id)
        this.taskDialogVisible = true
        this.currentTask = {
          id: task.task_id, course_id: task.course_id,
          course_name: task.course_name, status: task.status,
          log: '任务已提交……'
        }
        this.pollTask(task.task_id)
      } catch (error) {
        if (error !== 'cancel') {
          this.$message.error(error.response?.data?.detail || '构建失败')
        }
      }
    },
    pollTask(taskId) {
      if (this.pollTimer) clearInterval(this.pollTimer)
      this.pollTimer = setInterval(async () => {
        try {
          const task = await this.$api.adminAPI.getBuildTask(taskId)
          this.currentTask = task
          if (task.status === 'success' || task.status === 'failed') {
            clearInterval(this.pollTimer)
            this.pollTimer = null
            this.loadCourses()
            this.$message[task.status === 'success' ? 'success' : 'error'](
              task.status === 'success' ? '知识库构建成功' : '知识库构建失败'
            )
          }
        } catch (error) {
          // 网络异常时继续轮询
        }
      }, 2000)
    },
    async reloadCourse(row) {
      try {
        await this.$api.adminAPI.reloadCourse(row.course_id)
        this.$message.success('课程向量库已重新加载')
        this.loadCourses()
      } catch (error) {
        this.$message.error(error.response?.data?.detail || '重载失败')
      }
    },
    goRetrieval(row) {
      this.$router.push({ path: '/admin/retrieval-test', query: { course_id: row.course_id } })
    },
    taskTagType(status) {
      if (status === 'success') return 'success'
      if (status === 'failed') return 'danger'
      if (status === 'running') return 'warning'
      return 'info'
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
.mb-16 { margin-bottom: 16px; }
.log-box { margin-top: 18px; padding: 14px; background: #f7f9fc; border-radius: 12px; max-height: 320px; overflow: auto; }
.log-box pre { margin: 0; white-space: pre-wrap; color: #344563; font-size: 13px; line-height: 1.6; }
</style>
