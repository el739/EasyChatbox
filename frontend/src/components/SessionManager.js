import React, { useState } from 'react';
import './SessionManager.css';

const SessionManager = ({ sessions, currentSession, onCreateSession, onSwitchSession, onDeleteSession }) => {
  const [showNewSessionInput, setShowNewSessionInput] = useState(false);
  const [newSessionTitle, setNewSessionTitle] = useState('');

  const handleCreateSession = () => {
    if (newSessionTitle.trim()) {
      onCreateSession(newSessionTitle.trim());
      setNewSessionTitle('');
      setShowNewSessionInput(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleCreateSession();
    }
  };

  return (
    <div className="session-manager">
      <div className="session-header">
        <h3>会话历史</h3>
        <button 
          className="new-session-btn"
          onClick={() => setShowNewSessionInput(true)}
        >
          +
        </button>
      </div>
      
      {showNewSessionInput && (
        <div className="new-session-input">
          <input
            type="text"
            value={newSessionTitle}
            onChange={(e) => setNewSessionTitle(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="会话标题"
            autoFocus
          />
          <div className="new-session-actions">
            <button onClick={handleCreateSession}>创建</button>
            <button onClick={() => {
              setShowNewSessionInput(false);
              setNewSessionTitle('');
            }}>
              取消
            </button>
          </div>
        </div>
      )}
      
      <div className="session-list">
        {sessions.length > 0 ? (
          sessions.map((session) => (
            <div 
              key={session.id}
              className={`session-item ${currentSession && currentSession.id === session.id ? 'active' : ''}`}
            >
              <div 
                className="session-info"
                onClick={() => onSwitchSession(session)}
              >
                <div className="session-title" title={session.title}>
                  {session.title}
                </div>
                <div className="session-time">
                  {new Date(session.updated_at).toLocaleString()}
                </div>
              </div>
              <button 
                className="delete-session-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  onDeleteSession(session.id);
                }}
                title="删除会话"
              >
                ×
              </button>
            </div>
          ))
        ) : (
          <div className="no-sessions">
            <p>暂无会话历史</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SessionManager;