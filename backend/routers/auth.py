from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from database import get_db
from models import User, ResetToken
from schemas import (
    UserCreate, UserLogin, UserResponse, Token, MessageResponse,
    ForgotPasswordRequest, ResetPasswordRequest, SecurityQuestionRequest,
    SecurityQuestionResponse, VerifySecurityAnswerRequest
)
from config import settings
from auth import (
    get_password_hash, authenticate_user, create_access_token,
    generate_reset_token, get_current_user
)

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否已存在
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )
    
    # 创建新用户
    hashed_password = get_password_hash(user.password)
    hashed_security_answer = None
    if user.security_answer:
        hashed_security_answer = get_password_hash(user.security_answer.lower())
    
    db_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password,
        security_question=user.security_question,
        security_answer=hashed_security_answer,
        is_admin=user.username in settings.ADMIN_USERNAMES
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=Token)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    db_user = authenticate_user(db, user.username, user.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账户已被禁用"
        )
    
    access_token = create_access_token(data={"sub": db_user.username})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": db_user
    }

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user

@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """忘记密码 - 发送重置邮件"""
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        # 为了安全，即使邮箱不存在也返回成功消息
        return {"message": "如果邮箱存在，重置链接已发送"}
    
    # 删除该用户之前未使用的重置令牌
    db.query(ResetToken).filter(
        ResetToken.user_id == user.id,
        ResetToken.is_used == False
    ).delete()
    
    # 生成新的重置令牌
    token = generate_reset_token()
    expires_at = datetime.utcnow() + timedelta(minutes=30)  # 30分钟有效期
    
    reset_token = ResetToken(
        user_id=user.id,
        token=token,
        expires_at=expires_at
    )
    
    db.add(reset_token)
    db.commit()
    
    # TODO: 这里应该发送邮件
    # send_reset_email(user.email, token)
    
    print(f"重置令牌（开发用）: {token}")  # 开发环境使用，生产环境删除
    
    return {"message": "如果邮箱存在，重置链接已发送"}

@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """重置密码"""
    reset_token = db.query(ResetToken).filter(
        ResetToken.token == request.token,
        ResetToken.is_used == False,
        ResetToken.expires_at > datetime.utcnow()
    ).first()
    
    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="重置链接无效或已过期"
        )
    
    # 更新用户密码
    user = db.query(User).filter(User.id == reset_token.user_id).first()
    user.password = get_password_hash(request.password)
    
    # 标记令牌为已使用
    reset_token.is_used = True
    
    db.commit()
    
    return {"message": "密码重置成功"}

@router.post("/validate-reset-token", response_model=MessageResponse)
async def validate_reset_token(token: str, db: Session = Depends(get_db)):
    """验证重置令牌有效性"""
    reset_token = db.query(ResetToken).filter(
        ResetToken.token == token,
        ResetToken.is_used == False,
        ResetToken.expires_at > datetime.utcnow()
    ).first()
    
    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="重置链接无效或已过期"
        )
    
    return {"message": "令牌有效"}

@router.post("/security-question", response_model=SecurityQuestionResponse)
async def get_security_question(request: SecurityQuestionRequest, db: Session = Depends(get_db)):
    """获取用户安全问题"""
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not user.security_question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到安全问题"
        )
    
    return {"security_question": user.security_question}

@router.post("/verify-security-answer", response_model=MessageResponse)
async def verify_security_answer(request: VerifySecurityAnswerRequest, db: Session = Depends(get_db)):
    """验证安全问题答案"""
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not user.security_answer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="安全验证失败"
        )
    
    from auth import verify_password
    if not verify_password(request.security_answer.lower(), user.security_answer):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="安全答案错误"
        )
    
    return {"message": "安全验证通过"}