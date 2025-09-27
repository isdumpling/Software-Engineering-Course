"""
火山引擎豆包AI服务集成 (已集成RAG功能)
"""
import asyncio
from typing import Optional, Dict, Any
from config import settings
import logging
from volcenginesdkarkruntime import Ark
import os # 导入 os 模块

# --- RAG 相关导入 ---
from langchain_community.vectorstores import Chroma
# 尝试使用新的HuggingFace嵌入
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)

# --- RAG 配置 (使用绝对路径) ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_DB_PATH = os.path.normpath(os.path.join(SCRIPT_DIR, 'chroma_db'))
# EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_MODEL_NAME = "BAAI/bge-large-zh-v1.5"


class DoubaoAIService:
    """火山引擎豆包AI服务 (集成RAG)"""
    
    def __init__(self):
        self.api_key = settings.ARK_API_KEY
        self.model = settings.DOUBAO_MODEL
        self.client = Ark(api_key=self.api_key)
        
        # 初始化RAG组件
        print("🧠 正在加载嵌入模型 (用于RAG)...")
        self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
        print("✅ 嵌入模型加载成功。")

        # --- 最终诊断日志 ---
        print(f"📂 当前工作目录 (CWD): {os.getcwd()}")
        print(f"💾 正在从绝对路径加载向量数据库: {CHROMA_DB_PATH}")
        
        if not os.path.exists(CHROMA_DB_PATH):
            print(f"❌ 错误：向量数据库路径不存在！请确认 '{CHROMA_DB_PATH}' 文件夹存在。")
            return

        self.vectordb = Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=self.embeddings)
        
        # 验证加载的文档数量
        try:
            doc_count = len(self.vectordb._collection.get()['documents'])
            print(f"📊 成功加载了 {doc_count} 个文档到向量数据库中。")
            if doc_count < 100:
                 print(f"⚠️ 警告：加载的文档数量 ({doc_count}) 过少，可能不是最新的数据库！")
        except Exception as e:
            print(f"❌ 验证文档数量时出错: {e}")

        self.retriever = self.vectordb.as_retriever(search_kwargs={"k": 5}) # k=3 表示检索最相关的3个文本块
        print("✅ 向量数据库加载成功。")

    def _optimize_query(self, query: str) -> str:
        """
        在检索前优化查询语句，提高命中率。
        """
        print(f"🔍 原始查询: '{query.strip()}'")
        
        # 定义关键词和对应的优化查询
        optimizations = {
            "生命周期": "软件开发生命周期 软件过程",
            "生存周期": "软件开发生命周期 软件过程",
            "开发阶段": "软件开发生命周期 开发阶段",
            "几个阶段": "软件开发生命周期 开发阶段",
            "开发过程": "软件开发生命周期 开发过程",
            "瀑布模型": "瀑布模型 软件开发模型",
            "需求分析": "需求分析 需求获取",
            "测试": "软件测试 测试方法",
        }
        
        # 移除换行符并转换为小写以便匹配
        normalized_query = query.strip().lower()
        
        for keyword, optimal_query in optimizations.items():
            if keyword in normalized_query:
                print(f"✨ 检测到关键词 '{keyword}'，优化查询为: '{optimal_query}'")
                return optimal_query
        
        print("... 未进行查询优化。")
        return query

    async def generate_response(self, query: str, course_id: str, course_name: str = "") -> str:
        """
        调用豆包AI生成回答 (使用RAG)
        """
        try:
            # 1. 优化查询
            optimized_query = self._optimize_query(query)
            
            # 2. 从向量数据库检索相关上下文
            print(f"🔍 正在使用优化后的查询检索相关上下文: '{optimized_query.strip()}'")
            retrieved_docs = self.retriever.invoke(optimized_query)
            
            if not retrieved_docs:
                print("⚠️ 未找到相关上下文，将直接使用原始问题。")
                context = "没有找到相关背景信息。"
            else:
                context = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])
                print(f"✅ 检索到 {len(retrieved_docs)} 条相关上下文。")
                
                # --- 新增的调试代码 ---
                print("\n" + "="*50)
                print("🔍 以下是检索到的上下文内容送入AI前的内容:")
                print(context)
                print("="*50 + "\n")
                # --- 调试代码结束 ---

            # 2. 构造增强的提示词
            # ai_service.py 中的 rag_prompt
            rag_prompt = f"""
            你是一位严格的课程助教，你的任务是 **只能** 根据下面提供的“书籍内容”来回答用户的问题。
            - **严格遵守**：完全依据提供的上下文进行回答，不要补充任何你自己的额外知识。
            - **如果内容相关**：请整合书籍内容，清晰地回答用户的问题。
            - **如果内容不相关**：请直接回答：“抱歉，我提供的书籍内容中没有找到关于‘{query}’的直接答案。” 不要尝试用通用知识回答。

            --- 书籍内容 ---
            {context}
            --- 书籍内容结束 ---

            用户问题: {query}
            """
            
            # 构造消息列表
            messages = [
                {
                    "role": "system",
                    "content": self._get_system_prompt(course_id, course_name) # 可以保留原有的系统提示
                },
                {
                    "role": "user", 
                    "content": rag_prompt # 使用增强后的提示词
                }
            ]
            
            # 3. 调用大语言模型
            print("💬 正在调用豆包AI生成回答...")
            loop = asyncio.get_event_loop()
            completion = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.model,
                    messages=messages
                )
            )
            
            if completion.choices and len(completion.choices) > 0:
                ai_response = completion.choices[0].message.content
                logger.info(f"AI回答生成成功，长度: {len(ai_response)}")
                return ai_response.strip()
            else:
                logger.error("豆包API响应格式错误：没有找到choices")
                return self._get_fallback_response(query, course_id)
                    
        except Exception as e:
            logger.error(f"调用豆包AI失败: {str(e)}")
            return self._get_fallback_response(query, course_id)
    
    # _get_system_prompt 和 _get_fallback_response 方法保持不变...
    def _get_system_prompt(self, course_id: str, course_name: str = "") -> str:
        # ... (此处代码与您原文件相同，无需改动)
        course_prompts = {
            "software-engineering": """你是一位专业的软件工程课程助教。你精通软件开发生命周期、需求分析、系统设计、编程实践、测试方法、项目管理等软件工程各个方面。请用专业、易懂的方式回答学生的问题，并提供实际的例子和最佳实践。""",
            
            "operating-system": """你是一位专业的操作系统课程助教。你精通进程管理、内存管理、文件系统、I/O管理、并发控制、死锁处理等操作系统核心概念。请用清晰的逻辑和实例来解释复杂的操作系统原理。""",
            
            "computer-network": """你是一位专业的计算机网络课程助教。你精通OSI七层模型、TCP/IP协议栈、网络安全、路由算法、网络设备等网络技术。请用深入浅出的方式解释网络概念，并结合实际网络场景。""",
            
            "data-structure": """你是一位专业的数据结构与算法课程助教。你精通各种数据结构（数组、链表、栈、队列、树、图等）和算法设计与分析。请提供清晰的实现思路和时间复杂度分析。""",
            
            "database": """你是一位专业的数据库系统课程助教。你精通关系数据库理论、SQL语言、数据库设计、事务处理、并发控制、查询优化等数据库技术。请结合具体的SQL示例和实际应用场景来解答。""",
            
            "compiler": """你是一位专业的编译原理课程助教。你精通词法分析、语法分析、语义分析、中间代码生成、代码优化、目标代码生成等编译技术。请用清晰的编译过程和实例来解释复杂的编译原理。"""
        }
        
        base_prompt = f"""你是一位经验丰富的{course_name or '计算机科学'}课程助教，致力于帮助学生理解和掌握课程内容。

请遵循以下原则：
1. 使用简洁明了的中文回答
2. 提供准确、专业的知识
3. 适当举例说明复杂概念
4. 鼓励学生深入思考
5. 如果问题超出课程范围，请温和地指出并引导回到相关主题

请始终保持耐心、专业和友好的态度。"""
        
        return course_prompts.get(course_id, base_prompt)

    def _get_fallback_response(self, query: str, course_id: str) -> str:
        # ... (此处代码与您原文件相同，无需改动)
        course_names = {
            "software-engineering": "软件工程",
            "operating-system": "操作系统", 
            "computer-network": "计算机网络",
            "data-structure": "数据结构",
            "database": "数据库系统",
            "compiler": "编译原理"
        }
        
        course_name = course_names.get(course_id, "该课程")
        
        return f"""抱歉，AI服务暂时不可用。关于"{query}"这个问题，这是{course_name}中的重要概念。

建议您：
1. 查阅教材相关章节
2. 参考课程PPT和讲义
3. 与同学讨论交流
4. 向任课老师请教

我稍后会恢复正常服务，届时可以为您提供更详细的解答。"""


# 创建全局AI服务实例
# ai_service = DoubaoAIService()

# 改为函数，以便在应用启动时调用
def get_ai_service():
    print("🚀 正在创建全新的AI服务实例...")
    return DoubaoAIService()

# 全局变量，但在启动时才初始化
ai_service = None