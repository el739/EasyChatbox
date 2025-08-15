from typing import Dict, List
from datetime import datetime
from .models import ChatSession, Message
from .database import init_db, load_sessions_from_db, save_session_to_db, delete_session_from_db, add_message_to_db, clear_session_messages_from_db, update_session_in_db

# 全局变量存储会话
chat_sessions: Dict[str, ChatSession] = {}
current_session_id: str = None

def initialize_default_session():
    """初始化默认会话"""
    global current_session_id, chat_sessions
    
    # 初始化数据库
    init_db()
    
    # 从数据库加载现有会话
    chat_sessions = load_sessions_from_db()
    
    # 如果没有会话，创建默认会话
    if not chat_sessions:
        default_session = ChatSession(
            id="default",
            title="默认对话",
            messages=[],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        chat_sessions[default_session.id] = default_session
        save_session_to_db(default_session)
    
    # 设置当前会话ID为第一个会话
    if chat_sessions:
        current_session_id = next(iter(chat_sessions))

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
    save_session_to_db(new_session)
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
    
    # 更新数据库中的会话
    update_session_in_db(session_id, title, model, api_provider)
    
    return session

def delete_session(session_id: str) -> bool:
    """删除聊天会话"""
    if session_id in chat_sessions:
        del chat_sessions[session_id]
        # 从数据库中删除会话
        delete_session_from_db(session_id)
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
        
        # 将消息保存到数据库
        add_message_to_db(session_id, message)
        
        # 更新会话到数据库
        save_session_to_db(chat_sessions[session_id])
        
        return chat_sessions[session_id]
    return None

def clear_session_messages(session_id: str) -> ChatSession:
    """清空会话消息"""
    if session_id in chat_sessions:
        chat_sessions[session_id].messages = []
        chat_sessions[session_id].updated_at = datetime.now().isoformat()
        
        # 清空数据库中的消息
        clear_session_messages_from_db(session_id)
        
        # 更新会话到数据库
        save_session_to_db(chat_sessions[session_id])
        
        return chat_sessions[session_id]
    return None
