import React, { useState } from 'react';
import { getApiBaseUrl } from '../utils/api';
import './Login.css';

const Login = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!username || !password) {
      setError('请输入用户名和密码');
      return;
    }
    
    try {
      // 测试认证信息
      const response = await fetch(`${getApiBaseUrl()}/`, {
        method: 'GET',
        headers: {
          'Authorization': 'Basic ' + btoa(username + ':' + password)
        }
      });
      
      if (response.ok) {
        // 认证成功，调用父组件的登录函数
        onLogin(username, password);
      } else {
        setError('用户名或密码错误');
      }
    } catch (err) {
      setError('登录失败: ' + err.message);
    }
  };

  return (
    <div className="login-container">
      <div className="login-form">
        <h2>登录</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">用户名:</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="password">密码:</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          {error && <div className="error-message">{error}</div>}
          <button type="submit">登录</button>
        </form>
      </div>
    </div>
  );
};

export default Login;
