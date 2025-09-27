# 🚀 多课程知识库快速开始指南

## 📋 概述

本指南将帮助你快速将现有的单课程系统升级为支持多门课程的智能助教系统。

## 🎯 升级前后对比

### 升级前（单课程）
```
backend/
├── ai_service.py           # 单一软件工程课程
├── chroma_db/              # 软件工程向量数据库
└── knowledge_base/se.docx  # 软件工程教材
```

### 升级后（多课程）
```
backend/
├── ai_service.py              # 多课程AI服务
├── vector_databases/          # 各课程独立向量数据库
│   ├── software-engineering/
│   ├── operating-system/
│   ├── computer-network/
│   ├── data-structure/
│   ├── database/
│   └── compiler/
├── knowledge_base/            # 各课程教材文件
│   ├── software-engineering.docx
│   ├── operating-system.docx
│   ├── computer-network.docx
│   ├── data-structure.docx
│   ├── database.docx
│   └── compiler.docx
└── course_management/         # 课程管理工具
    ├── course_config.py
    ├── build_course_knowledge.py
    └── build_all_courses.py
```

---

## ⚡ 快速开始（5步完成）

### 第1步：系统迁移 🔄
```bash
cd backend
python migrate_to_multi_course.py
```

**预期输出**：
```
🚀 开始从单课程架构迁移到多课程架构
📦 备份原始ai_service.py...
🔄 替换ai_service.py为多课程版本...
📚 迁移现有的软件工程向量数据库...
✅ 迁移完成！
```

### 第2步：检查当前状态 📊
```bash
python demo_multi_course.py 课程状态
```

**预期输出**：
```
📖 软件工程:
   教材文件: ✅
   向量数据库: ✅
   文档数量: 300+
   
📖 操作系统:
   教材文件: ❌
   向量数据库: ❌
   
📖 计算机网络:
   教材文件: ❌
   向量数据库: ❌
...
```

### 第3步：准备其他课程教材 📚
将其他课程的教材文件放到正确位置：

```bash
# 示例：添加操作系统教材
cp /path/to/操作系统教材.docx knowledge_base/operating-system.docx

# 示例：添加计算机网络教材
cp /path/to/计算机网络教材.docx knowledge_base/computer-network.docx

# ... 添加其他课程教材
```

### 第4步：构建课程知识库 🏗️

**选项A：逐个构建（推荐新手）**
```bash
# 构建操作系统课程
python course_management/build_course_knowledge.py operating-system

# 构建计算机网络课程
python course_management/build_course_knowledge.py computer-network

# ... 依次构建其他课程
```

**选项B：批量构建（推荐有经验用户）**
```bash
# 批量构建所有准备好的课程
python course_management/build_all_courses.py
```

### 第5步：重启服务并测试 🚀
```bash
# 重启后端服务
python main.py
```

在前端测试不同课程的问答效果！

---

## 🎮 演示和测试

### 查看完整演示
```bash
python demo_multi_course.py
```

### 查看特定功能演示
```bash
python demo_multi_course.py 课程信息    # 查看支持的课程
python demo_multi_course.py 查询优化    # 查看查询优化规则
python demo_multi_course.py 文件结构    # 查看目录结构
python demo_multi_course.py 后续步骤    # 查看TODO清单
```

### 检查系统状态
```bash
python course_management/build_all_courses.py --status
```

---

## 🔧 常用管理命令

### 课程管理
```bash
# 单独重建某个课程
python course_management/build_course_knowledge.py software-engineering

# 检查所有课程状态
python course_management/build_all_courses.py --status

# 并行构建所有课程（速度更快）
python course_management/build_all_courses.py --parallel
```

### 故障排除
```bash
# 回滚到单课程模式
python migrate_to_multi_course.py --rollback

# 查看帮助
python migrate_to_multi_course.py --help
python course_management/build_all_courses.py --help
```

---

## 📝 配置文件说明

### 添加新课程支持

编辑 `course_management/course_config.py`：

```python
COURSE_CONFIG = {
    # ... 现有课程配置 ...
    
    "new-course": {
        "name": "新课程",
        "doc_file": "new-course.docx",
        "important_terms": [
            "重要概念1", "重要概念2", "..."
        ],
        "query_optimizations": {
            "用户常问词": "优化后的查询词"
        }
    }
}
```

### 自定义查询优化

为每门课程定制查询优化规则，提高检索准确性：

```python
"query_optimizations": {
    # 用户输入 -> 系统优化查询
    "生命周期": "软件开发生命周期 软件过程",
    "进程管理": "进程 进程调度 进程同步",
    "OSI模型": "OSI七层模型 网络协议栈"
}
```

---

## 🎯 性能优化建议

### 内存管理
- **单课程模式**: ~500MB 内存
- **多课程模式**: ~2GB 内存（6门课程）
- **建议**: 服务器至少4GB内存

### 启动时间
- **首次启动**: ~30秒（下载BGE模型）
- **后续启动**: ~10秒（加载已缓存的模型）

### 检索性能
- **单课程检索**: <200ms
- **多课程检索**: <300ms
- **并发支持**: 10+ 用户同时使用

---

## ⚠️ 注意事项

### 教材文件要求
- **格式**: 必须是 `.docx` 格式
- **编码**: UTF-8 编码
- **大小**: 建议 < 10MB
- **内容**: 结构化的教材内容

### 磁盘空间需求
| 课程数量 | 教材文件 | 向量数据库 | 总计 |
|---------|----------|------------|------|
| 1门课程 | ~2MB | ~50MB | ~52MB |
| 3门课程 | ~6MB | ~150MB | ~156MB |
| 6门课程 | ~12MB | ~300MB | ~312MB |

### 网络要求
- **首次运行**: 需要下载BGE模型（~500MB）
- **后续运行**: 无网络要求

---

## 🆘 故障排除

### 常见问题

**Q: 迁移失败，如何回滚？**
```bash
python migrate_to_multi_course.py --rollback
```

**Q: 某个课程检索效果差？**
1. 检查教材文件质量
2. 调整 `query_optimizations` 规则
3. 重新构建该课程：
```bash
python course_management/build_course_knowledge.py <course_id>
```

**Q: 内存不足怎么办？**
1. 减少同时加载的课程数量
2. 修改 `course_config.py`，只保留必要的课程
3. 升级服务器内存

**Q: 构建向量数据库失败？**
1. 检查教材文件是否存在
2. 确认文件格式为 `.docx`
3. 查看详细错误信息

### 获取帮助
```bash
# 查看各工具的帮助信息
python migrate_to_multi_course.py --help
python course_management/build_all_courses.py --help
python demo_multi_course.py 后续步骤
```

---

## 📈 升级路径

### 阶段1：基础升级（立即可用）
✅ 迁移现有软件工程数据  
✅ 升级AI服务支持多课程  
✅ 保持现有功能不变  

### 阶段2：逐步扩展（按需添加）
⏳ 添加操作系统课程  
⏳ 添加计算机网络课程  
⏳ 添加数据结构课程  

### 阶段3：全面部署（完整功能）
⏳ 支持所有6门课程  
⏳ 优化查询规则  
⏳ 性能调优  

---

**🎉 恭喜！你现在拥有了一个支持多门课程的智能助教系统！**

如有问题，请查看 `MULTI_COURSE_KNOWLEDGE_GUIDE.md` 获取更详细的信息。
