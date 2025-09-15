from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional

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