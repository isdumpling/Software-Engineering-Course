from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)  # 存储加密后的密码
    
    # 安全问题和答案
    security_question = Column(String(255), nullable=True)
    security_answer = Column(String(255), nullable=True)  # 存储加密后的安全答案
    
    # 用户状态
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联聊天记录
    chat_sessions = relationship("ChatSession", back_populates="user")
    chat_messages = relationship("ChatMessage", back_populates="user")

class ChatSession(Base):
    """聊天会话表"""
    __tablename__ = "chat_sessions"
    
    id = Column(String(50), primary_key=True, index=True)  # 前端生成的session_id
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(String(50), nullable=False)  # 课程ID，如'software-engineering'
    course_name = Column(String(100), nullable=False)  # 课程名称
    title = Column(String(255), nullable=False)  # 会话标题
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联用户和消息
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    """聊天消息表"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), ForeignKey("chat_sessions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    role = Column(String(20), nullable=False)  # 'user' 或 'assistant'
    content = Column(Text, nullable=False)  # 消息内容
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关联会话和用户
    session = relationship("ChatSession", back_populates="messages")
    user = relationship("User", back_populates="chat_messages")

class ResetToken(Base):
    """密码重置令牌表"""
    __tablename__ = "reset_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_used = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关联用户
    user = relationship("User")