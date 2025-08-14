from fastapi import FastAPI, HTTPException
from typing import List, Dict
from datetime import datetime
from .models import Message, ChatSession, SessionUpdate, ChatRequest
from .session_manager import (
    get_sessions, create_session, get_session, update_session, 
    delete_session, add_message_to_session, clear_session_messages,
    initialize_default_session
)
from .openai_client import call_openai_api
from .config import openai_clients, default_provider, default_model, providers

def setup_routes(app: FastAPI):
    """设置API路由"""
    
    @app.get("/")
    async def root():
        return {"message": "EasyChatbox API"}

    @app.get("/sessions")
    async def get_sessions_endpoint():
        """获取所有聊天会话"""
        return get_sessions()

    @app.post("/sessions")
    async def create_session_endpoint(title: str = "新对话"):
        """创建新聊天会话"""
        return create_session(title)

    @app.get("/sessions/{session_id}")
    async def get_session_endpoint(session_id: str):
        """获取特定聊天会话"""
        session = get_session(session_id)
        if session:
            return session
        return {"error": "会话未找到"}

    @app.put("/sessions/{session_id}")
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

    @app.delete("/sessions/{session_id}")
    async def delete_session_endpoint(session_id: str):
        """删除聊天会话"""
        if delete_session(session_id):
            return {"message": "会话已删除"}
        return {"error": "会话未找到"}

    @app.post("/sessions/{session_id}/messages")
    async def add_message_endpoint(session_id: str, message: Message):
        """向会话添加消息"""
        updated_session = add_message_to_session(session_id, message)
        if updated_session:
            return updated_session
        return {"error": "会话未找到"}

    @app.delete("/sessions/{session_id}/messages")
    async def clear_messages_endpoint(session_id: str):
        """清空会话消息"""
        updated_session = clear_session_messages(session_id)
        if updated_session:
            return updated_session
        return {"error": "会话未找到"}

    @app.post("/chat")
    async def chat_endpoint(chat_request: ChatRequest):
        """与LLM聊天（真实API调用）"""
        session_id = chat_request.session_id
        message = chat_request.message
        
        # 获取会话信息
        session = get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="会话未找到")
        
        # 添加用户消息
        user_message = Message(
            role="user",
            content=message,
            timestamp=datetime.now().isoformat()
        )
        session = add_message_to_session(session_id, user_message)
        
        # 准备消息历史用于API调用
        messages = []
        for msg in session.messages:
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

    @app.get("/config")
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
