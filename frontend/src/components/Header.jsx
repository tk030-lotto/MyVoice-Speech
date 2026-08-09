import React from 'react';
import { Mic, Activity, Cpu } from 'lucide-react';

export default function Header({ healthStatus }) {
  const isOnline = healthStatus?.status === 'online';
  const device = healthStatus?.device || '未知';
  const isLoaded = healthStatus?.is_loaded;

  return (
    <header className="app-header">
      <div className="brand">
        <div className="brand-icon">
          <Mic size={22} />
        </div>
        <div>
          <h1 className="brand-title">MyVoice Speech</h1>
          <p className="brand-subtitle">GPT-SoVITS v2 音声合成ローカルGUI</p>
        </div>
      </div>

      <div className="status-container">
        <div className={`badge ${isOnline ? 'badge-online' : 'badge-offline'}`}>
          <span className="status-dot"></span>
          {isOnline ? 'エンジン起動中' : 'エンジン停止中'}
        </div>

        <div className="badge">
          <Cpu size={14} />
          {device}
        </div>

        {isLoaded && (
          <div className="badge badge-online">
            <Activity size={14} />
            モデルロード済み
          </div>
        )}
      </div>
    </header>
  );
}
