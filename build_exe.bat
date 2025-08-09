@echo off
setlocal enabledelayedexpansion

echo ====================================
echo     Log Viewer GUI - Build EXE
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python and try again.
    pause
    exit /b 1
)

echo Python found: 
python --version
echo.

REM Check if pip is available
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip is not available!
    echo This usually means Python was installed without pip.
    echo.
    echo Solutions:
    echo 1. Reinstall Python with "Add to PATH" and "pip" options checked
    echo 2. Or download get-pip.py and run: python get-pip.py
    echo 3. Or use: python -m ensurepip --upgrade
    echo.
    pause
    exit /b 1
)

echo Pip found:
pip --version
echo.

REM Check if PyInstaller is installed
echo Checking for PyInstaller...
python -m PyInstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo PyInstaller not found. Installing...
    echo This may take a few minutes...
    echo.
    
    REM Try different installation methods
    pip install pyinstaller
    if %errorlevel% neq 0 (
        echo First attempt failed. Trying with --user flag...
        pip install --user pyinstaller
        if %errorlevel% neq 0 (
            echo Second attempt failed. Trying to upgrade pip first...
            python -m pip install --upgrade pip
            pip install pyinstaller
            if %errorlevel% neq 0 (
                echo ERROR: Failed to install PyInstaller!
                echo.
                echo Manual installation steps:
                echo 1. Open Command Prompt as Administrator
                echo 2. Run: pip install pyinstaller
                echo 3. Or try: python -m pip install pyinstaller
                echo 4. Then run this script again
                echo.
                pause
                exit /b 1
            )
        )
    )
    
    echo Verifying PyInstaller installation...
    python -m PyInstaller --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ERROR: PyInstaller installed but not accessible!
        echo This might be a PATH issue.
        echo.
        echo Try these solutions:
        echo 1. Restart your command prompt
        echo 2. Add Python Scripts directory to PATH
        echo 3. Use: python -m PyInstaller instead of pyinstaller
        echo.
        set /p try_python="Try using 'python -m PyInstaller'? (y/n): "
        if /i "!try_python!"=="y" (
            set "PYINSTALLER_CMD=python -m PyInstaller"
        ) else (
            pause
            exit /b 1
        )
    ) else (
        set "PYINSTALLER_CMD=python -m PyInstaller"
        echo PyInstaller installed successfully!
    )
    echo.
) else (
    set "PYINSTALLER_CMD=python -m PyInstaller"
    echo PyInstaller found:
    python -m PyInstaller --version
    echo.
)

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del "*.spec"
echo.

REM Build the executable
echo Building Log Viewer GUI executable...
echo This may take a few minutes...
echo.

%PYINSTALLER_CMD% ^
    --onefile ^
    --windowed ^
    --name "LogViewerGUI" ^
    --add-data "log_config.json;." ^
    --add-data "sample_logs.txt;." ^
    --clean ^
    LogViewerGUI.py

REM Check if build was successful
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Build failed!
    echo Please check the output above for error details.
    pause
    exit /b 1
)

REM Check if exe was created
if not exist "dist\LogViewerGUI.exe" (
    echo.
    echo ERROR: Executable not found in dist folder!
    pause
    exit /b 1
)

echo.
echo ====================================
echo        BUILD SUCCESSFUL!
echo ====================================
echo.
echo Executable created: dist\LogViewerGUI.exe
echo File size: 
for %%A in ("dist\LogViewerGUI.exe") do echo   %%~zA bytes

echo.
echo Additional files included:
echo   - log_config.json (configuration)
echo   - sample_logs.txt (sample data)
echo.

REM Test the executable
set /p test_exe="Do you want to test the executable now? (y/n): "
if /i "%test_exe%"=="y" (
    echo.
    echo Testing executable...
    start "" "dist\LogViewerGUI.exe"
    echo Executable launched. Check if it opens correctly.
)

echo.
echo ====================================
echo           DISTRIBUTION
echo ====================================
echo.
echo To distribute your application:
echo 1. Copy the entire "dist" folder to target machine
echo 2. Run LogViewerGUI.exe
echo.
echo Note: The exe is self-contained and doesn't require
echo       Python to be installed on the target machine.
echo.

pause