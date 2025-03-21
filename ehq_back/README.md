# English High Q 后端系统

这是一个英语题目解答系统的后端服务，提供用户认证、余额管理、英语题目处理和API池管理等功能。

## 功能特点

- 用户系统：注册、登录、余额管理
- API池管理：管理多个豆包API及其余额
- 英语题目处理：接收英语题目并调用合适的API
- 计费系统：根据token消耗扣除用户余额

## 技术栈

- FastAPI: 高性能的Python Web框架
- SQLAlchemy: ORM数据库操作
- JWT: 用户认证
- MySQL: 数据存储

## 安装与运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

编辑`.env`文件，设置数据库连接信息和JWT密钥：

```
# 数据库配置
DATABASE_URL=mysql+pymysql://username:password@localhost/ehq_db

# JWT配置
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 豆包API配置
DOUBAO_API_KEY_1=your_api_key_1
DOUBAO_API_KEY_2=your_api_key_2
```

### 3. 创建数据库

在MySQL中创建数据库：

```sql
CREATE DATABASE ehq_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. 运行服务

```bash
python main.py
```

服务将在 http://0.0.0.0:8000 上运行。

## API文档

启动服务后，访问 http://localhost:8000/docs 查看自动生成的API文档。

## 主要API端点

### 用户相关

- `POST /api/users/register`: 用户注册
- `POST /api/users/token`: 用户登录获取令牌
- `GET /api/users/me`: 获取当前用户信息
- `POST /api/users/recharge`: 用户充值
- `GET /api/users/balance`: 获取用户余额

### 问题相关

- `POST /api/questions/ask`: 提交英语题目
- `GET /api/questions/history`: 获取问题历史记录
- `GET /api/questions/record/{record_id}`: 获取特定问题记录

### 管理员相关

- `POST /api/admin/api-keys`: 创建API密钥
- `GET /api/admin/api-keys`: 获取所有API密钥
- `PUT /api/admin/api-keys/{api_key_id}`: 更新API密钥
- `GET /api/admin/users`: 获取所有用户
- `PUT /api/admin/users/{user_id}/activate`: 激活用户
- `PUT /api/admin/users/{user_id}/deactivate`: 停用用户

## 初始化管理员账户

系统启动后，需要手动将第一个注册的用户设置为管理员。可以通过直接修改数据库或使用以下SQL语句：

```sql
UPDATE users SET is_admin = 1 WHERE id = 1;
```

## 部署到AutoDL

1. 在AutoDL上创建一个实例
2. 上传项目文件
3. 安装依赖: `pip install -r requirements.txt`
4. 配置环境变量
5. 运行服务: `python main.py`

## 注意事项

- 在生产环境中，应该使用更安全的方式存储API密钥和JWT密钥
- 建议配置HTTPS以保护API通信安全
- 定期备份数据库