@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Pocket TTS - Enhanced Installer
echo ========================================
echo.

REM Check if running as administrator (optional but helpful for some installations)
net session >nul 2>&1
if %errorlevel% == 0 (
    echo [INFO] Running with administrator privileges
) else (
    echo [INFO] Running without administrator privileges (normal mode)
)
echo.

REM Check Python version
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.10 or higher from https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%a in ('python --version') do set PYTHON_VERSION=%%a
echo [OK] Found Python %PYTHON_VERSION%
echo.

REM Create virtual environment if it doesn't exist
if exist venv (
    echo [INFO] Virtual environment found.
    echo.
    echo Choose an option:
    echo   1. Update existing installation (keep models)
    echo   2. Reinstall fresh (delete and recreate)
    echo   3. Repair installation
    echo.
    choice /c 123 /n /m "Select option (1-3): "
    
    if errorlevel 3 (
        echo [INFO] Repairing installation...
        call :repair_installation
        goto :end
    )
    if errorlevel 2 (
        echo [INFO] Deleting old virtual environment...
        rmdir /s /q venv
        call :create_venv
    )
    if errorlevel 1 (
        echo [INFO] Updating existing installation...
    )
) else (
    call :create_venv
)

goto :after_venv

:repair_installation
echo [INFO] Repairing installation...
call venv\Scripts\activate.bat
pip install --force-reinstall pocket-tts soundfile scipy > nul 2>&1
echo [OK] Repair complete
goto :end

:after_venv

echo.
echo ========================================
echo Installing/Updating Dependencies
echo ========================================
echo.

call venv\Scripts\activate.bat

REM Upgrade core tools
echo [1/5] Upgrading pip, setuptools, and wheel...
python -m pip install --upgrade pip setuptools wheel > nul 2>&1
if errorlevel 1 (
    echo [WARNING] Failed to upgrade pip, attempting to continue...
)

REM Install PyTorch CPU version
echo [2/5] Installing PyTorch (CPU version)...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to install PyTorch
    pause
    exit /b 1
)

REM Install other requirements
echo [3/5] Installing requirements from requirements.txt...
if exist requirements.txt (
    pip install -r requirements.txt > nul 2>&1
    if errorlevel 1 (
        echo [WARNING] Some packages failed to install from requirements.txt
        echo Attempting fallback installation...
    )
) else (
    echo [WARNING] requirements.txt not found, using default installation
)

REM Install Pocket TTS
echo [4/5] Installing Pocket TTS...
pip install --upgrade pocket-tts > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to install pocket-tts
    pause
    exit /b 1
)

REM Create output directories
echo [5/5] Creating directories...
if not exist output mkdir output
if not exist temp mkdir temp
if not exist logs mkdir logs

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo [OK] Virtual environment: venv\
echo [OK] Python: %PYTHON_VERSION%
echo [OK] Models cached at: %USERPROFILE%\.cache\huggingface\hub
echo.
echo To start Pocket TTS:
echo   Method 1: Run run_pocket_tts.bat
echo   Method 2: venv\Scripts\activate.bat ^&^& python -m pocket_tts serve
echo.
echo Open browser: http://localhost:8000
echo.

choice /c yn /n /m "Would you like to run Pocket TTS now? (Y/N): "
if errorlevel 2 goto :end
if errorlevel 1 call run_pocket_tts.bat

goto :end

:create_venv
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    echo Make sure you have Python 3.10+ with venv support installed
    pause
    exit /b 1
)
echo [OK] Virtual environment created
echo.
goto :eof

:repair_installation
echo [INFO] Repairing installation...
call venv\Scripts\activate.bat
pip install --force-reinstall pocket-tts soundfile scipy > nul 2>&1
echo [OK] Repair complete
goto :eof

:end
echo.
echo Press any key to exit...
pause > nul
