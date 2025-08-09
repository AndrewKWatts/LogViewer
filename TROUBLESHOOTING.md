# Build Troubleshooting Guide

## Common Issues and Solutions

### 1. "pyinstaller is not recognized"

**Problem**: PyInstaller is not installed or not in PATH

**Solutions**:
```batch
# Option 1: Install PyInstaller
pip install pyinstaller

# Option 2: Use the install script
install_pyinstaller.bat

# Option 3: Install with user flag
pip install --user pyinstaller

# Option 4: Use Python module syntax
python -m pip install pyinstaller
```

**After installation, verify**:
```batch
pyinstaller --version
# OR
python -m PyInstaller --version
```

### 2. "pip is not recognized"

**Problem**: pip is not installed or Python not in PATH

**Solutions**:
```batch
# Check Python installation
python --version

# If Python works but pip doesn't:
python -m ensurepip --upgrade

# Or download get-pip.py and run:
python get-pip.py
```

**Reinstall Python** (recommended):
1. Go to https://python.org/downloads/
2. Download Python 3.8+
3. During installation:
   - ✅ Check "Add Python to PATH"
   - ✅ Check "Install pip"

### 3. "Python is not recognized"

**Problem**: Python not installed or not in PATH

**Solution**: Install Python properly
1. Download from https://python.org/downloads/
2. Run installer as Administrator
3. **IMPORTANT**: Check "Add Python 3.x to PATH"
4. Restart Command Prompt
5. Test: `python --version`

### 4. "Permission denied" or "Access denied"

**Problem**: Insufficient permissions

**Solutions**:
```batch
# Run Command Prompt as Administrator
# Right-click Command Prompt → "Run as administrator"

# Or install with user flag:
pip install --user pyinstaller
```

### 5. Build fails with module errors

**Problem**: Missing dependencies or import issues

**Solutions**:
```batch
# Install missing modules
pip install tkinter  # Usually built-in
pip install pathlib   # Usually built-in

# Use hidden imports
pyinstaller --hidden-import tkinter --hidden-import tkinter.ttk LogViewerGUI.py
```

### 6. "Large executable size"

**Problem**: Executable is 20-30MB+

**Explanation**: This is normal for PyInstaller
- Includes entire Python runtime
- Includes all dependencies
- Creates self-contained executable

**Reduce size**:
```batch
# Use directory distribution instead
pyinstaller --onedir LogViewerGUI.py

# Exclude unused modules
pyinstaller --exclude-module matplotlib LogViewerGUI.py
```

### 7. Antivirus blocks executable

**Problem**: Windows Defender or antivirus flags the .exe

**Solution**:
1. This is a false positive (common with PyInstaller)
2. Add exception in antivirus software
3. Or use `--console` flag for debugging:
```batch
pyinstaller --onefile --console LogViewerGUI.py
```

### 8. "No module named 'tkinter'"

**Problem**: tkinter not available

**Solutions**:
```batch
# On Ubuntu/Debian:
sudo apt-get install python3-tk

# On Windows:
# Reinstall Python with "tcl/tk and IDLE" option checked

# Test tkinter:
python -c "import tkinter; print('tkinter OK')"
```

## Manual Build Commands

If batch files don't work, try these manual commands:

### Basic Build
```batch
python -m PyInstaller --onefile --windowed LogViewerGUI.py
```

### With Resources
```batch
python -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name "LogViewerGUI" ^
    --add-data "log_config.json;." ^
    --add-data "sample_logs.txt;." ^
    LogViewerGUI.py
```

### Debug Version
```batch
python -m PyInstaller --onefile --console LogViewerGUI.py
```

## Step-by-Step Manual Installation

If automatic scripts fail:

### 1. Install Python
```
1. Go to https://python.org/downloads/
2. Download Python 3.8 or newer
3. Run installer as Administrator
4. Check "Add Python to PATH"
5. Check "Install pip"
6. Restart computer
```

### 2. Verify Installation
```batch
python --version
pip --version
```

### 3. Install PyInstaller
```batch
python -m pip install --upgrade pip
python -m pip install pyinstaller
```

### 4. Verify PyInstaller
```batch
pyinstaller --version
```

### 5. Build Executable
```batch
cd "path\to\Log Viewer"
pyinstaller --onefile --windowed LogViewerGUI.py
```

## Alternative: Using Virtual Environment

For clean builds:

```batch
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install PyInstaller
pip install pyinstaller

# Build
pyinstaller --onefile --windowed LogViewerGUI.py

# Deactivate
deactivate
```

## Getting Help

If you're still having issues:

1. **Check Python version**: `python --version` (need 3.6+)
2. **Check pip version**: `pip --version`
3. **Try console version** for error messages:
   ```batch
   pyinstaller --onefile --console LogViewerGUI.py
   ```
4. **Run the .exe from Command Prompt** to see errors:
   ```batch
   cd dist
   LogViewerGUI.exe
   ```

## Contact Information

If you need help:
- Check the error message carefully
- Try the solutions above step by step
- Use the console version to see detailed errors
- Make sure you have Python 3.6+ and pip installed