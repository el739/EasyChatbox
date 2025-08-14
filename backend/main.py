from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = FastAPI()

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 允许前端地址
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部
)

# 数据模型
class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: str

class ChatSession(BaseModel):
    id: str
    title: str
    messages: List[Message]
    created_at: str
    updated_at: str
    model: str = "gpt-3.5-turbo"
    api_provider: str = "openai"

class ChatConfig(BaseModel):
    api_key: str
    api_base: str
    model: str
    api_provider: str

class SessionUpdate(BaseModel):
    title: Optional[str] = None
    model: Optional[str] = None
    api_provider: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    session_id: str

# 简单的内存存储（生产环境应该使用数据库）
chat_sessions: Dict[str, ChatSession] = {}
current_session_id: Optional[str] = None

# 初始化默认会话
default_session = ChatSession(
    id="default",
    title="默认对话",
    messages=[],
    created_at=datetime.now().isoformat(),
    updated_at=datetime.now().isoformat()
)
chat_sessions[default_session.id] = default_session
current_session_id = default_session.id

# API路由
@app.get("/")
async def root():
    return {"message": "EasyChatbox API"}

@app.get("/sessions")
async def get_sessions():
    """获取所有聊天会话"""
    return list(chat_sessions.values())

@app.post("/sessions")
async def create_session(title: str = "新对话"):
    """创建新聊天会话"""
    session_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
    new_session = ChatSession(
        id=session_id,
        title=title,
        messages=[],
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )
    chat_sessions[session_id] = new_session
    return new_session

@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """获取特定聊天会话"""
    if session_id in chat_sessions:
        return chat_sessions[session_id]
    return {"error": "会话未找到"}

@app.put("/sessions/{session_id}")
async def update_session(session_id: str, update: SessionUpdate):
    """更新会话配置"""
    if session_id not in chat_sessions:
        return {"error": "会话未找到"}
    
    session = chat_sessions[session_id]
    if update.title is not None:
        session.title = update.title
    if update.model is not None:
        session.model = update.model
    if update.api_provider is not None:
        session.api_provider = update.api_provider
    session.updated_at = datetime.now().isoformat()
    
    return session

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """删除聊天会话"""
    if session_id in chat_sessions:
        del chat_sessions[session_id]
        return {"message": "会话已删除"}
    return {"error": "会话未找到"}

@app.post("/sessions/{session_id}/messages")
async def add_message(session_id: str, message: Message):
    """向会话添加消息"""
    if session_id in chat_sessions:
        chat_sessions[session_id].messages.append(message)
        chat_sessions[session_id].updated_at = datetime.now().isoformat()
        # 更新会话标题为第一条消息的前10个字符
        if len(chat_sessions[session_id].messages) == 1:
            chat_sessions[session_id].title = message.content[:10] + "..." if len(message.content) > 10 else message.content
        return chat_sessions[session_id]
    return {"error": "会话未找到"}

@app.delete("/sessions/{session_id}/messages")
async def clear_messages(session_id: str):
    """清空会话消息"""
    if session_id in chat_sessions:
        chat_sessions[session_id].messages = []
        chat_sessions[session_id].updated_at = datetime.now().isoformat()
        return chat_sessions[session_id]
    return {"error": "会话未找到"}

@app.post("/chat")
async def chat(chat_request: ChatRequest):
    """与LLM聊天（模拟响应）"""
    # 这里应该是调用实际的LLM API
    # 目前返回模拟响应
    session_id = chat_request.session_id
    message = chat_request.message
    
    if session_id not in chat_sessions:
        return {"error": "会话未找到"}
    
    # 添加用户消息
    user_message = Message(
        role="user",
        content=message,
        timestamp=datetime.now().isoformat()
    )
    chat_sessions[session_id].messages.append(user_message)
    
    # 模拟LLM响应
    assistant_message = Message(
        role="assistant",
        content=f"这是对 '{message}' 的模拟响应。在实际应用中，这里会调用真实的LLM API。",
        timestamp=datetime.now().isoformat()
    )
    chat_sessions[session_id].messages.append(assistant_message)
    chat_sessions[session_id].updated_at = datetime.now().isoformat()
    
    return {
        "session": chat_sessions[session_id],
        "response": assistant_message
    }

@app.get("/config")
async def get_config():
    """获取配置信息"""
    # 在实际应用中，这里应该从安全的地方获取配置
    return {
        "models": ["gpt-3.5-turbo", "gpt-4", "claude-2", "claude-3", "claude-3.5-sonnet"],
        "providers": ["openai", "anthropic", "azure", "google"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)