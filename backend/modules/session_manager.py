from typing import Dict, List
from datetime import datetime
from .models import ChatSession, Message

# 简单的内存存储（生产环境应该使用数据库）
chat_sessions: Dict[str, ChatSession] = {}
current_session_id: str = None

def initialize_default_session():
    """初始化默认会话"""
    global current_session_id
    default_session = ChatSession(
        id="default",
        title="默认对话",
        messages=[],
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )
    chat_sessions[default_session.id] = default_session
    current_session_id = default_session.id

def get_sessions() -> List[ChatSession]:
    """获取所有聊天会话"""
    return list(chat_sessions.values())

def create_session(title: str = "新对话") -> ChatSession:
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

def get_session(session_id: str) -> ChatSession:
    """获取特定聊天会话"""
    return chat_sessions.get(session_id)

def update_session(session_id: str, title: str = None, model: str = None, api_provider: str = None) -> ChatSession:
    """更新会话配置"""
    if session_id not in chat_sessions:
        return None
    
    session = chat_sessions[session_id]
    if title is not None:
        session.title = title
    if model is not None:
        session.model = model
    if api_provider is not None:
        session.api_provider = api_provider
    session.updated_at = datetime.now().isoformat()
    
    return session

def delete_session(session_id: str) -> bool:
    """删除聊天会话"""
    if session_id in chat_sessions:
        del chat_sessions[session_id]
        return True
    return False

def add_message_to_session(session_id: str, message: Message) -> ChatSession:
    """向会话添加消息"""
    if session_id in chat_sessions:
        chat_sessions[session_id].messages.append(message)
        chat_sessions[session_id].updated_at = datetime.now().isoformat()
        # 更新会话标题为第一条消息的前10个字符
        if len(chat_sessions[session_id].messages) == 1:
            chat_sessions[session_id].title = message.content[:10] + "..." if len(message.content) > 10 else message.content
        return chat_sessions[session_id]
    return None

def clear_session_messages(session_id: str) -> ChatSession:
    """清空会话消息"""
    if session_id in chat_sessions:
        chat_sessions[session_id].messages = []
        chat_sessions[session_id].updated_at = datetime.now().isoformat()
        return chat_sessions[session_id]
    return None
