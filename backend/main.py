from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from modules.config import openai_clients, auth_enabled, auth_username, auth_password
from modules.session_manager import initialize_default_session
from modules.api_routes import setup_routes
import secrets

app = FastAPI()

# 创建HTTP Basic认证实例
security = HTTPBasic()

# 认证依赖函数
def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    # 使用secrets.compare_digest来安全地比较用户名和密码
    correct_username = secrets.compare_digest(credentials.username, auth_username)
    correct_password = secrets.compare_digest(credentials.password, auth_password)
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

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

# 如果启用了认证，为所有路由添加依赖
if auth_enabled:
    # 为所有路由添加认证依赖
    for route in app.routes:
        if hasattr(route, "dependencies"):
            route.dependencies.append(Depends(authenticate))
        else:
            route.dependencies = [Depends(authenticate)]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
