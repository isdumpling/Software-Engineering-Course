<template>
  <div class="rp-container">
    <div class="rp-box">
      <!-- Loading/Validating Token -->
      <div v-if="isValidToken === null" class="status-section">
        <div class="status-icon">
          <i class="el-icon-loading"></i>
        </div>
        <h2>正在验证链接...</h2>
        <p>请稍候，我们正在检查您的密码重置链接的有效性。</p>
      </div>

      <!-- 重置密码表单 -->
      <div v-if="!resetComplete && isValidToken === true" class="reset-form-section">
        <div class="rp-header">
          <i class="el-icon-refresh-left rp-icon"></i>
          <h1>设置新密码</h1>
          <p>为了保障您的账户安全，请设置一个强密码</p>
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
              placeholder="新密码"
              prefix-icon="el-icon-lock"
              show-password
            ></el-input>
          </el-form-item>
          
          <el-form-item prop="confirmPassword">
            <el-input
              v-model="resetForm.confirmPassword"
              type="password"
              placeholder="确认新密码"
              prefix-icon="el-icon-check"
              show-password
              @keyup.enter.native="handleResetPassword"
            ></el-input>
          </el-form-item>
          
          <el-form-item>
            <el-button 
              type="primary" 
              @click="handleResetPassword"
              :loading="loading"
              class="rp-button"
            >
              {{ loading ? '正在重置...' : '确认并重置密码' }}
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 重置成功 -->
      <div v-if="resetComplete" class="status-section">
        <div class="status-icon success">
          <i class="el-icon-circle-check"></i>
        </div>
        <h2>密码重置成功</h2>
        <p>您现在可以使用新密码登录您的账户了。</p>
        
        <div class="actions">
          <el-button type="primary" @click="goToLogin" class="login-button">
            立即登录
          </el-button>
        </div>
      </div>

      <!-- 无效或过期的令牌 -->
      <div v-if="isValidToken === false" class="status-section">
        <div class="status-icon error">
          <i class="el-icon-circle-close"></i>
        </div>
        <h2>链接无效或已过期</h2>
        <p>抱歉，此链接无法用于重置密码。请返回并重新申请。</p>
        
        <div class="actions">
          <el-button type="primary" @click="goToForgotPassword">
            重新申请
          </el-button>
          <el-button @click="goToLogin">
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
      isValidToken: null, // null: validating, true: valid, false: invalid
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
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap');

.rp-container {
  min-height: 100vh;
  background-color: #f0f2f5;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  font-family: 'Noto Sans SC', sans-serif;
}

.rp-box {
  background: #fff;
  padding: 40px 50px;
  border-radius: 10px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 480px;
  text-align: center;
}

.rp-header {
  margin-bottom: 30px;
}

.rp-icon {
  font-size: 48px;
  color: #5A8DFF;
  margin-bottom: 15px;
}

.rp-header h1 {
  color: #333;
  margin: 0 0 10px 0;
  font-size: 26px;
  font-weight: 700;
}

.rp-header p {
  color: #999;
  margin: 0;
  font-size: 14px;
}

.rp-button {
  width: 100%;
  height: 45px;
  font-size: 16px;
  font-weight: 500;
  letter-spacing: 1px;
}

/* 状态通用样式 */
.status-section {
  padding: 20px 0;
}

.status-icon {
  margin-bottom: 20px;
  font-size: 64px;
}
.status-icon .el-icon-loading {
  color: #5A8DFF;
}
.status-icon.success i {
  color: #67C23A;
}
.status-icon.error i {
  color: #F56C6C;
}

.status-section h2 {
  color: #333;
  margin: 0 0 15px 0;
  font-size: 24px;
  font-weight: 600;
}

.status-section p {
  color: #666;
  margin: 0 0 30px 0;
  font-size: 14px;
  line-height: 1.6;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 20px;
}

.actions .el-button {
  width: 140px;
  height: 42px;
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
</style>