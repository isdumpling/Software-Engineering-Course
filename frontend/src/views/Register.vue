<template>
  <div class="register-container">
    <div class="register-box">
      <div class="register-left">
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
      <div class="register-right">
        <div class="register-form-wrapper">
          <div class="register-header">
            <h2>创建您的账户</h2>
            <p>开启您的智能学习之旅</p>
          </div>
          
          <el-form 
            :model="registerForm" 
            :rules="registerRules" 
            ref="registerForm" 
            label-width="0px"
            size="medium"
          >
            <el-form-item prop="username">
              <el-input
                v-model="registerForm.username"
                placeholder="用户名"
                prefix-icon="el-icon-user"
              ></el-input>
            </el-form-item>
            
            <el-form-item prop="email">
              <el-input
                v-model="registerForm.email"
                placeholder="邮箱"
                prefix-icon="el-icon-message"
              ></el-input>
            </el-form-item>
            
            <el-form-item prop="password">
              <el-input
                v-model="registerForm.password"
                type="password"
                placeholder="密码"
                prefix-icon="el-icon-lock"
                show-password
              ></el-input>
            </el-form-item>
            
            <el-form-item prop="confirmPassword">
              <el-input
                v-model="registerForm.confirmPassword"
                type="password"
                placeholder="确认密码"
                prefix-icon="el-icon-lock"
                show-password
              ></el-input>
            </el-form-item>
            
            <el-form-item prop="securityQuestion">
              <el-input
                v-model="registerForm.securityQuestion"
                placeholder="安全问题（可选）"
                prefix-icon="el-icon-question"
              ></el-input>
            </el-form-item>
            
            <el-form-item prop="securityAnswer" v-if="registerForm.securityQuestion">
              <el-input
                v-model="registerForm.securityAnswer"
                placeholder="安全问题答案"
                prefix-icon="el-icon-edit"
                @keyup.enter.native="handleRegister"
              ></el-input>
            </el-form-item>
            
            <el-form-item>
              <el-button 
                type="primary" 
                @click="handleRegister"
                :loading="loading"
                class="register-button"
              >
                {{ loading ? '注册中...' : '注 册' }}
              </el-button>
            </el-form-item>
          </el-form>
          
          <div class="register-footer">
            <span>已有账号？</span>
            <router-link to="/login" class="login-link">立即登录</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Register',
  data() {
    const validateConfirmPassword = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请再次输入密码'))
      } else if (value !== this.registerForm.password) {
        callback(new Error('两次输入密码不一致!'))
      } else {
        callback()
      }
    }
    
    return {
      registerForm: {
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
        securityQuestion: '',
        securityAnswer: ''
      },
      registerRules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
        ],
        email: [
          { required: true, message: '请输入邮箱地址', trigger: 'blur' },
          { type: 'email', message: '请输入正确的邮箱地址', trigger: ['blur', 'change'] }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, validator: validateConfirmPassword, trigger: 'blur' }
        ],
        securityQuestion: [
          { min: 5, max: 200, message: '安全问题长度在 5 到 200 个字符', trigger: 'blur' }
        ],
        securityAnswer: [
          { min: 1, max: 100, message: '安全答案长度在 1 到 100 个字符', trigger: 'blur' }
        ]
      },
      loading: false
    }
  },
  methods: {
    async handleRegister() {
      this.$refs.registerForm.validate(async (valid) => {
        if (valid) {
          this.loading = true
          
          try {
            // 准备注册数据
            const registerData = {
              username: this.registerForm.username,
              email: this.registerForm.email,
              password: this.registerForm.password
            }
            
            // 如果设置了安全问题，添加到注册数据
            if (this.registerForm.securityQuestion.trim()) {
              registerData.security_question = this.registerForm.securityQuestion
              registerData.security_answer = this.registerForm.securityAnswer
            }
            
            // 调用注册API
            await this.$api.authAPI.register(registerData)
            
            this.$message.success('注册成功！请登录')
            this.$router.push('/login')
            
          } catch (error) {
            console.error('注册失败:', error)
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

.register-container {
  min-height: 100vh;
  background-color: #f0f2f5;
  display: flex;
  justify-content: center;
  align-items: center;
  font-family: 'Noto Sans SC', sans-serif;
  padding: 20px 0;
}

.register-box {
  display: flex;
  width: 100%;
  max-width: 900px;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.register-left {
  flex: 1;
  background: linear-gradient(135deg, #5A8DFF 0%, #764BA2 100%);
  color: white;
  display: none; /* Hide on smaller screens */
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 40px;
  text-align: center;
}

@media (min-width: 900px) {
  .register-left {
    display: flex;
  }
}

.brand-logo {
  margin-bottom: 20px;
}

.register-left h1 {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 10px 0;
}

.register-left p {
  font-size: 16px;
  font-weight: 300;
}

.register-right {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px 20px;
}

.register-form-wrapper {
  width: 100%;
  max-width: 340px;
}

.register-header {
  text-align: left;
  margin-bottom: 25px;
}

.register-header h2 {
  color: #333;
  margin: 0 0 10px 0;
  font-size: 24px;
  font-weight: 700;
}

.register-header p {
  color: #999;
  margin: 0;
  font-size: 14px;
}

.register-button {
  width: 100%;
  height: 45px;
  font-size: 16px;
  font-weight: 500;
  letter-spacing: 2px;
}

.register-footer {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  color: #999;
}

.login-link {
  color: #5A8DFF;
  text-decoration: none;
  margin-left: 5px;
  font-weight: 500;
}

.login-link:hover {
  text-decoration: underline;
}

/* Element UI 样式覆盖 */
.el-form-item {
  margin-bottom: 18px;
}

.el-input__inner {
  height: 42px;
  line-height: 42px;
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
  line-height: 42px;
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
</style>