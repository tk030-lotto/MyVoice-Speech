import React, { useRef, useEffect } from 'react';
import { FileText, Save, FolderOpen, Trash2 } from 'lucide-react';

export default function ScriptInputSection({
  text,
  setText,
  apiBaseUrl,
  setError,
  setSuccess
}) {
  const fileInputRef = useRef(null);

  // マウント時に保存されたテキストがあれば自動ロード
  useEffect(() => {
    const autoLoadText = async () => {
      try {
        const res = await fetch(`${apiBaseUrl}/api/load-text`);
        const data = await res.json();
        if (res.ok && data.text && !text) {
          setText(data.text);
        }
      } catch {
        // サイレントエラー（自動ロード失敗時は無視）
      }
    };
    autoLoadText();
  }, []);

  const handleSaveText = async () => {

    try {
      const res = await fetch(`${apiBaseUrl}/api/save-text`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail);
      setSuccess('原稿テキストをサーバーに保存しました。');
    } catch (err) {
      setError(`テキスト保存に失敗しました: ${err.message}`);
    }
  };

  const handleLoadText = async () => {
    try {
      const res = await fetch(`${apiBaseUrl}/api/load-text`);
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail);
      setText(data.text || '');
      setSuccess('保存された原稿テキストを読み込みました。');
    } catch (err) {
      setError(`テキスト読み込みに失敗しました: ${err.message}`);
    }
  };

  const handleFileLoad = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      setText(event.target?.result || '');
      setSuccess(`ファイル '${file.name}' を読み込みました。`);
    };
    reader.readAsText(file, 'UTF-8');
  };

  return (
    <div className="card">
      <div className="card-title">
        <div className="card-title-left">
          <FileText size={18} style={{ color: 'var(--accent-blue)' }} />
          <span>2. 原稿入力</span>
        </div>

        <div className="btn-group">
          <input
            type="file"
            ref={fileInputRef}
            accept=".txt"
            style={{ display: 'none' }}
            onChange={handleFileLoad}
          />
          <button
            className="btn"
            onClick={() => fileInputRef.current?.click()}
            title="テキストファイルを開く"
          >
            <FolderOpen size={14} /> ファイル読込
          </button>
          <button className="btn" onClick={handleLoadText} title="前回保存したテキストを復元">
            復元
          </button>
          <button className="btn" onClick={handleSaveText} title="テキストを保存">
            <Save size={14} /> 保存
          </button>
          <button
            className="btn btn-danger"
            onClick={() => setText('')}
            title="全文消去"
          >
            <Trash2 size={14} /> クリア
          </button>
        </div>
      </div>

      <textarea
        className="textarea-input"
        placeholder="ここに読み上げさせる日本語原稿テキストを入力してください..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />

      <div className="textarea-footer">
        <span>対応言語: 日本語 (ja)</span>
        <span className="font-mono" style={{ color: text.length > 0 ? 'var(--text-primary)' : 'var(--text-muted)' }}>
          文字数: {text.length} 文字
        </span>
      </div>
    </div>
  );
}
