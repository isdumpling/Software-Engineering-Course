"""
多课程支持的火山引擎豆包AI服务 (已集成RAG功能)
"""
import asyncio
import sys
import os
from typing import Optional, Dict, Any
from config import settings
import logging
from volcenginesdkarkruntime import Ark

#嵌入模型访问走镜像站

if "HF_ENDPOINT" not in os.environ:
    os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

from typing import Optional, Dict, Any

#

# --- RAG 相关导入 ---
from langchain_community.vectorstores import Chroma
# 尝试使用新的HuggingFace嵌入
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)

# --- 多课程RAG 配置 ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VECTOR_DB_BASE_PATH = os.path.normpath(os.path.join(SCRIPT_DIR, 'vector_databases'))
EMBEDDING_MODEL_NAME = "BAAI/bge-large-zh-v1.5"

# 导入课程配置
sys.path.append(os.path.join(SCRIPT_DIR, 'course_management'))
from course_config import COURSE_CONFIG

class DoubaoAIService:
    """多课程支持的火山引擎豆包AI服务 (集成RAG)"""
    
    def __init__(self):
        self.api_key = settings.ARK_API_KEY
        self.model = settings.DOUBAO_MODEL
        self.client = Ark(api_key=self.api_key)
        
        # 初始化RAG组件
        print("🧠 正在加载嵌入模型 (用于多课程RAG)...")
        self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
        print("✅ 嵌入模型加载成功。")

        # --- 多课程向量数据库初始化 ---
        print(f"📂 当前工作目录 (CWD): {os.getcwd()}")
        print(f"💾 正在从多课程向量数据库基础路径加载: {VECTOR_DB_BASE_PATH}")
        
        # 为每个课程加载独立的向量数据库
        self.course_vectordbs = {}
        self.course_retrievers = {}
        
        for course_id, course_config in COURSE_CONFIG.items():
            course_name = course_config["name"]
            db_path = os.path.join(VECTOR_DB_BASE_PATH, course_id)
            
            if os.path.exists(db_path):
                try:
                    print(f"📚 正在加载 {course_name} 的向量数据库...")
                    vectordb = Chroma(persist_directory=db_path, embedding_function=self.embeddings)
                    
                    # 验证加载的文档数量
                    doc_count = len(vectordb._collection.get()['documents'])
                    print(f"   ✅ {course_name}: {doc_count} 个文档")
                    
                    self.course_vectordbs[course_id] = vectordb
                    self.course_retrievers[course_id] = vectordb.as_retriever(search_kwargs={"k": 5})
                    
                except Exception as e:
                    print(f"   ❌ {course_name} 加载失败: {e}")
            else:
                print(f"   ⚠️ {course_name} 的向量数据库不存在: {db_path}")
        
        loaded_courses = len(self.course_vectordbs)
        total_courses = len(COURSE_CONFIG)
        print(f"📊 多课程向量数据库加载完成: {loaded_courses}/{total_courses} 门课程")

    def _optimize_query_for_course(self, query: str, course_id: str) -> str:
        """
        为特定课程优化查询语句
        """
        print(f"🔍 [{course_id}] 原始查询: '{query.strip()}'")
        
        # 获取课程特定的查询优化规则
        course_config = COURSE_CONFIG.get(course_id, {})
        optimizations = course_config.get("query_optimizations", {})
        
        # 移除换行符并转换为小写以便匹配
        normalized_query = query.strip().lower()
        
        for keyword, optimal_query in optimizations.items():
            if keyword in normalized_query:
                print(f"✨ [{course_id}] 检测到关键词 '{keyword}'，优化查询为: '{optimal_query}'")
                return optimal_query
        
        print(f"   [{course_id}] 未进行查询优化。")
        return query

    async def generate_response(self, query: str, course_id: str, course_name: str = "") -> str:
        """
        调用豆包AI生成回答 (使用多课程RAG)
        """
        try:
            # 检查课程是否支持
            if course_id not in self.course_retrievers:
                available_courses = list(self.course_retrievers.keys())
                if available_courses:
                    available_names = [COURSE_CONFIG[cid]["name"] for cid in available_courses]
                    return f"抱歉，{course_name} 课程的知识库尚未配置。当前支持的课程有：{', '.join(available_names)}。请联系管理员添加该课程的教材。"
                else:
                    return "抱歉，系统尚未配置任何课程的知识库。请联系管理员。"
            
            # 1. 使用课程特定的查询优化
            optimized_query = self._optimize_query_for_course(query, course_id)
            
            # 2. 从课程特定的向量数据库检索相关上下文
            print(f"🔍 [{course_id}] 正在使用优化后的查询检索相关上下文: '{optimized_query.strip()}'")
            retriever = self.course_retrievers[course_id]
            retrieved_docs = retriever.invoke(optimized_query)
            
            if not retrieved_docs:
                print(f"⚠️ [{course_id}] 未找到相关上下文，将直接使用原始问题。")
                context = "没有找到相关背景信息。"
            else:
                context = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])
                print(f"✅ [{course_id}] 检索到 {len(retrieved_docs)} 条相关上下文。")
                
                # 调试输出（可选）
                print("\n" + "="*50)
                print(f"🔍 [{course_id}] 以下是检索到的上下文内容送入AI前的内容:")
                print(context)
                print("="*50 + "\n")

            # 3. 构造增强的提示词


            # 你是一位严格的{course_name}课程助教，你的任务是 **只能** 根据下面提供的"课程教材内容"来回答用户的问题。
            # - **严格遵守**：完全依据提供的上下文进行回答，不要补充任何你自己的额外知识。
            # - **如果内容相关**：请整合教材内容，清晰地回答用户的问题。
            # - **如果内容不相关**：请直接回答："抱歉，我提供的{course_name}教材内容中没有找到关于'{query}'的直接答案。建议您查阅教材其他章节或咨询任课老师。"
            
            rag_prompt = f"""
            你是一位专业的{course_name}课程助教。请严格根据下面提供的教材内容来回答用户的问题。

            **回答要求**：
            1. 仔细阅读提供的教材内容，寻找与用户问题相关的信息
            2. 如果教材内容包含了相关概念、定义或解释，请整合这些信息来回答问题
            3. 用清晰、易懂的语言解释概念，可以适当举例说明
            4. 只有当教材内容完全没有涉及用户问题的主题时，才说找不到答案

            --- {course_name}教材内容 ---
            {context}
            --- 教材内容结束 ---

            用户问题: {query}

            请基于上述教材内容回答用户的问题。如果内容中包含了相关信息，请整合并清晰地解释。
            """
            
            # 构造消息列表
            messages = [
                {
                    "role": "system",
                    "content": self._get_system_prompt(course_id, course_name)
                },
                {
                    "role": "user", 
                    "content": rag_prompt
                }
            ]
            
            # 4. 调用大语言模型
            print(f"💬 [{course_id}] 正在调用豆包AI生成回答...")
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
                logger.info(f"[{course_id}] AI回答生成成功，长度: {len(ai_response)}")
                return ai_response.strip()
            else:
                logger.error(f"[{course_id}] 豆包API响应格式错误：没有找到choices")
                return self._get_fallback_response(query, course_id, course_name)
                    
        except Exception as e:
            logger.error(f"[{course_id}] 调用豆包AI失败: {str(e)}")
            return self._get_fallback_response(query, course_id, course_name)

    def _get_system_prompt(self, course_id: str, course_name: str = "") -> str:
        """获取课程特定的系统提示词"""
        course_prompts = {
            "software-engineering": """你是一位专业的软件工程课程助教。你精通软件开发生命周期、需求分析、系统设计、编程实践、测试方法、项目管理等软件工程各个方面。请用专业、易懂的方式回答学生的问题，并提供实际的例子和最佳实践。""",
            
            "operating-system": """你是一位专业的操作系统课程助教。你精通进程管理、内存管理、文件系统、I/O管理、并发控制、死锁处理等操作系统核心概念。请用清晰的逻辑和实例来解释复杂的操作系统原理。""",
            
            "computer-network": """你是一位专业的计算机网络课程助教。你精通OSI七层模型、TCP/IP协议栈、网络安全、路由算法、网络设备等网络技术。请用深入浅出的方式解释网络概念，并结合实际网络场景。""",
            
            "data-structure": """你是一位专业的数据结构与算法课程助教。你精通各种数据结构（数组、链表、栈、队列、树、图等）和算法设计与分析。请提供清晰的实现思路和时间复杂度分析。""",
            
            "database": """你是一位专业的数据库系统课程助教。你精通关系数据库理论、SQL语言、数据库设计、事务处理、并发控制、查询优化等数据库技术。请结合具体的SQL示例和实际应用场景来解答。""",
            
            "compiler": """你是一位专业的编译原理课程助教。你精通词法分析、语法分析、语义分析、中间代码生成、代码优化、目标代码生成等编译技术。请用清晰的编译过程和实例来解释复杂的编译原理。"""
        }
        
        specific_prompt = course_prompts.get(course_id, "")
        
        base_prompt = f"""你是一位经验丰富的{course_name or '计算机科学'}课程助教，致力于帮助学生理解和掌握课程内容。

{specific_prompt}

请遵循以下原则：
1. 使用简洁明了的中文回答
2. 提供准确、专业的知识
3. 适当举例说明复杂概念
4. 鼓励学生深入思考
5. 如果问题超出{course_name}课程范围，请温和地指出并引导回到相关主题

请始终保持耐心、专业和友好的态度。"""
        
        return base_prompt

    def _get_fallback_response(self, query: str, course_id: str, course_name: str) -> str:
        """获取失败时的后备回复"""
        return f"""抱歉，AI服务暂时不可用。关于"{query}"这个问题，这可能是{course_name}中的重要概念。

建议您：
1. 查阅{course_name}教材相关章节
2. 参考课程PPT和讲义
3. 与同学讨论交流
4. 向任课老师请教

我稍后会恢复正常服务，届时可以为您提供更详细的解答。"""

    def get_loaded_courses(self):
        """获取已加载的课程列表"""
        return {
            course_id: COURSE_CONFIG[course_id]["name"] 
            for course_id in self.course_retrievers.keys()
        }

    def get_course_stats(self):
        """获取各课程的统计信息"""
        stats = {}
        for course_id, vectordb in self.course_vectordbs.items():
            try:
                doc_count = len(vectordb._collection.get()['documents'])
                stats[course_id] = {
                    "name": COURSE_CONFIG[course_id]["name"],
                    "document_count": doc_count,
                    "status": "loaded"
                }
            except Exception as e:
                stats[course_id] = {
                    "name": COURSE_CONFIG[course_id]["name"],
                    "document_count": 0,
                    "status": f"error: {e}"
                }
        return stats

# 改为函数，以便在应用启动时调用
def get_ai_service():
    print("🚀 正在创建全新的多课程AI服务实例...")
    return DoubaoAIService()

# 全局变量，但在启动时才初始化
ai_service = None