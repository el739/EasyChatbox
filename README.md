# EasyChatbox

一个简单的与LLM聊天的Web应用，支持聊天历史管理和多种模型选择。

## 功能特性

1. 前端和后端页面
2. 聊天历史管理（查看、切换、继续对话等）
3. 模型和API提供商选择
4. 可视化聊天界面

## 项目结构

```
EasyChatbox/
├── backend/
│   ├── main.py          # FastAPI后端应用
│   └── requirements.txt  # Python依赖
└── frontend/
    ├── public/
    ├── src/
    │   ├── components/   # React组件
    │   ├── App.js        # 主应用组件
    │   └── index.js      # 应用入口
    └── package.json      # Node.js依赖
```

## 安装和运行

### 一键启动 (推荐)

在Windows系统上，可以使用一键启动脚本：

1. 双击 `start.bat` 文件，或在命令行中运行：
   ```
   start.bat
   ```

该脚本会自动启动后端和前端服务，并在浏览器中打开应用。

### 手动启动

#### 后端 (FastAPI)

1. 进入后端目录:
   ```
   cd backend
   ```

2. 创建虚拟环境 (推荐):
   ```
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. 安装依赖:
   ```
   pip install -r requirements.txt
   ```

4. 运行后端服务:
   ```
   python main.py
   ```
   
   后端服务将在 `http://localhost:8000` 上运行。

#### 前端 (React)

1. 进入前端目录:
   ```
   cd frontend
   ```

2. 安装依赖:
   ```
   npm install
   ```

3. 运行前端应用:
   ```
   npm start
   ```
   
   前端应用将在 `http://localhost:3000` 上运行。

## 使用说明

1. 打开浏览器访问 `http://localhost:3000`
2. 在左侧边栏可以：
   - 创建新会话
   - 查看和切换历史会话
   - 删除不需要的会话
   - 选择不同的模型和API提供商
3. 在主聊天区域可以：
   - 发送消息与AI对话
   - 查看对话历史
   - 清空当前会话

## 配置

目前应用使用模拟响应来演示功能。要连接真实的LLM API，需要：

1. 在后端代码中实现真实的API调用逻辑
2. 在前端添加API密钥配置界面或通过环境变量配置

## API接口

- `GET /sessions` - 获取所有会话
- `POST /sessions` - 创建新会话
- `GET /sessions/{id}` - 获取特定会话
- `PUT /sessions/{id}` - 更新会话配置
- `DELETE /sessions/{id}` - 删除会话
- `POST /sessions/{id}/messages` - 向会话添加消息
- `DELETE /sessions/{id}/messages` - 清空会话消息
- `POST /chat` - 与AI聊天
- `GET /config` - 获取模型和提供商配置

## 开发

### 后端开发

后端使用 FastAPI 框架，主要文件是 `backend/main.py`。

### 前端开发

前端使用 React 框架，主要组件在 `frontend/src/components/` 目录下：
- `ChatBox.js` - 聊天界面
- `SessionManager.js` - 会话管理
- `ModelSelector.js` - 模型选择器

## 扩展功能建议

1. 添加用户认证系统
2. 实现真实的LLM API集成
3. 添加数据库支持（如SQLite, PostgreSQL）
4. 支持导出聊天记录
5. 添加主题切换功能
6. 实现更多模型参数配置

## 许可证

MIT