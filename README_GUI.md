# Log Viewer GUI

A graphical interface for the configurable log viewer application.

## Features

### ✅ Completed Features
- **Full GUI Interface** - Built with tkinter for cross-platform compatibility
- **File Loading** - Open log files through file dialog or drag & drop
- **Dynamic Filtering Panel** - Auto-generates filter inputs based on log categories
- **Search Functionality** - Real-time search with highlighting
- **Log Display** - Scrollable display with compact and detailed views
- **Statistics Panel** - Shows log counts and breakdowns by level
- **Export Functionality** - Export filtered logs to TXT, CSV, or JSON
- **Color Coding** - Different colors for log levels (ERROR, WARNING, INFO, DEBUG)
- **Keyboard Shortcuts** - Common actions have keyboard shortcuts
- **Configuration Loading** - Load custom configuration files

## How to Use

### Starting the GUI
```bash
python LogViewerGUI.py
```

### Loading Logs
1. **File Menu > Open Log File** or **Ctrl+O**
2. Select your log file in the dialog
3. Logs will be parsed and displayed automatically

### Filtering Logs
1. Use the **Search box** for text-based filtering
2. Use the **category-specific filters** in the left panel
3. Click **Apply Filters** to update the display
4. Click **Clear All** to reset filters

### View Options
- **Detailed View checkbox** - Toggle between compact and detailed display
- **Limit dropdown** - Control how many logs to display (50, 100, 500, 1000, All)

### Keyboard Shortcuts
- `Ctrl+O` - Open file
- `Ctrl+E` - Export logs
- `Ctrl+F` - Focus search box
- `Ctrl+R` - Clear filters
- `F5` - Refresh display
- `Ctrl+Q` - Quit application

## GUI Components

### Main Window Layout
- **Toolbar** - Quick access to common functions
- **Left Panel** - Filters and statistics
- **Right Panel** - Log display area
- **Status Bar** - Shows current status and progress

### Filter Panel
- **Search Box** - Global text search with live highlighting
- **Dynamic Filters** - Generated based on log configuration:
  - String fields: Text input for "contains" matching
  - Number fields: Numeric input for exact matching
  - DateTime fields: Text input for partial matching
- **Statistics** - Real-time counts and breakdowns

### Log Display
- **Compact View** - One line per log entry
- **Detailed View** - Expanded view showing all fields
- **Color Coding** - Log levels highlighted with different colors
- **Search Highlighting** - Search terms highlighted in yellow
- **Scrollable** - Handle large log files efficiently

## Configuration

The GUI uses the same configuration format as the CLI version:

```json
{
    "logViewerConfig": {
        "delimiters": {
            "logStartDelimiter": "[",
            "logEndDelimiter": "]###",
            "categorySeparator": "|",
            "keyValuePairsSeparator": ";",
            "keyValueSeparator": "=",
            "arrayElementSeparator": ","
        },
        "categories": [
            {"name": "Timestamp", "type": "datetime", "order": 1},
            {"name": "LogLevel", "type": "string", "order": 2},
            {"name": "Component", "type": "string", "order": 3},
            {"name": "Details", "type": "structured_string", "order": 4},
            {"name": "Tags", "type": "array_string", "order": 5},
            {"name": "ErrorCode", "type": "number", "order": 6}
        ]
    }
}
```

## Export Formats

### Text Export
- Plain text format with line numbers
- Preserves original log formatting

### CSV Export
- Structured data in CSV format
- Headers: Line, Raw Text, + all log categories
- Complex data (dict/list) converted to string representation

### JSON Export
- Full structured export with all metadata
- Includes line numbers, raw text, and parsed fields
- Ideal for programmatic processing

## Example Usage

1. **Start the GUI**:
   ```bash
   python LogViewerGUI.py
   ```

2. **Load sample logs**:
   - File > Open Log File
   - Select `sample_logs.txt`

3. **Filter for errors**:
   - In LogLevel filter, type "ERROR"
   - Click Apply Filters

4. **Search for specific terms**:
   - In Search box, type "payment"
   - Results automatically update

5. **Export results**:
   - File > Export Filtered Logs
   - Choose format (TXT/CSV/JSON)

## Technical Details

### Architecture
- **Backend**: Uses existing `LogViewer` class for parsing and filtering
- **Frontend**: tkinter with ttk widgets for modern appearance
- **Threading**: File loading runs in background to prevent GUI freezing
- **Configuration**: Dynamic UI generation based on log categories

### Performance
- **Lazy Loading**: Display limits prevent memory issues with large files
- **Background Processing**: File I/O doesn't block the UI
- **Efficient Filtering**: Leverages existing backend filtering engine

### Dependencies
- Python 3.6+
- tkinter (included with Python)
- No external dependencies required

## Next Steps

The GUI provides a solid foundation for the following enhancements:
- **Real-time monitoring** - Watch log files for changes
- **Advanced date filtering** - Date range pickers
- **Regular expressions** - Regex support in filters
- **Themes** - Dark mode and custom themes
- **Plugin system** - Custom parsers and filters