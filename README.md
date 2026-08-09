# MyVoice Speech

> **GPT-SoVITSを利用して、参照音声から日本語音声を生成するローカルWEB GUIツール**

MyVoice Speech は、オープンソースの音声合成エンジン **GPT-SoVITS v2** をバックエンドとして利用し、参照音声と日本語テキストから音声合成（ゼロショット・ボイスクローン）を実行・試聴・保存できるローカルGUIツールです。

---

## 1. 主な機能

- 🎙️ **参照音声指定**: ファイルドラッグ＆ドロップ・選択およびWebマイク直接録音・試聴プレビュー
- 📝 **日本語原稿入力**: テキスト入力、リアルタイム文字数カウント、テキストファイルの読込・保存・クリア
- ⚡ **音声生成・制御**: GPT-SoVITSエンジンによる音声合成、進行ステータス（待機/生成中/完了/エラー）表示
- 🔊 **結果再生＆保存**: 生成音声をブラウザ上で直接再生・シーク、WAV形式でローカルへ保存
- 🔒 **ローカル動作**: 外部APIキー不要、ユーザーの音声データや原稿テキストを外部へ送信しない安全設計

---

## 2. システム構成

```text
MyVoice Speech (Vite + React GUI)
      │
      ▼ (REST API / localhost:8000)
FastAPI Backend (app.py)
      │
      ▼
GPT-SoVITS Adapter (gpt_sovits_adapter.py)
      │
      ▼
GPT-SoVITS v2 Engine (PyTorch / CUDA)
      │
      ▼
Generated Audio (WAV)
```

---

## 3. 動作環境

- **OS**: Windows 10 / 11 (64bit)
- **Python**: 3.10 ~ 3.11 (推奨)
- **Node.js**: v18 以上
- **推奨ハードウェア**: NVIDIA GPU (VRAM 6GB 以上推奨 / CUDA 11.8+ / 12.x)
- **依存ライブラリ**: PyTorch, soundfile, librosa, faster-whisper, FastAPI, React, Vite

---

## 4. クイックスタート (セットアップと起動)

### 4.1 バックエンド起動

```bash
# 1. 依存ライブラリのインストール
pip install -r backend/requirements.txt

# 2. モデルダウンロード (初回のみ)
python scripts/download_gpt_sovits_models.py

# 3. APIサーバー起動
python backend/app.py
```
* APIサーバーが `http://localhost:8000` で起動します。

### 4.2 フロントエンド起動

```bash
# 1. フロントエンドディレクトリへ移動
cd frontend

# 2. パッケージインストール (初回のみ)
npm install

# 3. 開発サーバー起動
npm run dev
```
* ブラウザで `http://localhost:5173` にアクセスして操作します。

---

## 5. ⚠️【重要】現在の限界と制約事項

> ### 現在の制約
> 本ツールは個人環境で開発・検証している実験的なオープンソースソフトウェアです。
> 
> 現在使用しているPC環境およびGPT-SoVITSの設定では、**数秒〜十数秒程度の短時間の参照音声から、長文章や2〜3分程度の長い日本語スピーチを生成した場合、参照音声の人物と生成音声の声質・発音・抑揚などが十分に一致しない場合や、音声の途中で品質が変化する場合があります。**
> 
> 実際の検証では、短い参照音声のみから長時間の本人音声を高精度に再現することには限界が確認されています。
> 
> そのため、本ツールは**「特定の人物の声を完全に再現すること」を保証するものではありません。**
> 現在のバージョンは、ローカル環境でAI音声合成を検証し、GUIから手軽に利用できるようにした実験的ツールとして公開しています。

---

## 6. 実用上の注意とガイドライン

1. **権利保護・同意の取得**: 本ツールで第三者の音声を利用する場合は、**必ず本人の明示的な同意**を得てください。
2. **不正利用の禁止**: 他人になりすます目的、誤認を招く目的、その他不適切・違法な目的での利用は絶対に行わないでください。
3. **データ管理**: 個人の音声ファイルや生成物はGitリポジトリにコミットしないでください（`.gitignore` で除外されるよう設定されています）。

---

## 7. ディレクトリ構成

```text
MyVoice-Speech/
│
├─ backend/
│  ├─ app.py                   # FastAPI Web API サーバー
│  ├─ requirements.txt         # バックエンド依存パッケージ
│  ├─ tts/
│  │  ├─ base.py              # 音声合成エンジン共通インターフェース
│  │  └─ gpt_sovits_adapter.py # GPT-SoVITS v2 アダプター
│  ├─ uploads/                # 参照音声保存先 (.gitignore対象)
│  └─ outputs/                # 生成音声保存先 (.gitignore対象)
│
├─ frontend/
│  ├─ src/
│  │  ├─ components/          # 分割UIコンポーネント (Header, Audio, Script等)
│  │  ├─ App.jsx              # メイン画面 (プロジェクト統計ツールデザイン準拠)
│  │  └─ index.css            # ミニマルダークデザインCSS (プロジェクト統計ツール準拠)
│  └─ package.json
│
├─ docs/
│  └─ SPECIFICATION.md        # 詳細仕様書
│
├─ scripts/                   # テスト・モデルダウンロード用スクリプト
├─ samples/                   # サンプル用ディレクトリ
├─ README.md
├─ LICENSE
└─ .gitignore
```

---

## 8. ライセンス

- **MyVoice Speech (本体)**: [MIT License](LICENSE)
- **GPT-SoVITS**: [RVC-Boss/GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) (MIT License / AGPLv3 に準拠)
- **学習済みモデル**: 各モデルライセンス（chinese-roberta, chinese-hubert, gsv-v2）の利用条件に従います。
