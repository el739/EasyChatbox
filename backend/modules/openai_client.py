from fastapi import HTTPException
from typing import List, Dict, Union
from .config import openai_clients, default_client, provider_parameters

async def call_openai_api(messages: List[Dict[str, Union[str, List[Dict]]]], model: str, provider: str = None) -> str:
    """调用OpenAI API"""
    client = None
    selected_provider = None
    
    # 如果指定了提供商，使用对应的客户端
    if provider and provider in openai_clients:
        client = openai_clients[provider]
        selected_provider = provider
    # 否则使用默认客户端
    elif default_client:
        client = default_client
        selected_provider = [name for name, c in openai_clients.items() if c == default_client][0] if default_client in openai_clients.values() else None
    else:
        raise HTTPException(status_code=500, detail="API密钥未配置")
    
    # 获取提供商参数，默认参数
    params = {
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    if selected_provider and selected_provider in provider_parameters:
        params.update(provider_parameters[selected_provider])
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=params["temperature"],
            max_tokens=params["max_tokens"]
        )
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API调用失败: {str(e)}")
