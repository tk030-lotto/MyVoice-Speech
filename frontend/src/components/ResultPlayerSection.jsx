import React from 'react';
import { Sparkles, Download, History, Music } from 'lucide-react';

export default function ResultPlayerSection({
  resultAudio,
  history,
  apiBaseUrl
}) {
  if (!resultAudio && history.length === 0) {
    return null;
  }

  return (
    <div className="card">
      <div className="card-title">
        <div className="card-title-left">
          <Sparkles size={18} style={{ color: 'var(--accent-emerald)' }} />
          <span>3. 生成結果</span>
        </div>
      </div>

      {resultAudio && (
        <div style={{ marginBottom: '20px' }}>
          <div className="notice-box notice-success">
            <Sparkles size={16} />
            <span>音声の生成が完了しました！以下から再生および保存が可能です。</span>
          </div>

          <div style={{ marginTop: '16px' }}>
            <audio controls autoPlay src={resultAudio.url} />

            <div style={{ marginTop: '12px', display: 'flex', justifyContent: 'flex-end' }}>
              <a
                href={resultAudio.url}
                download={resultAudio.filename}
                className="btn btn-primary"
                style={{ textDecoration: 'none' }}
              >
                <Download size={16} /> WAV形式で保存 (ダウンロード)
              </a>
            </div>
          </div>
        </div>
      )}

      {history.length > 0 && (
        <div style={{ marginTop: resultAudio ? '24px' : '0', paddingTop: resultAudio ? '16px' : '0', borderTop: resultAudio ? '1px solid var(--border-color)' : 'none' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8125rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '12px' }}>
            <History size={14} />
            <span>生成履歴 ({history.length} 件)</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {history.map((item, idx) => (
              <div key={idx} className="audio-preview">
                <div className="audio-info">
                  <Music size={16} style={{ color: 'var(--text-muted)' }} />
                  <div>
                    <div className="audio-name" style={{ fontSize: '0.8125rem' }}>
                      {item.textSnippet}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      {item.timestamp} - {item.filename}
                    </div>
                  </div>
                </div>

                <div className="btn-group">
                  <a
                    href={item.url}
                    download={item.filename}
                    className="btn"
                    style={{ textDecoration: 'none', padding: '4px 10px', fontSize: '0.75rem' }}
                  >
                    <Download size={12} /> 保存
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
