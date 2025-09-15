<template>
  <div class="login-container">
    <div class="login-form">
      <div class="login-header">
        <h1>智能课程助教</h1>
        <p>欢迎使用智能课程助教聊天机器人</p>
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
            placeholder="请输入用户名"
            prefix-icon="el-icon-user"
          ></el-input>
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="el-icon-lock"
            show-password
          ></el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            @click="handleLogin"
            :loading="loading"
            class="login-button"
          >
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>
        
        <el-form-item class="forgot-password-item">
          <router-link to="/forgot-password" class="forgot-link">忘记密码？</router-link>
        </el-form-item>
      </el-form>
      
      <div class="login-footer">
        <span>还没有账号？</span>
        <router-link to="/register" class="register-link">立即注册</router-link>
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
              user: response.user
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
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.login-form {
  background: rgba(255, 255, 255, 0.95);
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
  backdrop-filter: blur(10px);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h1 {
  color: #333;
  margin: 0 0 10px 0;
  font-size: 28px;
  font-weight: 600;
}

.login-header p {
  color: #666;
  margin: 0;
  font-size: 14px;
}

.login-button {
  width: 100%;
  height: 45px;
  font-size: 16px;
  font-weight: 500;
}

.login-footer {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  color: #666;
}

.register-link {
  color: #409EFF;
  text-decoration: none;
  margin-left: 5px;
  font-weight: 500;
}

.register-link:hover {
  text-decoration: underline;
}

/* Element UI 样式覆盖 */
.el-form-item {
  margin-bottom: 20px;
}

.el-input__inner {
  height: 45px;
  border-radius: 6px;
}

.el-button--primary {
  background-color: #409EFF;
  border-color: #409EFF;
}

.el-button--primary:hover {
  background-color: #66b1ff;
  border-color: #66b1ff;
}

.forgot-password-item {
  margin-bottom: 0;
  text-align: center;
}

.forgot-link {
  color: #409EFF;
  text-decoration: none;
  font-size: 14px;
  font-weight: 400;
}

.forgot-link:hover {
  text-decoration: underline;
}
</style>