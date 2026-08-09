@echo off
chcp 65001 >nul
title MyVoice Speech 起動ランチャー

echo ===================================================
echo   MyVoice Speech を起動しています...
echo ===================================================
echo.

cd /d "%~dp0"

echo [1/3] FastAPI バックエンドサーバーを起動中...
start "MyVoice Speech Backend" cmd /k "python backend/app.py"

echo [2/3] Web GUI フロントエンドを起動中...
start "MyVoice Speech Frontend" cmd /k "cd frontend && npm run dev"

echo [3/3] ブラウザで GUI を開いています...
timeout /t 3 /nobreak >nul
start http://localhost:5173

echo.
echo ===================================================
echo   MyVoice Speech の起動処理が完了しました。
echo   ブラウザ (http://localhost:5173) をご確認ください。
echo ===================================================
