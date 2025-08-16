# EasyChatbox

EasyChatbox 是一个简单的聊天应用，支持多种AI模型。它包含前端和后端两部分，前端基于React，后端基于Python FastAPI。

## 配置

### 后端配置

1. 编辑 `backend/config.json` 文件：
   - 修改API密钥：将 `your-sk-here` 替换为实际的API密钥
   - 修改认证信息（可选）：更改默认的用户名和密码
   - 根据需要调整模型参数

### 前端配置

1. 在 `frontend` 目录下创建 `.env` 文件：
   - 复制 `.env.example` 文件内容
   - 设置 `REACT_APP_API_BASE_URL` 为后端服务地址（开发环境默认为 `http://localhost:8000`）

## 安装依赖

### 后端依赖安装

1. 确保已安装Python 3.8+
2. 进入 `backend` 目录
3. 运行以下命令安装依赖：
   ```
   pip install -r requirements.txt
   ```

### 前端依赖安装

1. 确保已安装Node.js 14+
2. 进入 `frontend` 目录
3. 运行以下命令安装依赖：
   ```
   npm install
   ```

## 启动

### 手动启动

1. 启动后端服务：
   ```
   cd backend
   python main.py
   ```
   后端服务将在 `http://localhost:8000` 运行

2. 启动前端服务：
   ```
   cd frontend
   npm start
   ```
   前端服务将在 `http://localhost:3000` 运行

### 一键启动（Windows）

在项目根目录下运行：
```
start_windows.bat
```

### 一键启动（Linux/macOS）

在项目根目录下运行：
```
./start_linux.sh
```

启动后，前端界面将在浏览器中自动打开，或访问 `http://localhost:3000` 手动打开。

## 使用

1. 首次使用需要登录：
   - 用户名：admin
   - 密码：securepassword
   （可在 `backend/config.json` 中修改）

2. 登录后可以选择不同的AI模型进行对话
