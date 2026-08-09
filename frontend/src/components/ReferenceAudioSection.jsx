import React, { useState, useRef } from 'react';
import { FileAudio, Upload, Mic, Square, Trash2, Volume2, CheckCircle2 } from 'lucide-react';

export default function ReferenceAudioSection({
  refAudio,
  setRefAudio,
  apiBaseUrl,
  setError
}) {
  const [isRecording, setIsRecording] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const fileInputRef = useRef(null);

  const handleFileUpload = async (file) => {
    if (!file) return;
    setIsUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${apiBaseUrl}/api/upload-reference`, {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'ファイルのアップロードに失敗しました。');
      }

      setRefAudio({
        filename: data.filename,
        originalName: data.original_name,
        relativePath: data.relative_path,
        absolutePath: data.absolute_path,
        url: `${apiBaseUrl}/api/audio/${data.filename}`,
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setIsUploading(false);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0) {
          audioChunksRef.current.push(e.data);
        }
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        const recordedFile = new File([audioBlob], `mic_record_${Date.now()}.wav`, {
          type: 'audio/wav',
        });
        await handleFileUpload(recordedFile);

        // トラック停止
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
      setError(null);
    } catch (err) {
      setError(`マイクアクセスの起動に失敗しました: ${err.message}`);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  return (
    <div className="card">
      <div className="card-title">
        <div className="card-title-left">
          <FileAudio size={18} className="text-blue" />
          <span>1. 参照音声指定</span>
        </div>
        {refAudio && (
          <span className="badge badge-online">
            <CheckCircle2 size={12} /> 設定完了
          </span>
        )}
      </div>

      <input
        type="file"
        ref={fileInputRef}
        accept="audio/*"
        style={{ display: 'none' }}
        onChange={(e) => {
          if (e.target.files?.[0]) {
            handleFileUpload(e.target.files[0]);
          }
        }}
      />

      {!refAudio ? (
        <div>
          <div
            className="dropzone"
            onClick={() => fileInputRef.current?.click()}
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => {
              e.preventDefault();
              if (e.dataTransfer.files?.[0]) {
                handleFileUpload(e.dataTransfer.files[0]);
              }
            }}
          >
            <Upload size={32} style={{ margin: '0 auto 8px', color: 'var(--text-muted)' }} />
            <p style={{ fontSize: '0.875rem', fontWeight: 500, color: 'var(--text-primary)' }}>
              {isUploading ? 'アップロード中...' : '音声ファイルをドラッグ＆ドロップまたは選択'}
            </p>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
              WAV, MP3, M4A 等 (推奨: 3～10秒程度のクリアな本人の発話)
            </p>
          </div>

          <div style={{ marginTop: '12px', display: 'flex', justifyContent: 'flex-end' }}>
            {!isRecording ? (
              <button className="btn" onClick={startRecording} disabled={isUploading}>
                <Mic size={16} /> マイクで録音
              </button>
            ) : (
              <button className="btn btn-danger" onClick={stopRecording}>
                <Square size={16} /> 録音停止
              </button>
            )}
          </div>
        </div>
      ) : (
        <div>
          <div className="audio-preview">
            <div className="audio-info">
              <Volume2 size={20} style={{ color: 'var(--accent-blue)' }} />
              <div>
                <div className="audio-name">{refAudio.originalName || refAudio.filename}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  パス: {refAudio.relativePath}
                </div>
              </div>
            </div>

            <div className="btn-group">
              <button
                className="btn btn-danger"
                onClick={() => setRefAudio(null)}
                title="音声を取り消し"
              >
                <Trash2 size={16} /> 削除・変更
              </button>
            </div>
          </div>

          <audio controls src={refAudio.url} />
        </div>
      )}
    </div>
  );
}
