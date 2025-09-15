from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List
from database import get_db
from models import User, ChatSession, ChatMessage
from schemas import (
    ChatMessageCreate, ChatResponse, ChatHistoryResponse,
    ChatSessionResponse, MessageResponse
)
from auth import get_current_user
from ai_service import ai_service
import uuid
from datetime import datetime

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/", response_model=ChatResponse)
async def send_message(
    message: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """发送聊天消息"""
    try:
        # 检查或创建聊天会话
        session = db.query(ChatSession).filter(
            ChatSession.id == message.session_id,
            ChatSession.user_id == current_user.id
        ).first()
        
        if not session:
            # 创建新会话
            session = ChatSession(
                id=message.session_id,
                user_id=current_user.id,
                course_id=message.course_id,
                course_name=message.course_name,
                title=message.query[:50] + "..." if len(message.query) > 50 else message.query
            )
            db.add(session)
            db.flush()  # 确保session被创建但还未提交
        
        # 保存用户消息
        user_message = ChatMessage(
            session_id=message.session_id,
            user_id=current_user.id,
            role="user",
            content=message.query
        )
        db.add(user_message)
        
        # 调用豆包AI生成回答
        ai_response = await ai_service.generate_response(
            query=message.query,
            course_id=message.course_id,
            course_name=message.course_name
        )
        
        # 保存AI回答
        ai_message = ChatMessage(
            session_id=message.session_id,
            user_id=current_user.id,
            role="assistant",
            content=ai_response
        )
        db.add(ai_message)
        
        # 更新会话时间
        session.updated_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "answer": ai_response,
            "session_id": message.session_id,
            "sources": []  # 暂时为空，后续可以添加来源信息
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"发送消息失败: {str(e)}"
        )

# AI回答生成现在由 ai_service.py 中的豆包AI服务处理

@router.get("/history", response_model=List[ChatSessionResponse])
async def get_chat_history(
    course_id: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取聊天历史列表"""
    query = db.query(
        ChatSession,
        func.count(ChatMessage.id).label('message_count')
    ).join(
        ChatMessage, ChatSession.id == ChatMessage.session_id
    ).filter(
        ChatSession.user_id == current_user.id
    )
    
    if course_id:
        query = query.filter(ChatSession.course_id == course_id)
    
    sessions = query.group_by(ChatSession.id).order_by(desc(ChatSession.updated_at)).all()
    
    result = []
    for session, message_count in sessions:
        result.append({
            "id": session.id,
            "course_id": session.course_id,
            "course_name": session.course_name,
            "title": session.title,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "message_count": message_count
        })
    
    return result

@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_detail(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取具体聊天记录详情"""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="聊天记录不存在"
        )
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at).all()
    
    message_list = []
    for msg in messages:
        message_list.append({
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.created_at
        })
    
    return {
        "id": session.id,
        "course_id": session.course_id,
        "course_name": session.course_name,
        "title": session.title,
        "messages": message_list,
        "created_at": session.created_at,
        "updated_at": session.updated_at
    }

@router.delete("/history/{session_id}", response_model=MessageResponse)
async def delete_chat_history(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除聊天记录"""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="聊天记录不存在"
        )
    
    # 删除会话（级联删除相关消息）
    db.delete(session)
    db.commit()
    
    return {"message": "聊天记录删除成功"}

@router.get("/stats")
async def get_chat_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取聊天统计信息"""
    # 按课程统计会话数量
    stats = db.query(
        ChatSession.course_id,
        ChatSession.course_name,
        func.count(ChatSession.id).label('session_count'),
        func.count(ChatMessage.id).label('message_count')
    ).join(
        ChatMessage, ChatSession.id == ChatMessage.session_id
    ).filter(
        ChatSession.user_id == current_user.id
    ).group_by(
        ChatSession.course_id, ChatSession.course_name
    ).all()
    
    result = {}
    for stat in stats:
        result[stat.course_id] = {
            "course_name": stat.course_name,
            "session_count": stat.session_count,
            "message_count": stat.message_count
        }
    
    return result