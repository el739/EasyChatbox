import os
import json
from dotenv import load_dotenv
import openai

# 加载环境变量
load_dotenv()

# 加载配置文件
def load_config():
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"providers": []}

# 获取配置
config = load_config()

# 获取提供商列表
providers = config.get("providers", [])

# 获取认证配置
auth_config = config.get("auth", {})
auth_enabled = auth_config.get("enabled", False)
auth_username = auth_config.get("username", "admin")
auth_password = auth_config.get("password", "password")

# 初始化默认值
default_provider = "OpenAI"
default_model = "gpt-4o"

# 如果有配置的提供商，使用第一个作为默认
if providers:
    default_provider = providers[0].get("name", default_provider)
    default_model = providers[0].get("models", [default_model])[0]

# 初始化OpenAI客户端字典和参数
openai_clients = {}
provider_parameters = {}

# 根据配置初始化客户端
for provider in providers:
    name = provider.get("name")
    api_key = provider.get("api_key")
    base_url = provider.get("baseURL")
    parameters = provider.get("parameters", {})
    
    # 存储提供商参数
    provider_parameters[name] = parameters
    
    if api_key and api_key != "your-sk-here":
        try:
            openai_clients[name] = openai.OpenAI(api_key=api_key, base_url=base_url)
        except Exception as e:
            print(f"初始化 {name} 客户端失败: {e}")

# 获取默认客户端
default_client = openai_clients.get(default_provider) if openai_clients else None
