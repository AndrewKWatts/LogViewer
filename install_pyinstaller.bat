@echo off
echo ====================================
echo   Installing PyInstaller
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python first:
    echo 1. Go to https://python.org/downloads/
    echo 2. Download Python 3.8+ 
    echo 3. During installation, check "Add to PATH"
    echo 4. Run this script again
    echo.
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Try to upgrade pip first
echo Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install PyInstaller
echo Installing PyInstaller...
echo This may take a few minutes...
echo.

pip install pyinstaller
if %errorlevel% neq 0 (
    echo First attempt failed. Trying alternative methods...
    echo.
    
    echo Method 2: Installing with --user flag...
    pip install --user pyinstaller
    if %errorlevel% neq 0 (
        echo Method 3: Using python -m pip...
        python -m pip install pyinstaller
        if %errorlevel% neq 0 (
            echo Method 4: Installing as administrator...
            echo Please run this script as Administrator and try again.
            pause
            exit /b 1
        )
    )
)

echo.
echo Verifying installation...
pyinstaller --version
if %errorlevel% neq 0 (
    echo PyInstaller installed but not in PATH.
    echo Trying alternative command...
    python -m PyInstaller --version
    if %errorlevel% neq 0 (
        echo ERROR: Installation verification failed!
        echo.
        echo Try these manual steps:
        echo 1. Open Command Prompt as Administrator
        echo 2. Run: python -m pip install pyinstaller
        echo 3. Restart your command prompt
        echo 4. Test with: pyinstaller --version
        echo.
        pause
        exit /b 1
    ) else (
        echo SUCCESS: Use 'python -m PyInstaller' instead of 'pyinstaller'
    )
) else (
    echo SUCCESS: PyInstaller installed and accessible!
)

echo.
echo ====================================
echo     INSTALLATION COMPLETE
echo ====================================
echo.
echo You can now run: build_exe.bat
echo.

pause