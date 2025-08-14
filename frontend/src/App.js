import React, { useState, useEffect, useRef } from 'react';
import ChatBox from './components/ChatBox';
import SessionManager from './components/SessionManager';
import ModelSelector from './components/ModelSelector';
import './App.css';

function App() {
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [models, setModels] = useState([]);
  const [providers, setProviders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // 获取所有会话
  const fetchSessions = async () => {
    try {
      const response = await fetch('http://localhost:8000/sessions');
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
      const response = await fetch('http://localhost:8000/config');
      const data = await response.json();
      setModels(data.models);
      setProviders(data.providers);
    } catch (err) {
      setError('获取配置失败: ' + err.message);
    }
  };

  // 创建新会话
  const createNewSession = async (title = '新对话') => {
    try {
      const response = await fetch(`http://localhost:8000/sessions?title=${encodeURIComponent(title)}`, {
        method: 'POST'
      });
      const newSession = await response.json();
      setSessions([...sessions, newSession]);
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
      await fetch(`http://localhost:8000/sessions/${sessionId}`, {
        method: 'DELETE'
      });
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
      const response = await fetch(`http://localhost:8000/sessions/${sessionId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(config)
      });
      
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
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: message,
          session_id: currentSession.id
        })
      });
      
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
      await fetch(`http://localhost:8000/sessions/${currentSession.id}/messages`, {
        method: 'DELETE'
      });
      
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
  useEffect(() => {
    fetchSessions();
    fetchConfig();
  }, []);

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