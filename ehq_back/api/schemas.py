from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# 用户相关模式
class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class User(UserBase):
    id: int
    balance: float
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# 令牌相关模式
class Token(BaseModel):
    access_token: str
    token_type: str


# 交易相关模式
class TransactionBase(BaseModel):
    amount: float
    transaction_type: str
    description: Optional[str] = None


class RechargeRequest(BaseModel):
    amount: float = Field(..., gt=0)
    description: Optional[str] = None


class Transaction(TransactionBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True


# API密钥相关模式
class ApiKeyBase(BaseModel):
    key_name: str
    provider: str
    is_active: bool = True
    priority: int = 1


class ApiKeyCreate(ApiKeyBase):
    api_key: str
    balance: float = 0.0


class ApiKeyUpdate(BaseModel):
    key_name: Optional[str] = None
    api_key: Optional[str] = None
    provider: Optional[str] = None
    balance: Optional[float] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None


class ApiKey(ApiKeyBase):
    id: int
    api_key: str
    balance: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# 问题记录相关模式
class QuestionRecordCreate(BaseModel):
    question: str


class QuestionResponse(BaseModel):
    id: int
    question: str
    answer: str
    tokens_used: int
    cost: float
    created_at: datetime


class QuestionRecord(QuestionResponse):
    user_id: int

    class Config:
        orm_mode = True