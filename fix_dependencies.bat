@echo off
echo ========================================
echo Pocket TTS - Dependency Fixer
echo ========================================
echo.

REM Check if virtual environment exists
if not exist venv (
    echo [ERROR] Virtual environment not found!
    echo Please run install_pocket_tts.bat first
    pause
    exit /b 1
)

echo [1/5] Activating virtual environment...
call venv\Scripts\activate.bat

echo [2/5] Upgrading pip...
python -m pip install --upgrade pip setuptools wheel

echo.
echo [3/5] Reinstalling critical packages...
pip install --force-reinstall pocket-tts soundfile scipy numpy pydub
pip install audioop-lts

echo.
echo [4/5] Verifying installation...
python -c "import pocket_tts; print('[OK] pocket_tts:', pocket_tts.__version__)" 2>nul
if errorlevel 1 (
    echo [ERROR] Verification failed
    echo Attempting full reinstall...
    pip uninstall pocket-tts -y
    pip install pocket-tts
)

echo.
echo [5/5] Running preflight checks (ffmpeg, HuggingFace auth)...
call preflight_checks.bat

echo.
echo ========================================
echo Dependency Fix Complete!
echo ========================================
echo.
choice /c yn /n /m "Would you like to run Pocket TTS now? (Y/N): "
if errorlevel 2 goto :end
if errorlevel 1 call run_pocket_tts.bat

:end
echo.
pause
