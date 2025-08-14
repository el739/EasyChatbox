import os
from dotenv import load_dotenv
import openai

# 加载环境变量
load_dotenv()

# 获取OpenAI配置
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_api_base = os.getenv("OPENAI_API_BASE")

# 获取默认模型配置
default_model = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")
default_provider = os.getenv("DEFAULT_PROVIDER", "openai")

# 初始化OpenAI客户端
openai_client = None

# 尝试初始化OpenAI客户端
if openai_api_key:
    if openai_api_base:
        openai_client = openai.OpenAI(api_key=openai_api_key, base_url=openai_api_base)
    else:
        openai_client = openai.OpenAI(api_key=openai_api_key)
