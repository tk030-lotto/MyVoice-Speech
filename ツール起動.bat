@echo off
chcp 65001 >nul
title MyVoice Speech 起動ランチャー

echo ===================================================
echo   MyVoice Speech を起動しています...
echo ===================================================
echo.

set "ROOT_DIR=%~dp0"

echo [1/3] バックエンド API サーバーを起動中...
start "MyVoice-Speech-Backend" cmd /k "cd /d "%ROOT_DIR%backend" && python app.py"

echo [2/3] Web GUI フロントエンドを起動中...
start "MyVoice-Speech-Frontend" cmd /k "cd /d "%ROOT_DIR%frontend" && npm run dev"

echo [3/3] ブラウザを起動中...
timeout /t 3 /nobreak >nul
start http://localhost:5173

echo.
echo ===================================================
echo   起動処理が完了しました。
echo   開いたウィンドウを閉じずにそのままご利用ください。
echo ===================================================
