# Advanced Filtering Features

## Overview

The Log Viewer GUI now includes significantly advanced filtering capabilities that support complex queries, multiple simultaneous filters, and range operations.

## New Filtering Features

### 1. **Advanced Filter UI**
- **Scrollable Filter Panel** - Handle many log categories without overwhelming the interface
- **Per-Field Filter Sections** - Each log category gets its own labeled section
- **Operator Dropdowns** - Smart operators based on field type
- **Range Inputs** - Support for "from-to" ranges on numbers and dates
- **Help Text** - Context-sensitive hints for each filter type

### 2. **Multiple Simultaneous Filters**
- **Combine Multiple Filters** - Apply filters to different fields simultaneously
- **Cumulative Filtering** - Each filter narrows down the previous results
- **Search + Field Filters** - Global search works alongside field-specific filters

### 3. **Advanced String Operators**

#### Regular Strings (LogLevel, Component):
- `contains` - Partial text match
- `equals` - Exact match
- `not contains` - Exclude text
- `not equals` - Not exact match
- `starts with` - Text starts with value
- `ends with` - Text ends with value

#### Structured Strings (Details):
- `has key` - Check if key exists (e.g., "action")
- `key equals` - Check key-value pair (e.g., "action=login")
- `contains` - Search within all key-value pairs
- `not contains` - Exclude from key-value pairs

#### Array Strings (Tags):
- `contains` - Any array element contains text
- `not contains` - No array element contains text
- `contains all` - Must contain all comma-separated items
- `contains any` - Must contain at least one of comma-separated items

### 4. **Number Range Filtering**

#### Number Field Operators (ErrorCode):
- `equals` - Exact number match
- `not equals` - Not equal to number
- `greater than` - Above threshold
- `less than` - Below threshold
- `between` - Range selection (shows "to" input)
- `not between` - Outside range

#### Range Examples:
- **Single Value**: `1001` (ErrorCode equals 1001)
- **Range**: `1000` to `3000` (ErrorCode between 1000-3000)
- **Threshold**: `>= 2000` (ErrorCode greater than 2000)

### 5. **DateTime Range Filtering**

#### DateTime Field Operators (Timestamp):
- `contains` - Partial date/time match
- `equals` - Exact timestamp match
- `not contains` - Exclude date/time
- `before` - Earlier than specified time
- `after` - Later than specified time
- `between` - Time range selection
- `not between` - Outside time range

#### DateTime Examples:
- **Date**: `2025-08-08` (logs from specific date)
- **Time**: `06:50` (logs around specific time)
- **Range**: `06:50:00` to `07:00:00` (30-minute window)
- **Partial**: `ERROR` (any timestamp containing "ERROR")

## Usage Examples

### Example 1: Finding Critical Errors
1. **LogLevel** = `equals` "ERROR"
2. **Tags** = `contains` "critical"
3. **ErrorCode** = `greater than` "1000"

Result: All ERROR logs tagged as critical with high error codes

### Example 2: Database Query Issues
1. **Component** = `equals` "DatabaseService"
2. **Details** = `has key` "action"
3. **Details** = `key equals` "action=query"

Result: All database service logs with query actions

### Example 3: Time Range Analysis
1. **Timestamp** = `between` "2025-08-08 06:50:00" to "2025-08-08 07:00:00"
2. **LogLevel** = `not equals` "INFO"

Result: All non-INFO logs from a 10-minute window

### Example 4: Payment Problems
1. **Component** = `contains` "Payment"
2. **Tags** = `contains any` "payment,critical"
3. **Details** = `contains` "error"

Result: Payment-related components with critical tags containing errors

## Filter Combination Logic

Filters are applied in sequence:
1. **Global Search** (if specified) filters all logs first
2. **Field Filters** are applied one by one to narrow results
3. **Final Result** shows logs matching ALL active filters

## UI Improvements

### Filter Panel Layout
```
[Search Box]
─────────────────────
┌─ Timestamp ────────┐
│ [between ▼] [from] │
│ [to      ]         │
│ Format: YYYY-MM-DD │
└────────────────────┘

┌─ LogLevel ─────────┐
│ [equals ▼] [value] │
└────────────────────┘

┌─ Details ──────────┐
│ [has key ▼] [key]  │
│ Format: key=value  │
└────────────────────┘
```

### Dynamic Controls
- **Range inputs** appear/hide based on operator selection
- **Help text** updates based on field type
- **Operator options** change based on data type
- **Scrollable panel** handles many filter categories

## Performance Notes

- **Efficient Filtering**: Filters applied sequentially to reduce processing
- **Smart UI Updates**: Only show relevant controls for each field type
- **Memory Efficient**: Works with large log files by filtering in-memory data
- **Real-time Updates**: Filters apply immediately when "Apply Filters" is clicked

## Backward Compatibility

- **Existing configs** work unchanged
- **Old filter format** still supported
- **CLI version** remains compatible
- **Export functions** work with filtered results

## Advanced Tips

### Structured String Filtering
- Use `has key` to find logs with specific data fields
- Use `key equals` with format `key=value` for exact matches
- Use `contains` to search across all key-value pairs

### Array String Filtering
- Use comma-separated values with `contains all/any`
- Example: "critical,error" finds logs with both tags
- Case-insensitive matching

### Range Filtering
- Leave second value empty for single-value operations
- Use appropriate operators (between requires two values)
- Number ranges work with decimals (e.g., 99.99 to 150.00)

## Future Enhancements

Potential improvements for future versions:
- **Regular Expression Support** - Pattern matching in text fields
- **Date Picker Widgets** - Calendar selection for date ranges
- **Filter Presets** - Save and load common filter combinations
- **Advanced Boolean Logic** - AND/OR combinations between filters
- **Performance Optimization** - Indexing for very large log files