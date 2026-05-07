<template>
  <div id="app">
    <!-- 顶部导航栏 -->
    <el-header v-if="showNavbar" class="app-header">
      <div class="navbar">
        <div class="navbar-brand">
          <router-link to="/home" class="brand-link">
            <svg width="32" height="32" viewBox="0 0 64 64" class="brand-logo">
              <path fill="none" stroke="#FFF" stroke-width="3" stroke-miterlimit="10" d="M1 20L32 6l31 14-31 14z"/>
              <path fill="none" stroke="#FFF" stroke-width="3" stroke-miterlimit="10" d="M11 26v18c0 4.418 9.399 8 21 8s21-3.582 21-8V26"/>
              <path fill="none" stroke="#FFF" stroke-width="3" stroke-miterlimit="10" d="M57 40V28"/>
            </svg>
            <h1 class="brand-title">智能课程助教</h1>
          </router-link>
        </div>
        
        <div class="navbar-menu">
           <el-menu mode="horizontal" :default-active="$route.path" router background-color="transparent" text-color="#fff" active-text-color="#fff">
            <el-menu-item index="/home" class="nav-item">
              <i class="el-icon-s-home"></i>
              <span>课程主页</span>
            </el-menu-item>
            <el-menu-item index="/history" class="nav-item">
              <i class="el-icon-time"></i>
              <span>对话历史</span>
            </el-menu-item>
            <el-menu-item
              v-if="isAdmin"
              index="/admin/dashboard"
              class="nav-item"
            >
              <i class="el-icon-s-tools"></i>
              <span>管理员控制台</span>
            </el-menu-item>
          </el-menu>
        </div>

        <div class="navbar-user">
          <el-dropdown trigger="click" @command="handleCommand">
            <span class="el-dropdown-link">
              <i class="el-icon-user-solid user-icon"></i>
              <span class="username">{{ username }}</span>
              <i class="el-icon-arrow-down el-icon--right"></i>
            </span>
            <el-dropdown-menu slot="dropdown">
              <el-dropdown-item command="logout" icon="el-icon-switch-button">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </el-dropdown>
        </div>
      </div>
    </el-header>
    
    <!-- 主要内容区域 -->
    <div class="main-content" :class="{ 'no-header': !showNavbar }">
      <router-view/>
    </div>
  </div>
</template>

<script>
export default {
  name: 'App',
  computed: {
    showNavbar() {
      const noNavRoutes = ['/login', '/register', '/forgot-password', '/reset-password', '/'];
      return !noNavRoutes.includes(this.$route.path);
    },
    username() {
      return this.$store.getters.username || '用户';
    },
    isAdmin() {
      return this.$store.getters.isAdmin;
    }
  },
  methods: {
    handleCommand(command) {
      if (command === 'logout') {
        this.logout();
      }
    },
    logout() {
      this.$store.dispatch('logout');
      this.$router.push('/login');
      this.$message.success('您已成功退出');
    }
  }
}
</script>

<style>
/* Global Styles */
body {
  margin: 0;
  background-color: #f7f8fc;
  font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

#app {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #333;
}

/* App Header */
.app-header {
  background: linear-gradient(135deg, #5A8DFF 0%, #764BA2 100%);
  padding: 0 30px;
  height: 65px !important;
  line-height: 65px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

.navbar-brand .brand-link {
  display: flex;
  align-items: center;
  text-decoration: none;
  gap: 12px;
}

.brand-title {
  color: #fff;
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}

/* Navbar Menu */
.navbar-menu .el-menu {
  border-bottom: none !important;
}

.navbar-menu .nav-item {
  font-size: 15px;
  font-weight: 500;
  border-bottom-color: #fff !important;
}

.navbar-menu .nav-item span {
  margin-left: 5px;
}

.navbar-menu .nav-item.is-active {
  background-color: rgba(255, 255, 255, 0.15) !important;
}

.navbar-menu .nav-item:hover {
  background-color: rgba(255, 255, 255, 0.1) !important;
}

/* User Dropdown */
.navbar-user .el-dropdown-link {
  cursor: pointer;
  color: #fff;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 10px;
}

.user-icon {
  font-size: 18px;
}

.username {
  font-weight: 500;
}

/* Main Content Area */
.main-content {
  min-height: calc(100vh - 65px);
  background-color: #f7f8fc;
}

.main-content.no-header {
  min-height: 100vh;
}

/* Element UI Overrides */
.el-button--primary {
  background-color: #5A8DFF !important;
  border-color: #5A8DFF !important;
  transition: all 0.3s;
}
.el-button--primary:hover {
  background-color: #73a0ff !important;
  border-color: #73a0ff !important;
}

.el-pagination.is-background .el-pager li:not(.disabled).active {
  background-color: #5A8DFF !important;
}
</style>