import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import ReferenceAudioSection from './components/ReferenceAudioSection';
import ScriptInputSection from './components/ScriptInputSection';
import GenerationControl from './components/GenerationControl';
import ResultPlayerSection from './components/ResultPlayerSection';
import { AlertTriangle, CheckCircle2, ShieldCheck } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000';

export default function App() {
  const [healthStatus, setHealthStatus] = useState(null);
  const [refAudio, setRefAudio] = useState(null);
  const [scriptText, setScriptText] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [resultAudio, setResultAudio] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // ヘルスチェックのポーリング
  const checkHealth = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/health`);
      const data = await res.json();
      setHealthStatus(data);
    } catch {
      setHealthStatus({ status: 'offline', device: 'Disconnected' });
    }
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleGenerate = async () => {
    if (!refAudio) {
      setError('参照音声が指定されていません。参照音声をアップロードまたは録音してください。');
      return;
    }

    if (!scriptText || !scriptText.trim()) {
      setError('原稿テキストが入力されていません。日本語テキストを入力してください。');
      return;
    }

    setIsGenerating(true);
    setError(null);
    setSuccess(null);

    try {
      const res = await fetch(`${API_BASE_URL}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: scriptText,
          reference_audio_path: refAudio.absolutePath || refAudio.relativePath,
          language: 'ja',
        }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || '音声生成に失敗しました。');
      }

      const generatedResult = {
        filename: data.filename,
        url: `${API_BASE_URL}${data.download_url}`,
        textSnippet: scriptText.slice(0, 30) + (scriptText.length > 30 ? '...' : ''),
        timestamp: new Date().toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' }),
      };

      setResultAudio(generatedResult);
      setHistory((prev) => [generatedResult, ...prev]);
      setSuccess('音声が正常に生成されました！');
    } catch (err) {
      setError(err.message);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="app-container">
      <Header healthStatus={healthStatus} />

      {/* エラー通知 */}
      {error && (
        <div className="notice-box notice-error" style={{ marginBottom: '16px' }}>
          <AlertTriangle size={18} />
          <div style={{ flex: 1 }}>{error}</div>
          <button
            style={{ background: 'none', border: 'none', color: 'currentColor', cursor: 'pointer' }}
            onClick={() => setError(null)}
          >
            ×
          </button>
        </div>
      )}

      {/* サクセス通知 */}
      {success && (
        <div className="notice-box notice-success" style={{ marginBottom: '16px' }}>
          <CheckCircle2 size={18} />
          <div style={{ flex: 1 }}>{success}</div>
          <button
            style={{ background: 'none', border: 'none', color: 'currentColor', cursor: 'pointer' }}
            onClick={() => setSuccess(null)}
          >
            ×
          </button>
        </div>
      )}

      <main>
        <ReferenceAudioSection
          refAudio={refAudio}
          setRefAudio={setRefAudio}
          apiBaseUrl={API_BASE_URL}
          setError={setError}
        />

        <ScriptInputSection
          text={scriptText}
          setText={setScriptText}
          apiBaseUrl={API_BASE_URL}
          setError={setError}
          setSuccess={setSuccess}
        />

        <GenerationControl
          isGenerating={isGenerating}
          onGenerate={handleGenerate}
          disabled={!refAudio || !scriptText.trim()}
        />

        <ResultPlayerSection
          resultAudio={resultAudio}
          history={history}
          apiBaseUrl={API_BASE_URL}
        />
      </main>

      {/* フッター (プロジェクト統計ツール準拠) */}
      <footer className="app-footer">
        <div className="footer-content">
          <div className="footer-copyright">
            MyVoice Speech v1.0.0 — Powered by GPT-SoVITS Engine
          </div>
          <div className="footer-security">
            <ShieldCheck size={14} style={{ color: 'var(--accent-emerald)' }} />
            <span>完全ローカル処理 / 外部データ送信なし / プライバシー保護</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
