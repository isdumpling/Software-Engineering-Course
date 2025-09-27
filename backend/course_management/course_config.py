#!/usr/bin/env python3
"""
多课程配置管理
"""
import os

# 支持的课程配置
COURSE_CONFIG = {
    "software-engineering": {
        "name": "软件工程",
        "doc_file": "software-engineering.docx",
        "important_terms": [
            "两次飞跃", "质的飞跃", "认识飞跃",
            "瀑布模型", "螺旋模型", "增量模型", "原型模型",
            "软件危机", "软件工程", "软件生存周期", "软件生命周期",
            "需求分析", "系统设计", "详细设计", "编码实现", "软件测试",
            "面向对象", "OOA", "OOD", "UML", "用例图", "类图",
            "黑盒测试", "白盒测试", "单元测试", "集成测试", "系统测试",
            "软件维护", "软件质量", "软件可靠性", "软件复用"
        ],
        "query_optimizations": {
            "生命周期": "软件开发生命周期 软件过程",
            "生存周期": "软件开发生命周期 软件过程",
            "开发阶段": "软件开发生命周期 开发阶段",
            "几个阶段": "软件开发生命周期 开发阶段",
            "开发过程": "软件开发生命周期 开发过程",
            "瀑布模型": "瀑布模型 软件开发模型",
            "需求分析": "需求分析 需求获取",
            "测试": "软件测试 测试方法",
        }
    },
    
    "operating-system": {
        "name": "操作系统",
        "doc_file": "operating-system.docx",
        "important_terms": [
            "进程", "线程", "进程调度", "进程同步", "进程通信",
            "内存管理", "虚拟内存", "分页", "分段", "内存分配",
            "文件系统", "文件管理", "目录结构", "文件存储",
            "死锁", "银行家算法", "资源分配", "并发控制",
            "中断", "系统调用", "内核", "用户态", "核心态",
            "磁盘调度", "I/O管理", "设备管理", "缓冲区"
        ],
        "query_optimizations": {
            "进程管理": "进程 进程调度 进程同步",
            "内存管理": "内存分配 内存回收 虚拟内存",
            "文件系统": "文件管理 目录结构 文件存储",
            "死锁": "死锁检测 死锁预防 银行家算法",
            "调度算法": "进程调度 CPU调度 调度策略",
            "同步机制": "进程同步 信号量 互斥锁",
            "IO": "输入输出 IO设备 IO控制器",
            "输入输出": "IO设备 IO控制器 IO管理",
            "设备管理": "IO设备 设备控制器 设备驱动",
            "中断": "中断处理 中断机制 系统调用"
        }
    },
    
    "computer-network": {
        "name": "计算机网络",
        "doc_file": "computer-network.docx", 
        "important_terms": [
            "OSI模型", "TCP/IP协议", "网络协议栈",
            "TCP协议", "UDP协议", "HTTP协议", "FTP协议",
            "路由算法", "路由协议", "IP地址", "子网掩码",
            "以太网", "局域网", "广域网", "因特网",
            "数据链路层", "网络层", "传输层", "应用层",
            "交换机", "路由器", "网关", "防火墙",
            "网络安全", "加密", "数字签名", "SSL"
        ],
        "query_optimizations": {
            "OSI模型": "OSI七层模型 网络协议栈",
            "TCP协议": "TCP协议 传输控制协议",
            "路由算法": "路由选择 路由协议",
            "网络层": "网络层 IP协议 路由",
            "数据链路层": "数据链路层 以太网 MAC地址",
            "网络安全": "网络安全 加密 防火墙"
        }
    },
    
    "data-structure": {
        "name": "数据结构与算法",
        "doc_file": "data-structure.docx",
        "important_terms": [
            "数据结构", "算法", "时间复杂度", "空间复杂度",
            "线性表", "链表", "栈", "队列", "数组",
            "二叉树", "平衡树", "B树", "红黑树", "堆",
            "图", "图遍历", "深度优先", "广度优先",
            "排序算法", "查找算法", "哈希表", "散列",
            "动态规划", "贪心算法", "分治算法", "回溯算法"
        ],
        "query_optimizations": {
            "时间复杂度": "算法复杂度 时间复杂度 大O表示法",
            "排序": "排序算法 冒泡排序 快速排序",
            "查找": "查找算法 二分查找 哈希查找",
            "树结构": "二叉树 平衡树 树的遍历",
            "图算法": "图遍历 最短路径 最小生成树"
        }
    },
    
    "database": {
        "name": "数据库系统",
        "doc_file": "database.docx",
        "important_terms": [
            "关系数据库", "SQL", "数据库设计", "范式",
            "实体关系模型", "ER图", "关系模型", "关系代数",
            "事务", "ACID", "并发控制", "锁机制",
            "索引", "B+树", "哈希索引", "查询优化",
            "数据仓库", "OLAP", "OLTP", "数据挖掘",
            "备份恢复", "数据安全", "访问控制"
        ],
        "query_optimizations": {
            "关系数据库": "关系模型 关系数据库 SQL",
            "数据库设计": "ER图 范式 数据库设计",
            "事务管理": "事务 ACID 并发控制",
            "查询优化": "SQL优化 索引 查询计划",
            "并发控制": "锁机制 死锁 事务隔离"
        }
    },
    
    "compiler": {
        "name": "编译原理", 
        "doc_file": "compiler.docx",
        "important_terms": [
            "词法分析", "语法分析", "语义分析", "代码生成",
            "编译器", "解释器", "词法单元", "语法树",
            "文法", "上下文无关文法", "LL分析", "LR分析",
            "符号表", "作用域", "类型检查", "错误处理",
            "中间代码", "目标代码", "代码优化", "寄存器分配"
        ],
        "query_optimizations": {
            "词法分析": "词法分析器 词法单元 正则表达式",
            "语法分析": "语法分析器 语法树 文法",
            "语义分析": "语义分析 类型检查 符号表",
            "代码生成": "目标代码 代码优化 寄存器分配"
        }
    }
}

# 跨课程概念映射
CROSS_COURSE_CONCEPTS = {
    "进程": ["operating-system", "software-engineering"],
    "数据结构": ["data-structure", "database", "compiler"],
    "算法": ["data-structure", "operating-system", "compiler"],
    "网络协议": ["computer-network", "operating-system"],
    "安全": ["computer-network", "database", "operating-system"],
    "优化": ["compiler", "database", "data-structure"]
}

class CourseManager:
    """课程管理器"""
    
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.knowledge_base_dir = os.path.join(self.base_dir, "knowledge_base")
        self.vector_db_dir = os.path.join(self.base_dir, "vector_databases")
    
    def get_all_courses(self):
        """获取所有支持的课程"""
        return list(COURSE_CONFIG.keys())
    
    def get_course_config(self, course_id):
        """获取指定课程的配置"""
        return COURSE_CONFIG.get(course_id)
    
    def get_course_doc_path(self, course_id):
        """获取课程教材文件路径"""
        config = self.get_course_config(course_id)
        if not config:
            return None
        return os.path.join(self.knowledge_base_dir, config["doc_file"])
    
    def get_course_vector_db_path(self, course_id):
        """获取课程向量数据库路径"""
        return os.path.join(self.vector_db_dir, course_id)
    
    def course_doc_exists(self, course_id):
        """检查课程教材文件是否存在"""
        doc_path = self.get_course_doc_path(course_id)
        return doc_path and os.path.exists(doc_path)
    
    def course_vector_db_exists(self, course_id):
        """检查课程向量数据库是否存在"""
        db_path = self.get_course_vector_db_path(course_id)
        return os.path.exists(db_path)
    
    def get_course_stats(self, course_id):
        """获取课程统计信息"""
        stats = {
            "course_id": course_id,
            "course_name": COURSE_CONFIG.get(course_id, {}).get("name", "未知"),
            "doc_exists": self.course_doc_exists(course_id),
            "vector_db_exists": self.course_vector_db_exists(course_id),
            "doc_size": 0,
            "vector_db_size": 0,
            "document_count": 0
        }
        
        # 获取教材文件大小
        doc_path = self.get_course_doc_path(course_id)
        if doc_path and os.path.exists(doc_path):
            stats["doc_size"] = os.path.getsize(doc_path)
        
        # 获取向量数据库大小和文档数量
        db_path = self.get_course_vector_db_path(course_id)
        if os.path.exists(db_path):
            # 计算目录大小
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(db_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(filepath)
            stats["vector_db_size"] = total_size
            
            # 尝试获取文档数量
            try:
                from langchain_community.vectorstores import Chroma
                try:
                    from langchain_huggingface import HuggingFaceEmbeddings
                except ImportError:
                    from langchain_community.embeddings import HuggingFaceEmbeddings
                
                embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-large-zh-v1.5")
                vectordb = Chroma(persist_directory=db_path, embedding_function=embeddings)
                stats["document_count"] = len(vectordb._collection.get()['documents'])
            except Exception as e:
                stats["document_count"] = -1  # 表示无法获取
        
        return stats
    
    def list_all_course_stats(self):
        """列出所有课程的统计信息"""
        all_stats = {}
        for course_id in self.get_all_courses():
            all_stats[course_id] = self.get_course_stats(course_id)
        return all_stats
