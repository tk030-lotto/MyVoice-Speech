@echo off
title MyVoice Speech Launcher

echo ===================================================
echo   Starting MyVoice Speech...
echo ===================================================
echo.

pushd "%~dp0"

echo [1/3] Starting FastAPI Backend Server...
pushd "%~dp0backend"
start "MyVoice-Speech-Backend" cmd /k "python app.py"
popd

echo [2/3] Starting Web GUI Frontend...
pushd "%~dp0frontend"
start "MyVoice-Speech-Frontend" cmd /k "npm run dev"
popd

echo [3/3] Opening Browser...
timeout /t 3 /nobreak >nul
start http://localhost:5173

popd

echo.
echo ===================================================
echo   Launch sequence complete.
echo   Please keep the opened windows running.
echo ===================================================
