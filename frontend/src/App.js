import React, { useState, useEffect, useRef } from 'react';
import ChatBox from './components/ChatBox';
import SessionManager from './components/SessionManager';
import ModelSelector from './components/ModelSelector';
import Login from './components/Login';
import { getApiBaseUrl } from './utils/api';
import './App.css';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [models, setModels] = useState([]);
  const [providers, setProviders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // 登录处理函数
  const handleLogin = (user, pass) => {
    setUsername(user);
    setPassword(pass);
    setIsLoggedIn(true);
  };

  // 当登录状态改变时初始化数据
  useEffect(() => {
    if (isLoggedIn) {
      initializeData();
    }
  }, [isLoggedIn]);

  // 创建带认证头的fetch选项
  const createFetchOptions = (options = {}) => {
    const authHeader = 'Basic ' + btoa(username + ':' + password);
    return {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': authHeader
      }
    };
  };

  // 获取所有会话
  const fetchSessions = async () => {
    try {
      const response = await fetch(`${getApiBaseUrl()}/sessions`, createFetchOptions());
      const data = await response.json();
      setSessions(data);
      if (data.length > 0 && !currentSession) {
        setCurrentSession(data[0]);
      }
    } catch (err) {
      setError('获取会话失败: ' + err.message);
    }
  };

  // 获取配置信息
  const fetchConfig = async () => {
    try {
      const response = await fetch(`${getApiBaseUrl()}/config`, createFetchOptions());
      const data = await response.json();
      setModels(data.models);
      setProviders(data.providers);
      
      // 如果当前会话没有配置，使用默认配置
      if (currentSession && (!currentSession.model || !currentSession.api_provider)) {
        const updatedSession = { ...currentSession };
        if (!updatedSession.api_provider && data.default_provider) {
          updatedSession.api_provider = data.default_provider;
        }
        // 根据提供商设置默认模型
        if (!updatedSession.model && updatedSession.api_provider && data.models[updatedSession.api_provider]) {
          updatedSession.model = data.models[updatedSession.api_provider][0] || data.default_model;
        }
        
        if (updatedSession.model !== currentSession.model || updatedSession.api_provider !== currentSession.api_provider) {
          setCurrentSession(updatedSession);
          // 更新sessions列表
          const updatedSessions = sessions.map(session => 
            session.id === currentSession.id ? updatedSession : session
          );
          setSessions(updatedSessions);
        }
      }
    } catch (err) {
      setError('获取配置失败: ' + err.message);
    }
  };

  // 创建新会话
  const createNewSession = async (title = '新对话') => {
    try {
      const response = await fetch(`${getApiBaseUrl()}/sessions?title=${encodeURIComponent(title)}`, createFetchOptions({
        method: 'POST'
      }));
      const newSession = await response.json();
      setSessions([...(Array.isArray(sessions) ? sessions : []), newSession]);
      setCurrentSession(newSession);
    } catch (err) {
      setError('创建会话失败: ' + err.message);
    }
  };

  // 切换会话
  const switchSession = (session) => {
    setCurrentSession(session);
  };

  // 删除会话
  const deleteSession = async (sessionId) => {
    try {
      await fetch(`${getApiBaseUrl()}/sessions/${sessionId}`, createFetchOptions({
        method: 'DELETE'
      }));
      const updatedSessions = sessions.filter(session => session.id !== sessionId);
      setSessions(updatedSessions);
      if (currentSession && currentSession.id === sessionId) {
        setCurrentSession(updatedSessions.length > 0 ? updatedSessions[0] : null);
      }
    } catch (err) {
      setError('删除会话失败: ' + err.message);
    }
  };

  // 更新会话配置
  const updateSessionConfig = async (sessionId, config) => {
    try {
      const response = await fetch(`${getApiBaseUrl()}/sessions/${sessionId}`, createFetchOptions({
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(config)
      }));
      
      const updatedSession = await response.json();
      if (updatedSession.error) {
        setError(updatedSession.error);
        return false;
      }
      
      // 更新当前会话
      if (currentSession && currentSession.id === sessionId) {
        setCurrentSession(updatedSession);
      }
      
      // 更新sessions列表
      const updatedSessions = sessions.map(session => 
        session.id === sessionId ? updatedSession : session
      );
      setSessions(updatedSessions);
      
      return true;
    } catch (err) {
      setError('更新会话配置失败: ' + err.message);
      return false;
    }
  };

  // 发送消息
  const sendMessage = async (message) => {
    if (!currentSession || !message.trim()) return;
    
    // 立即在本地添加用户消息
    const userMessage = {
      role: 'user',
      content: message,
      timestamp: new Date().toISOString()
    };
    
    // 更新当前会话状态（添加用户消息）
    const updatedCurrentSession = {
      ...currentSession,
      messages: [...currentSession.messages, userMessage]
    };
    setCurrentSession(updatedCurrentSession);
    
    // 更新sessions列表
    const updatedSessions = sessions.map(session => 
      session.id === currentSession.id ? updatedCurrentSession : session
    );
    setSessions(updatedSessions);
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${getApiBaseUrl()}/chat`, createFetchOptions({
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: message,
          session_id: currentSession.id
        })
      }));
      
      const data = await response.json();
      if (data.error) {
        setError(data.error);
      } else {
        setCurrentSession(data.session);
        // 更新sessions列表
        const updatedSessions = sessions.map(session => 
          session.id === data.session.id ? data.session : session
        );
        setSessions(updatedSessions);
      }
    } catch (err) {
      setError('发送消息失败: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  // 清空当前会话
  const clearCurrentSession = async () => {
    if (!currentSession) return;
    
    try {
      await fetch(`${getApiBaseUrl()}/sessions/${currentSession.id}/messages`, createFetchOptions({
        method: 'DELETE'
      }));
      
      const updatedSession = { ...currentSession, messages: [] };
      setCurrentSession(updatedSession);
      
      // 更新sessions列表
      const updatedSessions = sessions.map(session => 
        session.id === currentSession.id ? updatedSession : session
      );
      setSessions(updatedSessions);
    } catch (err) {
      setError('清空会话失败: ' + err.message);
    }
  };

  // 初始化数据
  const initializeData = async () => {
    await fetchSessions();
    await fetchConfig();
  };

  // 如果未登录，显示登录界面
  if (!isLoggedIn) {
    return (
      <div className="app">
        <Login onLogin={handleLogin} />
        {error && (
          <div className="error-banner">
            错误: {error}
            <button onClick={() => setError(null)}>×</button>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>EasyChatbox</h1>
      </header>
      
      <div className="app-main">
        <div className="sidebar">
          <SessionManager 
            sessions={sessions}
            currentSession={currentSession}
            onCreateSession={createNewSession}
            onSwitchSession={switchSession}
            onDeleteSession={deleteSession}
          />
          
          <ModelSelector 
            models={models}
            providers={providers}
            currentSession={currentSession}
            onUpdateSession={updateSessionConfig}
          />
        </div>
        
        <div className="main-content">
          <ChatBox 
            session={currentSession}
            onSendMessage={sendMessage}
            onClearSession={clearCurrentSession}
            loading={loading}
          />
        </div>
      </div>
      
      {error && (
        <div className="error-banner">
          错误: {error}
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}
    </div>
  );
}

export default App;
