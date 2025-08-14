from fastapi import HTTPException
from typing import List, Dict
from .config import openai_clients, default_client

async def call_openai_api(messages: List[Dict[str, str]], model: str, provider: str = None) -> str:
    """调用OpenAI API"""
    client = None
    
    # 如果指定了提供商，使用对应的客户端
    if provider and provider in openai_clients:
        client = openai_clients[provider]
    # 否则使用默认客户端
    elif default_client:
        client = default_client
    else:
        raise HTTPException(status_code=500, detail="API密钥未配置")
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API调用失败: {str(e)}")
