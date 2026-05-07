<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-left">
        <div class="brand-logo">
          <svg width="50" height="50" viewBox="0 0 64 64">
            <path fill="none" stroke="#FFF" stroke-width="3" stroke-miterlimit="10" d="M1 20L32 6l31 14-31 14z"/>
            <path fill="none" stroke="#FFF" stroke-width="3" stroke-miterlimit="10" d="M11 26v18c0 4.418 9.399 8 21 8s21-3.582 21-8V26"/>
            <path fill="none" stroke="#FFF" stroke-width="3" stroke-miterlimit="10" d="M57 40V28"/>
          </svg>
        </div>
        <h1>智能课程助教</h1>
        <p>一个懂你的 AI 学习伙伴</p>
      </div>
      <div class="login-right">
        <div class="login-form">
          <div class="login-header">
            <h2>欢迎回来</h2>
            <p>请登录以继续</p>
          </div>
          
          <el-form 
            :model="loginForm" 
            :rules="loginRules" 
            ref="loginForm" 
            label-width="0px"
            size="medium"
          >
            <el-form-item prop="username">
              <el-input
                v-model="loginForm.username"
                placeholder="用户名"
                prefix-icon="el-icon-user"
              ></el-input>
            </el-form-item>
            
            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="密码"
                prefix-icon="el-icon-lock"
                show-password
                @keyup.enter.native="handleLogin"
              ></el-input>
            </el-form-item>
            
             <el-form-item class="extra-options">
              <el-checkbox v-model="rememberMe">记住我</el-checkbox>
              <router-link to="/forgot-password" class="forgot-link">忘记密码？</router-link>
            </el-form-item>

            <el-form-item>
              <el-button 
                type="primary" 
                @click="handleLogin"
                :loading="loading"
                class="login-button"
              >
                {{ loading ? '登录中...' : '登 录' }}
              </el-button>
            </el-form-item>
          </el-form>
          
          <div class="login-footer">
            <span>还没有账号？</span>
            <router-link to="/register" class="register-link">立即注册</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data() {
    return {
      loginForm: {
        username: '',
        password: ''
      },
      rememberMe: false,
      loginRules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
        ]
      },
      loading: false
    }
  },
  methods: {
    async handleLogin() {
      this.$refs.loginForm.validate(async (valid) => {
        if (valid) {
          this.loading = true
          
          try {
            // 调用登录API
            const response = await this.$api.authAPI.login(this.loginForm)
            
            const userData = {
              username: response.user.username,
              token: response.access_token,
              isAdmin: response.user.is_admin
            }
            
            this.$store.dispatch('login', userData)
            this.$message.success('登录成功！')
            this.$router.push('/home')
            
          } catch (error) {
            console.error('登录失败:', error)
            // 错误信息已由axios拦截器处理
          } finally {
            this.loading = false
          }
        } else {
          return false
        }
      })
    }
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap');

.login-container {
  min-height: 100vh;
  background-color: #f0f2f5;
  display: flex;
  justify-content: center;
  align-items: center;
  font-family: 'Noto Sans SC', sans-serif;
}

.login-box {
  display: flex;
  width: 100%;
  max-width: 900px;
  min-height: 550px;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.login-left {
  flex: 1;
  background: linear-gradient(135deg, #5A8DFF 0%, #764BA2 100%);
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 40px;
  text-align: center;
}

.brand-logo {
  margin-bottom: 20px;
}

.login-left h1 {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 10px 0;
}

.login-left p {
  font-size: 16px;
  font-weight: 300;
}

.login-right {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 50px;
}

.login-form {
  width: 100%;
  max-width: 320px;
}

.login-header {
  text-align: left;
  margin-bottom: 30px;
}

.login-header h2 {
  color: #333;
  margin: 0 0 10px 0;
  font-size: 24px;
  font-weight: 700;
}

.login-header p {
  color: #999;
  margin: 0;
  font-size: 14px;
}

.login-button {
  width: 100%;
  height: 45px;
  font-size: 16px;
  font-weight: 500;
  letter-spacing: 2px;
}

.login-footer {
  text-align: center;
  margin-top: 30px;
  font-size: 14px;
  color: #999;
}

.register-link {
  color: #5A8DFF;
  text-decoration: none;
  margin-left: 5px;
  font-weight: 500;
}

.register-link:hover {
  text-decoration: underline;
}

.extra-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.forgot-link {
  color: #999;
  text-decoration: none;
  font-size: 14px;
}

.forgot-link:hover {
  color: #5A8DFF;
  text-decoration: underline;
}

/* Element UI 样式覆盖 */
.el-form-item {
  margin-bottom: 25px;
}

.el-input__inner {
  height: 45px;
  line-height: 45px;
  border-radius: 6px;
  background-color: #f7f7f7;
  border: 1px solid #e0e0e0;
  transition: all 0.3s;
}

.el-input__inner:focus {
  background-color: #fff;
  border-color: #5A8DFF;
  box-shadow: 0 0 0 2px rgba(90, 141, 255, 0.2);
}

.el-input__prefix {
  line-height: 45px;
  color: #999;
  left: 12px;
}

.el-button--primary {
  background-color: #5A8DFF;
  border-color: #5A8DFF;
  border-radius: 6px;
  transition: all 0.3s;
}

.el-button--primary:hover {
  background-color: #73a0ff;
  border-color: #73a0ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(90, 141, 255, 0.3);
}

.el-checkbox__label {
  color: #999;
}

.el-checkbox__input.is-checked .el-checkbox__inner {
  background-color: #5A8DFF;
  border-color: #5A8DFF;
}
</style>