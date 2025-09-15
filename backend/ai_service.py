"""
火山引擎豆包AI服务集成
"""
import asyncio
from typing import Optional, Dict, Any
from config import settings
import logging
from volcenginesdkarkruntime import Ark

logger = logging.getLogger(__name__)

class DoubaoAIService:
    """火山引擎豆包AI服务"""
    
    def __init__(self):
        self.api_key = settings.ARK_API_KEY
        self.model = settings.DOUBAO_MODEL
        self.client = Ark(api_key=self.api_key)
        
    async def generate_response(self, query: str, course_id: str, course_name: str = "") -> str:
        """
        调用豆包AI生成回答
        
        Args:
            query: 用户问题
            course_id: 课程ID
            course_name: 课程名称
            
        Returns:
            AI生成的回答文本
        """
        try:
            # 构造课程相关的系统提示
            system_prompt = self._get_system_prompt(course_id, course_name)
            
            # 构造消息列表
            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user", 
                    "content": query
                }
            ]
            
            # 使用同步调用（在线程池中执行以避免阻塞）
            loop = asyncio.get_event_loop()
            completion = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.model,
                    messages=messages
                )
            )
            
            # 提取AI回答
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
    
    def _get_system_prompt(self, course_id: str, course_name: str = "") -> str:
        """根据课程获取系统提示词"""
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
        """当AI调用失败时的备用回答"""
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
ai_service = DoubaoAIService()