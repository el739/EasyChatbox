import React, { useState, useRef, useEffect } from 'react';
import './ChatBox.css';

const ChatBox = ({ session, onSendMessage, onClearSession, loading }) => {
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // 滚动到最新消息
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [session?.messages]);

  // 处理发送消息
  const handleSend = () => {
    if (inputValue.trim() && !loading) {
      onSendMessage(inputValue);
      setInputValue('');
    }
  };

  // 处理回车发送
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // 处理粘贴
  const handlePaste = (e) => {
    e.preventDefault();
    const text = e.clipboardData.getData('text/plain');
    const textarea = e.target;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const newValue = inputValue.substring(0, start) + text + inputValue.substring(end);
    setInputValue(newValue);
  };

  return (
    <div className="chatbox">
      <div className="chatbox-header">
        <h2>{session ? session.title : '请选择或创建会话'}</h2>
        {session && (
          <button 
            className="clear-btn"
            onClick={onClearSession}
            disabled={loading}
          >
            清空对话
          </button>
        )}
      </div>
      
      <div className="messages-container">
        {session ? (
          session.messages.length > 0 ? (
            session.messages.map((message, index) => (
              <div key={index} className={`message ${message.role}`}>
                <div className="message-header">
                  <span className="message-role">
                    {message.role === 'user' ? '你' : '助手'}
                  </span>
                  <span className="message-time">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <div className="message-content">
                  {message.content}
                </div>
              </div>
            ))
          ) : (
            <div className="empty-messages">
              <p>开始对话吧！</p>
            </div>
          )
        ) : (
          <div className="no-session">
            <p>请选择一个会话或创建新会话开始聊天</p>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      {session && (
        <div className="input-container">
          <textarea
            ref={inputRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            onPaste={handlePaste}
            placeholder={loading ? "AI正在思考..." : "输入消息... (Enter发送, Shift+Enter换行)"}
            disabled={loading}
            rows="3"
          />
          <button 
            onClick={handleSend}
            disabled={!inputValue.trim() || loading}
            className="send-btn"
          >
            {loading ? '发送中...' : '发送'}
          </button>
        </div>
      )}
    </div>
  );
};

export default ChatBox;