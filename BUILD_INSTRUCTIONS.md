# Building Log Viewer GUI Executable

This guide explains how to create a standalone executable for the Log Viewer GUI.

## Quick Start

### Option 1: Simple Build (Recommended)
```batch
build_exe.bat
```
- Creates a single-file executable
- Includes configuration and sample files  
- No additional setup required

### Option 2: Advanced Build
```batch
build_exe_advanced.bat
```
- Multiple build options
- Custom configurations
- Testing and distribution packaging

## Build Options

### 1. Single File Executable
- **File**: One portable .exe file
- **Size**: Larger (~15-30 MB)
- **Startup**: Slower (extracts on run)
- **Best for**: Easy distribution

### 2. Directory Distribution  
- **Files**: Multiple files in folder
- **Size**: Smaller individual files
- **Startup**: Faster
- **Best for**: Local installation

### 3. Console Version
- **Features**: Shows debug output
- **Best for**: Troubleshooting

## Requirements

### System Requirements
- Windows 7/10/11
- Python 3.6+ (for building only)
- ~100MB free disk space

### Python Dependencies
```batch
pip install pyinstaller
```

Or install all at once:
```batch
pip install -r requirements.txt
```

## Manual Build Commands

### Basic Command
```batch
pyinstaller --onefile --windowed LogViewerGUI.py
```

### Advanced Command
```batch
pyinstaller ^
    --onefile ^
    --windowed ^
    --name "LogViewerGUI" ^
    --add-data "log_config.json;." ^
    --add-data "sample_logs.txt;." ^
    --clean ^
    LogViewerGUI.py
```

## Output Files

### After Build
```
dist/
├── LogViewerGUI.exe          # Main executable
└── (additional files if directory build)

build/                        # Build cache (can delete)
LogViewerGUI.spec            # Build specification (can delete)
```

### Distribution Package
```
LogViewer_Distribution/
├── LogViewerGUI.exe         # Main application
├── log_config.json          # Configuration file
├── sample_logs.txt          # Sample data
├── README_GUI.md            # Documentation
└── Run_LogViewer.bat        # Simple launcher
```

## Testing the Executable

1. **Basic Test**: Double-click the .exe
2. **File Loading**: Open sample_logs.txt
3. **Filtering**: Test search and filters
4. **Export**: Try exporting to different formats

## Troubleshooting

### Build Issues

**"Python not found"**
- Install Python 3.6+
- Add Python to system PATH

**"PyInstaller not found"**
- Run: `pip install pyinstaller`

**"Build failed"**
- Check Python version (3.6+ required)
- Ensure all files are present
- Try running as administrator

**"Large file size"**
- Normal for PyInstaller (~15-30MB)
- Use directory build for smaller files

### Runtime Issues

**"Application won't start"**
- Check Windows Defender/Antivirus
- Install Visual C++ Redistributable
- Run from Command Prompt to see errors

**"Missing configuration"**
- Ensure log_config.json is in same folder
- Or use File > Load Config in GUI

**"Can't load log files"**
- Check file permissions
- Verify log format matches configuration

## Distribution

### For End Users
1. Create zip file of distribution folder
2. Include README_GUI.md for instructions
3. Users extract and run .exe
4. No Python installation required

### System Requirements (End User)
- Windows 7/10/11
- ~50MB disk space
- No additional software required

## File Sizes

| Build Type | Typical Size |
|------------|-------------|
| Single File | 15-30 MB |
| Directory | 20-40 MB total |
| With Resources | +1-2 MB |

## Advanced Options

### Custom Icon
```batch
# Add icon.ico to project folder
pyinstaller --icon=icon.ico --onefile LogViewerGUI.py
```

### Debug Version
```batch
# Shows console output for debugging
pyinstaller --onefile --console LogViewerGUI.py
```

### Optimization
```batch
# Exclude unused modules
pyinstaller --exclude-module matplotlib --exclude-module numpy --onefile LogViewerGUI.py
```

## Security Notes

- Some antivirus software may flag PyInstaller executables
- This is a false positive - add exception if needed
- Code is open source and can be inspected
- Build from trusted source code only