<template>
  <div class="reset-password-container">
    <div class="reset-password-form">
      <!-- 重置密码表单 -->
      <div v-if="!resetComplete && isValidToken" class="reset-form-section">
        <div class="reset-password-header">
          <i class="el-icon-refresh-left reset-icon"></i>
          <h1>重置密码</h1>
          <p>请设置您的新密码</p>
        </div>
        
        <el-form 
          :model="resetForm" 
          :rules="resetRules" 
          ref="resetForm" 
          label-width="0px"
          size="medium"
        >
          <el-form-item prop="password">
            <el-input
              v-model="resetForm.password"
              type="password"
              placeholder="请输入新密码"
              prefix-icon="el-icon-lock"
              show-password
            ></el-input>
          </el-form-item>
          
          <el-form-item prop="confirmPassword">
            <el-input
              v-model="resetForm.confirmPassword"
              type="password"
              placeholder="请确认新密码"
              prefix-icon="el-icon-lock"
              show-password
            ></el-input>
          </el-form-item>
          
          <el-form-item>
            <el-button 
              type="primary" 
              @click="handleResetPassword"
              :loading="loading"
              class="reset-button"
            >
              {{ loading ? '重置中...' : '重置密码' }}
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 重置成功 -->
      <div v-if="resetComplete" class="success-section">
        <div class="success-icon">
          <i class="el-icon-circle-check"></i>
        </div>
        <h2>密码重置成功</h2>
        <p>您的密码已成功重置，请使用新密码登录</p>
        
        <div class="success-actions">
          <el-button type="primary" @click="goToLogin" class="login-button">
            立即登录
          </el-button>
        </div>
      </div>

      <!-- 无效或过期的令牌 -->
      <div v-if="!isValidToken" class="error-section">
        <div class="error-icon">
          <i class="el-icon-circle-close"></i>
        </div>
        <h2>链接无效或已过期</h2>
        <p>很抱歉，此重置密码链接无效或已过期</p>
        <p class="help-text">请重新申请密码重置</p>
        
        <div class="error-actions">
          <el-button type="primary" @click="goToForgotPassword">
            重新申请重置
          </el-button>
          <el-button type="text" @click="goToLogin">
            返回登录
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ResetPassword',
  data() {
    const validateConfirmPassword = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请再次输入密码'))
      } else if (value !== this.resetForm.password) {
        callback(new Error('两次输入密码不一致!'))
      } else {
        callback()
      }
    }
    
    return {
      resetForm: {
        password: '',
        confirmPassword: ''
      },
      resetRules: {
        password: [
          { required: true, message: '请输入新密码', trigger: 'blur' },
          { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, validator: validateConfirmPassword, trigger: 'blur' }
        ]
      },
      loading: false,
      resetComplete: false,
      isValidToken: true,
      token: ''
    }
  },
  created() {
    // 从URL参数获取重置令牌
    this.token = this.$route.query.token || ''
    
    if (!this.token) {
      this.isValidToken = false
      return
    }
    
    // 验证令牌有效性
    this.validateToken()
  },
  methods: {
    async validateToken() {
      try {
        // 调用API验证令牌
        await this.$api.authAPI.validateResetToken(this.token)
        this.isValidToken = true
        
      } catch (error) {
        console.error('令牌验证失败:', error)
        this.isValidToken = false
        this.$message.error('重置链接无效或已过期')
      }
    },
    
    async handleResetPassword() {
      this.$refs.resetForm.validate(async (valid) => {
        if (valid) {
          this.loading = true
          
          try {
            // 调用重置密码API
            await this.$api.authAPI.resetPassword(this.token, this.resetForm.password)
            
            this.resetComplete = true
            this.$message.success('密码重置成功！')
            
          } catch (error) {
            console.error('密码重置失败:', error)
            // 错误信息已由axios拦截器处理
          } finally {
            this.loading = false
          }
        } else {
          return false
        }
      })
    },
    
    goToLogin() {
      this.$router.push('/login')
    },
    
    goToForgotPassword() {
      this.$router.push('/forgot-password')
    }
  }
}
</script>

<style scoped>
.reset-password-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.reset-password-form {
  background: rgba(255, 255, 255, 0.95);
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 450px;
  backdrop-filter: blur(10px);
}

.reset-password-header {
  text-align: center;
  margin-bottom: 30px;
}

.reset-icon {
  font-size: 48px;
  color: #409EFF;
  margin-bottom: 15px;
}

.reset-password-header h1 {
  color: #333;
  margin: 0 0 10px 0;
  font-size: 28px;
  font-weight: 600;
}

.reset-password-header p {
  color: #666;
  margin: 0;
  font-size: 14px;
}

.reset-button {
  width: 100%;
  height: 45px;
  font-size: 16px;
  font-weight: 500;
}

/* 成功状态 */
.success-section {
  text-align: center;
}

.success-icon i {
  font-size: 64px;
  color: #67C23A;
  margin-bottom: 20px;
}

.success-section h2 {
  color: #333;
  margin: 0 0 15px 0;
  font-size: 24px;
  font-weight: 600;
}

.success-section p {
  color: #666;
  margin: 0 0 20px 0;
  font-size: 14px;
  line-height: 1.5;
}

.success-actions {
  margin-top: 30px;
}

.login-button {
  width: 100%;
  height: 45px;
  font-size: 16px;
  font-weight: 500;
}

/* 错误状态 */
.error-section {
  text-align: center;
}

.error-icon i {
  font-size: 64px;
  color: #F56C6C;
  margin-bottom: 20px;
}

.error-section h2 {
  color: #333;
  margin: 0 0 15px 0;
  font-size: 24px;
  font-weight: 600;
}

.error-section p {
  color: #666;
  margin: 0 0 10px 0;
  font-size: 14px;
  line-height: 1.5;
}

.help-text {
  font-size: 12px !important;
  color: #999 !important;
  margin-bottom: 20px !important;
}

.error-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 30px;
}

.error-actions .el-button {
  height: 40px;
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

/* 响应式设计 */
@media (max-width: 480px) {
  .reset-password-form {
    padding: 30px 20px;
  }
  
  .reset-password-header h1,
  .success-section h2,
  .error-section h2 {
    font-size: 22px;
  }
  
  .reset-icon,
  .success-icon i,
  .error-icon i {
    font-size: 48px;
  }
}
</style>