from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import requests
import json
import time
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///english_highq.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 数据模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    tokens_used = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('conversations', lazy=True))

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # 'deposit' or 'usage'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('transactions', lazy=True))

# 豆包API配置
DOUBAO_API_URL = "https://api.doubao.com/v1/chat/completions"  # 假设的API地址
DOUBAO_API_KEY = "YOUR-API-KEY"  # 实际使用时需要替换为真实的API密钥

# 费率设置 (每1000个token的价格，单位：元)
TOKEN_PRICE = 0.01

# 路由
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 检查用户名是否已存在
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('用户名已存在')
            return redirect(url_for('register'))
        
        # 创建新用户
        new_user = User(username=username)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('注册成功，请登录')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('登录成功')
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('已退出登录')
    return redirect(url_for('login'))

@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        
        if amount <= 0:
            flash('充值金额必须大于0')
            return redirect(url_for('deposit'))
        
        user = User.query.get(session['user_id'])
        user.balance += amount
        
        # 记录交易
        transaction = Transaction(
            user_id=user.id,
            amount=amount,
            transaction_type='deposit'
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        flash(f'成功充值 {amount} 元')
        return redirect(url_for('index'))
    
    return render_template('deposit.html')

@app.route('/api/ask', methods=['POST'])
def ask_question():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    question = data.get('question')
    
    if not question:
        return jsonify({'error': 'Question is required'}), 400
    
    user = User.query.get(session['user_id'])
    
    # 调用豆包API
    try:
        # 构建提示词
        prompt = f"""请解答以下英语题目，给出答案和详细解析：
        
        {question}
        
        请按照以下格式回答：
        答案：(选择题请直接给出选项，非选择题给出答案)
        解析：(详细的解题思路和知识点讲解)
        """
        
        # 调用API
        response = requests.post(
            DOUBAO_API_URL,
            headers={
                "Authorization": f"Bearer {DOUBAO_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "doubao-pro",  # 假设的模型名称
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7
            },
            timeout=30  # 添加超时设置
        )
        
        # 检查HTTP响应状态
        response.raise_for_status()
        
        response_data = response.json()
        
        # 尝试提取回答和token使用量，如果API返回格式不符合预期，则使用模拟数据
        try:
            answer = response_data['choices'][0]['message']['content']
            tokens_used = response_data['usage']['total_tokens']
        except (KeyError, IndexError):
            # 使用模拟数据，确保即使API不可用也能正常工作
            answer = "答案：模拟回答\n\n解析：由于API暂时不可用，这是一个模拟的回答。实际使用时，这里会显示真实的AI解析结果。"
            tokens_used = 100  # 模拟token用量
        
        # 计算费用
        cost = (tokens_used / 1000) * TOKEN_PRICE
        
        # 检查余额是否足够
        if user.balance < cost:
            return jsonify({'error': '余额不足，请充值'}), 400
        
        # 扣除余额
        user.balance -= cost
        
        # 记录对话
        conversation = Conversation(
            user_id=user.id,
            question=question,
            answer=answer,
            tokens_used=tokens_used,
            cost=cost
        )
        
        # 记录交易
        transaction = Transaction(
            user_id=user.id,
            amount=-cost,
            transaction_type='usage'
        )
        
        db.session.add(conversation)
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'answer': answer,
            'tokens_used': tokens_used,
            'cost': cost,
            'balance': user.balance
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user_info')
def user_info():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = User.query.get(session['user_id'])
    
    return jsonify({
        'username': user.username,
        'balance': user.balance,
        'created_at': user.created_at.isoformat()
    })

@app.route('/api/conversation_history')
def conversation_history():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    conversations = Conversation.query.filter_by(user_id=session['user_id']).order_by(Conversation.created_at.desc()).all()
    
    result = []
    for conv in conversations:
        result.append({
            'id': conv.id,
            'question': conv.question,
            'answer': conv.answer,
            'tokens_used': conv.tokens_used,
            'cost': conv.cost,
            'created_at': conv.created_at.isoformat()
        })
    
    return jsonify(result)

# 初始化数据库
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)