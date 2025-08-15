import sqlite3
import os
from typing import List, Optional
from datetime import datetime
from .models import ChatSession, Message

# 数据库文件路径
DB_PATH = "sessions.db"

def init_db():
    """初始化数据库，创建必要的表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建会话表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            model TEXT DEFAULT 'gpt-4o',
            api_provider TEXT DEFAULT 'OpenAI'
        )
    ''')
    
    # 创建消息表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
        )
    ''')
    
    # 创建索引以提高查询性能
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_messages_session_id 
        ON messages (session_id)
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
    return conn

def load_sessions_from_db() -> dict:
    """从数据库加载所有会话"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 获取所有会话
    cursor.execute("SELECT * FROM sessions")
    session_rows = cursor.fetchall()
    
    sessions = {}
    for row in session_rows:
        # 获取会话的消息
        cursor.execute("SELECT * FROM messages WHERE session_id = ? ORDER BY id", (row['id'],))
        message_rows = cursor.fetchall()
        
        messages = [
            Message(
                role=msg_row['role'],
                content=msg_row['content'],
                timestamp=msg_row['timestamp']
            )
            for msg_row in message_rows
        ]
        
        session = ChatSession(
            id=row['id'],
            title=row['title'],
            messages=messages,
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            model=row['model'],
            api_provider=row['api_provider']
        )
        sessions[session.id] = session
    
    conn.close()
    return sessions

def save_session_to_db(session: ChatSession):
    """将单个会话保存到数据库"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 插入或更新会话
    cursor.execute('''
        INSERT OR REPLACE INTO sessions 
        (id, title, created_at, updated_at, model, api_provider)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        session.id,
        session.title,
        session.created_at,
        session.updated_at,
        session.model,
        session.api_provider
    ))
    
    # 删除现有的消息
    cursor.execute("DELETE FROM messages WHERE session_id = ?", (session.id,))
    
    # 插入所有消息
    for message in session.messages:
        cursor.execute('''
            INSERT INTO messages 
            (session_id, role, content, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (
            session.id,
            message.role,
            message.content,
            message.timestamp
        ))
    
    conn.commit()
    conn.close()

def delete_session_from_db(session_id: str) -> bool:
    """从数据库删除会话"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    rows_affected = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    return rows_affected > 0

def add_message_to_db(session_id: str, message: Message):
    """向数据库中的会话添加消息"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO messages 
        (session_id, role, content, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (
        session_id,
        message.role,
        message.content,
        message.timestamp
    ))
    
    # 更新会话的updated_at时间
    cursor.execute('''
        UPDATE sessions 
        SET updated_at = ? 
        WHERE id = ?
    ''', (
        datetime.now().isoformat(),
        session_id
    ))
    
    conn.commit()
    conn.close()

def clear_session_messages_from_db(session_id: str):
    """清空数据库中会话的消息"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    
    # 更新会话的updated_at时间
    cursor.execute('''
        UPDATE sessions 
        SET updated_at = ? 
        WHERE id = ?
    ''', (
        datetime.now().isoformat(),
        session_id
    ))
    
    conn.commit()
    conn.close()

def update_session_in_db(session_id: str, title: str = None, model: str = None, api_provider: str = None):
    """更新数据库中的会话"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 构建动态更新语句
    updates = []
    params = []
    
    if title is not None:
        updates.append("title = ?")
        params.append(title)
    
    if model is not None:
        updates.append("model = ?")
        params.append(model)
    
    if api_provider is not None:
        updates.append("api_provider = ?")
        params.append(api_provider)
    
    # 总是更新updated_at时间
    updates.append("updated_at = ?")
    params.append(datetime.now().isoformat())
    
    if updates:
        query = f"UPDATE sessions SET {', '.join(updates)} WHERE id = ?"
        params.append(session_id)
        cursor.execute(query, params)
    
    conn.commit()
    conn.close()
