from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from db.models import User, ApiKey, QuestionRecord, Transaction
from api.schemas import ApiKeyCreate, ApiKey as ApiKeySchema, ApiKeyUpdate, User as UserSchema, QuestionRecord as QuestionRecordSchema
from api.auth import get_admin_user

router = APIRouter()


# API密钥管理
@router.post("/api-keys", response_model=ApiKeySchema)
async def create_api_key(api_key: ApiKeyCreate, db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    """创建新的API密钥"""
    db_api_key = ApiKey(
        key_name=api_key.key_name,
        api_key=api_key.api_key,
        provider=api_key.provider,
        balance=api_key.balance,
        is_active=api_key.is_active,
        priority=api_key.priority
    )
    
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    
    return db_api_key


@router.get("/api-keys", response_model=List[ApiKeySchema])
async def get_api_keys(db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    """获取所有API密钥"""
    api_keys = db.query(ApiKey).all()
    return api_keys


@router.get("/api-keys/{api_key_id}", response_model=ApiKeySchema)
async def get_api_key(api_key_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    """获取特定API密钥"""
    api_key = db.query(ApiKey).filter(ApiKey.id == api_key_id).first()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    return api_key


@router.put("/api-keys/{api_key_id}", response_model=ApiKeySchema)
async def update_api_key(api_key_id: int, api_key_update: ApiKeyUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    """更新API密钥信息"""
    db_api_key = db.query(ApiKey).filter(ApiKey.id == api_key_id).first()
    if not db_api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    # 更新字段
    update_data = api_key_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_api_key, key, value)
    
    db.commit()
    db.refresh(db_api_key)
    
    return db_api_key


@router.delete("/api-keys/{api_key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(api_key_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    """删除API密钥"""
    db_api_key = db.query(ApiKey).filter(ApiKey.id == api_key_id).first()
    if not db_api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    db.delete(db_api_key)
    db.commit()
    
    return {"status": "success"}


# 用户管理
@router.get("/users", response_model=List[UserSchema])
async def get_users(db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    """获取所有用户"""
    users = db.query(User).all()
    return users


@router.get("/users/{user_id}", response_model=UserSchema)
async def get_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    """获取特定用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/users/{user_id}/activate", response_model=UserSchema)
async def activate_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    """激活用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = True
    db.commit()
    db.refresh(user)
    
    return user


@router.put("/users/{user_id}/deactivate", response_model=UserSchema)
async def deactivate_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    """停用用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise