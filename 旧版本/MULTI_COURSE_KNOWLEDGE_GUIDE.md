# 【旧版本】📚 多课程知识库管理指南

## 🎯 支持的课程列表

根据 `ai_service.py` 中的课程配置，当前系统支持以下课程：

| 课程ID | 课程名称 | 教材文件路径 | 状态 |
|--------|----------|-------------|------|
| `software-engineering` | 软件工程 | `knowledge_base/software-engineering.docx` | ✅ 已配置 |
| `operating-system` | 操作系统 | `knowledge_base/operating-system.docx` | ⏳ 待添加 |
| `computer-network` | 计算机网络 | `knowledge_base/computer-network.docx` | ⏳ 待添加 |
| `data-structure` | 数据结构与算法 | `knowledge_base/data-structure.docx` | ⏳ 待添加 |
| `database` | 数据库系统 | `knowledge_base/database.docx` | ⏳ 待添加 |
| `compiler` | 编译原理 | `knowledge_base/compiler.docx` | ⏳ 待添加 |

---

## 🏗️ 多课程架构设计

### 方案选择

我们采用 **独立向量数据库** 方案，每个课程维护自己的向量数据库：

```
backend/
├── knowledge_base/                    # 原始教材文件
│   ├── software-engineering.docx     # 软件工程教材
│   ├── operating-system.docx         # 操作系统教材  
│   ├── computer-network.docx         # 计算机网络教材
│   ├── data-structure.docx           # 数据结构教材
│   ├── database.docx                 # 数据库教材
│   └── compiler.docx                 # 编译原理教材
├── vector_databases/                  # 向量数据库目录
│   ├── software-engineering/         # 软件工程向量DB
│   ├── operating-system/             # 操作系统向量DB
│   ├── computer-network/             # 计算机网络向量DB
│   ├── data-structure/               # 数据结构向量DB
│   ├── database/                     # 数据库向量DB
│   └── compiler/                     # 编译原理向量DB
└── course_management/                 # 课程管理脚本
    ├── build_course_knowledge.py     # 单课程知识库构建
    ├── build_all_courses.py          # 全部课程批量构建
    └── course_config.py              # 课程配置管理
```

### 优势分析
- ✅ **性能优异**: 每次查询只需搜索单个课程的向量数据库
- ✅ **维护方便**: 单独更新某门课程不影响其他课程
- ✅ **扩展容易**: 添加新课程只需增加新的数据库
- ✅ **存储高效**: 避免了跨课程的无关检索

---

## 🚀 快速开始：添加新课程

### 第一步：准备教材文件
```bash
# 将新课程的教材文件放到指定位置
cp 操作系统教材.docx backend/knowledge_base/operating-system.docx
cp 计算机网络教材.docx backend/knowledge_base/computer-network.docx
# ... 其他课程
```

### 第二步：运行批量构建脚本
```bash
cd backend
python course_management/build_all_courses.py
```

### 第三步：重启服务
```bash
python start.py
```

---

## 🔧 单课程更新

### 更新特定课程的知识库
```bash
# 更新操作系统课程
python course_management/build_course_knowledge.py operating-system

# 更新数据库课程  
python course_management/build_course_knowledge.py database
```

### 验证更新结果
```bash
# 检查特定课程的向量数据库
python -c "
from course_management.course_config import CourseManager
manager = CourseManager()
stats = manager.get_course_stats('operating-system')
print(f'操作系统课程: {stats}')
"
```

---

## 📖 课程专用查询优化

每个课程都有自己的专业术语，我们为每门课程定制了查询优化规则：

### 软件工程
```
"生命周期" → "软件开发生命周期 软件过程"
"开发阶段" → "软件开发生命周期 开发阶段"
"瀑布模型" → "瀑布模型 软件开发模型"
```

### 操作系统  
```
"进程管理" → "进程 进程调度 进程同步"
"内存管理" → "内存分配 内存回收 虚拟内存"
"文件系统" → "文件管理 目录结构 文件存储"
```

### 计算机网络
```
"OSI模型" → "OSI七层模型 网络协议栈"
"TCP协议" → "TCP协议 传输控制协议"
"路由算法" → "路由选择 路由协议"
```

---

## 🎯 高级功能

### 1. 跨课程概念关联
当某个概念在多门课程中都有涉及时，系统会：
- 优先搜索当前课程的知识库
- 如果未找到相关内容，提示用户该概念可能在其他课程中

### 2. 课程难度自适应
- **基础概念**: 提供详细解释和例子
- **高级概念**: 关联相关的基础知识点
- **跨学科概念**: 标明与其他课程的联系

### 3. 学习路径推荐
基于用户提问的概念，推荐相关的学习内容：
```
用户问: "什么是进程？"
系统答: "进程是程序的执行实例... 
📚 相关概念: 线程、进程调度、进程通信
📖 建议阅读: 操作系统第3章 - 进程管理"
```

---

## ⚙️ 技术实现细节

### AI服务改造
```python
class DoubaoAIService:
    def __init__(self):
        # 为每个课程加载独立的向量数据库
        self.course_vectordbs = {}
        self.course_retrievers = {}
        
        for course_id in SUPPORTED_COURSES:
            db_path = f"vector_databases/{course_id}"
            if os.path.exists(db_path):
                vectordb = Chroma(persist_directory=db_path, ...)
                self.course_vectordbs[course_id] = vectordb
                self.course_retrievers[course_id] = vectordb.as_retriever()
    
    async def generate_response(self, query, course_id, course_name):
        # 使用特定课程的检索器
        retriever = self.course_retrievers.get(course_id)
        if not retriever:
            return f"课程 {course_name} 的知识库尚未配置"
        
        # 使用课程专用的查询优化
        optimized_query = self._optimize_query_for_course(query, course_id)
        results = retriever.invoke(optimized_query)
        # ...
```

### 课程配置管理
```python
# course_management/course_config.py
COURSE_CONFIG = {
    "software-engineering": {
        "name": "软件工程",
        "doc_file": "software-engineering.docx",
        "important_terms": ["生命周期", "瀑布模型", "软件危机"],
        "query_optimizations": {
            "生命周期": "软件开发生命周期 软件过程"
        }
    },
    "operating-system": {
        "name": "操作系统", 
        "doc_file": "operating-system.docx",
        "important_terms": ["进程", "线程", "内存管理", "文件系统"],
        "query_optimizations": {
            "进程管理": "进程 进程调度 进程同步"
        }
    }
    # ... 其他课程配置
}
```

---

## 📊 存储和性能

### 预计存储需求
| 课程 | 教材大小 | 向量数据库大小 | 文档数量 |
|------|----------|----------------|----------|
| 软件工程 | ~2MB | ~50MB | ~300 |
| 操作系统 | ~3MB | ~70MB | ~400 |
| 计算机网络 | ~2.5MB | ~60MB | ~350 |
| **总计** | **~15MB** | **~350MB** | **~2000** |

### 性能指标
- **检索延迟**: <500ms (单课程)
- **内存占用**: ~2GB (全部课程加载)
- **启动时间**: ~30s (首次加载所有模型)

---

## 🔍 故障排除

### 问题1: 某课程知识库未加载
**症状**: 返回 "课程XX的知识库尚未配置"

**解决方法**:
```bash
# 检查教材文件是否存在
ls knowledge_base/课程ID.docx

# 重新构建该课程知识库
python course_management/build_course_knowledge.py 课程ID
```

### 问题2: 跨课程概念混淆
**症状**: 在A课程中询问B课程的概念，返回不相关答案

**解决方法**: 在课程配置中添加跨课程概念映射
```python
CROSS_COURSE_CONCEPTS = {
    "进程": ["operating-system", "software-engineering"],  # 进程概念同时存在于OS和SE中
    "数据结构": ["data-structure", "database"]           # 数据结构在多门课程中都有
}
```

### 问题3: 某课程检索效果差
**解决方法**: 
1. 检查该课程的 `important_terms` 配置
2. 添加更多的 `query_optimizations` 规则
3. 重新运行 `build_course_knowledge.py`

---

## 📝 维护清单

### 每学期开始
- [ ] 检查是否有新版本教材需要更新
- [ ] 运行 `build_all_courses.py` 重新构建所有课程
- [ ] 测试每门课程的典型问题

### 日常维护
- [ ] 监控各课程的查询成功率
- [ ] 根据用户反馈优化查询规则
- [ ] 定期备份 `vector_databases/` 目录

### 新课程上线
- [ ] 添加课程到 `COURSE_CONFIG`
- [ ] 准备教材文件
- [ ] 配置重要术语和查询优化
- [ ] 运行构建脚本并测试

---

**更新记录**:
- v1.0: 单课程架构（仅软件工程）
- v2.0: 多课程架构设计
- v2.1: 添加跨课程概念关联
