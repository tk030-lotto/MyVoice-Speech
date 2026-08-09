import os
import shutil
import uuid
import torch
from typing import Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from tts.gpt_sovits_adapter import GPTSoVITSAdapter

app = FastAPI(title="MyVoice Speech API", version="1.0.0")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
TEXT_SAVE_PATH = os.path.join(BASE_DIR, "saved_script.txt")

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# GPT-SoVITS アダプターシングルトン
adapter = GPTSoVITSAdapter()

class GenerateRequest(BaseModel):
    text: str
    reference_audio_path: str
    prompt_text: Optional[str] = None
    language: str = "ja"
    speed_factor: float = 1.0

class SaveTextRequest(BaseModel):
    text: str

@app.get("/api/health")
def health_check():
    cuda_available = torch.cuda.is_available()
    device_name = torch.cuda.get_device_name(0) if cuda_available else "CPU"
    adapter_available = adapter.is_available()

    return {
        "status": "online",
        "engine": "GPT-SoVITS v2",
        "adapter_available": adapter_available,
        "cuda_available": cuda_available,
        "device": device_name,
        "is_loaded": adapter._is_loaded
    }

@app.post("/api/upload-reference")
async def upload_reference(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="ファイルが指定されていません。")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".wav", ".mp3", ".m4a", ".ogg", ".flac"]:
        raise HTTPException(
            status_code=400,
            detail="対応していない音声形式です。(.wav, .mp3, .m4a, .ogg, .flac に対応)"
        )

    file_id = str(uuid.uuid4())[:8]
    filename = f"ref_{file_id}{ext}"
    save_path = os.path.join(UPLOADS_DIR, filename)

    try:
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ファイルの保存に失敗しました: {e}")

    return {
        "message": "参照音声をアップロードしました。",
        "filename": filename,
        "original_name": file.filename,
        "relative_path": f"uploads/{filename}",
        "absolute_path": os.path.abspath(save_path)
    }

@app.post("/api/generate")
def generate_speech(req: GenerateRequest):
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="原稿テキストが入力されていません。")

    ref_path = req.reference_audio_path
    if not os.path.isabs(ref_path):
        ref_path = os.path.join(BASE_DIR, ref_path)

    if not os.path.exists(ref_path):
        raise HTTPException(
            status_code=404,
            detail=f"指定された参照音声ファイルが存在しません: {req.reference_audio_path}"
        )

    output_id = str(uuid.uuid4())[:8]
    output_filename = f"speech_{output_id}.wav"
    output_path = os.path.join(OUTPUTS_DIR, output_filename)

    try:
        generated_path = adapter.generate(
            text=req.text.strip(),
            reference_audio_path=ref_path,
            output_path=output_path,
            language=req.language,
            prompt_text=req.prompt_text,
            speed_factor=req.speed_factor
        )

        return {
            "message": "音声生成が完了しました。",
            "filename": output_filename,
            "relative_path": f"outputs/{output_filename}",
            "download_url": f"/api/audio/{output_filename}",
            "absolute_path": generated_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"音声生成中にエラーが発生しました: {e}")

@app.get("/api/audio/{filename}")
def get_audio(filename: str):
    # uploads または outputs から探索
    path_in_outputs = os.path.join(OUTPUTS_DIR, filename)
    path_in_uploads = os.path.join(UPLOADS_DIR, filename)

    if os.path.exists(path_in_outputs):
        return FileResponse(path_in_outputs, media_type="audio/wav", filename=filename)
    elif os.path.exists(path_in_uploads):
        return FileResponse(path_in_uploads, filename=filename)
    else:
        raise HTTPException(status_code=404, detail="指定された音声ファイルが見つかりません。")

@app.post("/api/save-text")
def save_text(req: SaveTextRequest):
    try:
        with open(TEXT_SAVE_PATH, "w", encoding="utf-8") as f:
            f.write(req.text)
        return {"message": "原稿テキストを保存しました。"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"テキスト保存エラー: {e}")

@app.get("/api/load-text")
def load_text():
    if not os.path.exists(TEXT_SAVE_PATH):
        return {"text": ""}
    try:
        with open(TEXT_SAVE_PATH, "r", encoding="utf-8") as f:
            text = f.read()
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"テキスト読み込みエラー: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
