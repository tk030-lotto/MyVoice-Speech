# MyVoice Speech システム開発仕様書 (SPECIFICATION.md)

## 1. システム概要

MyVoice Speech は、GPT-SoVITS v2 エンジンを核とした日本語音声合成WEB GUIシステムです。
ローカルPC環境で高速かつ安全に音声生成を試行・検証することを目的として設計されています。

---

## 2. アーキテクチャ構成

```text
+-------------------------------------------------------+
|                Frontend (Vite + React)                |
|  - Header: エンジン・GPUステータス表示                  |
|  - ReferenceAudioSection: 音声ドラッグ＆ドロップ/録音 |
|  - ScriptInputSection: 原稿入力・文字数・テキスト保存  |
|  - GenerationControl: 生成実行・ローディング          |
|  - ResultPlayerSection: 音声試聴・WAV保存             |
+-------------------------------------------------------+
                           │ (HTTP REST / JSON / FormData)
                           ▼
+-------------------------------------------------------+
|               Backend (FastAPI / Uvicorn)             |
|  - /api/health                                        |
|  - /api/upload-reference                              |
|  - /api/generate                                      |
|  - /api/audio/{filename}                              |
|  - /api/save-text, /api/load-text                     |
+-------------------------------------------------------+
                           │ (Python Direct Call)
                           ▼
+-------------------------------------------------------+
|            Adapter (GPTSoVITSAdapter)                 |
|  - VAD (librosa.effects.split) スマートトリミング      |
|  - Faster-Whisper 自動文字起こし (Prompt Text)        |
|  - GPT-SoVITS v2 (TTS_infer_pack.TTS) 推論実行         |
+-------------------------------------------------------+
```

---

## 3. デザインシステム仕様

デスクトップの「プロジェクト統計ツール」のデザインシステムに完全準拠。

- **カラーパレット**:
  - `--bg-app`: `#09090b`
  - `--bg-card`: `#121215`
  - `--bg-inset`: `#050506`
  - `--border-color`: `#27272a`
  - `--text-primary`: `#f4f4f5`
  - `--text-secondary`: `#a1a1aa`
  - `--accent-blue`: `#3b82f6`
  - `--accent-emerald`: `#10b981`
- **フォント**: `Inter` (UIテキスト), `JetBrains Mono` (数値・ファイル名・ステータス)
- **レイアウト**: シングルページ / レスポンシブコンテナ (`max-width: 1100px`)

---

## 4. API インターフェース仕様

### 4.1 `GET /api/health`
- **概要**: サーバー・GPU・GPT-SoVITSモデルの動作状況を取得
- **レスポンス**:
  ```json
  {
    "status": "online",
    "engine": "GPT-SoVITS v2",
    "adapter_available": true,
    "cuda_available": true,
    "device": "NVIDIA GeForce RTX ...",
    "is_loaded": true
  }
  ```

### 4.2 `POST /api/upload-reference`
- **概要**: 参照音声ファイル（WAV/MP3/M4A）を受け取り `backend/uploads/` に保存
- **入力**: `multipart/form-data` (`file`)
- **レスポンス**:
  ```json
  {
    "message": "参照音声をアップロードしました。",
    "filename": "ref_a1b2c3d4.wav",
    "relative_path": "uploads/ref_a1b2c3d4.wav",
    "absolute_path": "C:/path/to/uploads/ref_a1b2c3d4.wav"
  }
  ```

### 4.3 `POST /api/generate`
- **概要**: 原稿テキストと参照音声から音声WAVを生成し `backend/outputs/` に保存
- **入力 JSON**:
  ```json
  {
    "text": "読み上げさせる日本語テキスト",
    "reference_audio_path": "C:/path/to/uploads/ref_a1b2c3d4.wav",
    "language": "ja"
  }
  ```
- **レスポンス**:
  ```json
  {
    "message": "音声生成が完了しました。",
    "filename": "speech_e5f6g7h8.wav",
    "download_url": "/api/audio/speech_e5f6g7h8.wav"
  }
  ```

---

## 5. 音声処理パイプライン詳細

1. **参照音声のアップロード/録音**:
   - Web Audio MediaRecorder または ファイルアップロードで取得。
2. **VAD (Voice Activity Detection) トリミング**:
   - `librosa.effects.split(top_db=25)` により、発話を最適（3.5s～7.5s）に切り出し。
3. **Prompt Text (自動文字起こし)**:
   - `Faster-Whisper (small / int8)` を用いて切り出した参照音声のテキストを全自動生成。
4. **GPT-SoVITS ゼロショット推論**:
   - s1BERT + s2G モデルによりクローン音声を生成し WAV として保存。

---

## 6. エラーハンドリング仕様

- **400 Bad Request**:
  - 参照音声未指定、テキスト未入力、非対応ファイル形式
- **404 Not Found**:
  - 参照音声または生成音声ファイルが存在しない場合
- **500 Internal Server Error**:
  - GPT-SoVITS推論失敗、メモリ/VRAM不足、ファイル書き込み失敗
  - エラーの詳細はバックエンドログに出力し、UIへは要約メッセージを提示。

---

## 7. 今後の拡張候補 (Future Roadmap)

- 長時間参照音声の分割生成・結合機能
- 無音長さ・話速・音量正規化調整パラメータのGUIコントロール
- 生成結果の履歴CSV/JSON保存
