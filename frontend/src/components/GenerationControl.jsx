import React from 'react';
import { Play, Loader2 } from 'lucide-react';

export default function GenerationControl({
  isGenerating,
  onGenerate,
  disabled
}) {
  return (
    <div style={{ marginBottom: '24px' }}>
      <button
        className="btn btn-primary btn-large"
        onClick={onGenerate}
        disabled={disabled || isGenerating}
      >
        {isGenerating ? (
          <>
            <Loader2 size={20} className="spin-icon" style={{ animation: 'spin 1s linear infinite' }} />
            <span>GPT-SoVITS で音声生成中... (数秒～十数秒かかります)</span>
          </>
        ) : (
          <>
            <Play size={20} fill="currentColor" />
            <span>音声生成を開始する</span>
          </>
        )}
      </button>
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
