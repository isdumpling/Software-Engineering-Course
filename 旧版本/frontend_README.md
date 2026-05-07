# 【旧版本】智能课程助教聊天机器人 - 前端

这是智能课程助教聊天机器人项目的前端部分，基于 Vue.js 2 和 Element UI 构建的现代化聊天界面。

## 📋 项目简介

本前端项目是软件工程课设的一部分，实现了一个智能课程助教聊天机器人的用户界面，支持：

- 🔐 用户登录注册
- 📚 多课程选择（操作系统、计算机网络、软件工程等）
- 💬 实时AI对话
- 📝 历史记录查看和继续对话
- 📱 响应式设计，支持移动端

## 🚀 快速开始

### 环境要求

- Node.js >= 12.0.0
- npm >= 6.0.0 或 yarn >= 1.0.0

### 安装依赖

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install
# 或使用 yarn
yarn install
```

### 开发环境运行

```bash
# 启动开发服务器
npm run serve
# 或
yarn serve
```

项目将在 `http://localhost:8080` 启动，并自动打开浏览器。

### 生产环境构建

```bash
# 构建生产版本
npm run build
# 或
yarn build
```

构建文件将输出到 `dist` 目录。

## 📁 项目结构

```
frontend/
├── public/
│   └── index.html          # 入口HTML文件
├── src/
│   ├── components/         # 通用组件（暂时未用到）
│   ├── router/
│   │   └── index.js       # 路由配置
│   ├── store/
│   │   └── index.js       # Vuex状态管理
│   ├── views/             # 页面组件
│   │   ├── Login.vue      # 登录页面
│   │   ├── Register.vue   # 注册页面
│   │   ├── Home.vue       # 主页选课
│   │   ├── Chat.vue       # AI对话页面
│   │   └── History.vue    # 历史记录页面
│   ├── App.vue            # 根组件
│   └── main.js            # 应用入口
├── package.json           # 依赖配置
├── vue.config.js          # Vue CLI配置
└── README.md              # 项目说明
```

## 🎯 主要功能

### 1. 用户认证
- 登录/注册界面，支持表单验证
- 用户状态持久化（localStorage）
- 路由守卫，确保访问权限

### 2. 课程选择
- 支持6门课程：软件工程、操作系统、计算机网络、数据结构、数据库系统、编译原理
- 显示每门课程的对话统计
- 美观的卡片式布局

### 3. AI对话
- 实时对话界面，类似微信聊天
- 支持快速问题选择
- 历史对话侧边栏
- 消息加载动画
- 自动滚动到底部

### 4. 历史记录
- 查看所有历史对话
- 按课程筛选和关键词搜索
- 分页显示
- 一键继续对话

## 🎨 UI设计特色

- **现代化设计**：采用Material Design风格，界面简洁美观
- **响应式布局**：适配桌面端和移动端
- **流畅动画**：页面切换和交互动画，提升用户体验
- **主题一致**：统一的色彩搭配和组件风格

## 📱 响应式设计

项目完全支持响应式设计：
- **桌面端**：完整功能展示
- **平板端**：优化布局适配
- **移动端**：触控友好的交互设计

## 🔌 API集成

前端通过axios与后端API通信：
- 基础URL配置：`http://localhost:8000`
- 自动请求/响应拦截
- 错误处理和用户提示

### API端点

- `POST /api/login` - 用户登录
- `POST /api/register` - 用户注册  
- `POST /api/chat` - 发送消息
- `POST /api/upload` - 上传文档

## 🛠️ 开发指南

### 添加新课程

在 `src/views/Home.vue` 的 `courses` 数组中添加新项目：

```javascript
{
  id: 'new-course',
  name: '新课程名称',
  description: '课程描述',
  icon: 'el-icon-xxxx',
  color: '#颜色代码'
}
```

### 修改UI主题

主要颜色变量在各组件的 `<style>` 部分定义，可以统一修改：
- 主色：`#409EFF`
- 成功：`#67C23A`
- 警告：`#E6A23C`
- 危险：`#F56C6C`

### 添加新功能页面

1. 在 `src/views/` 创建新的Vue组件
2. 在 `src/router/index.js` 添加路由配置
3. 如需要，在导航菜单中添加链接

## 🚀 部署说明

### 本地演示部署
```bash
npm run build
# 将dist目录内容部署到静态文件服务器
```

### 服务器部署
```bash
# 使用nginx部署
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
    }
}
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request来完善这个项目！

## 📞 支持

如果在使用过程中遇到问题，可以：
1. 查看控制台错误信息
2. 检查网络连接和API服务状态
3. 提交Issue描述问题

---

**注意**：这是课设项目的前端部分，需要配合后端API服务一起使用才能正常工作。