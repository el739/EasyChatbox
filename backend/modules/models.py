from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .config import default_model, default_provider

class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: str
    file_urls: Optional[List[str]] = None  # URLs to uploaded files

class ChatSession(BaseModel):
    id: str
    title: str
    messages: List[Message]
    created_at: str
    updated_at: str
    model: str = default_model
    api_provider: str = default_provider

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
    file_urls: Optional[List[str]] = None
