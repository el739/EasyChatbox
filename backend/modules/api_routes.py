from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import List, Dict
from datetime import datetime
import os
import uuid
import base64
from .models import Message, ChatSession, SessionUpdate, ChatRequest
from .session_manager import (
    get_sessions, create_session, get_session, update_session, 
    delete_session, add_message_to_session, clear_session_messages,
    initialize_default_session
)
from .openai_client import call_openai_api
from .config import openai_clients, default_provider, default_model, providers, auth_enabled, auth_username, auth_password
import secrets

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

def encode_image_to_base64(image_path: str) -> str:
    """将图片文件编码为base64字符串"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def is_image_file(file_path: str) -> bool:
    """检查文件是否为图片"""
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp']
    _, ext = os.path.splitext(file_path)
    return ext.lower() in image_extensions

def setup_routes(app: FastAPI):
    """设置API路由"""
    
    # 确定是否需要认证依赖
    auth_dependency = Depends(authenticate) if auth_enabled else None
    
    @app.get("/", dependencies=[auth_dependency] if auth_enabled else [])
    async def root():
        return {"message": "EasyChatbox API"}

    @app.get("/sessions", dependencies=[auth_dependency] if auth_enabled else [])
    async def get_sessions_endpoint():
        """获取所有聊天会话"""
        return get_sessions()

    @app.post("/sessions", dependencies=[auth_dependency] if auth_enabled else [])
    async def create_session_endpoint(title: str = "新对话"):
        """创建新聊天会话"""
        return create_session(title)

    @app.get("/sessions/{session_id}", dependencies=[auth_dependency] if auth_enabled else [])
    async def get_session_endpoint(session_id: str):
        """获取特定聊天会话"""
        session = get_session(session_id)
        if session:
            return session
        return {"error": "会话未找到"}

    @app.put("/sessions/{session_id}", dependencies=[auth_dependency] if auth_enabled else [])
    async def update_session_endpoint(session_id: str, update: SessionUpdate):
        """更新会话配置"""
        session = update_session(
            session_id, 
            update.title, 
            update.model, 
            update.api_provider
        )
        if session:
            return session
        return {"error": "会话未找到"}

    @app.delete("/sessions/{session_id}", dependencies=[auth_dependency] if auth_enabled else [])
    async def delete_session_endpoint(session_id: str):
        """删除聊天会话"""
        if delete_session(session_id):
            return {"message": "会话已删除"}
        return {"error": "会话未找到"}

    @app.post("/sessions/{session_id}/messages", dependencies=[auth_dependency] if auth_enabled else [])
    async def add_message_endpoint(session_id: str, message: Message):
        """向会话添加消息"""
        updated_session = add_message_to_session(session_id, message)
        if updated_session:
            return updated_session
        return {"error": "会话未找到"}

    @app.put("/sessions/{session_id}/messages/{message_index}", dependencies=[auth_dependency] if auth_enabled else [])
    async def edit_message_endpoint(session_id: str, message_index: int, message: Message):
        """编辑会话中的消息"""
        from .session_manager import edit_message_in_session
        updated_session = edit_message_in_session(session_id, message_index, message)
        if updated_session:
            return updated_session
        return {"error": "会话或消息未找到"}

    @app.delete("/sessions/{session_id}/messages/{message_index}", dependencies=[auth_dependency] if auth_enabled else [])
    async def delete_message_endpoint(session_id: str, message_index: int):
        """删除会话中的消息"""
        from .session_manager import delete_message_from_session
        updated_session = delete_message_from_session(session_id, message_index)
        if updated_session:
            return updated_session
        return {"error": "会话或消息未找到"}

    @app.delete("/sessions/{session_id}/messages", dependencies=[auth_dependency] if auth_enabled else [])
    async def clear_messages_endpoint(session_id: str):
        """清空会话消息"""
        updated_session = clear_session_messages(session_id)
        if updated_session:
            return updated_session
        return {"error": "会话未找到"}

    @app.post("/chat", dependencies=[auth_dependency] if auth_enabled else [])
    async def chat_endpoint(chat_request: ChatRequest):
        """与LLM聊天（真实API调用）"""
        session_id = chat_request.session_id
        message = chat_request.message
        file_urls = chat_request.file_urls
        
        # 获取会话信息
        session = get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="会话未找到")
        
        # 添加用户消息
        user_message = Message(
            role="user",
            content=message,
            timestamp=datetime.now().isoformat(),
            file_urls=file_urls
        )
        session = add_message_to_session(session_id, user_message)
        
        # 准备消息历史用于API调用
        messages = []
        for msg in session.messages:
            # 如果消息有文件URL，需要特殊处理图片文件
            if msg.file_urls:
                # 创建包含文本和图片的内容数组
                content_parts = [{"type": "text", "text": msg.content}]
                
                # 处理每个上传的文件
                for file_url in msg.file_urls:
                    # 转换URL为本地文件路径
                    file_path = file_url.lstrip('/')
                    
                    # 检查文件是否存在且是图片
                    if os.path.exists(file_path) and is_image_file(file_path):
                        try:
                            # 将图片编码为base64
                            base64_image = encode_image_to_base64(file_path)
                            # 添加图片到内容数组
                            content_parts.append({
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            })
                        except Exception as e:
                            # 如果图片处理失败，添加错误信息到文本内容
                            content_parts[0]["text"] += f"\n[图片处理失败: {str(e)}]"
                    else:
                        # 对于非图片文件，添加文件信息到文本内容
                        content_parts[0]["text"] += f"\n\n[已上传文件]: {file_url}"
                
                # 添加消息到历史记录
                messages.append({
                    "role": msg.role,
                    "content": content_parts
                })
            else:
                # 没有文件的普通消息
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # 调用OpenAI API
        try:
            response_content = await call_openai_api(messages, session.model, session.api_provider)
            
            # 添加助手消息
            assistant_message = Message(
                role="assistant",
                content=response_content,
                timestamp=datetime.now().isoformat()
            )
            session = add_message_to_session(session_id, assistant_message)
            
            return {
                "session": session,
                "response": assistant_message
            }
        except Exception as e:
            # 如果API调用失败，添加错误消息
            error_message = Message(
                role="assistant",
                content=f"API调用失败: {str(e)}",
                timestamp=datetime.now().isoformat()
            )
            add_message_to_session(session_id, error_message)
            
            raise HTTPException(status_code=500, detail=f"API调用失败: {str(e)}")

    @app.get("/config", dependencies=[auth_dependency] if auth_enabled else [])
    async def get_config_endpoint():
        """获取配置信息"""
        # 根据实际配置返回可用的模型和提供商
        available_providers = []
        available_models = {}
        
        # 从配置文件中获取提供商和模型信息
        for provider in providers:
            name = provider.get("name")
            models = provider.get("models", [])
            available_providers.append(name)
            available_models[name] = models
        
        # 如果没有配置提供商，仍然返回默认选项
        if not available_providers:
            available_providers = [default_provider]
            available_models = {default_provider: [default_model] if default_model else ["gpt-3.5-turbo"]}
        
        return {
            "providers": available_providers,
            "models": available_models,
            "default_provider": default_provider,
            "default_model": default_model
        }

    @app.post("/upload", dependencies=[auth_dependency] if auth_enabled else [])
    async def upload_file_endpoint(file: UploadFile = File(...)):
        """上传文件"""
        # 确保上传目录存在
        upload_dir = "uploads"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        # 生成唯一文件名
        file_extension = os.path.splitext(file.filename)[1] if '.' in file.filename else ''
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 返回文件URL
        file_url = f"/{file_path.replace(os.sep, '/')}"
        return {"file_url": file_url}
