# Configurable Color System

## Overview

The Log Viewer now supports fully configurable coloring based on log field values. Colors are defined in the JSON configuration file and can be applied in three different ways.

## Color Configuration Format

### Basic Structure

Add color configuration to any category in your `log_config.json`:

```json
{
    "name": "CategoryName",
    "type": "string",
    "order": 1,
    "ColourType": "ColoringMethod",
    "ColourMap": {
        "R,G,B": "MatchingValue",
        "R,G,B": "AnotherValue"
    }
}
```

### Color Specification

Colors are specified as RGB values in the format `"R,G,B"`:
- **Example**: `"122,44,75"` = Dark red color
- **Range**: Each value from 0-255
- **Conversion**: Automatically converted to hex colors for display

## Coloring Methods

### 1. WholeLine Coloring

Colors the entire log line based on field value.

```json
{
    "name": "LogLevel",
    "type": "string",
    "ColourType": "WholeLine",
    "ColourMap": {
        "122,44,75": "ERROR",
        "54,50,231": "WARNING",
        "0,128,0": "INFO"
    }
}
```

**Effect**: 
- ERROR logs display in dark red
- WARNING logs display in blue
- INFO logs display in green
- Entire log line gets colored

### 2. LineNumber Coloring

Colors only the line number/index area based on field value.

```json
{
    "name": "Component",
    "type": "string",
    "ColourType": "LineNumber",
    "ColourMap": {
        "122,44,75": "DatabaseService",
        "54,50,231": "ApplicationService",
        "255,165,0": "PaymentService"
    }
}
```

**Effect**:
- Line numbers get colored background
- `[1]` portion colored red for DatabaseService logs
- `[2]` portion colored blue for ApplicationService logs
- Main log text remains normal color

### 3. SpecificValue Coloring

Colors specific field values within the log line, supports ranges.

```json
{
    "name": "ErrorCode",
    "type": "number",
    "ColourType": "SpecificValue",
    "ColourMap": {
        "122,44,75": "1-20, 50-65",
        "54,50,231": "21-49",
        "255,0,0": "1001, 2003, 3001"
    }
}
```

**Effect**:
- Error codes 1-20 and 50-65 colored dark red
- Error codes 21-49 colored blue  
- Specific codes 1001, 2003, 3001 colored bright red
- Only the error code values are colored in the display

## Range Specifications

For `SpecificValue` coloring, you can specify:

### Single Values
```json
"255,0,0": "ERROR"           // Exact match
"0,255,0": "1001"           // Exact number
```

### Number Ranges  
```json
"122,44,75": "1-20"         // Range 1 to 20 inclusive
"54,50,231": "100-500"      // Range 100 to 500 inclusive
```

### Multiple Values/Ranges
```json
"255,0,0": "1-10, 20-30, 50"    // Ranges 1-10, 20-30, and exact value 50
"0,255,0": "ERROR, CRITICAL"     // Multiple string values
```

### Complex Examples
```json
"122,44,75": "1-20, 50-65, 100"              // Mixed ranges and values
"54,50,231": "DatabaseService, PaymentService" // Multiple components
```

## Complete Configuration Example

```json
{
    "logViewerConfig": {
        "delimiters": {
            "logStartDelimiter": "[",
            "logEndDelimiter": "]###",
            "categorySeparator": "|"
        },
        "categories": [
            {
                "name": "LogLevel",
                "type": "string",
                "order": 1,
                "ColourType": "WholeLine",
                "ColourMap": {
                    "122,44,75": "ERROR",
                    "54,50,231": "WARNING", 
                    "0,128,0": "INFO",
                    "128,128,128": "DEBUG"
                }
            },
            {
                "name": "Component",
                "type": "string", 
                "order": 2,
                "ColourType": "LineNumber",
                "ColourMap": {
                    "122,44,75": "DatabaseService",
                    "54,50,231": "ApplicationService",
                    "255,165,0": "PaymentService",
                    "128,0,128": "AuthService"
                }
            },
            {
                "name": "ErrorCode",
                "type": "number",
                "order": 3, 
                "ColourType": "SpecificValue",
                "ColourMap": {
                    "255,0,0": "1000-2000, 3000-4000",
                    "255,165,0": "500-999",
                    "0,255,0": "0"
                }
            }
        ]
    }
}
```

## Color Behavior

### Priority System
1. **WholeLine** colors override all other coloring
2. **LineNumber** colors are independent and always apply
3. **SpecificValue** colors apply to matching text within lines

### Color Mixing
- Multiple **SpecificValue** colors can appear in the same line
- **LineNumber** and **SpecificValue** can be combined
- **WholeLine** takes precedence over **SpecificValue**

### Fallback Behavior
- If no color match found, uses default text colors
- Invalid RGB values default to black (#000000)  
- Malformed ranges are ignored silently

## Visual Examples

### Before Coloring
```
[1] Line 1: ERROR | DatabaseService | Connection failed | ErrorCode: 1001
[2] Line 2: WARNING | AuthService | Invalid token | ErrorCode: 401  
[3] Line 3: INFO | PaymentService | Payment processed | ErrorCode: 0
```

### After Coloring (with config above)
```
[1] Line 1: ERROR | DatabaseService | Connection failed | ErrorCode: 1001
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
(Entire line in dark red due to LogLevel=ERROR WholeLine coloring)

[2] Line 2: WARNING | AuthService | Invalid token | ErrorCode: 401
^^^^                                                                  
(Line number [2] has colored background due to Component LineNumber coloring)

[3] Line 3: INFO | PaymentService | Payment processed | ErrorCode: 0
                                                                     ^
(Only the "0" is colored due to ErrorCode SpecificValue coloring)
```

## Usage Tips

### Effective Color Schemes
- Use **high contrast colors** for readability
- **Limit colors per scheme** to avoid confusion (3-5 colors max)
- **Test with actual data** to ensure colors are meaningful
- **Consider accessibility** - avoid red/green combinations

### Performance Notes
- **Minimal impact** - coloring is applied during display only
- **Efficient matching** - uses optimized string/number comparison
- **Memory friendly** - colors defined once, applied as needed

### Troubleshooting
- **Colors not appearing**: Check RGB format ("R,G,B")
- **Wrong values colored**: Verify exact string/number matching
- **Range not working**: Ensure proper "min-max" format
- **Conflicts**: WholeLine overrides SpecificValue

## Integration with Filtering

Color configuration works seamlessly with the enhanced filtering system:
- **Filtered results maintain colors**
- **Export functions preserve color information** (in supported formats)
- **Search highlighting** overlays color backgrounds
- **Statistics show color usage** by category

## Future Enhancements

The color system foundation supports future features:
- **Theme-based color schemes**
- **User-customizable color palettes**  
- **Conditional coloring** (if-then rules)
- **Color intensity** based on value ranges
- **Custom color picker GUI**