from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from api.routers import users, admin, questions
from db.database import engine, Base
import uvicorn

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用
app = FastAPI(
    title="English High Q API",
    description="API for English question answering system",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(questions.router, prefix="/api/questions", tags=["questions"])


@app.get("/")
async def root():
    return {"message": "Welcome to English High Q API"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)