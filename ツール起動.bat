@echo off
chcp 65001 >nul
title MyVoice Speech 起動ランチャー

echo ===================================================
echo   MyVoice Speech を起動しています...
echo ===================================================
echo.

pushd "%~dp0"

echo [1/3] バックエンド API サーバーを起動中...
pushd "%~dp0backend"
start "MyVoice-Speech-Backend" cmd /k "python app.py"
popd

echo [2/3] Web GUI フロントエンドを起動中...
pushd "%~dp0frontend"
start "MyVoice-Speech-Frontend" cmd /k "npm run dev"
popd

echo [3/3] ブラウザで GUI を開いています...
timeout /t 3 /nobreak >nul
start http://localhost:5173

popd

echo.
echo ===================================================
echo   起動処理が完了しました。
echo   開いたウィンドウを閉じずにそのままご利用ください。
echo ===================================================
