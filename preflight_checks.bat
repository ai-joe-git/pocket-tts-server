@echo off
REM Preflight checks for system tools and HuggingFace authentication.
REM Assumes the venv is already activated so that `hf` is on PATH.

echo [CHECK] Checking for ffmpeg...
where ffmpeg >nul 2>&1
if errorlevel 1 (
    call :install_ffmpeg
) else (
    echo [OK] ffmpeg found
)
echo.

echo [CHECK] Checking HuggingFace authentication...
hf auth whoami >nul 2>&1
if errorlevel 1 (
    call :hf_login
) else (
    echo [OK] HuggingFace authentication present
)
echo.

exit /b 0

:install_ffmpeg
echo [!] ffmpeg not found on PATH.
echo     pydub requires ffmpeg to decode MP3/OGG voice files for cloning.
echo.
where winget >nul 2>&1
if errorlevel 1 (
    echo [!] winget is not available on this system.
    echo     Please install ffmpeg manually:
    echo       1. Download a static build from https://www.gyan.dev/ffmpeg/builds/
    echo       2. Extract and add the 'bin' folder to your PATH
    echo.
    echo Press any key once ffmpeg is installed and on PATH...
    pause >nul
) else (
    echo [INFO] Installing ffmpeg via winget...
    winget install --id Gyan.FFmpeg --accept-source-agreements --accept-package-agreements
    if errorlevel 1 (
        echo [WARNING] winget install failed. Install ffmpeg manually:
        echo   https://www.gyan.dev/ffmpeg/builds/
        echo.
        echo Press any key to continue...
        pause >nul
    ) else (
        echo [OK] ffmpeg installed.
        echo [NOTE] You may need to restart this shell for PATH to refresh.
    )
)
goto :eof

:hf_login
echo [!] Not logged in to HuggingFace.
echo     pocket-tts needs HuggingFace credentials to download the
echo     voice-cloning model from kyutai/pocket-tts. Without it, custom
echo     voices will fail with 'Voice not found' errors.
echo.
echo Before continuing, in your browser:
echo   1. Open https://huggingface.co/kyutai/pocket-tts
echo   2. Sign in and click 'Agree and access repository'
echo   3. Create a Read token at https://huggingface.co/settings/tokens
echo.
echo Press any key when done to start 'hf auth login'...
pause >nul
hf auth login
if errorlevel 1 (
    echo [WARNING] hf auth login did not complete.
    echo You can rerun it later from the activated venv: hf auth login
) else (
    echo [OK] HuggingFace authentication configured
)
goto :eof
