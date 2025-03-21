# 英语高分 - 智能解题系统

这是一个基于Flask的英语题目智能解答系统，通过接入豆包API，为用户提供英语题目的解答和详细解析。

## 功能特点

- 用户注册和登录系统
- 账户余额管理和充值功能
- 英语题目智能解答（基于豆包API）
- 按token用量计费
- 历史对话记录查询

## 技术栈

- 后端：Python Flask
- 数据库：SQLite（通过SQLAlchemy ORM）
- 前端：HTML, CSS, JavaScript, Bootstrap 5
- API集成：豆包API

## 安装和运行

1. 克隆项目到本地

2. 安装依赖包
   ```
   pip install -r requirements.txt
   ```

3. 配置豆包API密钥
   - 在`app.py`文件中找到`DOUBAO_API_KEY`变量
   - 将其值替换为您的豆包API密钥

4. 运行应用
   ```
   python app.py
   ```

5. 在浏览器中访问 http://localhost:5000

## 使用说明

1. 注册/登录账号
2. 充值账户余额
3. 在对话页面输入英语题目
4