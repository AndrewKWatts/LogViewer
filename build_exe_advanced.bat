@echo off
setlocal enabledelayedexpansion

echo ====================================
echo  Log Viewer GUI - Advanced Build
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

REM Check required packages
echo Checking required packages...
set "missing_packages="

pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    set "missing_packages=!missing_packages! pyinstaller"
)

if defined missing_packages (
    echo Installing missing packages:!missing_packages!
    pip install!missing_packages!
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install required packages!
        pause
        exit /b 1
    )
    echo Packages installed successfully!
    echo.
)

REM Build options
echo ====================================
echo           BUILD OPTIONS
echo ====================================
echo.
echo 1. Single file executable (slower startup, portable)
echo 2. Directory distribution (faster startup, multiple files)
echo 3. Console version (shows debug output)
echo 4. Custom build (advanced options)
echo.

set /p build_option="Select build option (1-4): "

REM Set build parameters based on choice
set "build_args="
set "build_name=LogViewerGUI"

if "%build_option%"=="1" (
    set "build_args=--onefile --windowed"
    set "build_desc=Single file executable"
) else if "%build_option%"=="2" (
    set "build_args=--windowed"
    set "build_desc=Directory distribution"
) else if "%build_option%"=="3" (
    set "build_args=--onefile --console"
    set "build_desc=Console version"
    set "build_name=LogViewerGUI_Console"
) else if "%build_option%"=="4" (
    echo.
    echo Advanced Options:
    set /p onefile="Create single file? (y/n): "
    set /p console="Show console window? (y/n): "
    set /p debug="Include debug info? (y/n): "
    
    if /i "!onefile!"=="y" set "build_args=!build_args! --onefile"
    if /i "!console!"=="y" (
        set "build_args=!build_args! --console"
    ) else (
        set "build_args=!build_args! --windowed"
    )
    if /i "!debug!"=="y" set "build_args=!build_args! --debug"
    
    set "build_desc=Custom build"
) else (
    echo Invalid option. Using default (single file executable).
    set "build_args=--onefile --windowed"
    set "build_desc=Single file executable (default)"
)

REM Optional icon
if exist "icon.ico" (
    set "build_args=!build_args! --icon=icon.ico"
    echo Using icon: icon.ico
) else (
    echo No icon.ico found. Building without custom icon.
)

echo.
echo Build configuration: !build_desc!
echo Build arguments: !build_args!
echo.

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del "*.spec"
echo.

REM Create build directory for resources
if not exist "resources" mkdir "resources"
copy "log_config.json" "resources\" >nul 2>&1
copy "sample_logs.txt" "resources\" >nul 2>&1

REM Build the executable
echo ====================================
echo         BUILDING EXECUTABLE
echo ====================================
echo.
echo Building %build_name%.exe...
echo This may take a few minutes depending on your system...
echo.

pyinstaller ^
    !build_args! ^
    --name "%build_name%" ^
    --add-data "log_config.json;." ^
    --add-data "sample_logs.txt;." ^
    --add-data "README_GUI.md;." ^
    --hidden-import tkinter ^
    --hidden-import tkinter.ttk ^
    --hidden-import tkinter.filedialog ^
    --hidden-import tkinter.messagebox ^
    --hidden-import tkinter.scrolledtext ^
    --clean ^
    --noconfirm ^
    LogViewerGUI.py

REM Check if build was successful
if %errorlevel% neq 0 (
    echo.
    echo ====================================
    echo           BUILD FAILED!
    echo ====================================
    echo Please check the output above for error details.
    echo Common issues:
    echo - Missing dependencies
    echo - Insufficient disk space
    echo - Antivirus blocking the build
    pause
    exit /b 1
)

REM Verify executable exists
set "exe_path=dist\%build_name%.exe"
if "%build_option%"=="2" (
    set "exe_path=dist\%build_name%\%build_name%.exe"
)

if not exist "%exe_path%" (
    echo.
    echo ERROR: Executable not found at expected location!
    echo Expected: %exe_path%
    echo Please check the dist folder contents.
    pause
    exit /b 1
)

echo.
echo ====================================
echo        BUILD SUCCESSFUL!
echo ====================================
echo.

if "%build_option%"=="2" (
    echo Distribution folder: dist\%build_name%\
    echo Main executable: dist\%build_name%\%build_name%.exe
    echo.
    echo Note: Distribute the entire folder, not just the .exe file.
) else (
    echo Executable: %exe_path%
)

echo.
echo File size: 
for %%A in ("%exe_path%") do echo   %%~zA bytes (%%~zA KB)

echo.
echo Included resources:
echo   ✓ log_config.json (default configuration)
echo   ✓ sample_logs.txt (sample data)
echo   ✓ README_GUI.md (documentation)

REM Performance test
echo.
echo ====================================
echo         TESTING EXECUTABLE
echo ====================================
echo.
set /p test_exe="Test the executable now? (y/n): "
if /i "%test_exe%"=="y" (
    echo Starting %build_name%.exe...
    echo.
    echo If the application doesn't start, check:
    echo - Windows Defender/Antivirus warnings
    echo - Missing Visual C++ Redistributable
    echo - Firewall blocking execution
    echo.
    
    start "" "%exe_path%"
    
    echo Executable launched. Please verify:
    echo ✓ GUI opens correctly
    echo ✓ Can load sample_logs.txt
    echo ✓ Filtering works
    echo ✓ Export functions work
)

echo.
echo ====================================
echo      DISTRIBUTION PACKAGE
echo ====================================
echo.

REM Create distribution package
set "dist_name=LogViewer_Distribution"
if exist "%dist_name%" rmdir /s /q "%dist_name%"
mkdir "%dist_name%"

if "%build_option%"=="2" (
    xcopy "dist\%build_name%" "%dist_name%\" /E /I /Q
) else (
    copy "%exe_path%" "%dist_name%\" >nul
)

REM Copy additional files
copy "README_GUI.md" "%dist_name%\" >nul
copy "log_config.json" "%dist_name%\" >nul
copy "sample_logs.txt" "%dist_name%\" >nul

REM Create a simple launcher script
echo @echo off > "%dist_name%\Run_LogViewer.bat"
echo echo Starting Log Viewer GUI... >> "%dist_name%\Run_LogViewer.bat"
echo %build_name%.exe >> "%dist_name%\Run_LogViewer.bat"
echo if %%errorlevel%% neq 0 pause >> "%dist_name%\Run_LogViewer.bat"

echo Distribution package created: %dist_name%\
echo Contents:
dir /b "%dist_name%"

echo.
echo ====================================
echo            SUMMARY
echo ====================================
echo.
echo Build Type: !build_desc!
echo Output: %dist_name%\
echo.
echo To distribute:
echo 1. Zip the '%dist_name%' folder
echo 2. Send to users
echo 3. Users extract and run %build_name%.exe
echo.
echo No Python installation required on target machines!
echo.

pause