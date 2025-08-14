import React, { useState, useEffect } from 'react';
import './ModelSelector.css';

const ModelSelector = ({ models, providers, currentSession, onUpdateSession }) => {
  const [selectedProvider, setSelectedProvider] = useState(currentSession?.api_provider || '');
  const [selectedModel, setSelectedModel] = useState(currentSession?.model || '');

  // 当currentSession变化时更新本地状态
  useEffect(() => {
    if (currentSession) {
      setSelectedProvider(currentSession.api_provider || '');
      setSelectedModel(currentSession.model || '');
    }
  }, [currentSession]);

  // 处理提供商变化
  const handleProviderChange = async (e) => {
    const newProvider = e.target.value;
    setSelectedProvider(newProvider);
    
    if (currentSession && onUpdateSession) {
      await onUpdateSession(currentSession.id, { api_provider: newProvider });
    }
  };

  // 处理模型变化
  const handleModelChange = async (e) => {
    const newModel = e.target.value;
    setSelectedModel(newModel);
    
    if (currentSession && onUpdateSession) {
      await onUpdateSession(currentSession.id, { model: newModel });
    }
  };

  return (
    <div className="model-selector">
      <h3>模型配置</h3>
      <div className="config-item">
        <label>提供商:</label>
        <select 
          value={selectedProvider}
          onChange={handleProviderChange}
          disabled={!currentSession}
        >
          <option value="">请选择提供商</option>
          {providers.map((provider, index) => (
            <option key={index} value={provider}>
              {provider}
            </option>
          ))}
        </select>
      </div>
      
      <div className="config-item">
        <label>模型:</label>
        <select 
          value={selectedModel}
          onChange={handleModelChange}
          disabled={!currentSession}
        >
          <option value="">请选择模型</option>
          {models.map((model, index) => (
            <option key={index} value={model}>
              {model}
            </option>
          ))}
        </select>
      </div>
      
      <div className="config-info">
        <p>配置信息保存在本地配置文件中</p>
      </div>
    </div>
  );
};

export default ModelSelector;