@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Pocket TTS - Enhanced API Server
echo ========================================
echo.

REM Check if virtual environment exists
if not exist venv (
    echo [ERROR] Virtual environment not found!
    echo Please run install_pocket_tts.bat first
    pause
    exit /b 1
)

REM Check if config.json exists
if not exist config.json (
    echo [WARNING] config.json not found, using defaults
)

REM Check if voices directory exists
if not exist voices-celebrities (
    echo [WARNING] voices-celebrities directory not found!
    echo Creating directory...
    mkdir voices-celebrities
)

REM Activate virtual environment
echo [1/4] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment activated

REM Check dependencies
echo [2/4] Checking dependencies...
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo [INFO] Installing additional dependencies...
    pip install fastapi uvicorn pydantic python-multipart -q
)
echo [OK] Dependencies ready

REM Create necessary directories
echo [3/4] Creating directories...
if not exist output mkdir output
if not exist temp mkdir temp
if not exist logs mkdir logs
if not exist voices-celebrities mkdir voices-celebrities
echo [OK] Directories ready

REM Start server
echo [4/4] Starting Enhanced Pocket TTS API Server...
echo.

REM Get config values
set "HOST=localhost"
set "PORT=8000"

if exist config.json (
    for /f "tokens=2 delims=:, " %%a in ('type config.json ^| findstr /i "host"') do (
        set "HOST=%%a"
        set "HOST=!HOST:"=!"
        set "HOST=!HOST: =!"
    )
    for /f "tokens=2 delims=:, " %%a in ('type config.json ^| findstr /i "port"') do (
        set "PORT=%%a"
        set "PORT=!PORT:"=!"
        set "PORT=!PORT: =!"
    )
)

echo.
echo ========================================
echo Server Endpoints:
echo ========================================
echo   Web Interface: http://%HOST%:%PORT%
echo   API Docs:     http://%HOST%:%PORT%/docs
echo   Health Check: http://%HOST%:%PORT%/health
echo.
echo OpenAI-Compatible Endpoints:
echo   POST /v1/audio/speech       - Text to Speech
echo   GET  /v1/audio/voices       - List Voices
echo   POST /v1/chat/completions   - Voice Chat
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Check if enhanced API exists
if exist pocket_tts_api.py (
    echo Starting Enhanced API Server...
    python pocket_tts_api.py
) else (
    echo Starting Standard Pocket TTS...
    python -m pocket_tts serve --host %HOST% --port %PORT%
)

REM This line is reached when server stops
echo.
echo Server stopped.
echo.

choice /c yn /n /m "Restart server? (Y/N): "
if errorlevel 2 goto :end
if errorlevel 1 call run_pocket_tts.bat

:end
echo.
echo Press any key to exit...
pause > nul
