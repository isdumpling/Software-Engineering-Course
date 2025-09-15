<template>
  <div id="app">
    <!-- 顶部导航栏 -->
    <el-header v-if="showNavbar" style="padding: 0;">
      <div class="navbar">
        <div class="navbar-brand">
          <router-link to="/home">
            <h2>智能课程助教</h2>
          </router-link>
        </div>
        <div class="navbar-menu">
          <el-menu mode="horizontal" :default-active="$route.path" router>
            <el-menu-item index="/home">选择课程</el-menu-item>
            <el-menu-item index="/history">历史记录</el-menu-item>
            <el-menu-item @click="logout">退出登录</el-menu-item>
          </el-menu>
        </div>
      </div>
    </el-header>
    
    <!-- 主要内容区域 -->
    <div class="main-content">
      <router-view/>
    </div>
  </div>
</template>

<script>
export default {
  name: 'App',
  computed: {
    showNavbar() {
      // 在登录和注册页面不显示导航栏
      return this.$route.path !== '/login' && this.$route.path !== '/register' && this.$route.path !== '/'
    }
  },
  methods: {
    logout() {
      this.$store.commit('LOGOUT')
      this.$router.push('/login')
      this.$message.success('已成功退出登录')
    }
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  background: #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  height: 60px;
}

.navbar-brand h2 {
  color: #409EFF;
  margin: 0;
  text-decoration: none;
}

.navbar-brand a {
  text-decoration: none;
}

.main-content {
  min-height: calc(100vh - 60px);
  background: #f5f5f5;
}

/* 去除Element UI默认样式 */
.el-menu.el-menu--horizontal {
  border-bottom: none;
}

.el-header {
  background: #fff;
  height: 60px !important;
  line-height: 60px;
}
</style>