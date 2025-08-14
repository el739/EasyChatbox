# EasyChatbox

EasyChatbox 是一个基于 React 和 FastAPI 的聊天应用，支持与多个 AI 模型进行对话。用户可以通过简单的界面与 OpenAI、OpenRouter 等平台的模型进行交互。

## 功能特性

- 多会话管理：创建、切换和删除聊天会话
- 多模型支持：支持 OpenAI、OpenRouter 等平台的多种模型
- 实时对话：与 AI 模型进行实时对话
- 历史记录：保存和查看聊天历史
- 简洁界面：直观易用的用户界面

## 技术栈

### 前端
- React 18
- Axios
- CSS Modules

### 后端
- FastAPI
- OpenAI Python SDK
- Uvicorn (服务器)

## 项目结构

```
EasyChatbox/
├── backend/
│   ├── main.py              # 后端入口文件
│   ├── config.json          # 配置文件
│   ├── requirements.txt     # Python 依赖
│   └── modules/
│       ├── api_routes.py    # API 路由
│       ├── config.py        # 配置管理
│       ├── models.py        # 数据模型
│       ├── openai_client.py # OpenAI 客户端
│       └── session_manager.py # 会话管理
└── frontend/
    ├── package.json         # 前端依赖配置
    ├── public/
    └── src/
        ├── App.js           # 主应用组件
        ├── components/
        │   ├── ChatBox.js   # 聊天框组件
        │   ├── ModelSelector.js # 模型选择器
        │   └── SessionManager.js # 会话管理器
        └── ...
```

## 快速开始

### 后端设置

1. 进入后端目录：
   ```bash
   cd backend
   ```

2. 创建虚拟环境（推荐）：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate     # Windows
   ```

3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

4. 配置 API 密钥：
   编辑 `config.json` 文件，填入你的 API 密钥：
   ```json
   {
     "providers": [
       {
         "name": "OpenAI",
         "baseURL": "https://api.openai.com/v1",
         "api_key": "your-openai-api-key",
         "models": ["gpt-4o", "gpt-3.5-turbo"]
       },
       {
         "name": "OpenRouter",
         "baseURL": "https://openrouter.ai/v1",
         "api_key": "your-openrouter-api-key",
         "models": ["openai/gpt-4o", "google/gemini-1.5-flash"]
       }
     ]
   }
   ```

5. 启动后端服务：
   ```bash
   python main.py
   ```

### 前端设置

1. 进入前端目录：
   ```bash
   cd frontend
   ```

2. 安装依赖：
   ```bash
   npm install
   ```

3. 启动开发服务器：
   ```bash
   npm start
   ```

4. 打开浏览器访问 `http://localhost:3000`

## API 接口

后端提供以下 RESTful API 接口：

- `GET /sessions` - 获取所有会话
- `POST /sessions` - 创建新会话
- `GET /sessions/{session_id}` - 获取特定会话
- `PUT /sessions/{session_id}` - 更新会话配置
- `DELETE /sessions/{session_id}` - 删除会话
- `POST /sessions/{session_id}/messages` - 向会话添加消息
- `DELETE /sessions/{session_id}/messages` - 清空会话消息
- `POST /chat` - 与 AI 模型对话
- `GET /config` - 获取配置信息

## 开发

### 后端开发

后端使用 FastAPI 构建，提供了类型检查和自动生成的 API 文档。启动服务后，可以通过 `http://localhost:8000/docs` 访问交互式 API 文档。

### 前端开发

前端使用 React 构建，组件结构清晰：
- `App.js` - 主应用组件，负责状态管理和协调各组件
- `ChatBox.js` - 聊天界面组件
- `SessionManager.js` - 会话管理组件
- `ModelSelector.js` - 模型选择组件

## 部署

### 后端部署

可以使用以下方式部署后端：

1. 使用 Uvicorn（生产环境推荐使用 Gunicorn）：
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

2. 使用 Docker（需要 Dockerfile）：
   ```bash
   docker build -t easychatbox-backend .
   docker run -p 8000:8000 easychatbox-backend
   ```

### 前端部署

构建生产版本：
```bash
npm run build
```

然后将 `build` 目录中的文件部署到 Web 服务器。

## 许可证

本项目采用 Apache 2.0 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。
