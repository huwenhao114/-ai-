@echo off
title Campus Study Assistant

REM Switch to the directory where this bat file is located
cd /d "%~dp0"

echo ========================================
echo    Campus Study Assistant - Starting...
echo ========================================
echo.

REM Check if venv exists
if exist ".venv\Scripts\python.exe" goto :check_deps

echo [1/3] First run: creating virtual environment...
python -m venv .venv
if errorlevel 1 goto :no_python

:check_deps
REM Check if dependencies are installed
if exist ".venv\Lib\site-packages\streamlit" goto :start_app

echo [2/3] Installing dependencies (first run, please wait)...
call ".venv\Scripts\python.exe" -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
if errorlevel 1 goto :install_fail

:start_app
echo [3/3] Starting Streamlit...
echo.
echo ========================================
echo  Browser will open automatically.
echo  Enter your Ali Bailian API Key in the sidebar.
echo  Get Key: https://bailian.console.aliyun.com/
echo ========================================
echo.

REM Open browser after a short delay
start "" cmd /c "timeout /t 3 /nobreak >nul & start http://localhost:8502"

call ".venv\Scripts\streamlit.exe" run app.py --server.headless true --server.port 8502
goto :end

:no_python
echo.
echo [ERROR] Failed to create venv. Please install Python 3.10+
echo Download: https://www.python.org/downloads/
pause
exit /b 1

:install_fail
echo.
echo [ERROR] Dependency install failed. Check network connection.
pause
exit /b 1

:end
pause
