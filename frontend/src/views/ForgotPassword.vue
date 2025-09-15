<template>
  <div class="forgot-password-container">
    <div class="forgot-password-form">
      <div class="forgot-password-header">
        <i class="el-icon-key forgot-icon"></i>
        <h1>找回密码</h1>
        <p>请输入您的邮箱地址，我们将向您发送重置密码的链接</p>
      </div>
      
      <el-form 
        :model="forgotForm" 
        :rules="forgotRules" 
        ref="forgotForm" 
        label-width="0px"
        size="medium"
        v-if="!emailSent"
      >
        <el-form-item prop="email">
          <el-input
            v-model="forgotForm.email"
            placeholder="请输入注册时使用的邮箱"
            prefix-icon="el-icon-message"
          ></el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            @click="handleForgotPassword"
            :loading="loading"
            class="forgot-button"
          >
            {{ loading ? '发送中...' : '发送重置链接' }}
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 发送成功提示 -->
      <div v-if="emailSent" class="success-message">
        <div class="success-icon">
          <i class="el-icon-circle-check"></i>
        </div>
        <h3>邮件已发送</h3>
        <p>我们已向 <strong>{{ forgotForm.email }}</strong> 发送了重置密码的邮件</p>
        <p class="help-text">请查收邮件并点击其中的链接来重置您的密码</p>
        <p class="help-text">如果您没有收到邮件，请检查垃圾邮件文件夹</p>
        
        <div class="resend-section">
          <el-button 
            type="text" 
            @click="resendEmail"
            :loading="resendLoading"
            class="resend-button"
          >
            {{ resendLoading ? '重新发送中...' : '重新发送邮件' }}
          </el-button>
        </div>
      </div>
      
      <div class="forgot-password-footer">
        <router-link to="/login" class="back-link">
          <i class="el-icon-arrow-left"></i>
          返回登录
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ForgotPassword',
  data() {
    return {
      forgotForm: {
        email: ''
      },
      forgotRules: {
        email: [
          { required: true, message: '请输入邮箱地址', trigger: 'blur' },
          { type: 'email', message: '请输入正确的邮箱地址', trigger: ['blur', 'change'] }
        ]
      },
      loading: false,
      emailSent: false,
      resendLoading: false
    }
  },
  methods: {
    async handleForgotPassword() {
      this.$refs.forgotForm.validate(async (valid) => {
        if (valid) {
          this.loading = true
          
          try {
            // 调用忘记密码API
            await this.$api.authAPI.forgotPassword(this.forgotForm.email)
            
            this.emailSent = true
            this.$message.success('重置密码邮件发送成功！')
            
          } catch (error) {
            console.error('发送重置邮件失败:', error)
            // 错误信息已由axios拦截器处理
          } finally {
            this.loading = false
          }
        } else {
          return false
        }
      })
    },
    
    async resendEmail() {
      this.resendLoading = true
      
      try {
        // 重新发送邮件
        await this.$api.authAPI.forgotPassword(this.forgotForm.email)
        this.$message.success('邮件重新发送成功！')
        
      } catch (error) {
        console.error('重新发送邮件失败:', error)
      } finally {
        this.resendLoading = false
      }
    }
  }
}
</script>

<style scoped>
.forgot-password-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.forgot-password-form {
  background: rgba(255, 255, 255, 0.95);
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 450px;
  backdrop-filter: blur(10px);
}

.forgot-password-header {
  text-align: center;
  margin-bottom: 30px;
}

.forgot-icon {
  font-size: 48px;
  color: #409EFF;
  margin-bottom: 15px;
}

.forgot-password-header h1 {
  color: #333;
  margin: 0 0 10px 0;
  font-size: 28px;
  font-weight: 600;
}

.forgot-password-header p {
  color: #666;
  margin: 0;
  font-size: 14px;
  line-height: 1.5;
}

.forgot-button {
  width: 100%;
  height: 45px;
  font-size: 16px;
  font-weight: 500;
}

.success-message {
  text-align: center;
  padding: 20px 0;
}

.success-icon {
  margin-bottom: 20px;
}

.success-icon i {
  font-size: 64px;
  color: #67C23A;
}

.success-message h3 {
  color: #333;
  margin: 0 0 15px 0;
  font-size: 24px;
  font-weight: 600;
}

.success-message p {
  color: #666;
  margin: 0 0 10px 0;
  font-size: 14px;
  line-height: 1.5;
}

.help-text {
  font-size: 12px !important;
  color: #999 !important;
}

.resend-section {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
}

.resend-button {
  color: #409EFF;
  font-size: 14px;
}

.resend-button:hover {
  text-decoration: underline;
}

.forgot-password-footer {
  text-align: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  color: #409EFF;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
}

.back-link:hover {
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

/* 响应式设计 */
@media (max-width: 480px) {
  .forgot-password-form {
    padding: 30px 20px;
  }
  
  .forgot-password-header h1 {
    font-size: 24px;
  }
  
  .forgot-icon {
    font-size: 40px;
  }
}
</style>