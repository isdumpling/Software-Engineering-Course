<template>
  <div class="fp-container">
    <div class="fp-box">
      <div class="fp-header">
        <i class="el-icon-key fp-icon"></i>
        <h1>找回您的密码</h1>
        <p v-if="!emailSent">请输入与您账户关联的电子邮箱地址</p>
      </div>
      
      <el-form 
        v-if="!emailSent"
        :model="forgotForm" 
        :rules="forgotRules" 
        ref="forgotForm" 
        label-width="0px"
        size="medium"
        class="fp-form"
      >
        <el-form-item prop="email">
          <el-input
            v-model="forgotForm.email"
            placeholder="电子邮箱"
            prefix-icon="el-icon-message"
            @keyup.enter.native="handleForgotPassword"
          ></el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            @click="handleForgotPassword"
            :loading="loading"
            class="fp-button"
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
        <p>我们已向 <strong>{{ forgotForm.email }}</strong> 发送了重置密码的邮件，请注意查收。</p>
        <p class="help-text">如果没有收到，请检查您的垃圾邮件文件夹。</p>
        
        <div class="resend-section">
          <el-button 
            type="text" 
            @click="resendEmail"
            :loading="resendLoading"
            :disabled="resendLoading"
            class="resend-button"
          >
            {{ resendLoading ? '正在重新发送...' : '重新发送邮件' }}
          </el-button>
        </div>
      </div>
      
      <div class="fp-footer">
        <router-link to="/login" class="back-link">
          <i class="el-icon-arrow-left"></i>
          <span>返回登录</span>
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
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap');

.fp-container {
  min-height: 100vh;
  background-color: #f0f2f5;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  font-family: 'Noto Sans SC', sans-serif;
}

.fp-box {
  background: #fff;
  padding: 40px 50px;
  border-radius: 10px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 480px;
  text-align: center;
}

.fp-header {
  margin-bottom: 30px;
}

.fp-icon {
  font-size: 48px;
  color: #5A8DFF;
  margin-bottom: 15px;
}

.fp-header h1 {
  color: #333;
  margin: 0 0 10px 0;
  font-size: 26px;
  font-weight: 700;
}

.fp-header p {
  color: #999;
  margin: 0;
  font-size: 14px;
  line-height: 1.5;
}

.fp-form {
  margin-top: 20px;
}

.fp-button {
  width: 100%;
  height: 45px;
  font-size: 16px;
  font-weight: 500;
  letter-spacing: 2px;
}

.success-message {
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
  font-size: 13px !important;
  color: #999 !important;
}

.resend-section {
  margin-top: 25px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.resend-button {
  color: #5A8DFF;
  font-size: 14px;
  font-weight: 500;
}

.resend-button:hover {
  color: #73a0ff;
}

.fp-footer {
  text-align: center;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #5A8DFF;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: color 0.3s;
}

.back-link:hover {
  color: #333;
}

/* Element UI 样式覆盖 */
.el-form-item {
  margin-bottom: 25px;
}

.el-input__inner {
  height: 48px;
  line-height: 48px;
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
  line-height: 48px;
  color: #999;
  left: 15px;
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

/* 响应式设计 */
@media (max-width: 480px) {
  .fp-box {
    padding: 30px 25px;
  }
  
  .fp-header h1 {
    font-size: 22px;
  }
  
  .fp-icon {
    font-size: 40px;
  }
}
</style>