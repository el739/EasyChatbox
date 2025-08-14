from fastapi import HTTPException
from typing import List, Dict
from .config import openai_client

async def call_openai_api(messages: List[Dict[str, str]], model: str) -> str:
    """调用OpenAI API"""
    if not openai_client:
        raise HTTPException(status_code=500, detail="OpenAI API密钥未配置")
    
    try:
        response = openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API调用失败: {str(e)}")
