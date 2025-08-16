import React, { useState, useRef, useEffect } from 'react';
import './ChatBox.css';

const ChatBox = ({ session, onSendMessage, onClearSession, loading, onEditMessage, onDeleteMessage, username, password }) => {
  const [inputValue, setInputValue] = useState('');
  const [editingMessageIndex, setEditingMessageIndex] = useState(null);
  const [editingMessageContent, setEditingMessageContent] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const fileInputRef = useRef(null);

  // 滚动到最新消息
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [session?.messages]);

  // 处理发送消息
  const handleSend = () => {
    if ((inputValue.trim() || uploadedFiles.length > 0) && !loading) {
      // Prepare message data with file URLs
      const messageData = {
        message: inputValue,
        fileUrls: uploadedFiles.length > 0 ? uploadedFiles : undefined
      };
      
      onSendMessage(messageData);
      setInputValue('');
      setUploadedFiles([]);
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

  // 开始编辑消息
  const startEditing = (index, content) => {
    setEditingMessageIndex(index);
    setEditingMessageContent(content);
  };

  // 保存编辑的消息
  const saveEdit = () => {
    if (editingMessageContent.trim() && onEditMessage) {
      onEditMessage(editingMessageIndex, editingMessageContent);
    }
    cancelEdit();
  };

  // 取消编辑
  const cancelEdit = () => {
    setEditingMessageIndex(null);
    setEditingMessageContent('');
  };

  // 处理文件选择
  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
      uploadFiles(files);
    }
  };

  // 上传文件
  const uploadFiles = async (files) => {
    setIsUploading(true);
    try {
      const uploadedFileUrls = [];
      
      // 逐个上传文件
      for (let file of files) {
        const formData = new FormData();
        formData.append('file', file);
        
        // 获取API基础URL
        const apiBaseUrl = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
        
        // 创建带认证头的请求
        const authHeader = 'Basic ' + btoa(username + ':' + password);
        const response = await fetch(`${apiBaseUrl}/upload`, {
          method: 'POST',
          headers: {
            'Authorization': authHeader
          },
          body: formData
        });
        
        if (response.ok) {
          const data = await response.json();
          uploadedFileUrls.push(data.file_url);
        } else {
          throw new Error(`文件上传失败: ${file.name}`);
        }
      }
      
      // 更新已上传文件状态
      setUploadedFiles(prev => [...prev, ...uploadedFileUrls]);
    } catch (err) {
      console.error('文件上传错误:', err);
      alert('文件上传失败: ' + err.message);
    } finally {
      setIsUploading(false);
    }
  };

  // 触发文件选择
  const triggerFileSelect = () => {
    fileInputRef.current?.click();
  };

  // 移除已上传的文件
  const removeUploadedFile = (index) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  // 删除消息
  const deleteMessage = (index) => {
    if (window.confirm('确定要删除这条消息吗？') && onDeleteMessage) {
      onDeleteMessage(index);
    }
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
                {editingMessageIndex === index ? (
                  <div className="message-edit-container">
                    <textarea
                      value={editingMessageContent}
                      onChange={(e) => setEditingMessageContent(e.target.value)}
                      className="message-edit-textarea"
                      autoFocus
                    />
                    <div className="message-edit-buttons">
                      <button onClick={saveEdit} className="save-btn">保存</button>
                      <button onClick={cancelEdit} className="cancel-btn">取消</button>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="message-content">
                      {message.content}
                      {message.file_urls && message.file_urls.length > 0 && (
                        <div className="file-attachments">
                          <div className="file-attachments-title">📎 已上传文件:</div>
                          {message.file_urls.map((fileUrl, fileIndex) => (
                            <div key={fileIndex} className="file-attachment">
                              <a 
                                href={fileUrl} 
                                target="_blank" 
                                rel="noopener noreferrer"
                                className="file-link"
                              >
                                {fileUrl.split('/').pop()}
                              </a>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                    <div className="message-actions">
                      <button 
                        className="edit-btn"
                        onClick={() => startEditing(index, message.content)}
                        title="编辑消息"
                      >
                        ✏️
                      </button>
                      <button 
                        className="delete-btn"
                        onClick={() => deleteMessage(index)}
                        title="删除消息"
                      >
                        🗑️
                      </button>
                    </div>
                  </>
                )}
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
          {/* 隐藏的文件输入 */}
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileSelect}
            multiple
            style={{ display: 'none' }}
          />
          
          {/* 已上传的文件预览 */}
          {uploadedFiles.length > 0 && (
            <div className="file-preview-container">
              {uploadedFiles.map((fileUrl, index) => (
                <div key={index} className="file-preview-item">
                  <span className="file-name">{fileUrl.split('/').pop()}</span>
                  <button 
                    className="remove-file-btn"
                    onClick={() => removeUploadedFile(index)}
                    disabled={loading}
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}
          
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
          <div className="input-actions">
            <button 
              onClick={triggerFileSelect}
              disabled={loading || isUploading}
              className="upload-btn"
              title="上传文件"
            >
              {isUploading ? '上传中...' : '📎'}
            </button>
            <button 
              onClick={handleSend}
              disabled={(!inputValue.trim() && uploadedFiles.length === 0) || loading}
              className="send-btn"
            >
              {loading ? '发送中...' : '发送'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatBox;
