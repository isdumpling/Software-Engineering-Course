<template>
  <div class="admin-layout">
    <div class="admin-header">
      <div>
        <h2>管理员控制台</h2>
        <p>课程知识库、向量数据库与系统状态管理</p>
      </div>
    </div>

    <div class="admin-body">
      <aside class="admin-sidebar">
        <el-menu
          :default-active="$route.path"
          router
          class="admin-menu"
        >
          <el-menu-item index="/admin/dashboard">
            <i class="el-icon-data-analysis"></i>
            <span>系统概览</span>
          </el-menu-item>
          <el-menu-item index="/admin/courses">
            <i class="el-icon-collection"></i>
            <span>课程知识库</span>
          </el-menu-item>
          <el-menu-item index="/admin/retrieval-test">
            <i class="el-icon-search"></i>
            <span>检索测试</span>
          </el-menu-item>
          <el-menu-item index="/admin/system">
            <i class="el-icon-setting"></i>
            <span>系统状态</span>
          </el-menu-item>
        </el-menu>
      </aside>

      <main class="admin-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminLayout'
}
</script>

<style scoped>
.admin-layout {
  min-height: calc(100vh - 65px);
  background: #f5f7fb;
}

.admin-header {
  margin: 24px auto 0;
  max-width: 1180px;
  padding: 28px 32px;
  border-radius: 18px;
  background: linear-gradient(135deg, #5b8def 0%, #7b5cf0 100%);
  color: #fff;
  box-shadow: 0 12px 32px rgba(91, 141, 239, 0.24);
}

.admin-header h2 {
  margin: 0 0 8px;
  font-size: 26px;
  font-weight: 700;
}

.admin-header p {
  margin: 0;
  opacity: 0.9;
}

.admin-body {
  max-width: 1180px;
  margin: 24px auto;
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 20px;
}

.admin-sidebar {
  background: #fff;
  border-radius: 16px;
  padding: 12px;
  box-shadow: 0 8px 24px rgba(20, 40, 90, 0.08);
}

.admin-menu {
  border-right: none;
}

.admin-content {
  min-width: 0;
}

@media (max-width: 900px) {
  .admin-body {
    grid-template-columns: 1fr;
  }
}
</style>
