from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from modules.config import openai_client
from modules.session_manager import initialize_default_session
from modules.api_routes import setup_routes

app = FastAPI()

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 允许前端地址
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部
)

# 初始化默认会话
initialize_default_session()

# 设置API路由
setup_routes(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
