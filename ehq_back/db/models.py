from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
from passlib.context import CryptContext

# 密码哈希工具
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(100))
    balance = Column(Float, default=0.0)  # 用户余额
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)  # 管理员标志
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    transactions = relationship("Transaction", back_populates="user")
    question_records = relationship("QuestionRecord", back_populates="user")

    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float)  # 交易金额
    transaction_type = Column(String(20))  # 'deposit' 或 'consumption'
    description = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    user = relationship("User", back_populates="transactions")


class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key_name = Column(String(50))  # API密钥名称
    api_key = Column(String(200))  # 实际API密钥
    provider = Column(String(50))  # API提供商，如'doubao'
    balance = Column(Float, default=0.0)  # API余额
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=1)  # 优先级，数字越小优先级越高
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class QuestionRecord(Base):
    __tablename__ = "question_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    question = Column(Text)  # 用户提问的英语题目
    answer = Column(Text)  # AI回答内容
    tokens_used = Column(Integer)  # 使用的token数量
    cost = Column(Float)  # 消费金额
    api_key_id = Column(Integer, ForeignKey("api_keys.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    user = relationship("User", back_populates="question_records")
    api_key = relationship("ApiKey")