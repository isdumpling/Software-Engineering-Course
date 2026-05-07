from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Any, Dict, List, Optional

# 用户相关模式
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    security_question: Optional[str] = None
    security_answer: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    is_admin: bool = False
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# 密码重置相关模式
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    password: str

class SecurityQuestionRequest(BaseModel):
    email: EmailStr

class SecurityQuestionResponse(BaseModel):
    security_question: str

class VerifySecurityAnswerRequest(BaseModel):
    email: EmailStr
    security_answer: str

# 聊天相关模式
class ChatMessageCreate(BaseModel):
    session_id: str
    query: str
    course_id: str
    course_name: str

class ChatMessageResponse(BaseModel):
    role: str
    content: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

class ChatResponse(BaseModel):
    answer: str
    session_id: str
    sources: Optional[List[dict]] = None

class ChatSessionResponse(BaseModel):
    id: str
    course_id: str
    course_name: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    
    class Config:
        from_attributes = True

class ChatHistoryResponse(BaseModel):
    id: str
    course_id: str
    course_name: str
    title: str
    messages: List[ChatMessageResponse]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# 通用响应模式
class MessageResponse(BaseModel):
    message: str
    
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None

# 管理员接口模型
class AdminCourseStatus(BaseModel):
    course_id: str
    course_name: str
    doc_file: str
    doc_exists: bool
    doc_size: int
    vector_db_exists: bool
    vector_db_size: int
    document_count: int
    loaded: bool

class RetrievalTestRequest(BaseModel):
    course_id: str
    query: str
    top_k: int = 5

class RetrievalResultItem(BaseModel):
    content: str
    metadata: Dict[str, Any] = {}

class RetrievalTestResponse(BaseModel):
    success: bool
    course_id: str
    course_name: Optional[str] = None
    original_query: str
    optimized_query: str
    results: List[RetrievalResultItem] = []
    message: Optional[str] = None

class KnowledgeBuildTaskResponse(BaseModel):
    id: str
    course_id: str
    course_name: Optional[str] = None
    status: str
    source_file: Optional[str] = None
    vector_db_path: Optional[str] = None
    document_count: int = 0
    log: Optional[str] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True