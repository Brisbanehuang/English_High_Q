from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import requests
import json
import os
from dotenv import load_dotenv

from db.database import get_db
from db.models import User, ApiKey, QuestionRecord
from api.schemas import QuestionRecordCreate, QuestionResponse, QuestionRecord as QuestionRecordSchema
from api.auth import get_current_active_user

# 加载环境变量
load_dotenv()

router = APIRouter()


# 豆包API调用函数
def call_doubao_api(api_key: str, question: str):
    """调用豆包API处理英语题目"""
    # 这里是豆包API的调用实现
    # 根据实际的豆包API文档进行调用
    # 示例实现
    url = "https://api.doubao.com/v1/chat/completions"  # 替换为实际的豆包API地址
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 构建提示词，引导AI解答英语题目
    prompt = f"""请你作为一位专业的英语教师，解答以下英语题目。请提供详细的解析，包括语法分析、词汇解释和答案推导过程。

题目：{question}

请按照以下格式回答：
1. 题目分析
2. 解题思路
3. 详细解答
4. 正确答案
5. 相关知识点扩展"""
    
    payload = {
        "model": "doubao-model",  # 替换为实际的豆包模型名称
        "messages": [
            {"role": "system", "content": "你是一位专业的英语教师，擅长解答各类英语题目并提供详细解析。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        
        # 解析响应获取回答内容和token使用量
        answer = result["choices"][0]["message"]["content"]
        tokens_used = result["usage"]["total_tokens"]
        
        return {
            "answer": answer,
            "tokens_used": tokens_used,
            "success": True
        }
    except Exception as e:
        return {
            "answer": f"API调用失败: {str(e)}",
            "tokens_used": 0,
            "success": False
        }


# 获取可用的API密钥
def get_available_api_key(db: Session):
    """获取可用的API密钥，按优先级排序"""
    api_keys = db.query(ApiKey).filter(ApiKey.is_active == True).order_by(ApiKey.priority).all()
    if not api_keys:
        return None
    return api_keys[0]


# 计算费用
def calculate_cost(tokens_used: int):
    """根据使用的token数量计算费用"""
    # 这里可以根据实际的计费标准进行调整
    # 示例：每1000个token收费0.5元
    return (tokens_used / 1000) * 0.5


@router.post("/ask", response_model=QuestionResponse)
async def ask_question(question: QuestionRecordCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """处理用户提交的英语题目"""
    # 检查用户余额
    if current_user.balance <= 0:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Insufficient balance. Please recharge your account."
        )
    
    # 获取可用的API密钥
    api_key = get_available_api_key(db)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No available API key. Please try again later."
        )
    
    # 调用豆包API
    result = call_doubao_api(api_key.api_key, question.question)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to call API: {result['answer']}"
        )
    
    # 计算费用
    cost = calculate_cost(result["tokens_used"])
    
    # 检查用户余额是否足够
    if current_user.balance < cost:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Insufficient balance. Required: {cost}, Available: {current_user.balance}"
        )
    
    # 扣除用户余额
    current_user.balance -= cost
    db.commit()
    
    # 创建问题记录
    question_record = QuestionRecord(
        user_id=current_user.id,
        question=question.question,
        answer=result["answer"],
        tokens_used=result["tokens_used"],
        cost=cost,
        api_key_id=api_key.id
    )
    
    db.add(question_record)
    db.commit()
    db.refresh(question_record)
    
    # 返回结果
    return {
        "id": question_record.id,
        "question": question_record.question,
        "answer": question_record.answer,
        "tokens_used": question_record.tokens_used,
        "cost": question_record.cost,
        "created_at": question_record.created_at
    }


@router.get("/history", response_model=List[QuestionRecordSchema])
async def get_question_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """获取用户的问题历史记录"""
    records = db.query(QuestionRecord).filter(QuestionRecord.user_id == current_user.id).order_by(QuestionRecord.created_at.desc()).all()
    return records


@router.get("/record/{record_id}", response_model=QuestionRecordSchema)
async def get_question_record(record_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """获取特定问题记录的详细信息"""
    record = db.query(QuestionRecord).filter(QuestionRecord.id == record_id, QuestionRecord.user_id == current_user.id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question record not found"
        )
    return record